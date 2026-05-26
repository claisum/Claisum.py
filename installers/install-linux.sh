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
echo -e "  Claisum Installer for Linux"
echo -e "  https://github.com/claisum/Claisum.py"
echo -e "==========================================${RESET}"
echo ""

# Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] Python 3 was not found on your system.${RESET}"
    echo ""
    echo "Install it with your package manager:"
    echo "  Ubuntu / Debian:  sudo apt install python3 python3-pip"
    echo "  Arch Linux:       sudo pacman -S python python-pip"
    echo "  Fedora:           sudo dnf install python3 python3-pip"
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
    echo "Install it with: sudo apt install python3-pip"
    exit 1
fi

# Install directly from GitHub (no git or ZIP extraction required)
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

# Warn if ~/.local/bin is not on PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}Note: Add ~/.local/bin to your PATH if 'claisum' is not found:${RESET}"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"
    echo ""
fi
