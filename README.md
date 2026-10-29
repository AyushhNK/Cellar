# ◆ Cellar

A small, local, encrypted password vault for Linux and Windows. No cloud, no accounts, no telemetry. Your passwords live in one encrypted file on your machine.

## Features

- **Strong encryption:** Argon2id (256 MiB, 3 passes) derives the key from your master password; entries are sealed with AES-256-GCM.
- **Tamper-evident:** the KDF header is bound as authenticated data, so editing the file (e.g. weakening KDF parameters) makes it fail to open.
- **Crash-safe saves:** write to a temp file, `fsync`, then atomic rename.
- **Auto-lock** after 5 minutes idle.
- **Clipboard hygiene:** copied secrets clear after 20 s and are hinted to clipboard managers (KDE Klipper, Windows `Win+V`) as not-for-history.
- **Password generator:** 24 characters, guaranteed upper, lower, digit and symbol.
- Search, add, edit and delete entries; change the master password (re-keys with a fresh salt).

## Project layout

```
cellar/
├── src/cellar/
│   ├── __init__.py
│   ├── __main__.py       # python -m cellar
│   ├── vault.py          # crypto + file format (no Qt)
│   ├── ui.py             # windows and dialogs
│   └── theme.py          # Qt stylesheet
├── tests/
│   └── test_vault.py
├── assets/
│   └── cellar.svg        # app icon
├── packaging/
│   ├── cellar.spec       # PyInstaller build
│   └── cellar.desktop    # Linux launcher
├── scripts/
│   └── install-linux.sh  # installs the built binary for the current user
├── pyproject.toml
└── README.md
```

## Run from source

Requires Python 3.10+.

```bash
git clone https://github.com/<your-username>/cellar.git
cd cellar
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[build]"
cellar                           # or: python -m cellar
```

## Test

```bash
python tests/test_vault.py       # or: pytest
```

## Build a standalone executable

```bash
pyinstaller packaging/cellar.spec
```

The single-file binary appears at `dist/Cellar` (`dist\Cellar.exe` on Windows).

### Install on Linux (app menu / Super key)

```bash
./scripts/install-linux.sh
```

This copies the binary to `~/.local/bin/cellar` and installs the icon and a `.desktop` launcher, so Cellar shows up when you press Super and search for it.

## Where your data lives

| OS      | Path                                  |
|---------|---------------------------------------|
| Linux   | `~/.local/share/Cellar/vault.json`    |
| Windows | `%APPDATA%\Cellar\vault.json`         |

The file is created with owner-only permissions (`0600`). Back it up by copying it somewhere safe. To restore, put it back at the same path. **There is no password recovery:** if you forget your master password, the vault cannot be opened.

## Vault format

```json
{
  "header": { "v": 1, "salt": "<base64>", "kdf": { "memory_cost": 262144, "iterations": 3, "lanes": 4 } },
  "nonce": "<base64, 12 bytes>",
  "ct": "<base64 AES-256-GCM ciphertext of the entries JSON>"
}
```

The whole `header` (key-sorted JSON) is used as AES-GCM associated data.

## Threat model, briefly

Cellar protects your passwords **at rest**, for example a stolen laptop or a copied file. It does not protect against malware running as your user while the vault is unlocked (keyloggers, memory scraping). Python strings cannot be reliably wiped from memory.
