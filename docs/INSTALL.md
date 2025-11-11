# Installation Instructions

## Quick Start

### 1. Install Python Dependencies

Da macOS ein verwaltetes Python-Environment nutzt, gibt es mehrere Optionen:

#### Option A: Mit pipx (empfohlen für Tools)
```bash
brew install pipx
pipx install pillow
```

#### Option B: Mit virtuellem Environment
```bash
cd "/Users/martin/My Drive/3d print/___OpenSCAD/QRs"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Danach das Skript mit dem venv-Python ausführen:
```bash
./venv/bin/python generate_qr_model.py myqr.png
```

#### Option C: System-wide mit --user Flag
```bash
pip3 install --user Pillow
```

#### Option D: Mit --break-system-packages (nicht empfohlen)
```bash
pip3 install --break-system-packages Pillow
```

### 2. OpenSCAD installieren (optional)

```bash
brew install openscad
```

Oder Download von [openscad.org](https://openscad.org/downloads.html)

### 3. Testen

```bash
python3 generate_qr_model.py --help
```

## Verwendung

Siehe [README.md](README.md) für detaillierte Anweisungen.
