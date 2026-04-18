"""Scope resolution: env vars, project ancestor walk, global fallback."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from geno_notes import paths


def test_fresh_cwd_resolves_to_global(cwd):
    scope = paths.resolve_scope()
    assert scope.name == "global"
    assert scope.dir == paths.GLOBAL_DIR


def test_project_dir_is_detected_from_cwd(cwd):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    scope = paths.resolve_scope()
    assert scope.name == "project"
    assert scope.dir == cwd / "geno" / "geno-notes"


def test_project_dir_is_detected_from_descendant(cwd, monkeypatch):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    deep = cwd / "a" / "b" / "c"
    deep.mkdir(parents=True)
    monkeypatch.chdir(deep)
    scope = paths.resolve_scope()
    assert scope.name == "project"
    assert scope.dir == cwd / "geno" / "geno-notes"


def test_scope_env_var_forces_global(cwd, monkeypatch):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    monkeypatch.setenv("GENO_NOTES_SCOPE", "global")
    scope = paths.resolve_scope()
    assert scope.name == "global"


def test_scope_env_var_forces_project(cwd, monkeypatch):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    monkeypatch.setenv("GENO_NOTES_SCOPE", "project")
    scope = paths.resolve_scope()
    assert scope.name == "project"


def test_scope_env_var_project_with_no_project_errors(cwd, monkeypatch):
    monkeypatch.setenv("GENO_NOTES_SCOPE", "project")
    with pytest.raises(RuntimeError):
        paths.resolve_scope()


def test_dir_env_var_overrides(cwd, tmp_path, monkeypatch):
    custom = tmp_path / "mynotes"
    custom.mkdir()
    monkeypatch.setenv("GENO_NOTES_DIR", str(custom))
    scope = paths.resolve_scope()
    assert scope.dir == custom.resolve()


def test_legacy_labnotes_is_NOT_detected(cwd):
    """Per plan §7: legacy dirs are ignored. Must fall through to global."""
    (cwd / "geno-tools" / "labnotes").mkdir(parents=True)
    scope = paths.resolve_scope()
    assert scope.name == "global"


def test_ensure_structure_creates_all_dirs(cwd):
    scope = paths.resolve_scope()
    paths.ensure_structure(scope)
    d = scope.dir
    assert (d / "tasks").is_dir()
    assert (d / "journal").is_dir()
    assert (d / "plans").is_dir()
    assert (d / "wiki").is_dir()
    assert (d / ".geno-notes" / "locks").is_dir()
    assert (d / "inbox.md").is_file()
    assert (d / "wiki" / "README.md").is_file()
    assert (d / ".geno-notes" / "events.jsonl").is_file()
