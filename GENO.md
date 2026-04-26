# geno-notes — project journal skillset

Project journal for AI coding agents: tasks, timestamped journal entries, plans. Two coexisting scopes — global (`~/.geno/geno-notes/`) and per-project (`./geno/geno-notes/`).

## Skills

| Skill | Sub-skillset | Slash command |
|-------|-------------|---------------|
| geno-notes | — | — (umbrella) |

## Repo structure

```
geno-notes/
├── GENO.md              # agent instructions (this file)
├── SKILL.md             # umbrella skill manifest
├── genotools.yaml       # geno-tools manifest
├── skills/
│   └── geno-notes/      #   umbrella skill
│       └── SKILL.md
├── commands/
│   └── gt-notes.md      #   slash command dispatcher
├── geno_notes/          # Python CLI package
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
├── docs/                # MkDocs Material site
├── tests/
└── pyproject.toml       # Python package metadata
```

## Conventions

- geno-notes is a single-skill skillset backed by a Python CLI. Subcommands are dispatched via the CLI, not separate skill folders.
- The slash command `/gt-notes` dispatches to the `geno-notes` CLI binary.

## Architecture

geno-notes implements the [Karpathy llm-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Three layers:

| Layer | geno-notes | Role |
|---|---|---|
| **Primary sources** | `tasks/`, `journal/`, `plans/`, `inbox.md` | System of record. Human + agent edited. |
| **Wiki** | `wiki/` | Derived view. Agent-generated, rebuildable. Compounds over time. |
| **Schema** | `SKILL.md`, `GENO.md` | Tells the agent how to operate. |

## Runtime

- **Python CLI**: `pyproject.toml` entry point `geno_notes.cli:main` produces the `geno-notes` binary.
- **Venv**: installed into `~/.geno/venv`, PATH shim at `~/.local/bin/geno-notes`.
- **Dependencies**: `click>=8.0`, Python >=3.10.

## Scope resolution

Active scope resolves in this order:

1. `$GENO_NOTES_SCOPE` (`global` | `project`) if set
2. `$GENO_NOTES_DIR` if set — exact dir, scope from its `config.toml`
3. `./geno/geno-notes/` found walking up from cwd — **project** scope
4. Otherwise — **global** at `~/.geno/geno-notes/` (auto-created)

Use `--global` or `--project` on any command to override. Use `--all` on reads to union both scopes.

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
├── wiki/                             # compiled wiki pages
│   └── README.md
├── inbox.md
└── .geno-notes/
    ├── config.toml
    ├── events.jsonl                  # append-only audit log
    └── locks/
```
