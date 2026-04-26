"""
Convert already-scraped .md files from Jina header format to YAML frontmatter.
Run once after scrape_db.py finishes.
"""

from pathlib import Path

DB_DIR = Path("knowledge-docs/database")

SECTION_MAP = {
    "learning-models": "Learning Models",
    "mechanical-models": "Mechanical Models",
    "social-models": "Social Models",
    "strategic-models": "Strategic Models",
}


def convert(path: Path, section: str):
    raw = path.read_text(encoding="utf-8")

    # already converted
    if raw.startswith("---"):
        return False

    title = ""
    url = ""
    body = raw

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("Title:"):
            title = line.removeprefix("Title:").strip()
        elif line.startswith("URL Source:"):
            url = line.removeprefix("URL Source:").strip()

    if "Markdown Content:" in raw:
        body = raw.split("Markdown Content:", 1)[1].lstrip("\n").strip()

    frontmatter = f"---\ntitle: {title}\nurl: {url}\nsection: {section}\n---\n\n"
    path.write_text(frontmatter + body, encoding="utf-8")
    return True


def main():
    converted = 0
    for section_dir in DB_DIR.iterdir():
        if not section_dir.is_dir():
            continue
        section = SECTION_MAP.get(section_dir.name, section_dir.name)
        for md_file in sorted(section_dir.glob("*.md")):
            if convert(md_file, section):
                converted += 1
                print(f"  converted: {md_file}")
    print(f"\nDone. {converted} file(s) converted.")


if __name__ == "__main__":
    main()
