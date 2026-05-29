#!/usr/bin/env bash
# Claisum macOS Installer — no Python required, just curl + bash
set -euo pipefail

RESET="\033[0m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BOLD="\033[1m"
DIM="\033[2m"

REPO="claisum/Claisum.py"
INJECT_JS_URL="https://raw.githubusercontent.com/${REPO}/main/claisum/discord/claisum_inject.js"
MARKER="claisum_inject"
INJECT_LINE1="// [Claisum] Do NOT remove — uninstall via install-macos.sh --remove"
INJECT_LINE2="try{require('./claisum_inject.js');}catch(e){console.error('[Claisum load]',e);}"

echo ""
echo -e "${BOLD}=========================================="
echo -e "  ⚡ Claisum Installer for macOS"
echo -e "  https://github.com/${REPO}"
echo -e "==========================================${RESET}"
echo ""

# ── Find all Discord index.js paths ───────────────────────────────────────
find_discord_indices() {
    local lib="$HOME/Library/Application Support"
    local dirs=("discord" "discordptb" "discordcanary" "discorddev")
    local found=()
    for dir in "${dirs[@]}"; do
        local base="$lib/$dir"
        [ -d "$base" ] || continue
        while IFS= read -r -d '' f; do
            found+=("$f")
        done < <(find "$base" \
            -path "*/discord_desktop_core/index.js" \
            -print0 2>/dev/null | sort -rz)
    done
    printf '%s\n' "${found[@]}" 2>/dev/null | sort -u
}

# ── Kill Discord ────────────────────────────────────────────────────────────
kill_discord() {
    osascript -e 'tell application "Discord" to quit' 2>/dev/null || true
    sleep 0.8
    pkill -f "/Applications/Discord" 2>/dev/null || true
    pkill -f "Discord.app" 2>/dev/null || true
    sleep 0.5
}

# ── Restart Discord ─────────────────────────────────────────────────────────
open_discord() {
    for app in \
        "/Applications/Discord.app" \
        "$HOME/Applications/Discord.app" \
        "/Applications/Discord PTB.app" \
        "/Applications/Discord Canary.app"
    do
        if [ -d "$app" ]; then
            open "$app"
            return 0
        fi
    done
    return 1
}

# ── Strip existing Claisum lines from a file (safe, no Python) ─────────────
strip_claisum() {
    local file="$1"
    grep -v "$MARKER" "$file" | grep -v "\[Claisum\]" > /tmp/claisum_stripped.js
    cat /tmp/claisum_stripped.js > "$file"
}

# ── Inject Claisum into a single index.js ──────────────────────────────────
inject_into() {
    local idx="$1"
    local core
    core="$(dirname "$idx")"
    local dest="$core/claisum_inject.js"

    # Download claisum_inject.js
    echo -e "  ${DIM}·${RESET} Downloading claisum_inject.js…"
    curl -fsSL "$INJECT_JS_URL" -o "$dest"

    # Strip any old injection, then prepend fresh lines
    strip_claisum "$idx"
    { printf '%s\n%s\n' "$INJECT_LINE1" "$INJECT_LINE2"; cat "$idx"; } > /tmp/claisum_patched.js
    cat /tmp/claisum_patched.js > "$idx"
}

# ══ REMOVE mode ═══════════════════════════════════════════════════════════
if [[ "${1:-}" == "--remove" || "${1:-}" == "-r" ]]; then
    echo -e "${BOLD}Removing Claisum…${RESET}"
    echo ""

    mapfile -t INDICES < <(find_discord_indices)
    if [ ${#INDICES[@]} -eq 0 ]; then
        echo -e "  ${RED}✗${RESET} Discord not found."
        exit 1
    fi

    kill_discord
    echo -e "  ${GREEN}✓${RESET} Discord closed."

    REMOVED=0
    for idx in "${INDICES[@]}"; do
        if grep -q "$MARKER" "$idx" 2>/dev/null; then
            core="$(dirname "$idx")"
            strip_claisum "$idx"
            rm -f "$core/claisum_inject.js"
            echo -e "  ${GREEN}✓${RESET} Cleaned: $idx"
            REMOVED=$((REMOVED + 1))
        fi
    done

    if [ $REMOVED -eq 0 ]; then
        echo -e "  ${YELLOW}!${RESET} Claisum was not injected — nothing to remove."
    else
        echo ""
        echo -e "${BOLD}=========================================="
        echo -e "${GREEN}  ✓ Claisum removed successfully!${RESET}${BOLD}"
        echo -e "==========================================${RESET}"
        echo ""
        echo "  Restart Discord to confirm it's clean."
    fi
    exit 0
fi

# ══ INSTALL mode ══════════════════════════════════════════════════════════
echo -e "[1/4] Looking for Discord…"
mapfile -t INDICES < <(find_discord_indices)

if [ ${#INDICES[@]} -eq 0 ]; then
    echo -e "  ${RED}✗${RESET} Discord not found."
    echo ""
    echo "  → Install Discord from https://discord.com/download"
    echo "  → Launch Discord at least once, then re-run this script."
    exit 1
fi

echo -e "  ${GREEN}✓${RESET} Found ${#INDICES[@]} Discord installation(s)"
echo ""

echo -e "[2/4] Stopping Discord…"
kill_discord
echo -e "  ${GREEN}✓${RESET} Done"
echo ""

echo -e "[3/4] Injecting Claisum…"
PATCHED=0
for idx in "${INDICES[@]}"; do
    echo -e "  ${DIM}→${RESET} $idx"
    inject_into "$idx"
    echo -e "  ${GREEN}✓${RESET} Patched"
    PATCHED=$((PATCHED + 1))
done
echo ""

echo -e "[4/4] Verifying…"
OK=1
for idx in "${INDICES[@]}"; do
    if ! grep -q "$MARKER" "$idx" 2>/dev/null; then
        echo -e "  ${RED}✗${RESET} Verify failed: $idx"
        OK=0
    fi
done

if [ $OK -eq 0 ]; then
    echo -e "  ${RED}Installation could not be verified — try again.${RESET}"
    exit 1
fi

echo -e "  ${GREEN}✓${RESET} Verified"
echo ""
echo -e "${BOLD}=========================================="
echo -e "${GREEN}  ✓ Claisum installed successfully!${RESET}${BOLD}"
echo -e "==========================================${RESET}"
echo ""
echo -e "  Restart Discord to see the ${CYAN}⚡${RESET} button."
echo -e "  Press ${BOLD}F8${RESET} inside Discord to open the panel."
echo ""

printf "  Restart Discord now? [Y/n] "
read -r ans
ans="${ans:-y}"
if [[ "${ans,,}" == "y" ]]; then
    if open_discord; then
        echo -e "  ${GREEN}✓${RESET} Discord restarted."
    else
        echo -e "  ${YELLOW}!${RESET} Could not find Discord.app — restart manually."
    fi
fi
echo ""
