#!/data/data/com.termux/files/usr/bin/bash
# Claisum Android Installer — run this inside Termux
set -euo pipefail

RESET="\033[0m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BOLD="\033[1m"
DIM="\033[2m"

REPO="claisum/Claisum.py"
PIP_URL="https://github.com/${REPO}/archive/refs/heads/main.zip"

echo ""
echo -e "${BOLD}=========================================="
echo -e "  ⚡ Claisum Installer for Android"
echo -e "  https://github.com/${REPO}"
echo -e "==========================================${RESET}"
echo ""

# ── Termux check ───────────────────────────────────────────────────────────
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}✗ This script must be run inside Termux.${RESET}"
    echo ""
    echo "  Install Termux from F-Droid:"
    echo "  https://f-droid.org/packages/com.termux/"
    exit 1
fi

# ── Remove mode ────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--remove" || "${1:-}" == "-r" ]]; then
    echo -e "${BOLD}Removing Claisum…${RESET}"
    echo ""
    if pip show claisum &>/dev/null 2>&1; then
        pip uninstall claisum -y
        echo -e "  ${GREEN}✓${RESET} Claisum removed."
    else
        echo -e "  ${YELLOW}!${RESET} Claisum was not installed."
    fi
    echo ""
    exit 0
fi

# ══ Install ════════════════════════════════════════════════════════════════
echo -e "[1/4] Updating package list…"
pkg update -y -q 2>/dev/null || true
echo -e "  ${GREEN}✓${RESET} Done"
echo ""

echo -e "[2/4] Installing Python…"
if command -v python &>/dev/null || command -v python3 &>/dev/null; then
    echo -e "  ${GREEN}✓${RESET} Python already installed"
else
    pkg install python -y -q
    echo -e "  ${GREEN}✓${RESET} Python installed"
fi
echo ""

# Ensure pip is available
PYTHON="python"
if ! command -v python &>/dev/null; then
    PYTHON="python3"
fi
$PYTHON -m ensurepip --upgrade &>/dev/null 2>&1 || true
PIP="$PYTHON -m pip"

echo -e "[3/4] Downloading and installing Claisum…"
$PIP install --upgrade "$PIP_URL" --quiet
echo -e "  ${GREEN}✓${RESET} Claisum installed"
echo ""

echo -e "[4/4] Verifying installation…"
if ! command -v claisum &>/dev/null; then
    # Try adding Termux bin to PATH
    TERMUX_BIN="$HOME/.local/bin"
    export PATH="$TERMUX_BIN:$PATH"
fi

if command -v claisum &>/dev/null; then
    echo -e "  ${GREEN}✓${RESET} claisum command found"
else
    echo -e "  ${YELLOW}!${RESET} 'claisum' not on PATH yet — see note below"
fi
echo ""

echo -e "${BOLD}=========================================="
echo -e "${GREEN}  ✓ Claisum installed successfully!${RESET}${BOLD}"
echo -e "==========================================${RESET}"
echo ""
echo -e "  Try it:"
echo -e "  ${CYAN}claisum --help${RESET}"
echo -e "  ${CYAN}claisum discord themes list${RESET}"
echo -e "  ${CYAN}claisum discord plugins available${RESET}"
echo ""

# ── PATH reminder ──────────────────────────────────────────────────────────
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}Note:${RESET} Add Claisum to your PATH permanently:"
    echo ""
    echo '  echo '"'"'export PATH="$HOME/.local/bin:$PATH"'"'"' >> ~/.bashrc'
    echo "  source ~/.bashrc"
    echo ""
fi

echo -e "${DIM}Android note: The ⚡ floating button and F8 panel are"
echo -e "desktop-only features (Windows / macOS / Linux).${RESET}"
echo ""
echo -e "  Uninstall: ${CYAN}bash install-android.sh --remove${RESET}"
echo ""
