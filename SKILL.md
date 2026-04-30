---
name: geno-notes
description: >-
  Project journal — tasks, timestamped journal entries, plans. Two scopes
  coexist: global (~/.geno/geno-notes/) and per-project (./geno/geno-notes/).
  Use when user says /gt-notes, wants to add/start/complete a task, jot a
  timestamped note, list or search tasks and journal entries, or move work
  between scopes.
allowed-tools: "Bash(geno-notes *) Bash(~/.local/bin/geno-notes *) Bash(~/.geno/venv/bin/geno-notes *)"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
---

# geno-notes — Project Journal

Persistent, greppable, concurrent-safe project journal. One file per task,
chunked journal files, and two coexisting storage scopes.

## Available skills

| Skill | Slash command | Description |
|-------|--------------|-------------|
| geno-notes | /gt-notes | Manage tasks, journal entries, plans across global and project scopes |
| geno-notes-wiki-compile | /geno-notes-wiki-compile | Compile primary sources into wiki pages |
| geno-notes-wiki-lint | /geno-notes-wiki-lint | Health-check the wiki against primary sources |
| geno-notes-sites-generate | /geno-notes-sites-generate | Generate a MkDocs Material website from notes |
