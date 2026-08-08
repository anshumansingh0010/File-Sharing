#!/bin/bash
set -e

echo "=== Building File Sharing GTK App ==="

# Install PyInstaller if not present
if ! command -v pyinstaller &> /dev/null && ! python3 -m PyInstaller --version &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install --user pyinstaller || python3 -m pip install pyinstaller
fi

# Run PyInstaller build
python3 -m PyInstaller \
    --noconfirm \
    --onedir \
    --windowed \
    --name "FileSharing" \
    --add-data "frontend/style.css:frontend" \
    --hidden-import "gi" \
    --hidden-import "gi.repository.Gtk" \
    --hidden-import "gi.repository.Adw" \
    --hidden-import "gi.repository.Gio" \
    --hidden-import "gi.repository.Gdk" \
    --hidden-import "gi.repository.GLib" \
    main.py

echo "=== Build Complete! Executable created in dist/FileSharing/FileSharing ==="
