---
name: geno-notes-wiki-lint
description: >-
  Health-check the wiki against primary sources. Detect stale pages, orphans,
  missing pages, contradictions, and dead references, then fix them.
  Use when user says /geno-notes-wiki-lint, wants to lint or clean up the wiki,
  or check wiki health.
argument-hint: "[--global|--project]"
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *) Read Write Edit"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
---

# Wiki Lint

Health-check the wiki against primary sources.

## Input

`$ARGUMENTS` are passed as flags to `geno-notes lint`.

## Options

| Flag | Effect |
|------|--------|
| `--global` | Force global scope |
| `--project` | Force project scope |

## Workflow

1. Run `geno-notes lint` — this dumps existing wiki pages AND all source material.
2. Read the output. Check for:
   - **Stale pages** — wiki claims that newer tasks/journal entries have superseded
   - **Orphan pages** — wiki pages with no inbound wikilinks from other pages
   - **Missing pages** — topics referenced via `[[wikilink]]` but no page exists
   - **Gaps** — important topics in the sources that have no wiki page yet
   - **Contradictions** — wiki pages that conflict with each other or with source material
   - **Dead references** — citations to task IDs or journal entries that no longer exist
3. Report findings as a checklist. For each issue, state what's wrong and suggest a fix.
4. If the user approves, apply fixes directly (update/create/delete wiki pages).
5. Log the lint: `geno-notes note "wiki lint: N issues found, M fixed" --kind milestone`

## Examples

```bash
geno-notes lint
geno-notes lint --global
geno-notes lint --project
```
