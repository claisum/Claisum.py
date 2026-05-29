[![Application](https://img.shields.io/badge/Application-Open-blue?style=for-the-badge)](https://forms.gle/fh86mjy2GWvkf6KG7) [![Bug Wiki](https://img.shields.io/badge/Bug_wiki-Open-blue?style=for-the-badge)](https://github.com/claisum/Claisum.py/wiki/Bug-Wiki)

# Claisum ⚡

**Discord customization tool—themes & plugins, built right into Discord.**

Claisum injects a floating **⚡ button** into Discord. Click it (or press **Ctrl+Shift+C**) to open the Claisum panel with Themes and Plugins tabs.

No BetterDiscord. No extra apps. Just one install.

---

## Installation

### Windows

1. Go to [Releases](https://github.com/claisum/Claisum.py/releases/latest)
2. Download **`Claisum_Setup.exe`**
3. Double-click → follow the 4-step wizard
4. Restart Discord → look for the **⚡** in the bottom-left corner.

> No Python, Git or Node.js required.

### Linux

1. Download **`Claisum_Linux_Setup`** from [Releases](https://github.com/claisum/Claisum.py/releases/latest)
2. Run in a terminal:

```bash
chmod +x Claisum_Linux_Setup
./Claisum_Linux_Setup
```

> If Discord is owned by root: `sudo ./Claisum_Linux_Setup`

**Remove:** `./Claisum_Linux_Setup --remove`
**Status:** `./Claisum_Linux_Setup --status`

### Python CLI (advanced)

```bash
pip install git+https://github.com/claisum/Claisum.py.git
claisum discord inject
claisum discord themes list
claisum discord plugins available
```

---

## The Claisum Panel

Open with the **⚡**FAB button (bottom-left in Discord) or **Ctrl+Shift+C**.

### Themes tab

| Theme | Description |
|-------|-------------|
| Midnight | Deep dark blue accents |
| Dracula | Classic Dracula palette |
| Catppuccin Mocha | Soothing pastel |
| Nord | Arctic bluish |
| Rosé Pine | Natural pine + gold |
| Gruvbox Dark | Retro groove |
| Solarized Dark | Classic Solarized |

Toggle any theme on/off with one click. Only one theme is active at a time. Preference is saved across Discord restarts.

### Plugins tab

| Plugin | Description |
|--------|-------------|
| Compact Mode | Tighter message layout |
| Square Corners | Removes all border-radius |
| Big Emoji | Solo emoji enlarged to 48 px |
| Hide Game Activity | Hides “playing a game” bar |
| Hide Avatars | Removes all user avatars |

Multiple plugins can be active at once. All saved in Discord's `localStorage`.

---

## Keyboard shortcut

**Ctrl+Shift+C—toggle the Claisum panel from anywhere in Discord.

---

## Auto-update

Claisum checks GitHub for a new release every time Discord starts (via XHR, non-blocking). If an update is available, a red **!** The badge appears on the ⚡ FAB. Run the installer again to update.

---

## Uninstall

**Windows:** Run `Claisum_Setup.exe` → choose **Uninstall**

**Linux:** `./Claisum_Linux_Setup --remove`

**Python CLI:** `claisum discord remove`

---

## CLI reference

```
claisum discord inject              Inject Claisum into Discord
claisum discord remove              Remove Claisum from Discord
Claim Discord status: Check injection status
claisum discord themes list         List all themes
claisum discord themes apply <id>   Apply a theme
claisum discord themes remove       Remove active theme
claisum discord plugins list        List installed plugins
claisum discord plugins available   List all available plugins
claisum discord plugins install <id>
claisum discord plugins remove <id>
```

---

## License

MIT — see [LICENSE](LICENSE)

Thanks to everyone ♡
