from pathlib import Path
import re
import json
import html as html_lib
from difflib import get_close_matches
from dotenv import load_dotenv
from chatlas import ChatAnthropic, ContentToolResult
from faicons import icon_svg
from shiny import App, reactive, ui, Session

load_dotenv()

MAX_USER_TURNS = 10

_HERE = Path(__file__).parent
DB_DIR = _HERE / "knowledge-docs" / "database"

SECTION_DIRS = {
    "Learning Models": "learning-models",
    "Mechanical Models": "mechanical-models",
    "Social Models": "social-models",
    "Strategic Models": "strategic-models",
}

INDEX: list[dict] = [
    {**e, "section": e["section"].replace("\xa0", " ")}
    for e in json.loads(
        (_HERE / "knowledge-docs" / "bjj-mental-models-index.json").read_text(encoding="utf-8")
    )
]


# --- RAG helpers ---

def _entry_path(entry: dict) -> Path:
    slug = entry["url"].rstrip("/").split("/")[-1]
    folder = SECTION_DIRS.get(entry["section"], "")
    return DB_DIR / folder / f"{slug}.md"


def _read_body(entry: dict, strip_iframes: bool = False) -> str:
    path = _entry_path(entry)
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        _, _, body = text.split("---", 2)
    else:
        body = text
    if strip_iframes:
        # for search: drop podcast section entirely so iframes don't pollute text matching
        body = re.sub(r"## Podcast Episode.*?(?=\n##|\Z)", "", body, flags=re.DOTALL)
        body = re.sub(r"<iframe[^>]*>.*?</iframe>", "", body, flags=re.DOTALL)
    return body.strip()


# --- Tools ---

def _make_tools():
    def get_mental_models(titles: list[str]) -> str:
        """Get the full content of one or more BJJ mental models by title.

        Use this whenever the user asks about specific models or concepts by name.
        Pass all desired titles in a single call to avoid multiple round-trips.
        Fuzzy matching is applied, so approximate titles are fine.

        Parameters
        ----------
        titles:
            Names of the mental models to retrieve
            (e.g. ['Position Over Submission', 'Win Conditions']).
        """
        all_titles = [e["title"] for e in INDEX]
        sections: list[str] = []

        for title in titles:
            matches = get_close_matches(title, all_titles, n=1, cutoff=0.3)
            if not matches:
                sections.append(
                    f"No model found matching '{title}'. "
                    "Try search_models() to find what's available."
                )
                continue
            entry = next(e for e in INDEX if e["title"] == matches[0])
            if entry.get("deprecated") and entry.get("redirects_to"):
                redirect_slug = entry["redirects_to"].rstrip("/").split("/")[-1]
                replacement = next(
                    (e for e in INDEX if e["url"].rstrip("/").split("/")[-1] == redirect_slug),
                    None,
                )
                if replacement:
                    entry = replacement
            body = _read_body(entry)
            if not body:
                sections.append(f"Could not read content for '{entry['title']}'.")
                continue
            sections.append(
                f"# {entry['title']}\nSection: {entry['section']}\nURL: {entry['url']}\n\n{body.strip()}"
            )

        return "\n\n---\n\n".join(sections)

    def search_models(queries: list[str]) -> str:
        """Search for BJJ mental models by keyword across titles and content.

        Use this when the user asks a broad question, mentions a theme, or when
        you're not sure which specific model(s) to retrieve. Pass all relevant
        search terms in a single call to avoid multiple round-trips. Returns
        matching model titles and a short snippet from each.

        Parameters
        ----------
        queries:
            One or more keywords or phrases to search for
            (e.g. ['competition anxiety', 'guard passing']).
        """
        seen: set[str] = set()
        results_by_query: dict[str, list[tuple[str, str, str]]] = {}

        for query in queries:
            q = query.lower()
            matches = []
            for entry in INDEX:
                if entry.get("deprecated"):
                    continue
                if entry["title"] in seen:
                    continue
                body = _read_body(entry, strip_iframes=True)
                if q in entry["title"].lower() or q in body.lower():
                    snippet = next(
                        (l.strip().lstrip("#*").strip() for l in body.splitlines() if l.strip()),
                        "",
                    )
                    matches.append((entry["title"], entry["section"], snippet[:120]))
                    seen.add(entry["title"])
            results_by_query[query] = matches

        total = sum(len(v) for v in results_by_query.values())
        if total == 0:
            return f"No models found matching: {', '.join(repr(q) for q in queries)}."

        lines = [f"Found {total} model(s) across {len(queries)} search term(s):\n"]
        shown = 0
        for query, matches in results_by_query.items():
            if not matches:
                lines.append(f"**'{query}'**: no matches.")
                continue
            lines.append(f"**'{query}'** ({len(matches)} match(es)):")
            for title, section, snippet in matches[:20]:
                lines.append(f"  - **{title}** ({section}): {snippet}")
                shown += 1
            if len(matches) > 20:
                lines.append(f"  ...and {len(matches) - 20} more for this term.")
        return "\n".join(lines)

    return get_mental_models, search_models


