# Claisum

**Customize your Discord with Themes and Plugins — built right into Discord Settings.**

Claisum adds two new tabs to Discord's Settings panel:
- 🎨 **Themes** — change Discord's look with beautiful themes
- 🔌 **Plugins** — extend Discord with useful plugins

Browse the built-in library, **create your own**, and **publish them for the community!**
No commands to memorize. Everything is inside Discord Settings.

## Installation

### Windows

1. Go to [GitHub Releases](https://github.com/claisum/Claisum.py/releases/latest)
2. Download **`Claisum_Setup.exe`**
3. Double-click and follow the steps
4. Restart Discord → open Settings → find **Themes** and **Plugins** tabs

No Python, Git or Node.js required.

---

### Linux

1. Download **`Claisum_Linux_Setup`** from [GitHub Releases](https://github.com/claisum/Claisum.py/releases/latest)
2. Open a terminal and run:

```bash
chmod +x Claisum_Linux_Setup
./Claisum_Linux_Setup
```

Or if you need admin rights:
```bash
sudo ./Claisum_Linux_Setup
```

No Python installation required — the binary includes everything.

---

### Android

Android Discord is a native app and does not support direct injection.
See **[installer-src/ANDROID.md](installer-src/ANDROID.md)** for options including Aliucord integration.

---

## What you can do

### Themes tab (Discord Settings → Themes)
| Feature | Description |
|---------|-------------|
| Browse  | Choose from built-in and community themes |
| Apply   | One click to apply any theme |
| Create  | Write your own CSS theme with a built-in editor |
| Publish | Share your theme with the community on GitHub |

### Plugins tab (Discord Settings → Plugins)
| Feature | Description |
|---------|-------------|
| Browse  | Toggle built-in and community plugins on/off |
| Create  | Write your own JavaScript plugin with a built-in editor |
| Publish | Share your plugin with the community on GitHub |

## Built-in Themes

| Theme | Description |
|-------|-------------|
| Midnight | Deep dark theme with blue accents |
| Dracula | The classic Dracula color scheme |
| Catppuccin Mocha | Soothing pastel theme |
| Nord | Arctic, north-bluish elegant theme |
| Rosé Pine | Natural pine with soho vibes |

## Built-in Plugins

| Plugin | Description |
|--------|-------------|
| Compact Mode | Reduces message spacing |
| Hide Nitro Upsells | Removes Nitro ads and banners |
| Bigger Emojis | Makes emojis larger |
| Always Show Timestamps | Shows full timestamps on every message |
| Hide Activities Tab | Hides the activity tab from sidebar |

## Publishing Your Theme or Plugin

Inside Discord, go to Settings → Themes (or Plugins) → Create → fill in your code → click **Save & Publish**.
This will guide you to open a GitHub Issue where the Claisum team reviews and adds it to the marketplace.

## Uninstall

**Windows:** Add/Remove Programs → Claisum → Uninstall

**Linux:**
```bash
./Claisum_Linux_Setup --remove
```

## License

MIT — see [LICENSE](LICENSE)

Thanks to everyone ♡
