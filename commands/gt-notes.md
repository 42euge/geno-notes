---
description: "Manage project notes: tasks, timestamped journal entries, plans. Scope-aware (global + per-project)."
argument-hint: "[scope|path|init|add|start|done|abandon|note|inbox|triage|list|show|search|promote|reindex|compile] [args...]"
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *)"
---

# geno-notes

Parse `$ARGUMENTS` and dispatch via the `geno-notes` CLI (on PATH via `~/.local/bin/` shim).

## Resolution

Every scope-sensitive command accepts `--global` or `--project` to override; read commands accept `--all` to union both scopes. Without flags, scope is chosen by:

1. `$GENO_NOTES_SCOPE` if set to `global` or `project`.
2. `$GENO_NOTES_DIR` if set.
3. `./geno/geno-notes/` detected in cwd or any ancestor → **project**.
4. Otherwise → **global** at `~/.geno/geno-notes/` (auto-created).

## Dispatch

| Subcommand | What it does |
|---|---|
| `scope` (or no args) | `geno-notes scope` — show active scope + both dir paths |
| `path` | `geno-notes path` |
| `init [--global|--project]` | `geno-notes init ...` |
| `add "<desc>" [--tag T ...]` | `geno-notes add "<desc>" [-t T ...]` |
| `start <pat>` | `geno-notes start <pat>` |
| `done <pat>` | `geno-notes done <pat>` |
| `abandon <pat>` | `geno-notes abandon <pat>` |
| `note "<text>" [--task <pat>] [--kind K]` | `geno-notes note "<text>" [--task <pat>] [--kind K]` |
| `inbox "<text>"` | `geno-notes inbox "<text>"` |
| `triage` | `geno-notes triage` (interactive) |
| `list [--status S] [--json] [--all]` | `geno-notes list ...` |
| `show <pat> [--all]` | `geno-notes show <pat> [--all]` |
| `search <q> [--all]` | `geno-notes search <q> [--all]` |
| `promote <pat> [--to G|P]` | `geno-notes promote <pat> [--to ...]` |
| `reindex` | `geno-notes reindex` |
| `compile` | `geno-notes compile` (v0.2 stub) |

If the user passes `--global`/`--project`/`--all`, forward those flags verbatim.

## When to use which scope

- **Project** — task is specific to a repo. Matches commits, plans, repo-local docs. Default for `gt-start-task`, `gt-research-repo-docs`, `gt-run-kaggle-bench`.
- **Global** — cross-project insight, personal dev log, knowledge you want available in every repo.
- **`--all` on reads** — when synthesizing across projects (e.g., `gt-research-paper-generate` pulling together findings from several related repos).

## Examples

```bash
/gt-notes                              # show scope
/gt-notes add "Auth login flow" -t security
/gt-notes start auth
/gt-notes note "Scope 'user:email' insufficient — need 'read:user'" --task auth-flow --kind finding
/gt-notes list --status active
/gt-notes search oauth --all
/gt-notes done auth-flow
/gt-notes promote auth-flow --to global
```
