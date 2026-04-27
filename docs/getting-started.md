# Getting Started

## Prerequisites

- Python 3.10+
- [geno-tools](https://42euge.github.io/geno-tools) installed
- A supported coding CLI (Claude Code, Gemini CLI, Codex, or OpenCode)

## Install

```bash
geno-tools install geno-notes
```

Or from within an agent session:

```
/geno-tools install geno-notes
```

## First use

Once installed, the `/gt-notes` slash command is available in any agent session.

### Check scope

```
/gt-notes
```

Shows the active scope (global or project) and both directory paths.

### Initialize a project scope

```
/gt-notes init --project
```

Creates `./geno/geno-notes/` in the current repo for project-scoped tasks and journal entries.

### Add a task

```
/gt-notes add "Implement auth flow" --tag security
```

### Start working on it

```
/gt-notes start auth
```

Fuzzy-matches on id, slug, or title.

### Add a journal note

```
/gt-notes note "Discovered scope 'user:email' is insufficient" --task auth --kind finding
```

### Complete the task

```
/gt-notes done auth
```

## Scope resolution

Active scope resolves in this order:

1. `$GENO_NOTES_SCOPE` (`global` | `project`) if set
2. `$GENO_NOTES_DIR` if set
3. `./geno/geno-notes/` found walking up from cwd — **project** scope
4. Otherwise — **global** at `~/.geno/geno-notes/`

Use `--global` or `--project` on any command to override. Use `--all` on reads to union both scopes.
