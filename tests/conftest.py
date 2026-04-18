"""Shared pytest fixtures — isolate every test from $HOME and the real global scope."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Redirect HOME so GLOBAL_DIR lands in tmp_path, not the real ~/.geno/."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    # Strip env overrides that might leak in from the developer's shell.
    monkeypatch.delenv("GENO_NOTES_SCOPE", raising=False)
    monkeypatch.delenv("GENO_NOTES_DIR", raising=False)

    # paths.GLOBAL_DIR was computed at import time; patch it for the tests.
    import geno_notes.paths as paths_mod
    monkeypatch.setattr(paths_mod, "GLOBAL_DIR", fake_home / ".geno" / "geno-notes")
    return fake_home


@pytest.fixture
def cwd(tmp_path, monkeypatch):
    """Jump into a fresh dir so project-scope detection has a clean slate."""
    d = tmp_path / "proj"
    d.mkdir()
    monkeypatch.chdir(d)
    return d
