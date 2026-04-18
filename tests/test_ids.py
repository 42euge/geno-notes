"""Slug derivation + collision handling."""

from __future__ import annotations

from datetime import date

from geno_notes import ids


def test_slugify_basic():
    assert ids.slugify("Auth Login Flow") == "auth-login-flow"


def test_slugify_strips_punctuation():
    assert ids.slugify("Fix the #!@ bug in login!!!") == "fix-the-bug-in-login"


def test_slugify_max_len():
    s = ids.slugify("x" * 60)
    assert len(s) <= ids.SLUG_MAX


def test_slugify_empty_becomes_task():
    assert ids.slugify("   ") == "task"


def test_make_id_has_date_prefix():
    d = date(2026, 4, 18)
    assert ids.make_id("Auth", today=d) == "20260418-auth"


def test_make_id_collision_gets_numeric_suffix():
    d = date(2026, 4, 18)
    existing = {"20260418-auth"}
    assert ids.make_id("Auth", today=d, existing_ids=existing) == "20260418-auth-2"

    existing.add("20260418-auth-2")
    assert ids.make_id("Auth", today=d, existing_ids=existing) == "20260418-auth-3"


def test_existing_ids_in_scans_md_files(tmp_path):
    d = tmp_path / "tasks"
    d.mkdir()
    (d / "20260418-a.md").write_text("")
    (d / "20260418-b.md").write_text("")
    (d / "_index.md").write_text("")  # must be ignored
    (d / "readme.txt").write_text("")  # non-md ignored
    got = ids.existing_ids_in(d)
    assert got == {"20260418-a", "20260418-b"}
