# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for QR Code 3D Generator
Builds standalone executables for macOS, Windows, and Linux
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect PyQt6 data files
pyqt6_datas = collect_data_files('PyQt6')

# Collect all necessary modules
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    'PIL',
    'PIL.Image',
    'PIL.ImageQt',
    'qrcode',
    'qrcode.image.pil',
    'qrly',
    'qrly.app',
    'qrly.generator',
    'qrly.gui',
    'qrly.gui.viewer_widget',
]

a = Analysis(
    ['src/qrly/app.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/qrly/__init__.py', 'qrly'),
        ('src/qrly/generator.py', 'qrly'),
        ('src/qrly/gui/', 'qrly/gui'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ] + pyqt6_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='QR3DGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file if available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QR3DGenerator',
)

# macOS: Create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='QR3DGenerator.app',
        icon=None,  # TODO: Add .icns file if available
        bundle_identifier='com.qrgen.qrlygenerator',
        info_plist={
            'CFBundleName': 'QR Code 3D Generator',
            'CFBundleDisplayName': 'QR Code 3D Generator',
            'CFBundleVersion': '0.1.0',
            'CFBundleShortVersionString': '0.1.0',
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
