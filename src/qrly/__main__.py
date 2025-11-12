"""CLI entry point for qrly package

This allows running the generator as: python -m qrly
"""
import sys
from .generator import main

if __name__ == '__main__':
    sys.exit(main())
