#!/usr/bin/env python3
"""
qrly - Simplified GUI without 3D viewer
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QGridLayout, QProgressBar, QFileDialog, QMessageBox, QCheckBox, QDialog, QSizePolicy, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from qrly.generator import QRModelGenerator
from qrly import __version__

# Default output directory in user's home folder
DEFAULT_OUTPUT_DIR = Path.home() / "qr-codes"


class GeneratorThread(QThread):
    """Background thread for STL generation"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, str)  # success, stl_path, message

    def __init__(self, input_path, output_name, mode, params, text_content='', text_rotation=0, text_content_top=''):
        super().__init__()
        self.input_path = input_path
        self.output_name = output_name
        self.mode = mode
        self.params = params
        self.text_content = text_content
        self.text_rotation = text_rotation
        self.text_content_top = text_content_top

    def run(self):
        try:
            # Check if input is a URL
            actual_input = self.input_path
            temp_qr_file = None

            if QRModelGenerator.is_url(self.input_path):
                # Generate QR code from URL - save to temp location
                self.progress.emit(f"Generating QR code from URL...")

                # Generate QR to temporary file (generate() will handle final placement)
                actual_input = QRModelGenerator.generate_qr_image(self.input_path)
                self.progress.emit(f"QR code created")

            self.progress.emit("Generating 3D model...")

            generator = QRModelGenerator(
                actual_input,
                self.mode,
                str(DEFAULT_OUTPUT_DIR),
                output_name=self.output_name
            )

            # Apply custom parameters
            generator.card_height = self.params['height']
            generator.qr_margin = self.params['margin']
            generator.qr_relief = self.params['relief']
            generator.corner_radius = self.params['corner_radius']
            generator.size_scale = self.params['size_scale']
            generator.text_content = self.text_content
            generator.text_content_top = self.text_content_top
            generator.text_rotation = self.text_rotation
            # Sync text relief with QR relief (always same height)
            generator.text_height = self.params['relief']

            self.progress.emit("Creating 3D model...")
            scad_path, stl_path, json_path = generator.generate(qr_input=self.input_path)

            self.progress.emit("Model generated successfully!")
            self.finished.emit(True, str(stl_path), f"Generated: {Path(stl_path).name}")

        except Exception as e:
            self.finished.emit(False, "", f"Error: {str(e)}")


