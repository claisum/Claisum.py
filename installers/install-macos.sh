#!/usr/bin/env bash
set -e

RESET="\033[0m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BOLD="\033[1m"

echo ""
echo -e "${BOLD}=========================================="
echo -e "  Claisum Installer for macOS"
echo -e "  https://github.com/claisum/Claisum.py"
echo -e "==========================================${RESET}"
echo ""

# Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] Python 3 was not found on your system.${RESET}"
    echo ""
    echo "Install it from https://www.python.org/downloads/ or via Homebrew:"
    echo "  brew install python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}Python found: ${PYTHON_VERSION}${RESET}"
echo ""

# Check for pip
PIP=""
if command -v pip3 &>/dev/null; then
    PIP="pip3"
elif python3 -m pip --version &>/dev/null 2>&1; then
    PIP="python3 -m pip"
else
    echo -e "${RED}[ERROR] pip was not found.${RESET}"
    echo "Install it with: python3 -m ensurepip --upgrade"
    exit 1
fi

# Install from GitHub
echo "Installing Claisum from GitHub..."
$PIP install --upgrade \
    "https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip" \
    --quiet

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Installation failed.${RESET}"
    echo ""
    echo "Try running manually:"
    echo "  pip3 install https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip"
    exit 1
fi

echo ""
echo -e "${BOLD}=========================================="
echo -e "${GREEN}  Claisum installed successfully!${RESET}${BOLD}"
echo -e "==========================================${RESET}"
echo ""
echo -e "Get started:"
echo -e "  ${CYAN}claisum --help${RESET}"
echo -e "  ${CYAN}claisum discord themes list${RESET}"
echo -e "  ${CYAN}claisum discord plugins available${RESET}"
echo ""
echo -e "Inject into Discord:"
echo -e "  ${CYAN}claisum discord inject${RESET}"
echo ""

# Warn if ~/.local/bin is not on PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]] && [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
    echo -e "${YELLOW}Note: If 'claisum' is not found, add Python scripts to PATH:${RESET}"
    echo "  echo 'export PATH=\"\$HOME/Library/Python/3.x/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
    echo ""
fi
