#!/bin/bash
# Wrapper script for QR Code 3D Model Generator
# Uses the virtual environment automatically

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
VENV_PYTHON="$PROJECT_ROOT/venv-gui/bin/python"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3.13 -m venv venv-gui && ./venv-gui/bin/pip install -e ."
    exit 1
fi

# Run the generator with all passed arguments
"$VENV_PYTHON" -m qr3d "$@"
