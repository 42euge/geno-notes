---
name: geno-notes-sites-generate
description: >-
  Generate a MkDocs Material website from geno-notes content.
  Builds tasks, journal entries, wiki pages, and plans into a browsable
  static site. Use when user says /geno-notes-sites-generate, wants to
  build or preview a site from their notes, or deploy their journal as a website.
argument-hint: "[--serve] [--open] [--port PORT] [--all] [--global|--project]"
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *)"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
observability:
  success_signal: "MkDocs site built (or serve started) with content from active scope"
  failure_signals:
    - "geno-notes site command fails or staging directory is empty"
    - "mkdocs or mkdocs-material not installed and user declines install"
    - "serve mode fails to bind port"
  knowledge_reads:
    - "tasks, journal entries, wiki pages, and plans from active scope"
  knowledge_writes:
    - "static site at .geno-notes/_site_staging/site/"
---

# Generate Site

Generate a MkDocs Material website from the notes in the active scope. The site is built to `.geno-notes/_site_staging/site/` (never checked in).

## Input

`$ARGUMENTS` are passed as flags to `geno-notes site`.

## Options

| Flag | Effect |
|------|--------|
| `--open` | Build and open the site in the default browser |
| `--serve` | Start `mkdocs serve` for live-reloading preview |
| `--port PORT` | Port for serve mode (default 8000) |
| `--all` | Merge project + global scopes into one site |
| `--global` | Force global scope |
| `--project` | Force project scope |

Default behavior (no flags): build, then ask the user if they want to open.

## Examples

```bash
geno-notes site --open
geno-notes site --serve --all
geno-notes site --serve --port 3000 --project
```

## What it builds

The site generator stages content from the active scope(s) into a temporary MkDocs project:

- **Tasks** — grouped by status (active, backlog, done, abandoned)
- **Journal** — monthly entries rendered as timeline pages
- **Wiki** — compiled topic pages with wikilinks
- **Plans** — task-linked planning documents

## Completion

When this skill finishes, emit a trace:

```bash
geno-trace emit \
  --skill geno-notes-sites-generate \
  --status <success|failure|abandoned> \
  --tool-calls <approximate count> \
  --errors <count of tool/command errors>
```

- `success` = site built to _site_staging/site/ (or serve started and accessible)
- `failure` = site command failed, missing dependencies not resolved, or serve could not bind port
- `abandoned` = user stopped early

## Dependencies

Requires `mkdocs` and `mkdocs-material`. The CLI will prompt to install them if missing.
