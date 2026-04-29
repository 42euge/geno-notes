"""Generate a MkDocs Material site from geno-notes content."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

from geno_notes.paths import Scope


MKDOCS_DEPS = {"mkdocs": "mkdocs", "mkdocs-material": "material"}

BUILD_DIR_NAME = "site"
STAGING_DIR_NAME = "_site_staging"


def check_deps() -> list[str]:
    """Return list of missing mkdocs dependencies."""
    missing = []
    for pip_name, import_name in MKDOCS_DEPS.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    return missing


def install_deps(missing: list[str]) -> None:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", *missing],
        stdout=subprocess.DEVNULL,
    )


def _collect_nav(docs_dir: Path) -> list:
    """Build a nav list from the staged docs directory."""
    nav: list = []

    index = docs_dir / "index.md"
    if index.exists():
        nav.append({"Home": "index.md"})

    tasks_dir = docs_dir / "tasks"
    if tasks_dir.is_dir():
        task_entries = []
        task_index = tasks_dir / "_index.md"
        if task_index.exists():
            task_entries.append({"Overview": "tasks/_index.md"})
        for f in sorted(tasks_dir.glob("*.md")):
            if f.name.startswith("_"):
                continue
            label = f.stem.replace("-", " ").replace("_", " ")
            task_entries.append({label: f"tasks/{f.name}"})
        if task_entries:
            nav.append({"Tasks": task_entries})

    journal_dir = docs_dir / "journal"
    if journal_dir.is_dir():
        journal_entries = []
        for year_dir in sorted(journal_dir.iterdir(), reverse=True):
            if not year_dir.is_dir():
                continue
            for f in sorted(year_dir.glob("*.md"), reverse=True):
                label = f.stem
                journal_entries.append({label: f"journal/{year_dir.name}/{f.name}"})
        if journal_entries:
            nav.append({"Journal": journal_entries})

    wiki_dir = docs_dir / "wiki"
    if wiki_dir.is_dir():
        wiki_entries = []
        wiki_index = wiki_dir / "index.md"
        if wiki_index.exists():
            wiki_entries.append({"Overview": "wiki/index.md"})
        for f in sorted(wiki_dir.glob("*.md")):
            if f.name in ("index.md", "README.md"):
                continue
            label = f.stem.replace("-", " ").replace("_", " ").title()
            wiki_entries.append({label: f"wiki/{f.name}"})
        if wiki_entries:
            nav.append({"Wiki": wiki_entries})

    plans_dir = docs_dir / "plans"
    if plans_dir.is_dir():
        plan_entries = []
        for f in sorted(plans_dir.glob("*.md")):
            label = f.stem.replace("-", " ").replace("_", " ")
            plan_entries.append({label: f"plans/{f.name}"})
        if plan_entries:
            nav.append({"Plans": plan_entries})

    inbox = docs_dir / "inbox.md"
    if inbox.exists():
        nav.append({"Inbox": "inbox.md"})

    return nav


def _generate_mkdocs_yml(staging_dir: Path, site_name: str, nav: list) -> Path:
    """Write mkdocs.yml into the staging directory."""
    import yaml

    config = {
        "site_name": site_name,
        "docs_dir": str(staging_dir / "docs"),
        "site_dir": str(staging_dir / BUILD_DIR_NAME),
        "theme": {
            "name": "material",
            "palette": [
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Switch to dark mode",
                    },
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Switch to light mode",
                    },
                },
            ],
            "font": {"text": "Inter", "code": "JetBrains Mono"},
            "features": [
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
                "content.code.copy",
                "search.highlight",
                "search.suggest",
                "toc.follow",
            ],
        },
        "markdown_extensions": [
            "admonition",
            "pymdownx.details",
            "pymdownx.superfences",
            {"pymdownx.highlight": {"anchor_linenums": True}},
            "pymdownx.inlinehilite",
            {"pymdownx.tabbed": {"alternate_style": True}},
            "attr_list",
            "md_in_html",
            "def_list",
            {"toc": {"permalink": True}},
        ],
    }

    if nav:
        config["nav"] = nav

    yml_path = staging_dir / "mkdocs.yml"
    yml_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False), encoding="utf-8")
    return yml_path


def _stage_scope(scope: Scope, docs_dir: Path) -> None:
    """Copy a scope's content into the docs directory."""
    src = scope.dir

    skip = {"README.md"}

    for section in ("tasks", "journal", "plans", "wiki"):
        section_src = src / section
        if section_src.is_dir():
            section_dst = docs_dir / section
            if section_dst.exists():
                for item in section_src.rglob("*"):
                    if item.is_file() and item.name not in skip:
                        rel = item.relative_to(section_src)
                        dst = section_dst / rel
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        if not dst.exists():
                            shutil.copy2(item, dst)
            else:
                shutil.copytree(
                    section_src,
                    section_dst,
                    ignore=shutil.ignore_patterns(*skip),
                )

    for fname in ("index.md", "inbox.md"):
        f = src / fname
        if f.exists():
            dst = docs_dir / fname
            if not dst.exists():
                shutil.copy2(f, dst)


def generate(scopes: list[Scope], output_base: Path | None = None) -> Path:
    """Scaffold a MkDocs project from one or more scopes. Returns the staging dir."""
    primary = scopes[0]

    if output_base is None:
        output_base = primary.dir / ".geno-notes"
    staging_dir = output_base / STAGING_DIR_NAME
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)

    docs_dir = staging_dir / "docs"
    docs_dir.mkdir()

    for scope in scopes:
        _stage_scope(scope, docs_dir)

    if len(scopes) == 1:
        site_name = f"geno-notes ({primary.name})"
    else:
        site_name = "geno-notes (all scopes)"

    nav = _collect_nav(docs_dir)
    _generate_mkdocs_yml(staging_dir, site_name, nav)

    return staging_dir


def build(staging_dir: Path) -> Path:
    """Run mkdocs build. Returns the site output directory."""
    yml_path = staging_dir / "mkdocs.yml"
    subprocess.check_call(
        [sys.executable, "-m", "mkdocs", "build", "-f", str(yml_path), "-q"],
    )
    return staging_dir / BUILD_DIR_NAME


def serve(staging_dir: Path, port: int = 8000) -> subprocess.Popen:
    """Start mkdocs serve. Returns the Popen handle."""
    yml_path = staging_dir / "mkdocs.yml"
    return subprocess.Popen(
        [sys.executable, "-m", "mkdocs", "serve", "-f", str(yml_path), "-a", f"localhost:{port}"],
    )
