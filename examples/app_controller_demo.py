#!/usr/bin/env python3
"""
Demo script showing AppController functionality.

This script demonstrates how the AppController coordinates all components
of the Subtitle Creator application, managing project state and handling
user interactions.
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer

from subtitle_creator.app_controller import AppController


class DemoMainWindow(QMainWindow):
    """Simple demo main window to show AppController integration."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AppController Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Demo buttons
        self.new_project_btn = QPushButton("New Project")
        self.new_project_btn.clicked.connect(self.create_new_project)
        layout.addWidget(self.new_project_btn)
        
        self.load_media_btn = QPushButton("Load Demo Media")
        self.load_media_btn.clicked.connect(self.load_demo_media)
        layout.addWidget(self.load_media_btn)
        
        self.apply_effect_btn = QPushButton("Apply Demo Effect")
        self.apply_effect_btn.clicked.connect(self.apply_demo_effect)
        layout.addWidget(self.apply_effect_btn)
        
        self.start_playback_btn = QPushButton("Start Playback")
        self.start_playback_btn.clicked.connect(self.start_playback)
        layout.addWidget(self.start_playback_btn)
        
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_action)
        layout.addWidget(self.undo_btn)
        
        # Initialize AppController
        self.app_controller = AppController(self)
        
        # Connect controller signals
        self.app_controller.status_message.connect(self.update_status)
        self.app_controller.project_loaded.connect(self.on_project_loaded)
        self.app_controller.project_modified.connect(self.on_project_modified)
        self.app_controller.effects_changed.connect(self.on_effects_changed)
        
        # Mock GUI component methods that AppController expects
        self.set_project_loaded = lambda loaded: self.update_status(f"Project loaded: {loaded}", 0)
        self.set_project_modified = lambda modified: self.update_status(f"Project modified: {modified}", 0)
        self.set_playback_state = lambda playing: self.update_status(f"Playing: {playing}", 0)
        self.show_status_message = lambda msg, timeout: self.update_status(msg, timeout)
        
        # Mock GUI components
        self.get_preview_panel = lambda: None
        self.get_subtitle_editor = lambda: None
        self.get_effects_panel = lambda: None
    
    def update_status(self, message: str, timeout: int = 0):
        """Update status label."""
        self.status_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
    
    def create_new_project(self):
        """Create a new project."""
        self.app_controller.create_new_project()
    
    def load_demo_media(self):
        """Load demo media files."""
        # Create a simple demo media file for testing
        demo_media_path = Path(__file__).parent / "demo_media.txt"
        if not demo_media_path.exists():
            demo_media_path.write_text("Demo media file")
        
        try:
            self.app_controller.load_background_media(str(demo_media_path))
        except Exception as e:
            self.update_status(f"Media load failed (expected): {e}", 3000)
    
    def apply_demo_effect(self):
        """Apply a demo effect."""
        try:
            self.app_controller.apply_effect("DemoEffect", {"intensity": 0.5})
        except Exception as e:
            self.update_status(f"Effect apply failed (expected): {e}", 3000)
    
    def start_playback(self):
        """Start playback."""
        self.app_controller.start_playback()
    
    def undo_action(self):
        """Perform undo."""
        if self.app_controller.undo():
            self.update_status("Undo successful", 2000)
        else:
            self.update_status("Nothing to undo", 2000)
    
    def on_project_loaded(self, loaded: bool):
        """Handle project loaded signal."""
        self.update_status(f"Project loaded signal: {loaded}", 2000)
    
    def on_project_modified(self, modified: bool):
        """Handle project modified signal."""
        self.update_status(f"Project modified signal: {modified}", 2000)
    
    def on_effects_changed(self, effects):
        """Handle effects changed signal."""
        self.update_status(f"Effects changed: {len(effects)} active", 2000)


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    # Create and show demo window
    window = DemoMainWindow()
    window.show()
    
    # Print demo instructions
    print("AppController Demo")
    print("==================")
    print("This demo shows how the AppController coordinates all components.")
    print("Try the buttons to see how the controller manages state and signals.")
    print("")
    print("Features demonstrated:")
    print("- Project management (new project)")
    print("- Media loading coordination")
    print("- Effect system integration")
    print("- Playback control")
    print("- Undo/redo state management")
    print("- Reactive signal propagation")
    print("")
    print("Watch the status messages to see the controller in action!")
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()