"""Scope resolution and directory scaffolding.

Two scopes coexist:
- global:   ~/.geno/geno-notes/
- project:  ./geno/geno-notes/  (walking up from cwd)

Scope resolution order:
  1. $GENO_NOTES_SCOPE (global|project)
  2. $GENO_NOTES_DIR   (exact dir; scope read from its config.toml)
  3. ancestor-walk for ./geno/geno-notes/ → project
  4. otherwise → global (auto-created on first use)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

GLOBAL_DIR = Path.home() / ".geno" / "geno-notes"
PROJECT_DIRNAME = "geno"
PROJECT_SUBDIRNAME = "geno-notes"


@dataclass(frozen=True)
class Scope:
    name: str          # "global" | "project"
    dir: Path


def _find_project_dir(start: Path) -> Path | None:
    """Walk up from `start` looking for ./geno/geno-notes/."""
    cur = start.resolve()
    while True:
        candidate = cur / PROJECT_DIRNAME / PROJECT_SUBDIRNAME
        if candidate.is_dir():
            return candidate
        if cur.parent == cur:
            return None
        cur = cur.parent


def resolve_scope(
    cwd: Path | None = None,
    override: str | None = None,  # "global" | "project" | None
) -> Scope:
    """Return the active scope (may create the global dir on first use)."""
    cwd = (cwd or Path.cwd()).resolve()

    # Explicit override wins.
    if override == "global":
        return Scope("global", GLOBAL_DIR)
    if override == "project":
        pdir = _find_project_dir(cwd)
        if not pdir:
            raise RuntimeError(
                "No project scope found. "
                "Run `geno-notes init --project` here first, or walk into a dir with ./geno/geno-notes/."
            )
        return Scope("project", pdir)

    # Env var takes precedence over detection.
    env_scope = os.environ.get("GENO_NOTES_SCOPE", "").strip().lower()
    if env_scope in ("global", "project"):
        return resolve_scope(cwd, override=env_scope)

    env_dir = os.environ.get("GENO_NOTES_DIR", "").strip()
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
        # Scope name: read from config.toml if present, else infer.
        from geno_notes.config import read_config  # local to avoid cycle
        cfg = read_config(p) if p.exists() else None
        scope_name = (cfg or {}).get("scope") or ("project" if PROJECT_SUBDIRNAME in p.parts else "global")
        return Scope(scope_name, p)

    # Project detection via ancestor walk.
    pdir = _find_project_dir(cwd)
    if pdir:
        return Scope("project", pdir)

    # Fall through to global (auto-created).
    return Scope("global", GLOBAL_DIR)


def scope_for(name: str) -> Scope:
    """Return the scope struct for 'global' or 'project' without resolution rules."""
    if name == "global":
        return Scope("global", GLOBAL_DIR)
    if name == "project":
        pdir = _find_project_dir(Path.cwd())
        if not pdir:
            raise RuntimeError("No project scope found in cwd or ancestors.")
        return Scope("project", pdir)
    raise ValueError(f"Unknown scope: {name!r}")


def ensure_structure(scope: Scope) -> None:
    """Create the directory layout + empty files if missing. Idempotent."""
    d = scope.dir
    d.mkdir(parents=True, exist_ok=True)
    (d / "tasks").mkdir(exist_ok=True)
    (d / "journal").mkdir(exist_ok=True)
    (d / "plans").mkdir(exist_ok=True)
    (d / "wiki").mkdir(exist_ok=True)
    (d / ".geno-notes").mkdir(exist_ok=True)
    (d / ".geno-notes" / "locks").mkdir(exist_ok=True)

    # Seed files.
    _seed(d / "inbox.md", "# Inbox\n\nQuick captures. Use `geno-notes triage` to promote.\n")
    _seed(
        d / "wiki" / "README.md",
        "# Wiki (reserved for v0.2)\n\n"
        "This directory is reserved for Karpathy-style llm-wiki compilation.\n"
        "Run `geno-notes compile` once v0.2 ships.\n",
    )
    _seed(d / "tasks" / "_index.md", "# Tasks\n\n_Auto-generated. Do not edit._\n")
    _seed(d / "index.md", f"# geno-notes ({scope.name})\n\n_Auto-generated dashboard._\n")

    # Touch append-only log + config if missing (config handled elsewhere).
    events = d / ".geno-notes" / "events.jsonl"
    if not events.exists():
        events.touch()


def _seed(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def list_all_scopes(cwd: Path | None = None) -> list[Scope]:
    """Return (project?, global) in that order — project first if discoverable."""
    cwd = (cwd or Path.cwd()).resolve()
    out: list[Scope] = []
    pdir = _find_project_dir(cwd)
    if pdir:
        out.append(Scope("project", pdir))
    if GLOBAL_DIR.is_dir():
        out.append(Scope("global", GLOBAL_DIR))
    return out
