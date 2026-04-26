# BJJ Mental Models Chat App

An interactive AI chat application built with Python and Shiny, powered by the [BJJ Mental Models database](https://www.bjjmentalmodels.com/database). Ask questions about Brazilian Jiu-Jitsu strategic and tactical mental models and get answers grounded in the BJJ Mental Models knowledge base.

## Core Technology

The application uses:

- **[shinychat](https://posit-dev.github.io/shinychat/py/)** — chat UI component for Shiny apps
- **[chatlas](https://posit-dev.github.io/chatlas/)** — LLM provider integration, model-agnostic Python library
- **[shiny](https://shiny.posit.co/py/)** — Python web application framework

The system defaults to Claude Sonnet 4.6 via `ChatAnthropic` but can be switched to other providers (OpenAI, Google, etc.) by updating the `Chat*()` constructor in `app.py`.

## Key Configuration

The app enforces a `MAX_USER_TURNS` limit of 10 messages per session to control costs. Users reaching this threshold receive a prompt to refresh their session.

## Getting Started

### 1. Install dependencies

```bash
uv pip install shiny shinychat chatlas
```

### 2. Set your Anthropic API key

Add your API key to your environment. You can get a key from [console.anthropic.com](https://console.anthropic.com).

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Or add it to a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-key-here
```

### 3. Run the app

```bash
uv shiny run --reload app.py
```

## Credits

All BJJ mental models content is sourced from **[BJJ Mental Models](https://www.bjjmentalmodels.com)**, one of the world's top Jiu-Jitsu podcasts and educational resources, founded by Steve Kwan. Their free [database](https://www.bjjmentalmodels.com/database) distills frameworks from sport science, psychology, physics, and competitive strategy into actionable concepts for the mat.

This project is an unofficial tool and is not affiliated with or endorsed by BJJ Mental Models. All intellectual property in the database belongs to BJJ Mental Models.

## Knowledge Management

The project maintains a `knowledge-docs/` directory containing fetched documentation in markdown format. An index file (`knowledge-docs/links.md`) tracks all source URLs by category.

Fetch the BJJ Mental Models database using the `/defuddle` skill in Claude Code:

```
/defuddle https://www.bjjmentalmodels.com/database
```

Or directly via curl:

```bash
curl -s "https://defuddle.md/www.bjjmentalmodels.com/database" > knowledge-docs/bjj-mental-models-database.md
```
