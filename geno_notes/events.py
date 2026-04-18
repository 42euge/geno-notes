"""Append-only audit log in <scope>/.geno-notes/events.jsonl.

Each line is one event: {"ts": ISO8601, "op": str, "target": str, "meta": {...}}

Writes use O_APPEND for atomicity across concurrent sessions.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _events_path(scope_dir: Path) -> Path:
    return scope_dir / ".geno-notes" / "events.jsonl"


def log(scope_dir: Path, op: str, target: str | None = None, **meta: Any) -> None:
    """Append one event. Atomic for writes <=4 KiB on POSIX."""
    path = _events_path(scope_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": _now_iso(),
        "op": op,
        "target": target,
    }
    if meta:
        rec["meta"] = meta
    line = json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n"
    # O_APPEND guarantees atomic append on POSIX.
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_all(scope_dir: Path) -> list[dict]:
    """Parse the full event log. Small scopes only — streaming consumers should
    read the file directly."""
    p = _events_path(scope_dir)
    if not p.exists():
        return []
    out: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
