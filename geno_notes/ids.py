"""Task ID derivation: `YYYYMMDD-<slug>`.

- Slug is kebab-case, alphanumeric + hyphens, max 40 chars, derived from task title.
- Date prefix guarantees chronological sort via `ls tasks/` and prevents slug
  collisions across time.
- If a same-day collision occurs (`geno-notes add "Auth"` twice on one day),
  append `-2`, `-3`, …
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

SLUG_MAX = 40


def slugify(title: str) -> str:
    # Lowercase, strip non-alphanumerics to hyphens, collapse, trim.
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = "task"
    return s[:SLUG_MAX].rstrip("-")


def make_id(title: str, today: date | None = None, existing_ids: set[str] | None = None) -> str:
    """Return a unique task ID for `title`.

    Collisions on the same day get a numeric suffix (-2, -3, …).
    """
    d = (today or date.today()).strftime("%Y%m%d")
    base = f"{d}-{slugify(title)}"
    if not existing_ids or base not in existing_ids:
        return base
    i = 2
    while f"{base}-{i}" in existing_ids:
        i += 1
    return f"{base}-{i}"


def existing_ids_in(tasks_dir: Path) -> set[str]:
    if not tasks_dir.is_dir():
        return set()
    return {p.stem for p in tasks_dir.glob("*.md") if p.stem != "_index"}
