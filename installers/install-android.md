# Claisum for Android

Install Claisum on Android using [Termux](https://termux.dev) — a free terminal emulator app.

> **Note:** Discord's mobile app uses a different architecture than the desktop app.
> Theme and plugin injection works through Termux's CLI — the floating panel (F8) is a desktop-only feature.

## Prerequisites

- Android 7.0 or higher
- [Termux](https://f-droid.org/packages/com.termux/) installed from F-Droid (recommended) or Play Store
- Internet connection

---

## Installation

### Step 1 — Install Termux

Download from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended — Play Store version is outdated).

### Step 2 — Install Python and Claisum

Open Termux and run:

```bash
pkg update && pkg upgrade -y
pkg install python -y
pip install https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip
```

### Step 3 — Verify

```bash
claisum --help
```

---

## Usage on Android

Since Discord mobile uses a sandboxed environment, direct injection is limited.
Use the CLI to manage themes and plugins that get applied on next Discord startup:

```bash
# List available themes
claisum discord themes list

# Apply a theme
claisum discord themes apply dracula

# List available plugins
claisum discord plugins available

# Install a plugin
claisum discord plugins install compact-mode
```

**Available themes:** `midnight`, `dracula`, `catppuccin`, `nord`, `rose-pine`, `gruvbox`, `solarized`

**Available plugins:** `compact-mode`, `square-corners`, `big-emoji`, `hide-game-activity`, `hide-avatars`

---

## Keyboard Shortcuts

| Platform | Open/Close Panel |
|----------|-----------------|
| Windows  | `F8`            |
| Linux    | `F8`            |
| macOS    | `F8`            |
| Android  | Tap the ⚡ button (bottom-left corner in Discord) |

---

## Uninstall

```bash
pip uninstall claisum -y
```

---

## Support

- Issues: https://github.com/claisum/Claisum.py/issues
- Source: https://github.com/claisum/Claisum.py
