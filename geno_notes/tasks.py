"""One file per task: tasks/<task-id>.md with YAML-ish frontmatter.

Status lifecycle: backlog → active → (done | abandoned).

Frontmatter is hand-rolled (no PyYAML dep) — supported fields are flat
scalars, ISO timestamps, and a single list (tags). Bodies are freeform
markdown below the frontmatter.

State mutations acquire flock on <scope>/.geno-notes/locks/<id> before
rewrite-then-rename to avoid torn writes across concurrent sessions.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from geno_notes import events, ids
from geno_notes.locks import file_lock

VALID_STATUSES = {"backlog", "active", "done", "abandoned"}


@dataclass
class Task:
    id: str
    title: str
    status: str = "backlog"
    created: str = ""
    activated: str | None = None
    completed: str | None = None
    tags: list[str] = field(default_factory=list)
    body: str = ""


# ─── path helpers ──────────────────────────────────────────────────────


def tasks_dir(scope_dir: Path) -> Path:
    return scope_dir / "tasks"


def task_path(scope_dir: Path, task_id: str) -> Path:
    return tasks_dir(scope_dir) / f"{task_id}.md"


def lock_path(scope_dir: Path, task_id: str) -> Path:
    return scope_dir / ".geno-notes" / "locks" / task_id


# ─── (de)serialize ─────────────────────────────────────────────────────


def _dump(task: Task) -> str:
    def s(v: Any) -> str:
        if v is None:
            return "null"
        return str(v)

    tags_line = "[" + ", ".join(task.tags) + "]"
    fm = (
        "---\n"
        f"id: {task.id}\n"
        f"status: {task.status}\n"
        f"created: {s(task.created)}\n"
        f"activated: {s(task.activated)}\n"
        f"completed: {s(task.completed)}\n"
        f"tags: {tags_line}\n"
        "---\n\n"
    )
    body = task.body.rstrip() + "\n" if task.body.strip() else ""
    return f"{fm}# {task.title}\n\n{body}"


def _parse(text: str) -> Task:
    if not text.startswith("---\n"):
        raise ValueError("Task file missing frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("Task file has unterminated frontmatter")
    fm_block = text[4:end]
    rest = text[end + 5 :]

    fields: dict[str, Any] = {"tags": []}
    for raw in fm_block.splitlines():
        if ":" not in raw:
            continue
        k, _, v = raw.partition(":")
        k = k.strip()
        v = v.strip()
        if k == "tags":
            inner = v.strip().lstrip("[").rstrip("]")
            fields["tags"] = [t.strip() for t in inner.split(",") if t.strip()]
        else:
            fields[k] = None if v == "null" else v

    # Pull title (first "# " heading in body) + body-below-title.
    title = fields.get("id", "untitled")
    body = ""
    lines = rest.lstrip("\n").splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = "\n".join(lines[1:]).lstrip("\n")
    else:
        body = "\n".join(lines)

    return Task(
        id=str(fields.get("id") or ""),
        title=title,
        status=str(fields.get("status") or "backlog"),
        created=str(fields.get("created") or ""),
        activated=fields.get("activated") if fields.get("activated") not in (None, "null") else None,
        completed=fields.get("completed") if fields.get("completed") not in (None, "null") else None,
        tags=list(fields.get("tags", [])),
        body=body,
    )


# ─── CRUD ──────────────────────────────────────────────────────────────


def load(scope_dir: Path, task_id: str) -> Task:
    return _parse(task_path(scope_dir, task_id).read_text(encoding="utf-8"))


def load_all(scope_dir: Path) -> list[Task]:
    d = tasks_dir(scope_dir)
    if not d.is_dir():
        return []
    out: list[Task] = []
    for p in sorted(d.glob("*.md")):
        if p.stem == "_index":
            continue
        try:
            out.append(_parse(p.read_text(encoding="utf-8")))
        except Exception:
            # Skip malformed files rather than crash the whole CLI.
            continue
    return out


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=".tmp-", suffix=".md", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def save(scope_dir: Path, task: Task) -> None:
    path = task_path(scope_dir, task.id)
    with file_lock(lock_path(scope_dir, task.id)):
        _atomic_write(path, _dump(task))


def create(scope_dir: Path, title: str, tags: list[str] | None = None) -> Task:
    existing = ids.existing_ids_in(tasks_dir(scope_dir))
    task_id = ids.make_id(title, existing_ids=existing)
    task = Task(
        id=task_id,
        title=title,
        status="backlog",
        created=_now_iso(),
        tags=list(tags or []),
    )
    save(scope_dir, task)
    events.log(
        scope_dir,
        "task.create",
        target=task_id,
        title=title,
        status="backlog",
    )
    return task


def transition(scope_dir: Path, task_id: str, new_status: str) -> Task:
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Unknown status: {new_status}")
    with file_lock(lock_path(scope_dir, task_id)):
        task = _parse(task_path(scope_dir, task_id).read_text(encoding="utf-8"))
        if task.status == new_status:
            return task
        task.status = new_status
        now = _now_iso()
        if new_status == "active" and not task.activated:
            task.activated = now
        if new_status in ("done", "abandoned"):
            task.completed = now
        _atomic_write(task_path(scope_dir, task_id), _dump(task))
    events.log(scope_dir, f"task.{new_status}", target=task_id)
    return task


# ─── fuzzy match ───────────────────────────────────────────────────────


def find_candidates(all_tasks: list[Task], pattern: str) -> list[Task]:
    """Exact > prefix > substring over {task_id, slug-of-title}.
    Returns the top tier only (all tasks matching at the highest tier found).
    """
    p = pattern.strip().lower()
    if not p:
        return []

    def keys(t: Task) -> list[str]:
        slug = ids.slugify(t.title)
        # Drop date prefix for more natural matching on "auth-flow".
        id_tail = t.id.split("-", 1)[1] if "-" in t.id else t.id
        return [t.id.lower(), id_tail.lower(), slug.lower(), t.title.lower()]

    exact, prefix, sub = [], [], []
    for t in all_tasks:
        ks = keys(t)
        if any(k == p for k in ks):
            exact.append(t)
        elif any(k.startswith(p) for k in ks):
            prefix.append(t)
        elif any(p in k for k in ks):
            sub.append(t)
    for tier in (exact, prefix, sub):
        if tier:
            return tier
    return []


# ─── helpers ───────────────────────────────────────────────────────────


def append_journal_ref(scope_dir: Path, task_id: str, ts_iso: str, note_text: str) -> None:
    """Append a line to the task's `## Journal refs` section so the task file
    keeps a local backlink to its journal entries. Creates the section if
    missing. Lock held during rewrite.
    """
    path = task_path(scope_dir, task_id)
    if not path.exists():
        return  # free-floating note; nothing to back-link
    with file_lock(lock_path(scope_dir, task_id)):
        text = path.read_text(encoding="utf-8")
        line = f"- {ts_iso} — {note_text.splitlines()[0][:120]}"
        header = "## Journal refs"
        if header in text:
            new_text = text.rstrip() + "\n" + line + "\n"
        else:
            new_text = text.rstrip() + f"\n\n{header}\n\n{line}\n"
        _atomic_write(path, new_text)


def to_dict(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "created": task.created,
        "activated": task.activated,
        "completed": task.completed,
        "tags": list(task.tags),
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
