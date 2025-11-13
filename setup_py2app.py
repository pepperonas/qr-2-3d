"""
py2app setup script for Qrly
"""
from setuptools import setup

APP = ['src/qrly/app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/icons/app_icon.icns',
    'plist': {
        'CFBundleName': 'Qrly',
        'CFBundleDisplayName': 'Qrly - QR Code 3D Generator',
        'CFBundleIdentifier': 'com.qrly.app',
        'CFBundleVersion': '0.3.1',
        'CFBundleShortVersionString': '0.3.1',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
    'packages': ['PyQt6', 'PIL', 'qrcode', 'qrly'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui'],
}

setup(
    app=APP,
    name='Qrly',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
