"""Dual-write journal: journal/YYYY/YYYY-MM.md + YYYY-MM.jsonl.

Humans read .md, consumers parse .jsonl. Both are appended in a single CLI
call so they stay in sync.

Each entry is a {note, finding, decision, bug, milestone} with ISO-8601
timestamp (seconds precision) and an optional linked task_id.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_KINDS = {"note", "finding", "decision", "bug", "milestone"}


def _month_paths(scope_dir: Path, when: datetime) -> tuple[Path, Path]:
    year_dir = scope_dir / "journal" / f"{when.year:04d}"
    base = year_dir / f"{when.year:04d}-{when.month:02d}"
    return base.with_suffix(".md"), base.with_suffix(".jsonl")


def append(
    scope_dir: Path,
    text: str,
    *,
    kind: str = "note",
    task_id: str | None = None,
    when: datetime | None = None,
) -> dict[str, Any]:
    """Append an entry to this month's .md + .jsonl. Returns the record."""
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"kind must be one of {sorted(ALLOWED_KINDS)}, got {kind!r}")
    now = when or datetime.now(timezone.utc)
    ts_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    md_path, jsonl_path = _month_paths(scope_dir, now)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    # Seed month file if first entry.
    if not md_path.exists():
        md_path.write_text(
            f"# Journal — {now.year:04d}-{now.month:02d}\n\n",
            encoding="utf-8",
        )

    # Human-readable entry.
    task_suffix = f" (task: {task_id})" if task_id else ""
    kind_tag = "" if kind == "note" else f" [{kind}]"
    md_entry = f"## {ts_iso}{kind_tag}{task_suffix}\n\n{text.rstrip()}\n\n"
    _append_atomic(md_path, md_entry.encode("utf-8"))

    # Machine-readable mirror.
    rec: dict[str, Any] = {"ts": ts_iso, "kind": kind, "text": text}
    if task_id:
        rec["task_id"] = task_id
    _append_atomic(
        jsonl_path,
        (json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"),
    )
    return rec


def _append_atomic(path: Path, data: bytes) -> None:
    """Append-only write. Atomic for <=4 KiB on POSIX."""
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def iter_jsonl(scope_dir: Path):
    """Iterate every journal .jsonl record across all months (oldest first)."""
    j = scope_dir / "journal"
    if not j.is_dir():
        return
    for year_dir in sorted(p for p in j.iterdir() if p.is_dir()):
        for f in sorted(year_dir.glob("*.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
