#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="$HOME/.local/share/applications/com.anshuman.FileSharing.desktop"

mkdir -p "$HOME/.local/share/applications"

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=File Sharing
Comment=Local Network File Transfer Application
Exec=python3 $APP_DIR/main.py
Icon=folder-download-symbolic
Terminal=false
Type=Application
Categories=Network;FileTransfer;GTK;
StartupNotify=true
EOF

chmod +x "$DESKTOP_FILE"
echo "Installed desktop launcher to $DESKTOP_FILE"
