# Claisum

**Customize your Discord the way you want it.**

Claisum is an open-source CLI tool that lets you manage Discord themes and plugins with a single command. Inspired by Spicetify, built for everyone.

## Installation

### Windows

**Option 1 — GUI Installer (recommended, no dependencies required):**

1. Go to [GitHub Releases](https://github.com/claisum/Claisum.py/releases/latest)
2. Download `Claisum-Setup.exe`
3. Double-click and follow the steps

No Python, Git or Node.js required.

**Option 2 — pip:**
```bash
pip install https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip
```

### Linux

```bash
pip install https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip
```

Or clone and install manually:
```bash
git clone https://github.com/claisum/Claisum.py
cd Claisum.py
pip install .
```

### Android

Use [Termux](https://termux.dev) and run:
```bash
pip install https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip
```

Requires **Python 3.12 or higher**.

## Quick Start

```bash
# List available Discord themes
claisum discord themes list

# Apply a theme
claisum discord themes apply midnight

# Install a plugin
claisum discord plugins install compact-mode

# List installed plugins
claisum discord plugins list

# Remove a plugin
claisum discord plugins remove compact-mode

# Check current status
claisum discord status

# Reset Discord to defaults
claisum discord reset
```

## Supported Apps

| App      | Themes | Plugins | Status  |
|----------|--------|---------|---------|
| Discord  | ✓      | ✓       | Stable  |
| Telegram | Soon   | Soon    | Planned |
| Spotify  | Soon   | Soon    | Planned |

## Built-in Discord Themes

| ID           | Name             | Description                           |
|--------------|------------------|---------------------------------------|
| `midnight`   | Midnight         | Deep dark theme with blue accents     |
| `dracula`    | Dracula          | The classic Dracula color scheme      |
| `catppuccin` | Catppuccin Mocha | Soothing pastel theme (Mocha variant) |

## Requirements

- Python 3.12+
- Discord desktop installed (Windows / Linux)

## Contributing

Pull requests are welcome! See the [GitHub repository](https://github.com/claisum/Claisum.py).

## Full Website

The Full Website i here -> [Claisum Website](https://claisum-configurator--claisumpy.replit.app/).

Thanks to everyone ♡

## License

MIT
