#!/usr/bin/env python3
"""
QR Code 3D Generator - Simplified GUI without 3D viewer
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QProgressBar, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from generate_qr_model import QRModelGenerator


class GeneratorThread(QThread):
    """Background thread for STL generation"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, str)  # success, stl_path, message

    def __init__(self, input_path, output_name, mode, params, text_content='', text_rotation=0):
        super().__init__()
        self.input_path = input_path
        self.output_name = output_name
        self.mode = mode
        self.params = params
        self.text_content = text_content
        self.text_rotation = text_rotation

    def run(self):
        try:
            # Check if input is a URL
            actual_input = self.input_path
            temp_qr_file = None

            if QRModelGenerator.is_url(self.input_path):
                # Generate QR code from URL
                self.progress.emit(f"Generating QR code from URL...")

                # Create QR code image in generated folder
                from pathlib import Path
                import os

                output_dir = Path("generated")
                os.makedirs(output_dir, exist_ok=True)

                qr_filename = f"{self.output_name}.png"
                qr_path = output_dir / qr_filename

                QRModelGenerator.generate_qr_image(self.input_path, qr_path)
                actual_input = str(qr_path)
                self.progress.emit(f"QR code created: {qr_filename}")

            self.progress.emit("Generating 3D model...")

            generator = QRModelGenerator(
                actual_input,
                self.mode,
                "generated"
            )

            # Apply custom parameters
            generator.card_height = self.params['height']
            generator.qr_margin = self.params['margin']
            generator.qr_relief = self.params['relief']
            generator.corner_radius = self.params['corner_radius']
            generator.text_content = self.text_content
            generator.text_rotation = self.text_rotation

            self.progress.emit("Creating 3D model...")
            scad_path, stl_path = generator.generate()

            self.progress.emit("Model generated successfully!")
            self.finished.emit(True, str(stl_path), f"Generated: {Path(stl_path).name}")

        except Exception as e:
            self.finished.emit(False, "", f"Error: {str(e)}")


