---
name: geno-notes-wiki-compile
description: >-
  Compile primary sources (tasks, journal, plans) into wiki pages using the
  Karpathy llm-wiki pattern. Use when user says /geno-notes-wiki-compile,
  wants to compile or rebuild the wiki, synthesize notes into topic pages,
  or update the wiki from recent activity.
argument-hint: "[--global|--project]"
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *) Read Write Edit"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
observability:
  success_signal: "wiki pages created or updated and index.md refreshed"
  failure_signals:
    - "geno-notes compile command fails or returns no source material"
    - "write to wiki directory fails (permissions, missing scope dir)"
    - "compile produces zero pages from non-empty sources"
  knowledge_reads:
    - "primary sources (tasks, journal entries, plans) via geno-notes compile"
    - "existing wiki pages for update-vs-create decisions"
  knowledge_writes:
    - "wiki topic pages in <scope-dir>/wiki/<topic-slug>.md"
    - "wiki index at <scope-dir>/wiki/index.md"
    - "milestone note logged via geno-notes note"
---

# Wiki Compile

Compile primary sources into wiki pages (Karpathy llm-wiki pattern).

The primary sources (tasks, journal, plans) are the system of record. The wiki is a **derived view** — a persistent, compounding synthesis that can always be rebuilt from the primaries.

## Input

`$ARGUMENTS` are passed as flags to `geno-notes compile`.

## Options

| Flag | Effect |
|------|--------|
| `--global` | Force global scope |
| `--project` | Force project scope |

## Workflow

1. Run `geno-notes compile` — this dumps all source material AND existing wiki pages.
2. Read the output. Identify distinct topics, entities, themes, and connections across the sources.
3. For each topic, either **update an existing wiki page** or **create a new one**:
   - Write to `<scope-dir>/wiki/<topic-slug>.md`
   - Use `[[page-name]]` wikilinks to connect related pages
   - Cite source tasks by ID (e.g. `(task: 20260425-auth-flow)`) and journal entries by date
   - Include YAML frontmatter: `tags`, `sources` (list of task IDs / journal months referenced), `updated` (ISO date)
4. Update `<scope-dir>/wiki/index.md` — a catalog of every wiki page with a link and one-line summary, organized by category.
5. Log the compile: `geno-notes note "wiki compile: N pages created, M updated" --kind milestone`

## Page guidelines

- Each page covers one distinct topic, entity, or concept
- Pages should be self-contained but link to related pages
- Prefer updating over creating — the wiki compounds over time
- When sources contradict, note the contradiction and cite both sides
- Status-aware: reflect task statuses (done = resolved, active = in progress, abandoned = dropped)

## Examples

```bash
geno-notes compile
geno-notes compile --global
geno-notes compile --project
```

## Completion

When this skill finishes, emit a trace:

```bash
geno-trace emit \
  --skill geno-notes-wiki-compile \
  --status <success|failure|abandoned> \
  --tool-calls <approximate count> \
  --errors <count of tool/command errors>
```

- `success` = wiki pages created/updated and index.md refreshed from primary sources
- `failure` = compile produced no pages, write errors, or source material could not be read
- `abandoned` = user stopped early
