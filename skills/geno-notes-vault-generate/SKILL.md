---
name: geno-notes-vault-generate
description: >-
  Generate an Obsidian vault from geno-notes content.
  Builds tasks, journal entries, wiki pages, and plans into a browsable
  Obsidian vault with graph view, MOCs, and wikilinks. Use when user says
  /geno-notes-vault-generate, wants to open their notes in Obsidian, or
  export their journal as an Obsidian vault.
argument-hint: "[--all] [--global|--project]"
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *) Bash(open *)"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
observability:
  success_signal: "Obsidian vault staged at _vault_staging/ with content ready to open"
  failure_signals:
    - "geno-notes vault command fails or produces empty staging directory"
    - "vault path not captured from output"
    - "Obsidian open URI fails or Obsidian not installed"
  knowledge_reads:
    - "tasks, journal entries, wiki pages, and plans from active scope"
  knowledge_writes:
    - "Obsidian vault directory at .geno-notes/_vault_staging/"
---

# Generate Obsidian Vault

Generate an Obsidian vault from the notes in the active scope. The vault is created at `.geno-notes/_vault_staging/` (never checked in).

## Input

`$ARGUMENTS` are passed as flags to `geno-notes vault`.

## Options

| Flag | Effect |
|------|--------|
| `--all` | Merge project + global scopes into one vault |
| `--global` | Force global scope |
| `--project` | Force project scope |

## Workflow

1. Run `geno-notes vault` with any scope flags from `$ARGUMENTS`. Pipe `n` to stdin to skip the interactive prompt: `echo n | geno-notes vault [flags]`
2. Capture the vault path from the "Vault ready →" output line.
3. Report what was generated — number of tasks, journal months, wiki pages, plans staged.
4. Ask the user if they'd like to open the vault in Obsidian.
5. If yes, open it: `open "obsidian://open?path=<vault-path>"`

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

## Examples

```bash
geno-notes vault
geno-notes vault --all
geno-notes vault --project
```

## Completion

When this skill finishes, emit a trace:

```bash
geno-trace emit \
  --skill geno-notes-vault-generate \
  --status <success|failure|abandoned> \
  --tool-calls <approximate count> \
  --errors <count of tool/command errors>
```

- `success` = vault staged at _vault_staging/ with content, user informed (and optionally opened in Obsidian)
- `failure` = vault command failed, staging directory empty, or vault path not captured
- `abandoned` = user stopped early
