# geno-notes — project journal skillset

Project journal for Claude Code: tasks, timestamped journal entries, plans. Two coexisting scopes — global (`~/.geno/geno-notes/`) and per-project (`./geno/geno-notes/`).

## Skills

| Skill name | Slash command |
|-----------|---------------|
| `geno-notes` | `/gt-notes` |

## Compliance

This repo follows geno-ecosystem conventions. All contributors and agents must adhere to:

### Nomenclature

Skill names follow: `{skillset}-{sub-skillset}-{skill-slug}`

- **Skillset** = this repo's name: `geno-notes`
- geno-notes is a single-skill skillset backed by a Python CLI. Subcommands are dispatched via the CLI, not separate skill folders.

Full spec: https://42euge.github.io/geno-tools/skillsets/nomenclature/

### Repo structure

Every geno-ecosystem repo must have:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project instructions for agents (this file) |
| `package.json` | Skills manifest with name, version, skills map |
| `.geno-agents` | Agent identity: role, description, capabilities |
| `skills/geno-notes/SKILL.md` | Skill definition |
| `README.md` | Human-facing docs: install, commands table, repo tree |

### SKILL.md frontmatter

Every SKILL.md must include:

```yaml
---
name: geno-notes
description: >-
  What this skill does.
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
---
```

### Runtime

geno-notes has a Python CLI backend (`geno_notes/` package). Installation is via `install.sh`, which:
1. `pip install -e .` into `~/.geno/venv`
2. Symlinks the binary to `~/.local/bin/geno-notes`
3. Symlinks the skill to `~/.claude/skills/geno-notes`
4. Symlinks the slash command to `~/.claude/commands/gt-notes.md`
5. Scaffolds the global scope at `~/.geno/geno-notes/`
