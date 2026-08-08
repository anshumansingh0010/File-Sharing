# File Sharing App

A fast, secure, and modern local network file sharing desktop application built with **Python 3**, **GTK 4**, and **Libadwaita**.

![GTK 4](https://img.shields.io/badge/GUI-GTK%204-purple)
![Libadwaita](https://img.shields.io/badge/Style-Libadwaita-blue)
![Python 3](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **Automatic Device Discovery**: Discovers active receivers on your local Wi-Fi / LAN automatically using UDP broadcasts.
- **Secure OTP Authentication**: Time-limited 6-digit OTP verification ensures unauthorized network devices cannot send or receive files.
- **File & Folder Transfers**: Send individual files or complete directory structures recursively.
- **Modern Libadwaita UI**: Sleek GTK 4 user interface with automatic light/dark mode support and width clamping.
- **Path Traversal Security**: Built-in path sanitization protects receivers against directory traversal attacks (`../`).
- **Line-Framed TCP Protocol**: Reliable binary streaming over TCP prevents packet coalescing and data corruption.
- **Self-Device Filtering**: Automatically filters out local interface IP addresses so you never discover your own machine.

---

## Prerequisites & System Requirements

### System Packages

The application requires **Python 3.8+**, **GTK 4**, **Libadwaita**, and **PyGObject** system bindings.

#### Ubuntu / Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

#### Fedora:
```bash
sudo dnf install -y python3 python3-pip python3-gobject gtk4 libadwaita
```

#### Arch Linux:
```bash
sudo pacman -S --needed python python-pip python-gobject gtk4 libadwaita
```

### Python Dependencies

Install the required Python modules:
```bash
pip install -r requirements.txt
```
*(Dependencies: `psutil`, `PyGObject`)*

---

## Quick Start

To launch the application directly:

```bash
python3 main.py
```

---

## Installation & Desktop Integration

### 1. Install Desktop Launcher

To add the application to your system application menu (GNOME / KDE Application Launcher):

```bash
./install_desktop.sh
```

### 2. Build Standalone Desktop Executable

To bundle the application into a standalone binary executable using `PyInstaller`:

```bash
./build.sh
```
The compiled executable will be generated at `dist/FileSharing/FileSharing`.

### 3. Install as Python Package

To install globally as a command-line application (`file-sharing`):

```bash
pip install .
```

---

## Uninstallation

To cleanly remove the desktop launcher, build artifacts, and package installations:

```bash
./uninstall.sh
```

---

## Running Unit Tests

Run the comprehensive test suite to verify backend networking, OTP verification, path sanitization, and discovery filtering:

```bash
python3 tests/test_backend.py
```

---

## Project Structure

```
File-Sharing/
├── backend/
│   ├── receiver/
│   │   ├── receiver.py    # TCP server & SessionManager for receiving files
│   │   └── res.py         # UDP discovery responder thread
│   └── sender/
│       ├── req.py         # UDP discovery broadcast search thread
│       └── sender.py      # TCP client & OTP Authenticate implementation
├── frontend/
│   ├── main.py            # MainWindow (Adw.ApplicationWindow) & stack manager
│   ├── receive.py         # ReceivePage UI component
│   ├── send.py            # SenderPage UI component
│   └── style.css          # Libadwaita custom styling
├── tests/
│   └── test_backend.py    # Automated test suite
├── main.py                # Main application entry point
├── build.sh               # PyInstaller executable build script
├── install_desktop.sh     # Desktop launcher installer
├── uninstall.sh           # Clean uninstallation script
├── setup.py               # Python setuptools build configuration
└── README.md              # Project documentation
```

---

## License

This project is open-source and available under the [MIT License](LICENSE).
