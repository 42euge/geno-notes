# geno-notes

Project journal for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Tasks, timestamped journal entries, and plans with two coexisting scopes — global and per-project.

Part of the [geno-tools](https://42euge.github.io/geno-tools) ecosystem.

<div class="feature-grid" markdown>

<div class="feature-card" markdown>
<span class="card-icon">:material-checkbox-marked-outline:</span>

### Task management

Create, activate, complete, and abandon tasks with stable IDs and YAML frontmatter. Fuzzy-match by id, slug, or title.

[See command :material-arrow-right:](commands.md#task-lifecycle)
</div>

<div class="feature-card" markdown>
<span class="card-icon">:material-notebook-edit:</span>

### Timestamped journal

Append notes with optional task links and kind tags. Chunked by month — human-readable markdown plus machine-readable JSONL.

[See command :material-arrow-right:](commands.md#journal)
</div>

<div class="feature-card" markdown>
<span class="card-icon">:material-swap-horizontal:</span>

### Two-scope storage

Global scope (`~/.geno/geno-notes/`) for cross-project knowledge, project scope (`./geno/geno-notes/`) for repo-specific work. Promote tasks between scopes.

[See command :material-arrow-right:](commands.md#scope-management)
</div>

<div class="feature-card" markdown>
<span class="card-icon">:material-magnify:</span>

### Search & discovery

Grep across tasks, journal, plans, and inbox. Union both scopes with `--all`. Machine-readable output with `--json`.

[See command :material-arrow-right:](commands.md#search)
</div>

</div>

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
| `/gt-notes note "<text>" [--task <pat>]` | Append a timestamped journal entry |
| `/gt-notes list [--status S] [--all]` | List tasks in active scope |
| `/gt-notes search <query> [--all]` | Grep across tasks, journal, plans, inbox |
| `/gt-notes promote <pat> [--to scope]` | Move a task between scopes |

## Scope resolution

Active scope resolves in this order:

1. `$GENO_NOTES_SCOPE` (`global` | `project`) if set
2. `$GENO_NOTES_DIR` if set — exact dir
3. `./geno/geno-notes/` found walking up from cwd — **project**
4. Otherwise — **global** at `~/.geno/geno-notes/`

Use `--global` or `--project` on any command to override. Use `--all` on reads to union both scopes.

## Runtime

Python CLI installed into `~/.geno/venv`. PATH shim at `~/.local/bin/geno-notes`.
