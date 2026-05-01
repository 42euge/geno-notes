"""Generate an Obsidian vault from geno-notes content."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from geno_notes import tasks
from geno_notes.paths import Scope

STAGING_DIR_NAME = "_vault_staging"


def _stage_scope(scope: Scope, vault_dir: Path) -> None:
    """Copy a scope's content into the vault directory, adapting for Obsidian."""
    src = scope.dir

    for section in ("tasks", "journal", "plans", "wiki"):
        section_src = src / section
        if not section_src.is_dir():
            continue
        section_dst = vault_dir / section.capitalize()
        section_dst.mkdir(parents=True, exist_ok=True)
        for item in sorted(section_src.rglob("*")):
            if not item.is_file():
                continue
            if item.suffix == ".jsonl" or item.name == "README.md":
                continue
            rel = item.relative_to(section_src)
            dst = section_dst / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                shutil.copy2(item, dst)

    for fname in ("inbox.md",):
        f = src / fname
        if f.exists():
            dst = vault_dir / fname.replace("inbox", "Inbox")
            if not dst.exists():
                shutil.copy2(f, dst)


def _task_status_icon(status: str) -> str:
    return {"active": "🔵", "backlog": "⚪", "done": "✅", "abandoned": "❌"}.get(
        status, "⚪"
    )


def _build_home(vault_dir: Path, scopes: list[Scope]) -> None:
    """Create the Home MOC (Map of Content) as the vault's landing page."""
    lines = ["# geno-notes", ""]

    all_tasks: list[tasks.Task] = []
    for scope in scopes:
        all_tasks.extend(tasks.load_all(scope.dir))

    active = [t for t in all_tasks if t.status == "active"]
    backlog = [t for t in all_tasks if t.status == "backlog"]
    done = [t for t in all_tasks if t.status == "done"]

    if active:
        lines.append("## Active tasks")
        lines.append("")
        for t in active:
            lines.append(f"- {_task_status_icon(t.status)} [[Tasks/{t.id}|{t.title}]]")
        lines.append("")

    lines.append(f"## Navigation")
    lines.append("")
    lines.append(f"- [[Tasks/_index|Tasks]] ({len(active)} active, {len(backlog)} backlog, {len(done)} done)")

    journal_dir = vault_dir / "Journal"
    if journal_dir.is_dir():
        months = sorted(journal_dir.rglob("*.md"), reverse=True)
        count = len(months)
        lines.append(f"- Journal ({count} months)")
        for m in months[:6]:
            rel = m.relative_to(vault_dir)
            label = m.stem
            lines.append(f"  - [[{rel.with_suffix('')}|{label}]]")
        if count > 6:
            lines.append(f"  - _…and {count - 6} more_")

    wiki_dir = vault_dir / "Wiki"
    if wiki_dir.is_dir():
        pages = [p for p in sorted(wiki_dir.glob("*.md")) if p.name not in ("index.md", "README.md")]
        lines.append(f"- [[Wiki/index|Wiki]] ({len(pages)} pages)")
        for p in pages[:10]:
            label = p.stem.replace("-", " ").replace("_", " ").title()
            lines.append(f"  - [[Wiki/{p.stem}|{label}]]")

    plans_dir = vault_dir / "Plans"
    if plans_dir.is_dir():
        plans = sorted(plans_dir.glob("*.md"))
        if plans:
            lines.append(f"- Plans ({len(plans)})")
            for p in plans:
                label = p.stem.replace("-", " ").replace("_", " ")
                lines.append(f"  - [[Plans/{p.stem}|{label}]]")

    inbox = vault_dir / "Inbox.md"
    if inbox.exists():
        lines.append("- [[Inbox]]")

    lines.append("")
    (vault_dir / "Home.md").write_text("\n".join(lines), encoding="utf-8")


