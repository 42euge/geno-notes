---
name: geno-notes-vault-generate
description: >-
  Generate an Obsidian vault from geno-notes content.
  Builds tasks, journal entries, wiki pages, and plans into a browsable
  Obsidian vault with graph view, MOCs, and wikilinks. Use when user says
  /geno-notes-vault-generate, wants to open their notes in Obsidian, or
  export their journal as an Obsidian vault.
argument-hint: "[--open] [--all] [--global|--project]"
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *)"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
---

# Generate Obsidian Vault

Generate an Obsidian vault from the notes in the active scope. The vault is created at `.geno-notes/_vault_staging/` (never checked in).

## Input

`$ARGUMENTS` are passed as flags to `geno-notes vault`.

## Options

| Flag | Effect |
|------|--------|
| `--open` | Build and open the vault in Obsidian |
| `--all` | Merge project + global scopes into one vault |
| `--global` | Force global scope |
| `--project` | Force project scope |

Default behavior (no flags): build, then ask the user if they want to open in Obsidian.

## Examples

```bash
geno-notes vault --open
geno-notes vault --all
geno-notes vault --open --project
```

## What it builds

The vault generator stages content from the active scope(s) into an Obsidian-ready directory:

- **Home.md** — Map of Content (MOC) linking to all sections
- **Tasks/** — one file per task with frontmatter, plus `_index.md` MOC grouped by status
- **Journal/** — monthly entries preserving the `YYYY/YYYY-MM.md` structure
- **Wiki/** — compiled topic pages with native `[[wikilinks]]`
- **Plans/** — task-linked planning documents
- **Inbox.md** — quick captures
- **.obsidian/** — vault config with graph view color groups, workspace defaults

## Obsidian features

- **Graph view** — color-coded by section (Tasks=purple, Journal=teal, Wiki=orange, Plans=gray)
- **Wikilinks** — `[[page]]` links work natively (geno-notes already uses this format)
- **Tags** — task tags rendered as `#tag` for Obsidian tag search
- **MOCs** — Home and Tasks index pages for navigation

## Dependencies

Requires Obsidian to be installed for `--open`. The vault itself is plain markdown — no build step needed.
