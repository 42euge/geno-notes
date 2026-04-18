"""Task CRUD + fuzzy matching."""

from __future__ import annotations

from geno_notes import paths, tasks


def _mk_scope(cwd):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    scope = paths.resolve_scope()
    paths.ensure_structure(scope)
    return scope


def test_create_and_reload(cwd):
    scope = _mk_scope(cwd)
    t = tasks.create(scope.dir, "Auth login flow")
    assert t.status == "backlog"
    assert t.title == "Auth login flow"

    loaded = tasks.load(scope.dir, t.id)
    assert loaded.title == "Auth login flow"
    assert loaded.status == "backlog"
    assert loaded.created.endswith("Z")


def test_transition_activate_and_complete(cwd):
    scope = _mk_scope(cwd)
    t = tasks.create(scope.dir, "Auth login flow")
    tasks.transition(scope.dir, t.id, "active")
    reloaded = tasks.load(scope.dir, t.id)
    assert reloaded.status == "active"
    assert reloaded.activated is not None
    assert reloaded.completed is None

    tasks.transition(scope.dir, t.id, "done")
    done = tasks.load(scope.dir, t.id)
    assert done.status == "done"
    assert done.completed is not None


def test_exact_match_beats_substring(cwd):
    scope = _mk_scope(cwd)
    tasks.create(scope.dir, "Auth")
    tasks.create(scope.dir, "Auth fallback")
    all_tasks = tasks.load_all(scope.dir)
    cands = tasks.find_candidates(all_tasks, "auth")
    # "auth" is an exact slug match for the first task; should be unique.
    assert len(cands) == 1
    assert cands[0].title == "Auth"


def test_ambiguous_prefix_returns_all(cwd):
    scope = _mk_scope(cwd)
    tasks.create(scope.dir, "Authfoo")
    tasks.create(scope.dir, "Authbar")
    all_tasks = tasks.load_all(scope.dir)
    cands = tasks.find_candidates(all_tasks, "auth")
    # Both slug into "authfoo" / "authbar", prefix-match "auth"; tier has 2.
    assert len(cands) == 2


def test_no_match_returns_empty(cwd):
    scope = _mk_scope(cwd)
    tasks.create(scope.dir, "Auth login flow")
    cands = tasks.find_candidates(tasks.load_all(scope.dir), "nonexistent")
    assert cands == []


def test_tags_round_trip(cwd):
    scope = _mk_scope(cwd)
    t = tasks.create(scope.dir, "Auth", tags=["infra", "security"])
    reloaded = tasks.load(scope.dir, t.id)
    assert reloaded.tags == ["infra", "security"]
