#!/usr/bin/env sh
# Install the built binary, icon and launcher for the current user.
set -eu
cd "$(dirname "$0")/.."
[ -f dist/Cellar ] || { echo "dist/Cellar not found; build first: pyinstaller packaging/cellar.spec" >&2; exit 1; }

install -Dm755 dist/Cellar "$HOME/.local/bin/cellar"
install -Dm644 assets/cellar.svg "$HOME/.local/share/icons/hicolor/scalable/apps/cellar.svg"
sed "s|^Exec=.*|Exec=$HOME/.local/bin/cellar|" packaging/cellar.desktop > "$HOME/.local/share/applications/cellar.desktop"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
echo "Installed. Press Super and search for Cellar."
