# Claisum for Android

Install Claisum on Android using [Termux](https://termux.dev) — a free terminal app.

## Steps

1. Install **Termux** from [F-Droid](https://f-droid.org/packages/com.termux/) or the [Play Store](https://play.google.com/store/apps/details?id=com.termux)
2. Open Termux and run:

```bash
pkg update && pkg install python
pip install https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip
```

3. Verify the installation:

```bash
claisum --help
```

## Requirements

- Android 7.0 or higher
- Termux installed
- Internet connection

## Notes

- Discord on Android stores data in `/data/data/com.discord/` — root access may be required for theme/plugin features.
- The `claisum discord` commands work best on desktop (Windows/Linux).

## Support

https://github.com/claisum/Claisum.py/issues
