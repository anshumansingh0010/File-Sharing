#!/bin/bash
set -e

echo "=== Uninstalling File Sharing GTK App ==="

DESKTOP_FILE="$HOME/.local/share/applications/com.anshuman.FileSharing.desktop"

# 1. Remove desktop launcher
if [ -f "$DESKTOP_FILE" ]; then
    rm -f "$DESKTOP_FILE"
    echo "Removed desktop launcher: $DESKTOP_FILE"
fi

# 2. Update desktop database if command available
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

# 3. Uninstall pip package if installed
if pip show file-sharing &> /dev/null; then
    pip uninstall -y file-sharing
    echo "Uninstalled pip package 'file-sharing'"
fi

# 4. Remove build/dist directories if present
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rm -rf "$APP_DIR/build" "$APP_DIR/dist" "$APP_DIR/*.egg-info"

echo "=== Uninstall Complete ==="