class PreviewDialog(QDialog):
    """Dialog showing OpenSCAD-rendered preview of the model"""

    def __init__(self, input_path, mode, params, text_content='', text_content_top='', text_rotation=0, parent=None):
        super().__init__(parent)
        self.input_path = input_path
        self.mode = mode
        self.params = params
        self.text_content = text_content
        self.text_content_top = text_content_top
        self.text_rotation = text_rotation
        self.preview_image = None
        self.setup_ui()
        self.generate_preview()

    def setup_ui(self):
        """Setup preview dialog UI"""
        self.setWindowTitle("3D Model Preview")
        self.resize(800, 700)

        layout = QVBoxLayout(self)

        # Status label
        self.status_label = QLabel("Generating preview...")
        self.status_label.setStyleSheet("font-weight: bold; padding: 10px; color: #0066cc;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #ccc; background-color: #ffffff;")
        self.image_label.setMinimumSize(600, 500)
        layout.addWidget(self.image_label)

        # Set dialog background to white
        self.setStyleSheet("QDialog { background-color: #ffffff; }")

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        layout.addWidget(close_btn)

    def generate_preview(self):
        """Generate preview by creating temporary SCAD and rendering it"""
        import tempfile
        import subprocess

        try:
            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix='qrly_preview_'))

            # Check if input is URL and generate QR code if needed
            actual_input = self.input_path
            if self.input_path and QRModelGenerator.is_url(self.input_path):
                self.status_label.setText("Generating QR code from URL...")
                QApplication.processEvents()
                actual_input = QRModelGenerator.generate_qr_image(self.input_path)
            elif not self.input_path:
                # Create a dummy QR code for preview
                self.status_label.setText("Generating sample QR code...")
                QApplication.processEvents()
                actual_input = QRModelGenerator.generate_qr_image("https://example.com")

            # Create generator
            self.status_label.setText("Creating 3D model...")
            QApplication.processEvents()

            generator = QRModelGenerator(actual_input, self.mode, str(temp_dir), output_name='preview')

            # Apply parameters
            generator.card_height = self.params['height']
            generator.qr_margin = self.params['margin']
            generator.qr_relief = self.params['relief']
            generator.corner_radius = self.params['corner_radius']
            generator.size_scale = self.params['size_scale']
            generator.text_content = self.text_content
            generator.text_content_top = self.text_content_top
            generator.text_rotation = self.text_rotation
            generator.text_height = self.params['relief']

            # Load and process image
            matrix, width, height = generator.load_and_process_image()
            dimensions = generator.calculate_dimensions(height)

            # Generate SCAD file
            scad_content = generator.generate_openscad(matrix, dimensions)

            # Add colors for preview (white base, black QR/text)
            scad_content = scad_content.replace(
                '        // Base card with rounded corners (hull is MUCH faster than minkowski)\n        rounded_square(card_width, card_length, card_height, corner_radius);',
                '        // Base card with rounded corners (hull is MUCH faster than minkowski)\n        color("white")\n        rounded_square(card_width, card_length, card_height, corner_radius);'
            )
            scad_content = scad_content.replace(
                '        // QR Code pattern (raised)\n        translate([qr_offset_x, qr_offset_y, card_height])\n            qr_pattern();',
                '        // QR Code pattern (raised)\n        color("black")\n        translate([qr_offset_x, qr_offset_y, card_height])\n            qr_pattern();'
            )
            scad_content = scad_content.replace(
                '        // Top text label (if enabled, for rectangle-text-2x mode)\n        text_label_top();',
                '        // Top text label (if enabled, for rectangle-text-2x mode)\n        color("black")\n        text_label_top();'
            )
            scad_content = scad_content.replace(
                '        // Bottom text label (if enabled)\n        text_label();',
                '        // Bottom text label (if enabled)\n        color("black")\n        text_label();'
            )

            scad_file = temp_dir / 'preview.scad'
            with open(scad_file, 'w', encoding='utf-8') as f:
                f.write(scad_content)

            # Render preview image with OpenSCAD
            self.status_label.setText("Rendering preview (this may take a few seconds)...")
            QApplication.processEvents()

            preview_image = temp_dir / 'preview.png'

            # Find OpenSCAD binary
            from qrly.generator import find_openscad_binary
            openscad_bin = find_openscad_binary()

            # Camera position for nice 3D view
            # translate_x,y,z,rot_x,rot_y,rot_z,distance
            camera_pos = "0,0,0,55,0,205,200"  # x,y,z,rot_x,rot_y,rot_z,distance (205 = 25 + 180)

            # Render command (similar to export_stl but with PNG-specific parameters)
            cmd = [
                openscad_bin,
                '-o', str(preview_image),
                '--autocenter',
                '--viewall',
                '--camera=' + camera_pos,
                '--imgsize=800,800',
                '--projection=ortho',
                '--colorscheme=Starnight',
                str(scad_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and preview_image.exists():
                # Load and display image
                pixmap = QPixmap(str(preview_image))
                if not pixmap.isNull():
                    # Scale to fit
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.status_label.setText("Preview ready")
                    self.status_label.setStyleSheet("font-weight: bold; padding: 10px; color: #28a745;")
                else:
                    raise Exception("Failed to load rendered image")
            else:
                raise Exception(f"OpenSCAD rendering failed: {result.stderr}")

            # Cleanup temp files (keep them for a moment for debugging)
            # import shutil
            # shutil.rmtree(temp_dir)

        except Exception as e:
            self.status_label.setText(f"Preview generation failed: {str(e)}")
            self.status_label.setStyleSheet("font-weight: bold; padding: 10px; color: #cc0000;")
            self.image_label.setText("Could not generate preview")
            self.image_label.setStyleSheet("border: 2px solid #ccc; background-color: #f8f9fa; color: #666;")


class SimpleMainWindow(QMainWindow):
    """Simplified main window without 3D viewer"""

    def __init__(self):
        super().__init__()
        self.generator_thread = None
        self.setup_ui()

        # Enable drag and drop for JSON config files
        self.setAcceptDrops(True)

    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(f"QR Code 3D Generator v{__version__}")
        self.setMinimumSize(600, 900)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)  # Reduce spacing between sections

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
        input_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(input_group)

        # Google Review Options (Place ID)
        google_group = QGroupBox("🗺️  Google Review (Optional)")
        google_layout = QVBoxLayout()

        # Place ID input
        place_id_label = QLabel("Google Place ID:")
        google_layout.addWidget(place_id_label)

        self.place_id_input = QLineEdit()
        self.place_id_input.setPlaceholderText("ChIJ... (Leave empty for regular QR code)")
        google_layout.addWidget(self.place_id_input)

        # Help button
        help_btn = QPushButton("❓ How to get Place ID")
        help_btn.clicked.connect(self.show_place_id_help)
        help_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        google_layout.addWidget(help_btn)

        google_group.setLayout(google_layout)
        layout.addWidget(google_group)

        # Mode selection
        mode_group = QGroupBox("Model Type")
        mode_layout = QVBoxLayout()

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Square",
            "Pendant (with hole)",
            "Rectangle + Text",
            "Pendant + Text",
            "Rectangle + Text (2x)"
        ])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        # Size display label
        self.size_label = QLabel()
        self.size_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px 0px;")
        mode_layout.addWidget(self.size_label)

        # Text input for top text (only visible for rectangle-text-2x)
        text_top_layout = QHBoxLayout()
        text_top_layout.addWidget(QLabel("Text Top:"))
        self.text_field_top = QLineEdit()
        self.text_field_top.setPlaceholderText("Enter top text (max 20 chars)")
        self.text_field_top.setMaxLength(20)
        text_top_layout.addWidget(self.text_field_top)
        mode_layout.addLayout(text_top_layout)

        # Text input for bottom text (visible for all text modes)
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text Bottom:"))
        self.text_field = QLineEdit()
        self.text_field.setPlaceholderText("Enter text (max 20 chars)")
        self.text_field.setMaxLength(20)
        text_layout.addWidget(self.text_field)
        mode_layout.addLayout(text_layout)

        # Store text widgets for show/hide
        self.text_label_top = text_top_layout.itemAt(0).widget()
        self.text_label = text_layout.itemAt(0).widget()

        # Initially hide text fields (square mode is default)
        self.text_label_top.setVisible(False)
        self.text_field_top.setVisible(False)
        self.text_label.setVisible(False)
        self.text_field.setVisible(False)

        # Size presets
        size_preset_layout = QHBoxLayout()
        size_preset_layout.addWidget(QLabel("Size:"))

        # Small button
        small_btn = QPushButton("Small (0.5x)")
        small_btn.clicked.connect(lambda: self.set_size_scale(0.5))
        small_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        size_preset_layout.addWidget(small_btn)

        # Medium button (default)
        medium_btn = QPushButton("Medium (1x)")
        medium_btn.clicked.connect(lambda: self.set_size_scale(1.0))
        medium_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        size_preset_layout.addWidget(medium_btn)

        # Large button
        large_btn = QPushButton("Large (2x)")
        large_btn.clicked.connect(lambda: self.set_size_scale(2.0))
        large_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e64a19;
            }
        """)
        size_preset_layout.addWidget(large_btn)

        mode_layout.addLayout(size_preset_layout)

        # Store current size scale
        self.current_size_scale = 1.0

        mode_group.setLayout(mode_layout)
        mode_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(mode_group)

        # Parameters section - 2x2 Grid Layout
        params_group = QGroupBox("Parameters")
        params_layout = QGridLayout()

        # Row 1, Column 1: Card Height
        params_layout.addWidget(QLabel("Card Height:"), 0, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.5, 5.0)
        self.height_spin.setValue(0.5)  # Default: Dünn
        self.height_spin.setSingleStep(0.25)
        self.height_spin.setSuffix(" mm")
        params_layout.addWidget(self.height_spin, 0, 1)

        # Row 1, Column 2: QR Margin
        params_layout.addWidget(QLabel("QR Margin:"), 0, 2)
        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setRange(0, 10)
        self.margin_spin.setValue(2.0)
        self.margin_spin.setSingleStep(0.25)
        self.margin_spin.setSuffix(" mm")
        params_layout.addWidget(self.margin_spin, 0, 3)

        # Row 2, Column 1: Relief (QR and Text)
        self.relief_label = QLabel("QR Relief:")
        params_layout.addWidget(self.relief_label, 1, 0)
        self.relief_spin = QDoubleSpinBox()
        self.relief_spin.setRange(0.1, 2.0)
        self.relief_spin.setValue(0.5)  # Default: Dünn
        self.relief_spin.setSingleStep(0.1)
        self.relief_spin.setSuffix(" mm")
        params_layout.addWidget(self.relief_spin, 1, 1)

        # Row 2, Column 2: Corner Radius
        params_layout.addWidget(QLabel("Corner Radius:"), 1, 2)
        self.corner_spin = QDoubleSpinBox()
        self.corner_spin.setRange(0, 5)
        self.corner_spin.setValue(2)
        self.corner_spin.setSingleStep(0.5)
        self.corner_spin.setSuffix(" mm")
        params_layout.addWidget(self.corner_spin, 1, 3)

        params_group.setLayout(params_layout)
        params_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(params_group)

        # Thickness presets
        thickness_group = QGroupBox("Thickness Presets")
        thickness_layout = QHBoxLayout()

        # Thin button (default)
        thin_btn = QPushButton("Thin (0.5mm)")
        thin_btn.clicked.connect(lambda: self.set_thickness(0.5, 0.5))
        thin_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        thickness_layout.addWidget(thin_btn)

        # Medium button
        medium_btn = QPushButton("Medium (1.0mm)")
        medium_btn.clicked.connect(lambda: self.set_thickness(1.0, 1.0))
        medium_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        thickness_layout.addWidget(medium_btn)

        # Thick button
        thick_btn = QPushButton("Thick (1.5mm)")
        thick_btn.clicked.connect(lambda: self.set_thickness(1.5, 1.5))
        thick_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
        """)
        thickness_layout.addWidget(thick_btn)

        thickness_group.setLayout(thickness_layout)
        thickness_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(thickness_group)

        # Preview and Generate button row
        button_row = QHBoxLayout()

        # Preview button
        self.preview_btn = QPushButton("Preview 3D Model")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.preview_btn.clicked.connect(self.show_preview)
        button_row.addWidget(self.preview_btn)

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
        button_row.addWidget(self.generate_btn)

        # Help button
        help_btn = QPushButton("?")
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                min-width: 45px;
                max-width: 45px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        help_btn.clicked.connect(self.show_help_dialog)
        button_row.addWidget(help_btn)

        layout.addLayout(button_row)

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

        # Initialize size label
        self.update_size_label()

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
        """Show/hide text fields based on selected mode"""
        # Text modes: 2=rectangle-text, 3=pendant-text, 4=rectangle-text-2x
        is_text_mode = index >= 2
        is_text_2x_mode = index == 4  # rectangle-text-2x

        # Show bottom text field for all text modes
        self.text_label.setVisible(is_text_mode)
        self.text_field.setVisible(is_text_mode)

        # Show top text field only for rectangle-text-2x
        self.text_label_top.setVisible(is_text_2x_mode)
        self.text_field_top.setVisible(is_text_2x_mode)

        # Update relief label based on mode
        if is_text_mode:
            self.relief_label.setText("QR/Text Relief:")
        else:
            self.relief_label.setText("QR Relief:")

        # Update size label
        self.update_size_label()

    def set_thickness(self, card_height, qr_relief):
        """Set both card height and QR relief to preset values"""
        self.height_spin.setValue(card_height)
        self.relief_spin.setValue(qr_relief)

    def set_size_scale(self, scale):
        """Set the size scale factor (0.5 = small, 1.0 = medium, 2.0 = large)"""
        self.current_size_scale = scale
        self.update_size_label()

    def update_size_label(self):
        """Update the size label based on current mode and scale"""
        mode_index = self.mode_combo.currentIndex()
        scale = self.current_size_scale

        # Base dimensions (at scale 1.0)
        if mode_index == 0:  # Square
            width = 55 * scale
            length = 55 * scale
            size_text = f"Size: {width:.1f} x {length:.1f} mm"
        elif mode_index == 1:  # Pendant
            width = 55 * scale
            length = 61 * scale  # 55 + 6mm for hole area
            size_text = f"Size: {width:.1f} x {length:.1f} mm"
        elif mode_index == 2:  # Rectangle + Text
            width = 54 * scale
            length = 64 * scale
            size_text = f"Size: {width:.1f} x {length:.1f} mm"
        elif mode_index == 3:  # Pendant + Text
            width = 55 * scale
            length = 65 * scale  # Approximate
            size_text = f"Size: {width:.1f} x {length:.1f} mm"
        elif mode_index == 4:  # Rectangle + Text (2x)
            width = 54 * scale
            length = 74 * scale  # Approximate (with text top and bottom)
            size_text = f"Size: {width:.1f} x {length:.1f} mm"
        else:
            size_text = ""

        self.size_label.setText(size_text)

    def show_place_id_help(self):
        """Show help dialog for getting Place ID"""
        help_text = """<h3>How to get a Google Place ID:</h3>

<ol>
<li><b>Visit Place ID Finder:</b><br>
<a href="https://developers.google.com/maps/documentation/places/web-service/place-id">https://developers.google.com/maps/documentation/places/web-service/place-id</a></li>

<li><b>Scroll down</b> to the "Place ID Finder" widget</li>

<li><b>Search</b> for your business name (e.g., "celox.io Berlin")</li>

<li><b>Select</b> your business from suggestions</li>

<li><b>Copy</b> the Place ID (starts with ChIJ)</li>

<li><b>Paste</b> it into the field above</li>
</ol>

<p><b>The Place ID should look like:</b><br>
<code>ChIJp4JiUCNP0xQR1JaSjpW_Hms</code></p>

<p><i>See README.md for complete step-by-step instructions</i></p>
"""

        msg = QMessageBox(self)
        msg.setWindowTitle("Get Google Place ID")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def show_preview(self):
        """Show preview dialog"""
        # Get input
        input_text = self.input_field.text().strip()

        # Get mode
        mode_index = self.mode_combo.currentIndex()
        mode_map = {
            0: 'square',
            1: 'pendant',
            2: 'rectangle-text',
            3: 'pendant-text',
            4: 'rectangle-text-2x'
        }
        mode = mode_map.get(mode_index, 'square')

        # Get text content
        text_content = self.text_field.text().strip() if mode_index >= 2 else ''
        text_content_top = self.text_field_top.text().strip() if mode_index == 4 else ''

        # Get text rotation
        if mode_index >= 2:  # All text modes
            text_rotation = 180
        else:
            text_rotation = 0

        # Get parameters
        params = {
            'height': self.height_spin.value(),
            'margin': self.margin_spin.value(),
            'relief': self.relief_spin.value(),
            'corner_radius': self.corner_spin.value(),
            'size_scale': self.current_size_scale
        }

        # Show preview dialog
        dialog = PreviewDialog(input_text, mode, params, text_content, text_content_top, text_rotation, self)
        dialog.exec()

    def generate_model(self):
        """Start model generation in background thread"""
        input_text = self.input_field.text().strip()
        place_id = self.place_id_input.text().strip()

        if not input_text and not place_id:
            QMessageBox.warning(self, "Input Required", "Please enter a URL/image file or a Google Place ID.")
            return

        # Google Review Processing (Place ID only)
        if place_id:
            from .google_review import is_valid_place_id, generate_review_url

            if not is_valid_place_id(place_id):
                QMessageBox.warning(
                    self,
                    "Invalid Place ID",
                    f"Invalid Place ID: {place_id}\n\n"
                    f"Place IDs must start with 'ChIJ' or 'EI'.\n\n"
                    f"Click '❓ How to get Place ID' for instructions."
                )
                return

            # Generate review URL and use it as input
            review_url = generate_review_url(place_id)
            input_text = review_url
            self.status_label.setText(f"✅ Review link: {review_url[:50]}...")

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
            3: 'pendant-text',
            4: 'rectangle-text-2x'
        }
        mode = mode_map.get(mode_index, 'square')

        # Get text content (for text modes)
        text_content = self.text_field.text().strip() if mode_index >= 2 else ''
        text_content_top = self.text_field_top.text().strip() if mode_index == 4 else ''

        # Validate text for text modes
        if mode_index in [2, 3] and not text_content:
            QMessageBox.warning(self, "Text Required", "Please enter text for the text-mode model.")
            return

        # For rectangle-text-2x, require at least one text field
        if mode_index == 4 and not text_content and not text_content_top:
            QMessageBox.warning(self, "Text Required", "Please enter at least one text (top or bottom) for rectangle-text-2x mode.")
            return

        # Get text rotation
        # All text modes always use 180° rotation
        if mode_index >= 2:  # All text modes
            text_rotation = 180
        else:
            text_rotation = 0

        # Get parameters
        params = {
            'height': self.height_spin.value(),
            'margin': self.margin_spin.value(),
            'relief': self.relief_spin.value(),
            'corner_radius': self.corner_spin.value(),
            'size_scale': self.current_size_scale
        }

        # Start generation in background
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Starting generation...")

        self.generator_thread = GeneratorThread(input_text, output_name, mode, params, text_content, text_rotation, text_content_top)
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
            success_msg = f"✅ {message}\n📁 Files saved in: {DEFAULT_OUTPUT_DIR}/"
            self.status_label.setText(success_msg)
            self.status_label.setStyleSheet("padding: 10px; color: #008800; font-size: 12px; font-weight: bold;")
        else:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet("padding: 10px; color: #cc0000; font-size: 12px; font-weight: bold;")
            QMessageBox.critical(self, "Generation Failed", message)

    def show_help_dialog(self):
        """Show help dialog with usage tips"""
        help_text = """<h2>QR Code 3D Model Generator</h2>

<p>This tool generates 3D-printable QR code models from URLs or images.</p>

<h3>Input:</h3>
<ul>
<li><b>Enter URL:</b> QR code is generated automatically</li>
<li><b>Or select image file:</b> PNG/JPG files are supported</li>
</ul>

<h3>Model Type:</h3>
<ul>
<li><b>Square:</b> Square model (55x55mm)</li>
<li><b>Pendant (with hole):</b> With hole for keychain</li>
<li><b>Rectangle + Text:</b> Rectangular with text field (bottom)</li>
<li><b>Pendant + Text:</b> With hole and text field (bottom)</li>
<li><b>Rectangle + Text (2x):</b> Rectangular with text top AND bottom</li>
</ul>

<h3>Size:</h3>
<ul>
<li><b>Small (0.5x):</b> Half size - saves material</li>
<li><b>Medium (1x):</b> Standard size (recommended)</li>
<li><b>Large (2x):</b> Double size - better scannability</li>
</ul>
<p><i>Current dimensions are displayed below Model Type.</i></p>

<h3>Thickness Presets:</h3>
<ul>
<li><b>Thin (0.5mm):</b> Faster printing, less material</li>
<li><b>Medium (1.0mm):</b> Balanced</li>
<li><b>Thick (1.5mm):</b> More stable, better readability</li>
</ul>

<h3>Preview:</h3>
<p>Click <b>"Preview 3D Model"</b> to see a top-down view of how the QR code and text will be positioned on the model.</p>

<h3>Output:</h3>
<p>Generated files are saved in the <b>'{DEFAULT_OUTPUT_DIR}'</b> folder:</p>
<ul>
<li>.stl file for 3D printing</li>
<li>.scad file (OpenSCAD source code)</li>
<li>.json file (metadata)</li>
<li>.png file (QR code, if generated from URL)</li>
</ul>

<h3>Performance:</h3>
<p>With OpenSCAD 2025+ generation takes only ~1 second!</p>
"""

        footer_text = """<hr>
<p style='text-align: center; color: #666; font-size: 11px;'>
Open Source Project by Martin Pfeffer | MIT License | © 2025<br>
<a href='https://github.com/pepperonas/qrly' style='color: #0066cc;'>github.com/pepperonas/qrly</a>
</p>
"""

        dialog = QDialog(self)
        dialog.setWindowTitle("Help - QR Code 3D Generator")
        dialog.resize(700, 500)  # Wider and less high

        layout = QVBoxLayout(dialog)

        # Content label with scrolling
        text_browser = QTextBrowser()
        text_browser.setHtml(help_text + footer_text)
        text_browser.setOpenExternalLinks(True)  # Enable clickable links
        layout.addWidget(text_browser)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        layout.addWidget(close_btn)

        dialog.exec()

    def dragEnterEvent(self, event):
        """Handle drag enter event - accept JSON files"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().endswith('.json'):
                event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event - load settings from JSON file"""
        urls = event.mimeData().urls()
        if urls:
            json_path = urls[0].toLocalFile()
            if json_path.endswith('.json'):
                try:
                    self.load_settings_from_json(json_path)
                    self.status_label.setText(f"✅ Settings loaded from: {Path(json_path).name}")
                    self.status_label.setStyleSheet("padding: 10px; color: #008800; font-size: 12px;")
                except Exception as e:
                    QMessageBox.warning(self, "Load Error", f"Failed to load settings:\n{str(e)}")

    def load_settings_from_json(self, json_path: str):
        """Load all settings from a JSON metadata file"""
        import json

        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Check version compatibility
        json_version = config.get('version', 'unknown')
        if json_version != __version__:
            warning_msg = (
                f"Version Mismatch!\n\n"
                f"JSON file version: {json_version}\n"
                f"Current app version: {__version__}\n\n"
                f"Loading settings may cause incompatibilities, but the developer "
                f"tries their best to prevent inconsistencies. Proceed with caution."
            )
            QMessageBox.warning(self, "Version Compatibility Warning", warning_msg)

        # Load URL/Input
        if 'qr_input' in config:
            self.input_field.setText(config['qr_input'])

        # Load mode
        if 'mode' in config:
            mode_map = {
                'square': 0,
                'pendant': 1,
                'rectangle-text': 2,
                'pendant-text': 3,
                'rectangle-text-2x': 4
            }
            if config['mode'] in mode_map:
                self.mode_combo.setCurrentIndex(mode_map[config['mode']])

        # Load parameters
        params = config.get('parameters', {})
        if 'card_height_mm' in config.get('dimensions', {}):
            self.height_spin.setValue(config['dimensions']['card_height_mm'])
        if 'qr_margin_mm' in params:
            self.margin_spin.setValue(params['qr_margin_mm'])
        if 'qr_relief_mm' in params:
            self.relief_spin.setValue(params['qr_relief_mm'])
        if 'corner_radius_mm' in params:
            self.corner_spin.setValue(params['corner_radius_mm'])

        # Load text settings (if text mode)
        text_data = config.get('text', {})
        if text_data:
            # Load bottom text (or single text content)
            if 'content' in text_data:
                self.text_field.setText(text_data['content'])
            elif 'content_bottom' in text_data:
                self.text_field.setText(text_data['content_bottom'])
            # Load top text (for rectangle-text-2x mode)
            if 'content_top' in text_data:
                self.text_field_top.setText(text_data['content_top'])
            # Note: rotation is now always 180° for text modes, no checkbox needed

        # Load size scale (if available in newer JSON files)
        # For older files, try to infer from card_width
        if 'size_scale' in params:
            scale = params['size_scale']
            self.current_size_scale = scale
        else:
            # Infer from card_width: 27.5=0.5x, 55=1x, 110=2x
            card_width = config.get('dimensions', {}).get('card_width_mm', 55)
            if card_width <= 28:
                scale = 0.5
            elif card_width >= 100:
                scale = 2.0
            else:
                scale = 1.0
            self.current_size_scale = scale

        # Update size label
        self.update_size_label()


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
