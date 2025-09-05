"""
Main entry point for the Subtitle Creator with Effects application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from subtitle_creator.gui.main_window import MainWindow
from subtitle_creator.app_controller import AppController


def main():
    """Main application entry point."""
    print("Subtitle Creator with Effects v0.1.0")
    print("Starting GUI application...")
    
    # Initialize PyQt6 application
    app = QApplication(sys.argv)
    app.setApplicationName("Subtitle Creator with Effects")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("SubtitleCreator")
    
    # Enable high DPI scaling (PyQt6 handles this automatically)
    # These attributes are not needed in PyQt6 as they're enabled by default
    
    try:
        # Create main window
        main_window = MainWindow()
        
        # Create application controller and connect to main window
        app_controller = AppController(main_window, test_mode=True)
        
        # Show main window
        main_window.show()
        
        print("Application started successfully!")
        print("GUI is now running...")
        
        # Run the application event loop
        return app.exec()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())