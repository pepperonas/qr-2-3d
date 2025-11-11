"""CLI entry point for qr3d package

This allows running the generator as: python -m qr3d
"""
import sys
from .generator import main

if __name__ == '__main__':
    sys.exit(main())
