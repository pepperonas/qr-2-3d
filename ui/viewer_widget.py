"""
3D Viewer Widget using PyVista
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from pyvistaqt import QtInteractor
import pyvista as pv
from pathlib import Path


class ViewerWidget(QWidget):
    """3D model viewer using PyVista"""

    def __init__(self, parent=None):
        super().__init__(parent)
        print("  ViewerWidget.__init__() started")
        self.current_mesh = None
        print("  Setting up viewer UI...")
        self.setup_ui()
        print("  ViewerWidget.__init__() completed")

    def setup_ui(self):
        """Setup the viewer UI"""
        layout = QVBoxLayout(self)

        # Info label
        print("    Creating info label...")
        self.info_label = QLabel("No model loaded")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # PyVista viewer
        print("    Creating QtInteractor (PyVista 3D viewer)...")
        self.plotter = QtInteractor(self)
        print("    QtInteractor created")
        self.plotter.set_background('lightgray')
        print("    Adding plotter to layout...")
        layout.addWidget(self.plotter.interactor, stretch=1)
        print("    Plotter added to layout")

        # Control buttons
        btn_layout = QHBoxLayout()

        self.reset_btn = QPushButton("Reset Camera")
        self.reset_btn.clicked.connect(self.reset_camera)
        btn_layout.addWidget(self.reset_btn)

        self.wireframe_btn = QPushButton("Toggle Wireframe")
        self.wireframe_btn.clicked.connect(self.toggle_wireframe)
        self.wireframe_btn.setEnabled(False)
        btn_layout.addWidget(self.wireframe_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.wireframe_mode = False

    def load_stl(self, stl_path: Path):
        """Load and display STL file"""
        try:
            if not stl_path.exists():
                self.info_label.setText(f"File not found: {stl_path.name}")
                return False

            # Load mesh
            mesh = pv.read(str(stl_path))
            self.current_mesh = mesh

            # Clear previous meshes
            self.plotter.clear()

            # Add mesh with nice rendering
            self.plotter.add_mesh(
                mesh,
                color='lightblue',
                show_edges=False,
                smooth_shading=True
            )

            # Reset camera to show full model
            self.plotter.reset_camera()

            # Update info
            n_points = mesh.n_points
            n_cells = mesh.n_cells
            self.info_label.setText(
                f"Loaded: {stl_path.name} | "
                f"Vertices: {n_points:,} | Faces: {n_cells:,}"
            )

            # Enable controls
            self.wireframe_btn.setEnabled(True)

            return True

        except Exception as e:
            self.info_label.setText(f"Error loading STL: {str(e)}")
            return False

    def reset_camera(self):
        """Reset camera to default view"""
        if self.current_mesh is not None:
            self.plotter.reset_camera()

    def toggle_wireframe(self):
        """Toggle between solid and wireframe view"""
        if self.current_mesh is None:
            return

        self.wireframe_mode = not self.wireframe_mode

        # Clear and re-add with new style
        self.plotter.clear()

        if self.wireframe_mode:
            self.plotter.add_mesh(
                self.current_mesh,
                color='blue',
                style='wireframe',
                line_width=2
            )
        else:
            self.plotter.add_mesh(
                self.current_mesh,
                color='lightblue',
                show_edges=False,
                smooth_shading=True
            )

        self.plotter.reset_camera()
