---
name: defuddle
description: Fetch a URL as clean raw markdown using defuddle.md. Use when the user wants to fetch a webpage as markdown, save a reference source, or populate a ref-sources/ folder. Trigger phrases include "fetch with defuddle", "get the markdown for", "save to ref-sources", or any request to fetch a URL as clean markdown without AI summarization.
disable-model-invocation: true
allowed-tools: Bash, Write, Read, Glob
---

# Defuddle — Fetch URL as Raw Markdown

Fetch $ARGUMENTS as clean markdown using defuddle.md.

## How defuddle works

Prepend `https://defuddle.md/` to the URL path (strip the `https://` from the original URL):

- `https://example.com/some/page/` → `https://defuddle.md/example.com/some/page/`

## Steps

1. Parse the URL from $ARGUMENTS to build the defuddle URL
2. Determine the output filename from the URL path (last meaningful path segment + `.md`)
3. If a `ref-sources/` directory exists in the project, save there by default; otherwise save in the current directory
4. Fetch and save:

```bash
curl -s "https://defuddle.md/{url-without-https://}" > {output-path}
```

5. Confirm the file was written and show the first few lines

## Notes

- Works for HTML pages. Does not work for PDFs — note this to the user and skip.
- If the user provides multiple URLs, fetch them all in parallel using a single Bash command with `&` and `wait`, or sequentially with `&&`.
- Do not use WebFetch — it summarizes content through an AI model and loses detail. Always use `curl` directly.
- The saved file will contain defuddle's YAML frontmatter (title, source, language, word_count) followed by the verbatim page content as markdown.