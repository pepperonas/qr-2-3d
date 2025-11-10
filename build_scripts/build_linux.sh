#!/bin/bash
# Build script for Linux
# Creates an AppImage portable executable

set -e  # Exit on error

echo "========================================="
echo "QR Code 3D Generator - Linux Build Script"
echo "========================================="

# Get version from __version__.py
VERSION=$(python3 -c "from __version__ import __version__; print(__version__)")
echo "Building version: $VERSION"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Run PyInstaller
echo "Running PyInstaller..."
pyinstaller qr3d.spec --clean --noconfirm

# Check if build was successful
if [ ! -f "dist/QR3DGenerator/QR3DGenerator" ]; then
    echo "ERROR: Build failed! Executable not found."
    exit 1
fi

echo "Build successful!"
echo "Executable created at: dist/QR3DGenerator/QR3DGenerator"

# Create tarball
echo "Creating tarball..."
cd dist
tar -czf "QR3DGenerator-${VERSION}-Linux.tar.gz" QR3DGenerator/
cd ..
echo "Tarball created: dist/QR3DGenerator-${VERSION}-Linux.tar.gz"

# AppImage creation (requires appimagetool)
# Download from: https://github.com/AppImage/AppImageKit/releases
if command -v appimagetool &> /dev/null; then
    echo "Creating AppImage..."

    # Create AppDir structure
    APPDIR="dist/QR3DGenerator.AppDir"
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

    # Copy executable
    cp -r dist/QR3DGenerator/* "$APPDIR/usr/bin/"

    # Create desktop entry
    cat > "$APPDIR/usr/share/applications/qr3dgenerator.desktop" << EOF
[Desktop Entry]
Type=Application
Name=QR Code 3D Generator
Comment=Generate 3D-printable QR code models
Exec=QR3DGenerator
Icon=qr3dgenerator
Categories=Graphics;3DGraphics;Utility;
Terminal=false
EOF

    # Create AppRun script
    cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/:${LD_LIBRARY_PATH}"
cd "${HERE}/usr/bin"
exec ./QR3DGenerator "$@"
EOF
    chmod +x "$APPDIR/AppRun"

    # Symlink desktop file and icon
    ln -sf usr/share/applications/qr3dgenerator.desktop "$APPDIR/"
    # Note: Icon would need to be created/provided

    # Create AppImage
    ARCH=$(uname -m)
    appimagetool "$APPDIR" "dist/QR3DGenerator-${VERSION}-${ARCH}.AppImage"

    if [ -f "dist/QR3DGenerator-${VERSION}-${ARCH}.AppImage" ]; then
        echo "AppImage created: dist/QR3DGenerator-${VERSION}-${ARCH}.AppImage"
        chmod +x "dist/QR3DGenerator-${VERSION}-${ARCH}.AppImage"
    fi

    # Clean up
    rm -rf "$APPDIR"
else
    echo "NOTE: appimagetool not found. Skipping AppImage creation."
    echo "To create AppImages, download from:"
    echo "https://github.com/AppImage/AppImageKit/releases"
fi

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo "Output:"
echo "  - Executable: dist/QR3DGenerator/QR3DGenerator"
echo "  - Tarball: dist/QR3DGenerator-${VERSION}-Linux.tar.gz"
if [ -f "dist/QR3DGenerator-${VERSION}-$(uname -m).AppImage" ]; then
    echo "  - AppImage: dist/QR3DGenerator-${VERSION}-$(uname -m).AppImage"
fi
echo ""
echo "To test the app: ./dist/QR3DGenerator/QR3DGenerator"
