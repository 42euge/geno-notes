"""Plain-text search across tasks/, journal/*.md, plans/, inbox.md.

Case-insensitive substring match. Scope-local by default; use `union=True`
(via --all) to cover multiple scopes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from geno_notes.paths import Scope


@dataclass
class Hit:
    scope: str
    path: Path
    line_no: int
    line: str


def search(scopes: list[Scope], query: str) -> list[Hit]:
    q = query.lower()
    hits: list[Hit] = []
    for scope in scopes:
        for target in _walk(scope.dir):
            try:
                text = target.read_text(encoding="utf-8")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), start=1):
                if q in line.lower():
                    hits.append(Hit(scope=scope.name, path=target, line_no=i, line=line.rstrip()))
    return hits


def _walk(scope_dir: Path):
    for sub in ("tasks", "journal", "plans"):
        d = scope_dir / sub
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.is_file() and p.suffix in (".md", ".jsonl"):
                yield p
    inbox = scope_dir / "inbox.md"
    if inbox.exists():
        yield inbox