def _build_task_index(vault_dir: Path, scopes: list[Scope]) -> None:
    """Create the Tasks overview MOC."""
    tasks_dir = vault_dir / "Tasks"
    if not tasks_dir.is_dir():
        return

    all_tasks: list[tasks.Task] = []
    for scope in scopes:
        all_tasks.extend(tasks.load_all(scope.dir))

    groups = {"active": [], "backlog": [], "done": [], "abandoned": []}
    for t in all_tasks:
        groups.setdefault(t.status, []).append(t)

    lines = ["# Tasks", ""]
    for status in ("active", "backlog", "done", "abandoned"):
        items = groups.get(status, [])
        if not items:
            continue
        lines.append(f"## {status.capitalize()} ({len(items)})")
        lines.append("")
        for t in items:
            icon = _task_status_icon(status)
            tags = " ".join(f"#{tag}" for tag in t.tags) if t.tags else ""
            suffix = f"  {tags}" if tags else ""
            lines.append(f"- {icon} [[{t.id}|{t.title}]]{suffix}")
        lines.append("")

    (tasks_dir / "_index.md").write_text("\n".join(lines), encoding="utf-8")


def _write_obsidian_config(vault_dir: Path) -> None:
    """Write minimal .obsidian/ config for a pleasant default experience."""
    obsidian_dir = vault_dir / ".obsidian"
    obsidian_dir.mkdir(exist_ok=True)

    app_json = {
        "defaultViewMode": "preview",
        "showLineNumber": True,
        "strictLineBreaks": True,
        "readableLineLength": True,
    }
    (obsidian_dir / "app.json").write_text(
        json.dumps(app_json, indent=2), encoding="utf-8"
    )

    appearance_json = {
        "accentColor": "#7b6cf6",
        "baseFontSize": 16,
    }
    (obsidian_dir / "appearance.json").write_text(
        json.dumps(appearance_json, indent=2), encoding="utf-8"
    )

    workspace_json = {
        "main": {
            "id": "main",
            "type": "split",
            "children": [
                {
                    "id": "leaf-1",
                    "type": "leaf",
                    "state": {
                        "type": "markdown",
                        "state": {"file": "Home.md", "mode": "preview"},
                    },
                }
            ],
            "direction": "vertical",
        },
        "left": {"id": "left", "type": "split", "children": [], "direction": "horizontal", "width": 300},
        "right": {"id": "right", "type": "split", "children": [], "direction": "horizontal", "width": 300},
        "active": "leaf-1",
    }
    (obsidian_dir / "workspace.json").write_text(
        json.dumps(workspace_json, indent=2), encoding="utf-8"
    )

    graph_json = {
        "collapse-filter": False,
        "search": "",
        "showTags": True,
        "showAttachments": False,
        "hideUnresolved": False,
        "showOrphans": True,
        "collapse-color-groups": False,
        "colorGroups": [
            {"query": "path:Tasks", "color": {"a": 1, "rgb": 5145582}},
            {"query": "path:Journal", "color": {"a": 1, "rgb": 2271478}},
            {"query": "path:Wiki", "color": {"a": 1, "rgb": 16744448}},
            {"query": "path:Plans", "color": {"a": 1, "rgb": 10066329}},
        ],
        "collapse-display": False,
        "showArrow": True,
        "textFadeMultiplier": 0,
        "nodeSizeMultiplier": 1,
        "lineSizeMultiplier": 1,
        "collapse-forces": True,
        "centerStrength": 0.5,
        "repelStrength": 10,
        "linkStrength": 1,
        "linkDistance": 250,
    }
    (obsidian_dir / "graph.json").write_text(
        json.dumps(graph_json, indent=2), encoding="utf-8"
    )


def generate(scopes: list[Scope], output_base: Path | None = None) -> Path:
    """Create an Obsidian vault from one or more scopes. Returns the vault dir."""
    primary = scopes[0]

    if output_base is None:
        output_base = primary.dir / ".geno-notes"
    vault_dir = output_base / STAGING_DIR_NAME
    if vault_dir.exists():
        shutil.rmtree(vault_dir)
    vault_dir.mkdir(parents=True)

    for scope in scopes:
        _stage_scope(scope, vault_dir)

    _build_task_index(vault_dir, scopes)
    _build_home(vault_dir, scopes)
    _write_obsidian_config(vault_dir)

    return vault_dir


def open_vault(vault_dir: Path) -> None:
    """Open the vault in Obsidian."""
    import platform
    import subprocess as sp

    system = platform.system()
    vault_uri = f"obsidian://open?path={vault_dir.resolve()}"

    if system == "Darwin":
        sp.Popen(["open", vault_uri])
    elif system == "Linux":
        sp.Popen(["xdg-open", vault_uri])
    else:
        print(f"Open Obsidian and add vault at: {vault_dir}")
