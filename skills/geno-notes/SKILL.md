---
name: geno-notes
description: >-
  Project journal — tasks, timestamped journal entries, plans. Two scopes
  coexist: global (~/.geno/geno-notes/) and per-project (./geno/geno-notes/).
  Use when user says /gt-notes, wants to add/start/complete a task, jot a
  timestamped note, list or search tasks and journal entries, or move work
  between scopes.
argument-hint: "[scope|path|init|add|start|done|abandon|note|inbox|triage|list|show|search|promote|reindex|compile|lint] [args...]"
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *)"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
---

# geno-notes — Project Journal

```!
command -v geno-notes >/dev/null 2>&1 || echo "⚠️ geno-notes is not installed. Run install.sh from the geno-notes repo."
```

A persistent, greppable, concurrent-safe project journal. Replaces the legacy `geno-tools/labnotes/` layout with one file per task, chunked journal files, and two coexisting storage scopes.

## Scopes

- **Global** (`~/.geno/geno-notes/`) — cross-project knowledge, personal dev log that spans repos.
- **Project** (`./geno/geno-notes/` found by walking up from cwd) — tasks, notes, plans tied to one repo.

Active scope resolves in this order:
1. `$GENO_NOTES_SCOPE=global|project`
2. `$GENO_NOTES_DIR=<path>`
3. Project detected in cwd or ancestors
4. Global (auto-created on first use)

Any command takes `--global` or `--project` to override. Read commands take `--all` to union both.

## Commands

Parse the user's `$ARGUMENTS` and dispatch to the CLI.

### `/gt-notes` (no args) or `/gt-notes scope`
Show the active scope + both dir paths.
```bash
geno-notes scope
```

### `/gt-notes init [--global|--project]`
Scaffold a scope at the right location and write `config.toml`.
- No flag in a cwd without a project scope → creates `./geno/geno-notes/` (project).
- `--global` → ensures `~/.geno/geno-notes/` is scaffolded.

### `/gt-notes add "<description>" [--tag infra --tag security]`
Create a new task in Backlog. Returns the task ID.

### `/gt-notes start <pattern>`
Move a task from Backlog → Active. Fuzzy matches on id, slug, or title (exact > prefix > substring). If multiple tasks match in the top tier, the CLI lists them and exits 1 — ask the user to disambiguate.

### `/gt-notes done <pattern>`  /  `/gt-notes abandon <pattern>`
Complete or abandon a task. Same fuzzy-match rules.

### `/gt-notes note "<text>" [--task <pattern>] [--kind note|finding|decision|bug|milestone]`
Append a timestamped entry to `journal/YYYY/YYYY-MM.{md,jsonl}`. If `--task` is given, also appends a backlink to the task's `## Journal refs` section.

### `/gt-notes inbox "<text>"`
Free-floating quick capture — appends to `inbox.md`. Promote later with `triage`.

### `/gt-notes triage`
Interactively walk inbox items, promoting each to a task or discarding.

### `/gt-notes list [--status active|backlog|done|abandoned] [--json] [--all]`
List tasks in the active scope. `--all` unions both scopes. `--json` for programmatic use.

### `/gt-notes show <pattern> [--all]`
Render a task file + its journal refs.

### `/gt-notes search <query> [--all]`
Plain-text grep across tasks, journal, plans, inbox.

### `/gt-notes promote <pattern> [--to global|project]`
Move a task (and its plan file, if any) between scopes. Useful when a project-scope task turns out to be cross-cutting.

### `/gt-notes reindex`
Regenerate `index.md` and `tasks/_index.md`. The CLI does this automatically on every mutation, so run manually only after hand-editing a task file.

### `/gt-notes compile`
Compile primary sources into wiki pages (Karpathy llm-wiki pattern).

The primary sources (tasks, journal, plans) are the system of record. The wiki is a **derived view** — a persistent, compounding synthesis that can always be rebuilt from the primaries.

**Workflow:**

1. Run `geno-notes compile` — this dumps all source material AND existing wiki pages.
2. Read the output. Identify distinct topics, entities, themes, and connections across the sources.
3. For each topic, either **update an existing wiki page** or **create a new one**:
   - Write to `<scope-dir>/wiki/<topic-slug>.md`
   - Use `[[page-name]]` wikilinks to connect related pages
   - Cite source tasks by ID (e.g. `(task: 20260425-auth-flow)`) and journal entries by date
   - Include YAML frontmatter: `tags`, `sources` (list of task IDs / journal months referenced), `updated` (ISO date)
4. Update `<scope-dir>/wiki/index.md` — a catalog of every wiki page with a link and one-line summary, organized by category.
5. Log the compile: `geno-notes note "wiki compile: N pages created, M updated" --kind milestone`

**Page guidelines:**
- Each page covers one distinct topic, entity, or concept
- Pages should be self-contained but link to related pages
- Prefer updating over creating — the wiki compounds over time
- When sources contradict, note the contradiction and cite both sides
- Status-aware: reflect task statuses (done = resolved, active = in progress, abandoned = dropped)

### `/gt-notes lint`
Health-check the wiki against primary sources.

**Workflow:**

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

## Architecture

geno-notes implements the [Karpathy llm-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Three layers:

| Layer | geno-notes | Role |
|---|---|---|
| **Primary sources** | `tasks/`, `journal/`, `plans/`, `inbox.md` | System of record. Human + agent edited. |
| **Wiki** | `wiki/` | Derived view. Agent-generated, rebuildable. Compounds over time. |
| **Schema** | `SKILL.md`, `CLAUDE.md` | Tells the agent how to operate. |

## Files (per scope)

```
<scope-dir>/
├── index.md                       # auto-gen dashboard
├── tasks/
│   ├── _index.md                  # auto-gen list
│   └── <task-id>.md               # YYYYMMDD-<slug>.md with YAML frontmatter
├── journal/YYYY/YYYY-MM.{md,jsonl}
├── plans/<task-id>.md
├── wiki/
│   ├── index.md                   # catalog of all wiki pages
│   └── <topic-slug>.md            # compiled topic/entity pages
├── inbox.md
└── .geno-notes/
    ├── config.toml
    ├── events.jsonl               # audit log
    └── locks/                     # flock files
```

Humans edit `.md`; consumers that need structured data should read `.jsonl` (journal) or call `geno-notes list --json`.
