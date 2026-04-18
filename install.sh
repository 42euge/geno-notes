#!/usr/bin/env bash
# install.sh — geno-notes installer.
#
# Does:
#   1. pip install -e . into ~/.geno/venv
#   2. Symlink ~/.geno/venv/bin/geno-notes → ~/.local/bin/geno-notes (PATH shim
#      so consumers can call a bare `geno-notes`, no hardcoded venv paths).
#   3. Symlink skills/geno-notes/ → ~/.claude/skills/geno-notes
#   4. Symlink commands/gt-notes.md → ~/.claude/commands/gt-notes.md
#   5. Scaffold ~/.geno/geno-notes/ (global scope) on first install.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${HOME}/.geno/venv"
LOCAL_BIN="${HOME}/.local/bin"
CLAUDE_SKILLS="${HOME}/.claude/skills"
CLAUDE_COMMANDS="${HOME}/.claude/commands"
GLOBAL_SCOPE="${HOME}/.geno/geno-notes"

echo "geno-notes installer"
echo "  Source:  $REPO_DIR"
echo "  Venv:    $VENV_DIR"
echo "  Bin:     $LOCAL_BIN"
echo "  Claude:  $CLAUDE_SKILLS, $CLAUDE_COMMANDS"
echo ""

link_file() {
    local src="$1" dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -L "$dst" ] || [ -e "$dst" ]; then
        rm -f "$dst"
    fi
    ln -s "$src" "$dst"
    echo "  Linked: $dst → $src"
}

# ── 1. pip install into venv ─────────────────────────────────────────
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "error: $VENV_DIR/bin/python not found."
    echo "       Create the ecosystem venv first (geno-agents / geno-term etc.)."
    exit 1
fi
echo "Installing Python package into $VENV_DIR..."
"$VENV_DIR/bin/pip" install -e "$REPO_DIR" --quiet
echo "  Installed: geno-notes (editable)"
echo ""

# ── 2. PATH shim ─────────────────────────────────────────────────────
mkdir -p "$LOCAL_BIN"
link_file "$VENV_DIR/bin/geno-notes" "$LOCAL_BIN/geno-notes"
echo ""

# ── 3. Claude skill ──────────────────────────────────────────────────
link_file "$REPO_DIR/skills/geno-notes" "$CLAUDE_SKILLS/geno-notes"
echo ""

# ── 4. Claude commands ───────────────────────────────────────────────
echo "Installing slash commands..."
for cmd_file in "$REPO_DIR"/commands/gt-*.md; do
    [ -f "$cmd_file" ] || continue
    name="$(basename "$cmd_file")"
    link_file "$cmd_file" "$CLAUDE_COMMANDS/$name"
done
echo ""

# ── 5. Initialize global scope ───────────────────────────────────────
if [ ! -d "$GLOBAL_SCOPE" ]; then
    echo "Initializing global scope at $GLOBAL_SCOPE..."
    "$VENV_DIR/bin/geno-notes" init --global >/dev/null
    echo "  Created: $GLOBAL_SCOPE"
else
    echo "Global scope already exists: $GLOBAL_SCOPE"
fi

echo ""
echo "Done. Verify with:  geno-notes scope"