# --- Prompts ---

def _build_model_index() -> str:
    lines = []
    for section in SECTION_DIRS:
        titles = [e["title"] for e in INDEX if e["section"] == section]
        lines.append(f"\n### {section}\n" + ", ".join(titles))
    return "\n".join(lines)


_prompt_base = (_HERE / "system-prompt.md").read_text(encoding="utf-8")
SYSTEM_PROMPT = (
    _prompt_base
    + "\n\n## Available Models\n\n"
    + "Use `get_mental_models(titles)` to retrieve one or more models' full content in a single call "
    + "and `search_models(queries)` to find relevant models — pass multiple terms in one call to avoid round-trips.\n"
    + _build_model_index()
)

_welcome_template = (_HERE / "welcome-message.md").read_text(encoding="utf-8")
WELCOME = (
    _welcome_template
    .replace("{MAX_USER_TURNS}", str(MAX_USER_TURNS))
    .replace("{MODEL_COUNT}", str(len(INDEX)))
)

_ASSISTANT_ICON = icon_svg("podcast")

_PODCAST_PLAYER_SCRIPT = ui.tags.script("""
if (!customElements.get('buzzsprout-player')) {
  class BuzzsproutPlayer extends HTMLElement {
    connectedCallback() {
      const src = this.getAttribute('src');
      if (!src) return;
      this.style.cssText = 'display:block;margin-top:8px';
      const iframe = document.createElement('iframe');
      iframe.src = src;
      iframe.width = '100%';
      iframe.height = '200';
      iframe.setAttribute('frameborder', '0');
      iframe.setAttribute('scrolling', 'no');
      this.appendChild(iframe);
    }
  }
  customElements.define('buzzsprout-player', BuzzsproutPlayer);
}
""")

# --- UI ---

app_ui = ui.page_fillable(
    _PODCAST_PLAYER_SCRIPT,
    ui.chat_ui(
        "chat",
        messages=[WELCOME],
        placeholder="Ask about any BJJ mental model...",
        height="100%",
        icon_assistant = icon_svg("podcast")
    ),
    fillable_mobile=True,
)


# --- Server ---

def server(input, output, session: Session):
    chat = ui.Chat(id="chat")
    chat.update_user_input(placeholder="Ask about any BJJ mental model...")

    turn_count = reactive.value(0)

    get_mental_models, search_models = _make_tools()
    client = ChatAnthropic(
        model="claude-sonnet-4-6",
        system_prompt=SYSTEM_PROMPT,
    )
    client.register_tool(get_mental_models)
    client.register_tool(search_models)

    @chat.on_user_submit
    async def _():
        user_input = chat.user_input()

        count = turn_count.get() + 1
        turn_count.set(count)

        if count > MAX_USER_TURNS:
            await chat.append_message(
                f"You've reached the {MAX_USER_TURNS}-message limit for this session. "
                "Please refresh the page to start a new conversation."
            )
            return

        collected_iframes: list[str] = []

        def _capture_iframes(result: ContentToolResult) -> None:
            text = result.value if isinstance(result.value, str) else ""
            for src in re.findall(r'<iframe\b[^>]*?src="([^"]+)"', text):
                collected_iframes.append(src)

        remove_callback = client.on_tool_result(_capture_iframes)
        response = await client.stream_async(user_input, content="all")
        # Use _append_message_stream directly so we can await full completion
        # before reading collected_iframes (append_message_stream uses
        # extended_task and returns before the stream finishes).
        await chat._append_message_stream(response)
        remove_callback()

        for src in collected_iframes:
            escaped = html_lib.escape(src)
            await chat.append_message(
                ui.HTML(
                    f'<a href="{escaped}" target="_blank" rel="noopener">🎙 Open episode in browser</a>'
                    f'<buzzsprout-player src="{escaped}"></buzzsprout-player>'
                )
            )


app = App(app_ui, server)
