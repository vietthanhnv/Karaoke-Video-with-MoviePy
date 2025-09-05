#!/usr/bin/env python3
"""
Demo script for the MainWindow GUI component.

This script demonstrates the main window layout, menu system, and basic functionality
of the Subtitle Creator with Effects application.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from subtitle_creator.gui.main_window import MainWindow


class MainWindowDemo:
    """Demo class for MainWindow functionality."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        self._setup_demo_content()
        self._connect_signals()
    
    def _setup_demo_content(self):
        """Add demo content to the main window panels."""
        # The main window now has integrated panels with full functionality
        # No need to add placeholder content since the panels are fully implemented
        pass
    
    def _connect_signals(self):
        """Connect MainWindow signals to demo handlers."""
        self.main_window.project_new_requested.connect(self._handle_new_project)
        self.main_window.project_open_requested.connect(self._handle_open_project)
        self.main_window.project_save_requested.connect(self._handle_save_project)
        self.main_window.project_export_requested.connect(self._handle_export_project)
        
        self.main_window.playback_play_requested.connect(self._handle_play)
        self.main_window.playback_pause_requested.connect(self._handle_pause)
        self.main_window.playback_stop_requested.connect(self._handle_stop)
    
    def _handle_new_project(self):
        """Handle new project request."""
        self.main_window.show_status_message("New project created", 2000)
        self.main_window.set_project_loaded(True)
        self.main_window.set_project_modified(False)
        print("Demo: New project requested")
    
    def _handle_open_project(self, file_path):
        """Handle open project request."""
        self.main_window.show_status_message(f"Opened project: {file_path}", 3000)
        self.main_window.set_project_loaded(True)
        self.main_window.set_project_modified(False)
        print(f"Demo: Open project requested - {file_path}")
    
    def _handle_save_project(self):
        """Handle save project request."""
        self.main_window.show_status_message("Project saved", 2000)
        self.main_window.set_project_modified(False)
        print("Demo: Save project requested")
    
    def _handle_export_project(self):
        """Handle export project request."""
        self.main_window.show_status_message("Exporting video...", 5000)
        print("Demo: Export project requested")
    
    def _handle_play(self):
        """Handle play request."""
        self.main_window.show_status_message("Playing preview", 1000)
        self.main_window.set_playback_state(True)
        print("Demo: Play requested")
    
    def _handle_pause(self):
        """Handle pause request."""
        self.main_window.show_status_message("Preview paused", 1000)
        self.main_window.set_playback_state(False)
        print("Demo: Pause requested")
    
    def _handle_stop(self):
        """Handle stop request."""
        self.main_window.show_status_message("Preview stopped", 1000)
        self.main_window.set_playback_state(False)
        print("Demo: Stop requested")
    
    def run(self):
        """Run the demo application."""
        print("MainWindow Demo")
        print("===============")
        print("Features demonstrated:")
        print("- Complete menu system (File, Edit, View, Effects, Help)")
        print("- Toolbar with common actions")
        print("- Three-panel responsive layout with splitters")
        print("- Window state persistence")
        print("- Signal-based communication")
        print("- Status bar messaging")
        print("")
        print("Try the following:")
        print("- Use File menu to create/open/save projects")
        print("- Use playback controls in toolbar")
        print("- Resize panels using splitter handles")
        print("- Toggle panel visibility in View menu")
        print("- Check keyboard shortcuts (Ctrl+N, Ctrl+O, Space, etc.)")
        print("")
        
        # Show the main window
        self.main_window.show()
        
        # Simulate a loaded project for demo
        self.main_window.set_project_loaded(True)
        self.main_window.show_status_message("Demo ready - Try the menu and toolbar actions!", 5000)
        
        # Run the application
        return self.app.exec()


def main():
    """Main entry point for the demo."""
    demo = MainWindowDemo()
    return demo.run()


if __name__ == "__main__":
    sys.exit(main())