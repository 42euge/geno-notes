# geno-notes

Project journal for the geno ecosystem — scalable, robust storage for tasks, timestamped journal entries, and plans.

Replaces the legacy `geno-tools/labnotes/` layout with:
- **One file per task** (`tasks/<task-id>.md` with YAML frontmatter) — stable IDs, concurrent-safe.
- **Chunked journal** (`journal/YYYY/YYYY-MM.md` + sibling `.jsonl`) — human + machine readable, bounded growth.
- **Two coexisting scopes**: global (`~/.geno/geno-notes/`) and per-project (`./geno/geno-notes/`).
- **Append-only event log** for full audit trail.
- **Concurrency safety** via `O_APPEND` and `flock`.

## Install

```bash
./install.sh
```

Installs:
- `~/.geno/venv/bin/geno-notes` (via `pip install -e .`)
- `~/.local/bin/geno-notes` → venv shim (consumers use bare `geno-notes` on PATH)
- `~/.claude/skills/geno-notes` → skill symlink
- `~/.claude/commands/gt-notes.md` → slash command
- `~/.geno/geno-notes/` → global-scope storage dir, initialized

## Scope resolution

When you run `geno-notes <cmd>`, the active scope is chosen in this order:

1. `$GENO_NOTES_SCOPE` (`global` | `project`) if set
2. `$GENO_NOTES_DIR` if set — exact dir, scope from its `config.toml`
3. `./geno/geno-notes/` found walking up from cwd → **project** scope
4. Otherwise → **global** at `~/.geno/geno-notes/` (auto-created)

Use `--global` or `--project` on any command to override. Use `--all` on reads to union both scopes.

## Usage

```bash
geno-notes scope                   # show active scope + both paths
geno-notes init --project          # scaffold project scope in cwd
geno-notes add "Auth login flow"   # create task
geno-notes start auth              # move to active
geno-notes note "oauth scope broken" --task auth-flow
geno-notes list --status active
geno-notes search oauth --all
geno-notes done auth-flow
geno-notes promote auth-flow --to global  # move task + plan across scopes
```

See `geno-notes --help` for the full CLI.

## Layout (v0.1)

```
<scope-dir>/
├── index.md                          # auto-gen dashboard
├── tasks/
│   ├── _index.md                     # auto-gen list grouped by status
│   └── <task-id>.md                  # frontmatter: id, status, created, activated, completed, tags
├── journal/
│   └── YYYY/
│       ├── YYYY-MM.md                # human-readable
│       └── YYYY-MM.jsonl             # machine-readable (consumers parse this)
├── plans/
│   └── <task-id>.md
├── wiki/                             # reserved for v0.2 llm-wiki compilation
│   └── README.md
├── inbox.md                          # quick captures
└── .geno-notes/
    ├── config.toml                   # schema_version, scope, tz
    ├── events.jsonl                  # append-only audit log
    └── locks/                        # flock files
```

## Design

See `docs/` or the [approved plan](./docs/plan.md) for the full design rationale.
