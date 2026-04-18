"""Concurrent mutation safety — flock must serialize rewrites."""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from geno_notes import journal, paths, tasks


def _mk_scope(cwd):
    (cwd / "geno" / "geno-notes").mkdir(parents=True)
    scope = paths.resolve_scope()
    paths.ensure_structure(scope)
    return scope


def test_concurrent_journal_appends_preserve_all_lines(cwd):
    scope = _mk_scope(cwd)
    N = 30

    def work(i):
        journal.append(scope.dir, f"entry-{i}")

    with ThreadPoolExecutor(max_workers=8) as ex:
        list(as_completed([ex.submit(work, i) for i in range(N)]))

    # Collect both files' contents.
    jl_files = list((scope.dir / "journal").rglob("*.jsonl"))
    total_jsonl = sum(
        sum(1 for ln in f.read_text().splitlines() if ln.strip())
        for f in jl_files
    )
    assert total_jsonl == N


def test_concurrent_transitions_idempotent(cwd):
    """Two threads flipping the same task to done — flock means we don't tear
    the frontmatter."""
    scope = _mk_scope(cwd)
    t = tasks.create(scope.dir, "Auth")

    errors: list[Exception] = []

    def flip():
        try:
            tasks.transition(scope.dir, t.id, "done")
        except Exception as e:  # pragma: no cover — should not happen
            errors.append(e)

    threads = [threading.Thread(target=flip) for _ in range(10)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    assert not errors
    final = tasks.load(scope.dir, t.id)
    assert final.status == "done"
    assert final.completed is not None