class SimpleMainWindow(QMainWindow):
    """Simplified main window without 3D viewer"""

    def __init__(self):
        super().__init__()
        self.generator_thread = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("QR Code 3D Generator (Simple Mode)")
        self.setMinimumSize(600, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("QR Code 3D Model Generator")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Input section
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout()

        # URL/File input
        url_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter URL or select image file...")
        url_layout.addWidget(self.input_field)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        url_layout.addWidget(browse_btn)
        input_layout.addLayout(url_layout)

        # Output name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Output name:"))
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Auto-generated from input")
        name_layout.addWidget(self.name_field)
        input_layout.addLayout(name_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Mode selection
        mode_group = QGroupBox("Model Type")
        mode_layout = QVBoxLayout()

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Square (55x55mm)",
            "Pendant (with hole)",
            "Rectangle + Text (54x64mm)",
            "Pendant + Text (55x65mm)"
        ])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        # Text input (only visible for text modes)
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text:"))
        self.text_field = QLineEdit()
        self.text_field.setPlaceholderText("Enter text (max 12 chars)")
        self.text_field.setMaxLength(12)
        text_layout.addWidget(self.text_field)
        mode_layout.addLayout(text_layout)

        # Text rotation checkbox (only visible for Rectangle+Text mode)
        self.text_rotation_checkbox = QCheckBox("Rotate text 180° (upside down)")
        mode_layout.addWidget(self.text_rotation_checkbox)

        # Store text widgets for show/hide
        self.text_label = text_layout.itemAt(0).widget()

        # Initially hide text field and rotation checkbox (square mode is default)
        self.text_label.setVisible(False)
        self.text_field.setVisible(False)
        self.text_rotation_checkbox.setVisible(False)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Parameters section
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout()

        # Height
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.5, 5.0)
        self.height_spin.setValue(1.25)
        self.height_spin.setSingleStep(0.25)
        self.height_spin.setSuffix(" mm")
        params_layout.addRow("Card Height:", self.height_spin)

        # Margin
        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setRange(0, 10)
        self.margin_spin.setValue(2.0)
        self.margin_spin.setSingleStep(0.25)
        self.margin_spin.setSuffix(" mm")
        params_layout.addRow("QR Margin:", self.margin_spin)

        # Relief
        self.relief_spin = QDoubleSpinBox()
        self.relief_spin.setRange(0.1, 2.0)
        self.relief_spin.setValue(1.0)
        self.relief_spin.setSingleStep(0.1)
        self.relief_spin.setSuffix(" mm")
        params_layout.addRow("QR Relief:", self.relief_spin)

        # Corner radius
        self.corner_spin = QDoubleSpinBox()
        self.corner_spin.setRange(0, 5)
        self.corner_spin.setValue(2)
        self.corner_spin.setSingleStep(0.5)
        self.corner_spin.setSuffix(" mm")
        params_layout.addRow("Corner Radius:", self.corner_spin)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Generate button
        self.generate_btn = QPushButton("Generate 3D Model")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_model)
        layout.addWidget(self.generate_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 10px; color: #666; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Info section
        info_label = QLabel(
            "Note: This is simplified mode without 3D preview.\n\n"
            "Tips:\n"
            "• Enter a URL to generate QR code automatically\n"
            "• Or select a PNG/JPG image file\n"
            "• Square mode: 55x55mm\n"
            "• Pendant mode: 55x61mm with chain hole\n"
            "• Rectangle+Text: 54x64mm with text label\n"
            "• Pendant+Text: ~55x65mm with hole and text\n"
            "• Generated files will be in 'generated' folder"
        )
        info_label.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            font-size: 11px;
            color: #555;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def browse_file(self):
        """Open file browser to select image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select QR Code Image",
            str(Path.home()),
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.input_field.setText(file_path)
            # Auto-fill name from filename
            if not self.name_field.text():
                name = Path(file_path).stem
                self.name_field.setText(name)

    def on_mode_changed(self, index):
        """Show/hide text field and rotation checkbox based on selected mode"""
        # Text modes are indices 2 and 3
        is_text_mode = index >= 2
        self.text_label.setVisible(is_text_mode)
        self.text_field.setVisible(is_text_mode)

        # Rotation checkbox only visible for Rectangle+Text (index 2)
        # Pendant+Text (index 3) always uses 180° rotation automatically
        is_rectangle_text = index == 2
        self.text_rotation_checkbox.setVisible(is_rectangle_text)

    def generate_model(self):
        """Start model generation in background thread"""
        input_text = self.input_field.text().strip()
        if not input_text:
            QMessageBox.warning(self, "Input Required", "Please enter a URL or select an image file.")
            return

        # Get output name
        output_name = self.name_field.text().strip()
        if not output_name:
            # Auto-generate from input
            if input_text.startswith(('http://', 'https://')):
                # Extract domain from URL
                from urllib.parse import urlparse
                parsed = urlparse(input_text)
                output_name = parsed.netloc.replace('www.', '').replace('.', '_')
            else:
                output_name = Path(input_text).stem

        # Get mode
        mode_index = self.mode_combo.currentIndex()
        mode_map = {
            0: 'square',
            1: 'pendant',
            2: 'rectangle-text',
            3: 'pendant-text'
        }
        mode = mode_map.get(mode_index, 'square')

        # Get text content (for text modes)
        text_content = self.text_field.text().strip() if mode_index >= 2 else ''

        # Validate text for text modes
        if mode_index >= 2 and not text_content:
            QMessageBox.warning(self, "Text Required", "Please enter text for the text-mode model.")
            return

        # Get text rotation
        # Pendant+Text: always 180° (automatic)
        # Rectangle+Text: user choice via checkbox
        if mode_index == 3:  # pendant-text
            text_rotation = 180
        elif mode_index == 2:  # rectangle-text
            text_rotation = 180 if self.text_rotation_checkbox.isChecked() else 0
        else:
            text_rotation = 0

        # Get parameters
        params = {
            'height': self.height_spin.value(),
            'margin': self.margin_spin.value(),
            'relief': self.relief_spin.value(),
            'corner_radius': self.corner_spin.value()
        }

        # Start generation in background
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Starting generation...")

        self.generator_thread = GeneratorThread(input_text, output_name, mode, params, text_content, text_rotation)
        self.generator_thread.progress.connect(self.on_progress)
        self.generator_thread.finished.connect(self.on_generation_finished)
        self.generator_thread.start()

    def on_progress(self, message: str):
        """Update progress message"""
        self.status_label.setText(message)

    def on_generation_finished(self, success: bool, stl_path: str, message: str):
        """Handle generation completion"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            stl_file = Path(stl_path)
            success_msg = f"✅ {message}\n📁 Files saved in: generated/"
            self.status_label.setText(success_msg)
            self.status_label.setStyleSheet("padding: 10px; color: #008800; font-size: 12px; font-weight: bold;")
        else:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet("padding: 10px; color: #cc0000; font-size: 12px; font-weight: bold;")
            QMessageBox.critical(self, "Generation Failed", message)


def main():
    print("Starting QR Code 3D Generator (Simple Mode)...")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("QR Code 3D Generator")
    app.setOrganizationName("QRGen")

    # Create and show main window
    window = SimpleMainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
