"""geno-notes — click CLI group."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import click

from geno_notes import SCHEMA_VERSION, events, journal, tasks
from geno_notes.config import ensure_config, read_config, write_config
from geno_notes.indexer import reindex
from geno_notes.paths import (
    GLOBAL_DIR,
    PROJECT_DIRNAME,
    PROJECT_SUBDIRNAME,
    Scope,
    ensure_structure,
    list_all_scopes,
    resolve_scope,
    scope_for,
)
from geno_notes.search import search as _search


# ─── scope option plumbing ─────────────────────────────────────────────


def _scope_options(f):
    f = click.option("--global", "global_", is_flag=True, help="Force global scope.")(f)
    f = click.option("--project", "project_", is_flag=True, help="Force project scope.")(f)
    return f


def _pick_scope(global_: bool, project_: bool) -> Scope:
    if global_ and project_:
        click.echo("error: --global and --project are mutually exclusive", err=True)
        sys.exit(2)
    override = "global" if global_ else "project" if project_ else None
    scope = resolve_scope(override=override)
    # Ensure the scope is scaffolded — we want `geno-notes note "x"` in a fresh
    # environment to just work against the auto-created global dir.
    ensure_structure(scope)
    ensure_config(scope.dir, scope.name)
    return scope


# ─── root ──────────────────────────────────────────────────────────────


@click.group()
@click.version_option(SCHEMA_VERSION, prog_name="geno-notes")
def main():
    """geno-notes — project journal with global + per-project scopes."""


# ─── scope + init ──────────────────────────────────────────────────────


@main.command()
@_scope_options
def path(global_: bool, project_: bool):
    """Print the active scope's directory."""
    scope = _pick_scope(global_, project_)
    click.echo(str(scope.dir))


@main.command()
def scope():
    """Print the active scope + both scope dirs."""
    active = resolve_scope()
    click.echo(f"active:  {active.name}  {active.dir}")
    click.echo(f"global:  {GLOBAL_DIR}  {'(exists)' if GLOBAL_DIR.is_dir() else '(not created)'}")
    try:
        pscope = scope_for("project")
        click.echo(f"project: {pscope.dir}  (exists)")
    except RuntimeError:
        click.echo("project: (none in cwd or ancestors)")


@main.command()
@_scope_options
def init(global_: bool, project_: bool):
    """Scaffold a scope's directory structure + config.toml."""
    if not global_ and not project_:
        # Default: if a project scope ALREADY exists, re-init it; else global.
        # But if user is in a fresh dir, default to project since that's the
        # more common case for a brand-new project setup.
        try:
            scope_for("project")
            target = Scope("project", scope_for("project").dir)
        except RuntimeError:
            # No existing project; create one in cwd.
            target_dir = Path.cwd() / PROJECT_DIRNAME / PROJECT_SUBDIRNAME
            target = Scope("project", target_dir)
    elif project_:
        target_dir = Path.cwd() / PROJECT_DIRNAME / PROJECT_SUBDIRNAME
        target = Scope("project", target_dir)
    else:
        target = Scope("global", GLOBAL_DIR)

    ensure_structure(target)
    write_config(target.dir, scope_name=target.name)
    reindex(target.dir, target.name)
    click.echo(f"Initialized {target.name} scope at {target.dir}")


# ─── tasks ─────────────────────────────────────────────────────────────


@main.command()
@click.argument("description", nargs=-1, required=True)
@click.option("--tag", "-t", "tags", multiple=True, help="Tag (repeatable).")
@_scope_options
def add(description: tuple, tags: tuple, global_: bool, project_: bool):
    """Create a new task in Backlog."""
    scope = _pick_scope(global_, project_)
    title = " ".join(description).strip()
    task = tasks.create(scope.dir, title, tags=list(tags))
    reindex(scope.dir, scope.name)
    click.echo(f"{task.id}  (backlog)")


def _resolve_task(scope: Scope, pattern: str) -> tasks.Task:
    all_tasks = tasks.load_all(scope.dir)
    candidates = tasks.find_candidates(all_tasks, pattern)
    if not candidates:
        click.echo(f"error: no task matches {pattern!r} in {scope.name} scope", err=True)
        sys.exit(1)
    if len(candidates) > 1:
        click.echo(f"error: {len(candidates)} tasks match {pattern!r}:", err=True)
        for t in candidates:
            click.echo(f"  {t.id}  [{t.status}]  {t.title}", err=True)
        sys.exit(1)
    return candidates[0]


