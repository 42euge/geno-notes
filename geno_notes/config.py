"""Config file read/write + schema guard.

config.toml lives at <scope-dir>/.geno-notes/config.toml and records:
    schema_version — the schema this scope was written with
    scope          — "global" | "project" (set at init time)
    tz             — IANA timezone name, used for localized headers
    default_tags   — tag list applied to new tasks
"""

from __future__ import annotations

import sys
from pathlib import Path

from geno_notes import SCHEMA_VERSION

# Python 3.11+ ships tomllib; tomli_w is an optional dep we'll write ourselves
# to avoid the dependency (our config is simple enough).
try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:  # Python <3.11 fallback
    import tomli as tomllib  # type: ignore[no-redef]


CONFIG_REL = Path(".geno-notes") / "config.toml"


def config_path(scope_dir: Path) -> Path:
    return scope_dir / CONFIG_REL


def read_config(scope_dir: Path) -> dict | None:
    p = config_path(scope_dir)
    if not p.exists():
        return None
    with p.open("rb") as f:
        return tomllib.load(f)


def write_config(scope_dir: Path, *, scope_name: str, tz: str = "UTC", default_tags: list[str] | None = None) -> None:
    p = config_path(scope_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    tags_line = "[" + ", ".join(f'"{t}"' for t in (default_tags or [])) + "]"
    body = (
        f'schema_version = "{SCHEMA_VERSION}"\n'
        f'scope = "{scope_name}"\n'
        f'tz = "{tz}"\n'
        f"default_tags = {tags_line}\n"
    )
    p.write_text(body, encoding="utf-8")


def ensure_config(scope_dir: Path, scope_name: str) -> dict:
    """Read config, creating it with defaults if missing. Enforces schema guard."""
    cfg = read_config(scope_dir)
    if cfg is None:
        write_config(scope_dir, scope_name=scope_name)
        cfg = read_config(scope_dir) or {}
    _check_schema(cfg)
    return cfg


def _check_schema(cfg: dict) -> None:
    got = str(cfg.get("schema_version", "0.0.0"))
    if _vt(got) > _vt(SCHEMA_VERSION):
        print(
            f"error: geno-notes schema_version {got} is newer than this CLI ({SCHEMA_VERSION}). "
            "Upgrade the geno-notes package.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def _vt(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)
