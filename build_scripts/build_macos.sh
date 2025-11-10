#!/bin/bash
# Build script for macOS
# Creates a .app bundle and .dmg installer

set -e  # Exit on error

echo "========================================="
echo "QR Code 3D Generator - macOS Build Script"
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
if [ ! -d "dist/QR3DGenerator.app" ]; then
    echo "ERROR: Build failed! .app bundle not found."
    exit 1
fi

echo "Build successful!"
echo "App bundle created at: dist/QR3DGenerator.app"

# Create DMG (requires create-dmg tool)
# Install with: brew install create-dmg
if command -v create-dmg &> /dev/null; then
    echo "Creating DMG installer..."

    # Create DMG folder structure
    mkdir -p dist/dmg
    cp -r dist/QR3DGenerator.app dist/dmg/

    # Create symbolic link to Applications folder
    ln -s /Applications dist/dmg/Applications

    # Create DMG
    DMG_NAME="QR3DGenerator-${VERSION}-macOS.dmg"
    create-dmg \
        --volname "QR Code 3D Generator" \
        --volicon "dist/QR3DGenerator.app/Contents/Resources/icon-windowed.icns" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "QR3DGenerator.app" 200 190 \
        --hide-extension "QR3DGenerator.app" \
        --app-drop-link 600 185 \
        "dist/${DMG_NAME}" \
        "dist/dmg/" || true  # create-dmg returns error even on success

    if [ -f "dist/${DMG_NAME}" ]; then
        echo "DMG created: dist/${DMG_NAME}"
    else
        echo "WARNING: DMG creation failed (create-dmg may not be installed)"
        echo "Install with: brew install create-dmg"
    fi

    # Clean up
    rm -rf dist/dmg
else
    echo "NOTE: create-dmg not found. Skipping DMG creation."
    echo "To create DMG installers, install with: brew install create-dmg"
fi

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo "Output:"
echo "  - App bundle: dist/QR3DGenerator.app"
if [ -f "dist/QR3DGenerator-${VERSION}-macOS.dmg" ]; then
    echo "  - DMG installer: dist/QR3DGenerator-${VERSION}-macOS.dmg"
fi
echo ""
echo "To test the app: open dist/QR3DGenerator.app"
