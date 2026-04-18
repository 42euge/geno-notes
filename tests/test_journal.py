"""Dual-write journal: .md + .jsonl stay in sync."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from geno_notes import journal, paths


def _mk_scope(cwd):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    scope = paths.resolve_scope()
    paths.ensure_structure(scope)
    return scope


def test_append_creates_both_files(cwd):
    scope = _mk_scope(cwd)
    when = datetime(2026, 4, 18, 14, 32, 7, tzinfo=timezone.utc)
    journal.append(scope.dir, "Started OAuth work", when=when)
    md = scope.dir / "journal" / "2026" / "2026-04.md"
    jl = scope.dir / "journal" / "2026" / "2026-04.jsonl"
    assert md.is_file()
    assert jl.is_file()
    assert "Started OAuth work" in md.read_text()
    line = jl.read_text().strip()
    rec = json.loads(line)
    assert rec["text"] == "Started OAuth work"
    assert rec["kind"] == "note"
    assert rec["ts"] == "2026-04-18T14:32:07Z"


def test_kind_and_task_link(cwd):
    scope = _mk_scope(cwd)
    journal.append(scope.dir, "OAuth scope broken", kind="bug", task_id="20260418-auth")
    jl = scope.dir / "journal" / "2026" / (datetime.now(timezone.utc).strftime("%Y-%m") + ".jsonl")
    # Figure out the actual file — use the one that exists.
    jl_files = list((scope.dir / "journal").rglob("*.jsonl"))
    assert len(jl_files) == 1
    records = [
        json.loads(line)
        for line in jl_files[0].read_text().splitlines()
        if line.strip()
    ]
    assert records[-1]["kind"] == "bug"
    assert records[-1]["task_id"] == "20260418-auth"


def test_seconds_precision_distinct(cwd):
    """Two appends at different seconds must get distinct timestamps."""
    scope = _mk_scope(cwd)
    t1 = datetime(2026, 4, 18, 14, 32, 7, tzinfo=timezone.utc)
    t2 = datetime(2026, 4, 18, 14, 32, 8, tzinfo=timezone.utc)
    journal.append(scope.dir, "first", when=t1)
    journal.append(scope.dir, "second", when=t2)
    jl_files = list((scope.dir / "journal").rglob("*.jsonl"))
    records = [
        json.loads(line)
        for line in jl_files[0].read_text().splitlines()
        if line.strip()
    ]
    assert len(records) == 2
    assert records[0]["ts"] != records[1]["ts"]


def test_invalid_kind_raises(cwd):
    scope = _mk_scope(cwd)
    import pytest
    with pytest.raises(ValueError):
        journal.append(scope.dir, "x", kind="gossip")
