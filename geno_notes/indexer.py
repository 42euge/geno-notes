"""Regenerate index.md + tasks/_index.md from on-disk state.

Auto-called after any state mutation (create / transition / promote) and
available as `geno-notes reindex`.
"""

from __future__ import annotations

import json
from pathlib import Path

from geno_notes import tasks as tasks_mod
from geno_notes.locks import file_lock


def reindex(scope_dir: Path, scope_name: str) -> None:
    lock = scope_dir / ".geno-notes" / "locks" / "_index"
    with file_lock(lock):
        all_tasks = tasks_mod.load_all(scope_dir)
        _write_tasks_index(scope_dir, all_tasks)
        _write_root_index(scope_dir, scope_name, all_tasks)


def _write_tasks_index(scope_dir: Path, all_tasks: list[tasks_mod.Task]) -> None:
    groups: dict[str, list[tasks_mod.Task]] = {
        "active": [],
        "backlog": [],
        "done": [],
        "abandoned": [],
    }
    for t in all_tasks:
        groups.setdefault(t.status, []).append(t)

    lines = ["# Tasks", "", "_Auto-generated. Do not edit._", ""]
    for label in ("active", "backlog", "done", "abandoned"):
        items = groups.get(label, [])
        lines.append(f"## {label.capitalize()} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("_(none)_")
            lines.append("")
            continue
        for t in items:
            lines.append(f"- [{t.id}](./{t.id}.md) — {t.title}")
        lines.append("")

    (scope_dir / "tasks" / "_index.md").write_text(
        "\n".join(lines).rstrip() + "\n", encoding="utf-8"
    )


def _write_root_index(scope_dir: Path, scope_name: str, all_tasks: list[tasks_mod.Task]) -> None:
    active = [t for t in all_tasks if t.status == "active"]
    backlog = [t for t in all_tasks if t.status == "backlog"]
    recent_events = _tail_events(scope_dir, n=10)

    lines = [
        f"# geno-notes — {scope_name}",
        "",
        f"**Scope dir:** `{scope_dir}`",
        "",
        f"## Active ({len(active)})",
        "",
    ]
    if active:
        for t in active:
            lines.append(f"- [{t.id}](./tasks/{t.id}.md) — {t.title}")
    else:
        lines.append("_(none)_")
    lines += ["", f"## Backlog ({len(backlog)})", ""]
    if backlog:
        for t in backlog:
            lines.append(f"- [{t.id}](./tasks/{t.id}.md) — {t.title}")
    else:
        lines.append("_(none)_")
    lines += ["", "## Recent events", ""]
    if recent_events:
        for e in recent_events:
            target = e.get("target") or ""
            lines.append(f"- `{e.get('ts','')}` **{e.get('op','?')}** {target}")
    else:
        lines.append("_(none)_")
    lines.append("")

    (scope_dir / "index.md").write_text(
        "\n".join(lines).rstrip() + "\n", encoding="utf-8"
    )


def _tail_events(scope_dir: Path, n: int = 10) -> list[dict]:
    p = scope_dir / ".geno-notes" / "events.jsonl"
    if not p.exists():
        return []
    tail = p.read_text(encoding="utf-8").splitlines()[-n:]
    out: list[dict] = []
    for line in tail:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