@main.command()
@click.argument("pattern")
@_scope_options
def start(pattern: str, global_: bool, project_: bool):
    """Activate a task (backlog → active)."""
    scope = _pick_scope(global_, project_)
    task = _resolve_task(scope, pattern)
    updated = tasks.transition(scope.dir, task.id, "active")
    reindex(scope.dir, scope.name)
    click.echo(f"{updated.id}  active")


@main.command()
@click.argument("pattern")
@_scope_options
def done(pattern: str, global_: bool, project_: bool):
    """Complete a task."""
    scope = _pick_scope(global_, project_)
    task = _resolve_task(scope, pattern)
    updated = tasks.transition(scope.dir, task.id, "done")
    reindex(scope.dir, scope.name)
    click.echo(f"{updated.id}  done")


@main.command()
@click.argument("pattern")
@_scope_options
def abandon(pattern: str, global_: bool, project_: bool):
    """Mark a task abandoned."""
    scope = _pick_scope(global_, project_)
    task = _resolve_task(scope, pattern)
    updated = tasks.transition(scope.dir, task.id, "abandoned")
    reindex(scope.dir, scope.name)
    click.echo(f"{updated.id}  abandoned")


# ─── journal + inbox ───────────────────────────────────────────────────


@main.command()
@click.argument("text", nargs=-1, required=True)
@click.option("--task", "task_pattern", default=None, help="Link to a task (fuzzy match).")
@click.option(
    "--kind",
    default="note",
    type=click.Choice(sorted(journal.ALLOWED_KINDS)),
    help="Entry kind.",
)
@_scope_options
def note(text: tuple, task_pattern: str | None, kind: str, global_: bool, project_: bool):
    """Append a timestamped entry to this month's journal."""
    scope = _pick_scope(global_, project_)
    body = " ".join(text).strip()
    task_id = None
    if task_pattern:
        task_id = _resolve_task(scope, task_pattern).id
    rec = journal.append(scope.dir, body, kind=kind, task_id=task_id)
    if task_id:
        tasks.append_journal_ref(scope.dir, task_id, rec["ts"], body)
    events.log(
        scope.dir,
        "note.append",
        target=task_id,
        kind=kind,
        journal=rec["ts"][:7],  # YYYY-MM
    )
    click.echo(f"{rec['ts']}  {kind}" + (f"  (task: {task_id})" if task_id else ""))


@main.command()
@click.argument("text", nargs=-1, required=True)
@_scope_options
def inbox(text: tuple, global_: bool, project_: bool):
    """Append a free-floating capture to inbox.md."""
    scope = _pick_scope(global_, project_)
    body = " ".join(text).strip()
    if not body:
        click.echo("error: empty inbox entry", err=True)
        sys.exit(1)
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"- `{ts}` — {body}\n"
    with (scope.dir / "inbox.md").open("a", encoding="utf-8") as f:
        f.write(line)
    events.log(scope.dir, "inbox.append", target=None, ts=ts)
    click.echo(f"{ts}  inbox")


@main.command()
@_scope_options
def triage(global_: bool, project_: bool):
    """Interactively promote inbox items to tasks (or drop them)."""
    scope = _pick_scope(global_, project_)
    inbox_path = scope.dir / "inbox.md"
    if not inbox_path.exists():
        click.echo("inbox is empty")
        return
    lines = inbox_path.read_text(encoding="utf-8").splitlines()
    entries: list[tuple[int, str]] = [
        (i, ln) for i, ln in enumerate(lines) if ln.strip().startswith("- `")
    ]
    if not entries:
        click.echo("no inbox items to triage")
        return
    keep = list(lines)
    for idx, ln in entries:
        click.echo(f"\n{ln}")
        choice = click.prompt(
            "[p]romote to task / [d]rop / [s]kip", default="s", type=click.Choice(["p", "d", "s"])
        )
        if choice == "p":
            title = click.prompt("task title", default=ln.split("—", 1)[-1].strip())
            t = tasks.create(scope.dir, title)
            click.echo(f"  → created {t.id}")
            keep[idx] = ""
        elif choice == "d":
            keep[idx] = ""
    kept = "\n".join(ln for ln in keep if ln != "")
    inbox_path.write_text(kept.rstrip() + "\n", encoding="utf-8")
    reindex(scope.dir, scope.name)


# ─── read ──────────────────────────────────────────────────────────────


