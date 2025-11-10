@echo off
REM Build script for Windows
REM Creates an executable and installer

echo =========================================
echo QR Code 3D Generator - Windows Build Script
echo =========================================

REM Get version from __version__.py
for /f "delims=" %%i in ('python -c "from __version__ import __version__; print(__version__)"') do set VERSION=%%i
echo Building version: %VERSION%

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller
echo Running PyInstaller...
pyinstaller qr3d.spec --clean --noconfirm

REM Check if build was successful
if not exist "dist\QR3DGenerator\QR3DGenerator.exe" (
    echo ERROR: Build failed! Executable not found.
    exit /b 1
)

echo Build successful!
echo Executable created at: dist\QR3DGenerator\QR3DGenerator.exe

REM Create ZIP archive
echo Creating ZIP archive...
powershell Compress-Archive -Path dist\QR3DGenerator -DestinationPath dist\QR3DGenerator-%VERSION%-Windows.zip -Force
echo ZIP created: dist\QR3DGenerator-%VERSION%-Windows.zip

REM Note about installer creation
echo.
echo NOTE: To create a professional installer, use Inno Setup or NSIS
echo - Inno Setup: https://jrsoftware.org/isinfo.php
echo - NSIS: https://nsis.sourceforge.io/

echo.
echo =========================================
echo Build completed successfully!
echo =========================================
echo Output:
echo   - Executable: dist\QR3DGenerator\QR3DGenerator.exe
echo   - ZIP archive: dist\QR3DGenerator-%VERSION%-Windows.zip
echo.
echo To test the app: dist\QR3DGenerator\QR3DGenerator.exe
