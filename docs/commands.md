# Commands

## Scope Management

**`/gt-notes`** or **`/gt-notes scope`**

Show the active scope and both directory paths (global + project).

**`/gt-notes init [--global|--project]`**

Scaffold a scope at the right location and write `config.toml`.

- No flag in a cwd without a project scope — creates `./geno/geno-notes/` (project)
- `--global` — ensures `~/.geno/geno-notes/` is scaffolded

---

## Task Lifecycle

**`/gt-notes add "<description>" [--tag T ...]`**

Create a new task in Backlog. Returns the task ID.

**`/gt-notes start <pattern>`**

Move a task from Backlog to Active. Fuzzy matches on id, slug, or title (exact > prefix > substring). If multiple tasks match, the CLI lists them and exits 1.

**`/gt-notes done <pattern>`**

Complete a task. Same fuzzy-match rules.

**`/gt-notes abandon <pattern>`**

Abandon a task. Same fuzzy-match rules.

!!! tip
    Patterns are matched in priority order: exact match, then prefix, then substring. If ambiguous, narrow the pattern.

---

## Journal

**`/gt-notes note "<text>" [--task <pattern>] [--kind note|finding|decision|bug|milestone]`**

Append a timestamped entry to `journal/YYYY/YYYY-MM.{md,jsonl}`. If `--task` is given, also appends a backlink to the task's journal refs section.

**`/gt-notes inbox "<text>"`**

Free-floating quick capture — appends to `inbox.md`. Promote later with `triage`.

**`/gt-notes triage`**

Interactively walk inbox items, promoting each to a task or discarding.

---

## Search

**`/gt-notes list [--status active|backlog|done|abandoned] [--json] [--all]`**

List tasks in the active scope. `--all` unions both scopes. `--json` for programmatic use.

**`/gt-notes show <pattern> [--all]`**

Render a task file plus its journal refs.

**`/gt-notes search <query> [--all]`**

Plain-text grep across tasks, journal, plans, inbox.

---

## Cross-Scope

**`/gt-notes promote <pattern> [--to global|project]`**

Move a task (and its plan file, if any) between scopes. Useful when a project-scope task turns out to be cross-cutting.

---

## Maintenance

**`/gt-notes reindex`**

Regenerate `index.md` and `tasks/_index.md`. The CLI does this automatically on every mutation — run manually only after hand-editing a task file.

**`/gt-notes compile`**

v0.2 stub. Reserved for llm-wiki compilation from tasks + journal into `wiki/`. Currently a no-op.

---

## Storage Layout

Each scope directory follows this structure:

```
<scope-dir>/
├── index.md                       # auto-gen dashboard
├── tasks/
│   ├── _index.md                  # auto-gen list by status
│   └── <task-id>.md               # YAML frontmatter: id, status, tags
├── journal/
│   └── YYYY/
│       ├── YYYY-MM.md             # human-readable
│       └── YYYY-MM.jsonl          # machine-readable
├── plans/
│   └── <task-id>.md
├── inbox.md
└── .geno-notes/
    ├── config.toml
    ├── events.jsonl               # append-only audit log
    └── locks/
```

Humans edit `.md`; consumers that need structured data should read `.jsonl` (journal) or call `geno-notes list --json`.
