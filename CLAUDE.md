# BJJ Mental Models Chat App

This is a shinychat-based interactive application built in Python, focused on the BJJ Mental Models database (https://www.bjjmentalmodels.com/database).

## Key Configuration Detail

The app includes a per-session message limit controlled by `MAX_USER_TURNS` in `app.py`. This single configuration value is referenced in both the welcome message and the turn-checking logic, meaning it only requires updating in one location. The README and welcome copy should also be adjusted if they explicitly mention this number.

## Tech Stack

- **shinychat** (`shinychat` Python package) — chat UI component for Shiny
- **chatlas** — LLM provider integration; defaults to `ChatOpenAI` with GPT-4o
- **shiny** — application framework

Install dependencies:

```bash
uv pip install shiny shinychat chatlas
```

## App Entry Point

`app.py` is the main application file. The LLM provider and model are configured there via `chatlas`. To switch models or providers, update the `Chat*()` constructor in `app.py`.

## Knowledge Documentation System

Reference materials are stored in `knowledge-docs/` (which is git-ignored). The primary source is the BJJ Mental Models database. New sources can be incorporated using the `/defuddle` skill:

```
/defuddle https://www.bjjmentalmodels.com/database
```

Alternatively, fetch content via curl:

```bash
curl -s "https://defuddle.md/www.bjjmentalmodels.com/database" > knowledge-docs/bjj-mental-models-database.md
```

An index file `knowledge-docs/links.md` tracks all previously fetched URLs and should be updated whenever new documentation is added to the system.
