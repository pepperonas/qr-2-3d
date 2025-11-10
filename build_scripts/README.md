# Build Scripts

This directory contains platform-specific build scripts for creating distributable packages of the QR Code 3D Generator application.

## Prerequisites

All platforms require:
- Python 3.13+
- PyInstaller (installed via `pip install pyinstaller`)
- Virtual environment with all dependencies installed

## macOS

### Build Script
```bash
./build_scripts/build_macos.sh
```

### Output
- `.app` bundle: `dist/QR3DGenerator.app`
- `.dmg` installer (if create-dmg installed): `dist/QR3DGenerator-X.X.X-macOS.dmg`

### Optional Tools
- `create-dmg`: Install with `brew install create-dmg` to create DMG installers

### Testing
```bash
open dist/QR3DGenerator.app
```

## Windows

### Build Script
```cmd
build_scripts\build_windows.bat
```

### Output
- Executable folder: `dist\QR3DGenerator\`
- ZIP archive: `dist\QR3DGenerator-X.X.X-Windows.zip`

### Optional Tools
- **Inno Setup** or **NSIS** for creating professional installers
- Inno Setup: https://jrsoftware.org/isinfo.php
- NSIS: https://nsis.sourceforge.io/

### Testing
```cmd
dist\QR3DGenerator\QR3DGenerator.exe
```

## Linux

### Build Script
```bash
./build_scripts/build_linux.sh
```

### Output
- Executable folder: `dist/QR3DGenerator/`
- Tarball: `dist/QR3DGenerator-X.X.X-Linux.tar.gz`
- AppImage (if appimagetool installed): `dist/QR3DGenerator-X.X.X-x86_64.AppImage`

### Optional Tools
- `appimagetool`: Download from https://github.com/AppImage/AppImageKit/releases

### Testing
```bash
./dist/QR3DGenerator/QR3DGenerator
```

## Notes

### Version Number
All scripts automatically read the version number from `__version__.py`. Update that file to change the version in build outputs.

### Build Output
All builds output to the `dist/` directory, which is gitignored. The `build/` directory contains temporary PyInstaller files.

### Clean Builds
All scripts automatically clean previous builds before starting. To manually clean:
```bash
rm -rf build dist
```

### Dependencies
The `.spec` file is configured to bundle all required Python dependencies. OpenSCAD must be installed separately by end users.

### CI/CD Integration
These scripts are designed to be called by GitHub Actions workflows. See `.github/workflows/` for automated build configurations.

## Troubleshooting

### Missing Dependencies
If the build fails due to missing modules:
1. Ensure all dependencies are installed: `pip install -r requirements-gui.txt`
2. Update `hiddenimports` in `qr3d.spec` if needed

### macOS Code Signing
For distribution outside the App Store, you'll need:
- Apple Developer account
- Code signing certificate
- Notarization (for macOS 10.15+)

See: https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution

### Windows Defender Warnings
PyInstaller executables may trigger false positives. Solutions:
- Use official code signing certificate
- Submit to Microsoft for analysis
- Use established installer tools (Inno Setup/NSIS)

### Linux Compatibility
AppImages are portable and work on most distributions. For distribution-specific packages (deb, rpm), consider using native packaging tools or tools like `fpm` (Effing Package Manager).
