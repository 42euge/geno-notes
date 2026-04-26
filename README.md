# geno-notes

Project journal for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Tasks, timestamped journal entries, and plans with two coexisting scopes — global (`~/.geno/geno-notes/`) and per-project (`./geno/geno-notes/`).

## Install

```bash
geno-tools install notes
```

## Commands

| Command | Description |
|---|---|
| `/gt-notes` | Show active scope and both dir paths |
| `/gt-notes init [--global\|--project]` | Scaffold a scope at the right location |
| `/gt-notes add "<desc>" [--tag T]` | Create a new task in Backlog |
| `/gt-notes start <pattern>` | Move a task from Backlog to Active |
| `/gt-notes done <pattern>` | Complete a task |
| `/gt-notes abandon <pattern>` | Abandon a task |
| `/gt-notes note "<text>" [--task <pat>]` | Append a timestamped journal entry |
| `/gt-notes inbox "<text>"` | Quick capture to inbox |
| `/gt-notes triage` | Walk inbox items, promote or discard |
| `/gt-notes list [--status S] [--all]` | List tasks in active scope |
| `/gt-notes show <pattern> [--all]` | Render a task file + journal refs |
| `/gt-notes search <query> [--all]` | Grep across tasks, journal, plans, inbox |
| `/gt-notes promote <pat> [--to global\|project]` | Move a task between scopes |

## Scope resolution

Active scope resolves in this order:

1. `$GENO_NOTES_SCOPE` (`global` | `project`) if set
2. `$GENO_NOTES_DIR` if set — exact dir, scope from its `config.toml`
3. `./geno/geno-notes/` found walking up from cwd → **project** scope
4. Otherwise → **global** at `~/.geno/geno-notes/` (auto-created)

Use `--global` or `--project` on any command to override. Use `--all` on reads to union both scopes.

## Repository structure

```
geno-notes/
├── package.json          # Vercel Skills manifest
├── .geno-agents          # agent identity for auto-registration
├── CLAUDE.md             # agent instructions
├── install.sh            # installer (venv, symlinks, global scope)
├── pyproject.toml        # Python package metadata
├── commands/
│   └── gt-notes.md       # slash command dispatcher
├── skills/
│   └── geno-notes/
│       └── SKILL.md      # skill definition
├── geno_notes/           # Python CLI package
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── events.py
│   ├── ids.py
│   ├── indexer.py
│   ├── journal.py
│   ├── locks.py
│   ├── paths.py
│   ├── search.py
│   └── tasks.py
└── tests/
    ├── conftest.py
    ├── test_ids.py
    ├── test_journal.py
    ├── test_locks.py
    ├── test_paths.py
    ├── test_scope.py
    └── test_tasks.py
```

## Storage layout (v0.1)

```
<scope-dir>/
├── index.md                          # auto-gen dashboard
├── tasks/
│   ├── _index.md                     # auto-gen list grouped by status
│   └── <task-id>.md                  # frontmatter: id, status, created, activated, completed, tags
├── journal/
│   └── YYYY/
│       ├── YYYY-MM.md                # human-readable
│       └── YYYY-MM.jsonl             # machine-readable
├── plans/
│   └── <task-id>.md
├── wiki/                             # llm-wiki output
│   └── README.md
├── inbox.md
└── .geno-notes/
    ├── config.toml
    ├── events.jsonl                  # append-only audit log
    └── locks/
```

## Runtime

Python CLI installed into `~/.geno/venv`. PATH shim at `~/.local/bin/geno-notes`.

## Design

See `docs/` or the [approved plan](./docs/plan.md) for the full design rationale.

## License

MIT
