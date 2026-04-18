"""Cross-scope: list_all_scopes + promote."""

from __future__ import annotations

import shutil
from pathlib import Path

from geno_notes import paths, tasks
from geno_notes.config import ensure_config


def _init_project(cwd):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    scope = paths.resolve_scope()
    paths.ensure_structure(scope)
    ensure_config(scope.dir, scope.name)
    return scope


def _init_global():
    scope = paths.resolve_scope(override="global")
    paths.ensure_structure(scope)
    ensure_config(scope.dir, scope.name)
    return scope


def test_list_all_scopes_project_first(cwd):
    project = _init_project(cwd)
    g = _init_global()
    scopes = paths.list_all_scopes()
    assert [s.name for s in scopes] == ["project", "global"]
    assert scopes[0].dir == project.dir
    assert scopes[1].dir == g.dir


def test_list_all_scopes_global_only(cwd):
    _init_global()
    scopes = paths.list_all_scopes()
    assert [s.name for s in scopes] == ["global"]


def test_promote_task_moves_file(cwd):
    project = _init_project(cwd)
    g = _init_global()
    t = tasks.create(project.dir, "Global gotcha")

    src = tasks.task_path(project.dir, t.id)
    dst = tasks.task_path(g.dir, t.id)
    assert src.exists() and not dst.exists()

    # Simulate promote: move file + plan if present.
    # (CLI does this via shutil; here we test that the helpers cooperate.)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    assert not src.exists() and dst.exists()

    reloaded = tasks.load(g.dir, t.id)
    assert reloaded.title == "Global gotcha"
