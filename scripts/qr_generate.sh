#!/bin/bash
# Wrapper script for QR Code 3D Model Generator
# Uses the virtual environment automatically

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Run the generator with all passed arguments
"$VENV_PYTHON" "$SCRIPT_DIR/generate_qr_model.py" "$@"
