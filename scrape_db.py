"""
Scrape the BJJ Mental Models database into knowledge-docs/.

Outputs:
  knowledge-docs/database/  -- one .md file per model page
  knowledge-docs/bjj-mental-models-database.md  -- single combined file
"""

import re
import time
import json
from pathlib import Path
import httpx
from bs4 import BeautifulSoup

_REDIRECT_RE = re.compile(
    r"[Ss]ee \[.*?\]\((https?://bjjmentalmodels\.com/[^)]+)\)",
)

DB_URL = "https://www.bjjmentalmodels.com/database"
JINA_BASE = "https://r.jina.ai"
OUT_DIR = Path("knowledge-docs/database")
COMBINED_FILE = Path("knowledge-docs/bjj-mental-models-database.md")
INDEX_FILE = Path("knowledge-docs/bjj-mental-models-index.json")

SECTIONS = [
    "Learning Models",
    "Mechanical Models",
    "Social Models",
    "Strategic\xa0Models",
]


def section_slug(section: str) -> str:
    return section.strip().lower().replace("\xa0", "-").replace(" ", "-")


def get_all_links() -> list[tuple[str, str]]:
    """Return list of (url, section) tuples."""
    resp = httpx.get(DB_URL, follow_redirects=True, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    links = []
    for section in SECTIONS:
        h2 = soup.find("h2", string=section)
        if not h2:
            print(f"  WARNING: section not found: {section!r}")
            continue
        parent = h2.find_parent("div")
        section_links = [a["href"] for a in parent.find_all("a", href=True)]
        print(f"  {section}: {len(section_links)} links")
        links.extend((url, section) for url in section_links)

    return links


def extract_iframes(url: str) -> list[str]:
    """Reconstruct Buzzsprout iframe tags from the script embeds on the raw page."""
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")
        iframes = []
        for script in soup.find_all("script", src=True):
            src = script["src"]
            if "buzzsprout.com" not in src:
                continue
            # src: https://www.buzzsprout.com/243161/episodes/17323513-slug.js?container_id=...&player=small
            episode_url = src.split(".js?")[0]  # strip .js and query string
            iframe_src = (
                f"{episode_url}?client_source=small_player&iframe=true&referrer={src}"
            )
            title = script.get("title", "")
            iframe_tag = (
                f'<iframe src="{iframe_src}" width="100%" height="200" '
                f'frameborder="0" scrolling="no" title="{title}"></iframe>'
            )
            iframes.append(iframe_tag)
        return iframes
    except Exception:
        return []


def build_content(raw: str, url: str, section: str, iframes: list[str]) -> tuple[str, str, str | None]:
    """Parse Jina output into YAML frontmatter + clean markdown body. Returns (title, content, redirect_url)."""
    title = ""
    body = raw

    # extract title from Jina header
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("Title:"):
            title = line.removeprefix("Title:").strip()
            break

    # extract body after "Markdown Content:"
    if "Markdown Content:" in raw:
        body = raw.split("Markdown Content:", 1)[1].lstrip("\n")

    # strip promotional footer
    for marker in ["### Master this mental model", "### Master this model"]:
        if marker in body:
            body = body[:body.index(marker)].rstrip()
            break

    # prepend podcast iframes
    if iframes:
        podcast_block = "## Podcast Episode\n\n" + "\n\n".join(iframes)
        body = podcast_block + "\n\n" + body.lstrip("\n")

    redirect_url = None
    if "This mental model is deprecated" in body:
        m = _REDIRECT_RE.search(body)
        if m:
            redirect_url = m.group(1).rstrip("/")

    extra = ""
    if redirect_url:
        extra = f"deprecated: true\nredirects_to: {redirect_url}\n"
    frontmatter = f"---\ntitle: {title}\nurl: {url}\nsection: {section}\n{extra}---\n\n"
    return title, frontmatter + body.strip(), redirect_url


def scrape_page(url: str, section: str = "", retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            resp = httpx.get(f"{JINA_BASE}/{url}", timeout=60, follow_redirects=True)
            resp.raise_for_status()
            iframes = extract_iframes(url)
            title, content, redirect_url = build_content(resp.text, url, section, iframes)
            result = dict(url=url, title=title, section=section, content=content)
            if redirect_url:
                result["deprecated"] = True
                result["redirects_to"] = redirect_url
            return result
        except Exception as e:
            if attempt == retries - 1:
                print(f"  FAILED {url}: {e}")
                return dict(url=url, title="", section=section, content="")
            time.sleep(2**attempt)
            time.sleep(2**attempt)


def slug(url: str) -> str:
    return url.rstrip("/").split("/")[-1] or "index"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching database index: {DB_URL}")
    links = get_all_links()
    print(f"Total links: {len(links)}\n")

    pages = []
    for i, (url, section) in enumerate(links, 1):
        print(f"[{i}/{len(links)}] [{section}] {url}")
        page = scrape_page(url, section=section)
        pages.append(page)

        # save into section subdirectory
        section_dir = OUT_DIR / section_slug(section)
        section_dir.mkdir(exist_ok=True)
        out_path = section_dir / f"{slug(url)}.md"
        out_path.write_text(page["content"], encoding="utf-8")

        if i < len(links):
            time.sleep(0.5)

    # save index JSON (url + title + section + optional deprecated/redirects_to, no content)
    index = []
    for p in pages:
        entry = {"url": p["url"], "title": p["title"], "section": p["section"]}
        if p.get("deprecated"):
            entry["deprecated"] = True
            entry["redirects_to"] = p["redirects_to"]
        index.append(entry)
    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"\nIndex written: {INDEX_FILE} ({len(index)} entries)")

    # save combined file grouped by section
    parts = [f"# BJJ Mental Models Database\n\nScraped from {DB_URL}\n\n---\n"]
    for section in SECTIONS:
        section_pages = [p for p in pages if p["section"] == section]
        if not section_pages:
            continue
        parts.append(f"\n\n# {section.strip()}\n\n---")
        for page in section_pages:
            if page["content"]:
                parts.append(f"\n\n{page['content']}\n\n---")
    COMBINED_FILE.write_text("\n".join(parts), encoding="utf-8")
    print(f"Combined file written: {COMBINED_FILE}")


if __name__ == "__main__":
    main()