@main.command("list")
@click.option("--status", "-s", default=None, help="Filter: backlog|active|done|abandoned")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON.")
@click.option("--all", "union", is_flag=True, help="Union project + global.")
@_scope_options
def list_cmd(status: str | None, as_json: bool, union: bool, global_: bool, project_: bool):
    """List tasks in the active scope (or all scopes with --all)."""
    if union:
        scopes = list_all_scopes()
    else:
        scopes = [_pick_scope(global_, project_)]

    rows: list[dict] = []
    for scope in scopes:
        for t in tasks.load_all(scope.dir):
            if status and t.status != status:
                continue
            d = tasks.to_dict(t)
            d["scope"] = scope.name
            rows.append(d)

    if as_json:
        click.echo(json.dumps(rows, indent=2))
        return

    if not rows:
        click.echo("(no tasks)")
        return
    for r in rows:
        click.echo(f"  [{r['status']:<9}] {r['id']:<28} {r['title']}  ({r['scope']})")


@main.command()
@click.argument("pattern")
@click.option("--all", "union", is_flag=True, help="Search both scopes.")
@_scope_options
def show(pattern: str, union: bool, global_: bool, project_: bool):
    """Render a task + its journal refs."""
    scopes = list_all_scopes() if union else [_pick_scope(global_, project_)]
    last_err = None
    for scope in scopes:
        try:
            task = _resolve_task(scope, pattern)
            path = tasks.task_path(scope.dir, task.id)
            click.echo(f"# [{scope.name}] {path}")
            click.echo(path.read_text(encoding="utf-8"))
            return
        except SystemExit as e:
            last_err = e
            continue
    raise last_err or SystemExit(1)


@main.command()
@click.argument("query")
@click.option("--all", "union", is_flag=True, help="Search both scopes.")
@_scope_options
def search(query: str, union: bool, global_: bool, project_: bool):
    """Grep across tasks, journal, plans, inbox."""
    scopes = list_all_scopes() if union else [_pick_scope(global_, project_)]
    hits = _search(scopes, query)
    if not hits:
        click.echo("(no matches)")
        return
    for h in hits:
        click.echo(f"  [{h.scope}] {h.path}:{h.line_no}: {h.line}")


# ─── cross-scope ops ───────────────────────────────────────────────────


@main.command()
@click.argument("pattern")
@click.option("--to", "to_scope", type=click.Choice(["global", "project"]), default=None)
@_scope_options
def promote(pattern: str, to_scope: str | None, global_: bool, project_: bool):
    """Move a task (and its plan) from one scope to the other."""
    src = _pick_scope(global_, project_)
    if to_scope is None:
        to_scope = "global" if src.name == "project" else "project"
    if to_scope == src.name:
        click.echo(f"error: already in {to_scope} scope", err=True)
        sys.exit(2)
    dst = scope_for(to_scope)
    ensure_structure(dst)
    ensure_config(dst.dir, dst.name)

    task = _resolve_task(src, pattern)
    src_path = tasks.task_path(src.dir, task.id)
    dst_path = tasks.task_path(dst.dir, task.id)
    if dst_path.exists():
        click.echo(f"error: {task.id} already exists in {dst.name} scope", err=True)
        sys.exit(1)

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_path), str(dst_path))

    # Move plan if one exists.
    plan_src = src.dir / "plans" / f"{task.id}.md"
    if plan_src.exists():
        plan_dst = dst.dir / "plans" / f"{task.id}.md"
        plan_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(plan_src), str(plan_dst))

    events.log(src.dir, "task.promote.out", target=task.id, to=dst.name)
    events.log(dst.dir, "task.promote.in", target=task.id, from_=src.name)
    reindex(src.dir, src.name)
    reindex(dst.dir, dst.name)
    click.echo(f"{task.id}  moved  {src.name} → {dst.name}")


@main.command("reindex")
@_scope_options
def reindex_cmd(global_: bool, project_: bool):
    """Regenerate index.md + tasks/_index.md."""
    scope = _pick_scope(global_, project_)
    reindex(scope.dir, scope.name)
    click.echo(f"Reindexed {scope.name} scope.")


# ─── wiki (llm-wiki wrapper) ───────────────────────────────────────────


@main.command("compile")
@_scope_options
def compile_cmd(global_: bool, project_: bool):
    """Compile tasks + journal into wiki/ via llm-wiki."""
    scope = _pick_scope(global_, project_)
    try:
        from llm_wiki import compile as wiki_compile
    except ImportError:
        click.echo(
            "llm-wiki is not installed. Install it with: pip install llm-wiki",
            err=True,
        )
        raise SystemExit(1)
    wiki_dir = scope.dir / "wiki"
    wiki_compile(source=scope.dir, output=wiki_dir)


if __name__ == "__main__":
    main()
