# Installation Guide

## macOS Installation

### Download and Install

1. Download `Qrly-0.3.0-macOS.dmg` from the [latest release](https://github.com/pepperonas/qrly/releases)
2. Open the DMG file
3. Drag `Qrly.app` to your Applications folder

### Install OpenSCAD (Required)

Qrly requires OpenSCAD 2021 or newer to generate STL files:

```bash
brew install openscad
```

Or download from: https://openscad.org/downloads.html

### macOS Security Fix

**Important:** macOS blocks unsigned apps with a "damaged" error. Fix with:

```bash
xattr -cr /Applications/Qrly.app
```

This removes the quarantine attribute. Then launch Qrly normally.

**Alternative:** Right-click Qrly.app → Open → Click "Open" in the dialog

### First Launch

1. Open Qrly from Applications
2. If prompted about OpenSCAD, ensure it's installed via Homebrew or from openscad.org
3. Enter a URL or select an image file to generate your first QR code model

---

## Windows Installation

### Download and Install

1. Download `Qrly-0.3.0-Windows-Setup.exe` from the [latest release](https://github.com/pepperonas/qrly/releases)
2. Run the installer
3. Follow the installation wizard
4. Launch Qrly from the Start Menu or Desktop shortcut

**Note:** OpenSCAD 2025.01.24 is bundled with the Windows installer - no separate installation needed!

### First Launch

1. Open Qrly from Start Menu
2. Enter a URL or select an image file
3. Click "Generate STL" - models render in ~1 second!

---

## Linux Installation

### Download

Download `Qrly-0.3.0-Linux.AppImage` from the [latest release](https://github.com/pepperonas/qrly/releases)

### Install OpenSCAD (Required)

Qrly requires OpenSCAD 2021 or newer:

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install openscad
```

**Fedora:**
```bash
sudo dnf install openscad
```

**Arch:**
```bash
sudo pacman -S openscad
```

### Make AppImage Executable

```bash
chmod +x Qrly-0.3.0-Linux.AppImage
```

### Run

```bash
./Qrly-0.3.0-Linux.AppImage
```

**Optional:** Move to `/usr/local/bin` for easy access:

```bash
sudo mv Qrly-0.3.0-Linux.AppImage /usr/local/bin/qrly
qrly  # Run from anywhere
```

### First Launch

1. Run the AppImage
2. If prompted about OpenSCAD, install it via your package manager
3. Enter a URL or select an image file to generate your first model

---

## Troubleshooting

### macOS: "Qrly.app is damaged"

This is a security feature for unsigned apps. Fix with:

```bash
xattr -cr /Applications/Qrly.app
```

### macOS: "OpenSCAD not found"

Install via Homebrew:

```bash
brew install openscad
```

Or download from https://openscad.org/downloads.html

### Windows: "OpenSCAD not found"

Reinstall Qrly - OpenSCAD is bundled with the installer. If still not working:
1. Check `C:\Program Files\Qrly\openscad.exe` exists
2. Reinstall Qrly

### Linux: AppImage won't run

1. Ensure execute permission: `chmod +x Qrly-*.AppImage`
2. Install FUSE: `sudo apt install fuse libfuse2`
3. Try running with `--appimage-extract-and-run` flag

### All Platforms: Generation fails

1. **Check OpenSCAD installation:**
   - macOS: `which openscad` or check `/Applications/OpenSCAD.app`
   - Windows: Check `C:\Program Files\Qrly\openscad.exe`
   - Linux: `which openscad`

2. **Check OpenSCAD version** (2021+ required):
   ```bash
   openscad --version
   ```

3. **Test OpenSCAD manually:**
   - Generate a model in Qrly (creates .scad file)
   - Open the .scad file in OpenSCAD
   - If it renders, the issue is with Qrly's OpenSCAD detection

### Need Help?

Open an issue on GitHub: https://github.com/pepperonas/qrly/issues

---

## Uninstallation

### macOS

Drag `Qrly.app` from Applications to Trash

### Windows

Use "Add or Remove Programs" in Windows Settings, or run the uninstaller from the Start Menu

### Linux

Simply delete the AppImage file

---

## System Requirements

- **macOS:** 10.13+ (High Sierra or later)
- **Windows:** Windows 10+ (64-bit)
- **Linux:** Most modern distributions (x86_64)
- **OpenSCAD:** 2021 or newer (bundled with Windows, separate install for macOS/Linux)
- **Disk Space:** ~100 MB for application + generated models
