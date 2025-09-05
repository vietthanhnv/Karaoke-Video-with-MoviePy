"""
Tests for the MainWindow GUI component.
"""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from src.subtitle_creator.gui.main_window import MainWindow


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def main_window(app):
    """Create MainWindow instance for testing."""
    window = MainWindow()
    return window


class TestMainWindow:
    """Test cases for MainWindow class."""
    
    def test_window_initialization(self, main_window):
        """Test that the main window initializes correctly."""
        assert main_window.windowTitle() == "Subtitle Creator with Effects"
        assert main_window.minimumSize().width() == 1200
        assert main_window.minimumSize().height() == 800
    
    def test_menu_bar_creation(self, main_window):
        """Test that all menus are created correctly."""
        menubar = main_window.menuBar()
        menu_titles = [action.text() for action in menubar.actions()]
        
        expected_menus = ["&File", "&Edit", "&View", "&Effects", "&Help"]
        for menu_title in expected_menus:
            assert menu_title in menu_titles
    
    def test_toolbar_creation(self, main_window):
        """Test that the toolbar is created with expected actions."""
        toolbars = main_window.findChildren(type(main_window.addToolBar("test")))
        assert len(toolbars) >= 1
        
        main_toolbar = toolbars[0]
        assert main_toolbar.objectName() == "MainToolbar"
        assert main_toolbar.isMovable()
    
    def test_layout_structure(self, main_window):
        """Test that the layout structure is correct."""
        central_widget = main_window.centralWidget()
        assert central_widget is not None
        
        # Check that splitters exist
        assert hasattr(main_window, 'main_splitter')
        assert hasattr(main_window, 'left_splitter')
        
        # Check that panel widgets exist
        assert hasattr(main_window, 'preview_panel')
        assert hasattr(main_window, 'timeline_widget')
        assert hasattr(main_window, 'effects_widget')
    
    def test_splitter_configuration(self, main_window):
        """Test that splitters are configured correctly."""
        # Main splitter should be horizontal
        assert main_window.main_splitter.orientation() == Qt.Orientation.Horizontal
        
        # Left splitter should be vertical
        assert main_window.left_splitter.orientation() == Qt.Orientation.Vertical
        
        # Check handle widths
        assert main_window.main_splitter.handleWidth() == 6
        assert main_window.left_splitter.handleWidth() == 6
    
    def test_panel_minimum_sizes(self, main_window):
        """Test that panels have appropriate minimum sizes."""
        assert main_window.preview_panel.minimumSize().width() == 400
        assert main_window.preview_panel.minimumSize().height() == 300
        
        assert main_window.timeline_widget.minimumHeight() == 150
        assert main_window.timeline_widget.maximumHeight() == 300
        
        assert main_window.effects_widget.minimumSize().width() == 300
        assert main_window.effects_widget.minimumSize().height() == 400
    
    def test_action_signals(self, main_window):
        """Test that actions emit appropriate signals."""
        # Test that signals exist
        assert hasattr(main_window, 'project_new_requested')
        assert hasattr(main_window, 'project_open_requested')
        assert hasattr(main_window, 'project_save_requested')
        assert hasattr(main_window, 'project_export_requested')
        assert hasattr(main_window, 'playback_play_requested')
        assert hasattr(main_window, 'playback_pause_requested')
        assert hasattr(main_window, 'playback_stop_requested')
    
    def test_project_state_management(self, main_window):
        """Test project state management methods."""
        # Test project modified state
        main_window.set_project_modified(True)
        assert main_window.action_save.isEnabled()
        assert "*" in main_window.windowTitle()
        
        main_window.set_project_modified(False)
        assert not main_window.action_save.isEnabled()
        assert "*" not in main_window.windowTitle()
        
        # Test project loaded state
        main_window.set_project_loaded(True)
        assert main_window.action_save_as.isEnabled()
        assert main_window.action_export.isEnabled()
        
        main_window.set_project_loaded(False)
        assert not main_window.action_save_as.isEnabled()
        assert not main_window.action_export.isEnabled()
    
    def test_playback_state_management(self, main_window):
        """Test playback state management."""
        # Test playing state
        main_window.set_playback_state(True)
        assert main_window.action_play.isChecked()
        assert "Pause" in main_window.action_play.text()
        
        # Test stopped state
        main_window.set_playback_state(False)
        assert not main_window.action_play.isChecked()
        assert "Play" in main_window.action_play.text()
    
    def test_panel_visibility_toggle(self, main_window):
        """Test panel visibility toggle functionality."""
        # Show the window to ensure proper visibility handling
        main_window.show()
        
        # Test timeline toggle
        main_window.action_toggle_timeline.setChecked(False)
        main_window._toggle_timeline_panel()
        assert not main_window.timeline_widget.isVisible()
        
        main_window.action_toggle_timeline.setChecked(True)
        main_window._toggle_timeline_panel()
        assert main_window.timeline_widget.isVisible()
        
        # Test effects panel toggle
        main_window.action_toggle_effects.setChecked(False)
        main_window._toggle_effects_panel()
        assert not main_window.effects_widget.isVisible()
        
        main_window.action_toggle_effects.setChecked(True)
        main_window._toggle_effects_panel()
        assert main_window.effects_widget.isVisible()
        
        # Hide the window after test
        main_window.hide()
    
    def test_status_message(self, main_window):
        """Test status message functionality."""
        test_message = "Test status message"
        main_window.show_status_message(test_message, 1000)
        
        # Check that status bar shows the message
        assert main_window.status_bar.currentMessage() == test_message
    
    def test_widget_accessors(self, main_window):
        """Test widget accessor methods."""
        assert main_window.get_preview_panel() is main_window.preview_panel
        assert main_window.get_timeline_widget() is main_window.timeline_widget
        assert main_window.get_effects_widget() is main_window.effects_widget
    
    @patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName')
    def test_open_project_dialog(self, mock_dialog, main_window):
        """Test open project dialog functionality."""
        mock_dialog.return_value = ("/path/to/project.json", "")
        
        # Connect signal to capture emission
        signal_emitted = False
        received_path = None
        
        def signal_handler(path):
            nonlocal signal_emitted, received_path
            signal_emitted = True
            received_path = path
        
        main_window.project_open_requested.connect(signal_handler)
        
        # Trigger the action
        main_window._handle_open_project()
        
        assert signal_emitted
        assert received_path == "/path/to/project.json"
    
    @patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_as_project_dialog(self, mock_dialog, main_window):
        """Test save as project dialog functionality."""
        mock_dialog.return_value = ("/path/to/new_project.json", "")
        
        # Connect signal to capture emission
        signal_emitted = False
        received_path = None
        
        def signal_handler(path):
            nonlocal signal_emitted, received_path
            signal_emitted = True
            received_path = path
        
        main_window.project_save_as_requested.connect(signal_handler)
        
        # Trigger the action
        main_window._handle_save_as_project()
        
        assert signal_emitted
        assert received_path == "/path/to/new_project.json"
    
    def test_play_pause_toggle(self, main_window):
        """Test play/pause toggle functionality."""
        # Mock preview engine for the preview panel
        from unittest.mock import Mock
        mock_engine = Mock()
        mock_engine.get_duration.return_value = 120.0
        mock_engine.get_current_time.return_value = 0.0
        mock_engine.is_playing.return_value = False
        main_window.preview_panel.set_preview_engine(mock_engine)
        
        # Test play action
        main_window.action_play.setChecked(True)
        
        # The main window now calls preview panel methods directly
        # Check that the preview panel state changes
        main_window._handle_play_pause()
        
        assert main_window.preview_panel._is_playing
        assert "Pause" in main_window.action_play.text()
        
        # Test pause action
        main_window.action_play.setChecked(False)
        main_window._handle_play_pause()
        
        assert not main_window.preview_panel._is_playing
        assert "Play" in main_window.action_play.text()
    
    def test_stop_functionality(self, main_window):
        """Test stop functionality."""
        # Mock preview engine for the preview panel
        from unittest.mock import Mock
        mock_engine = Mock()
        mock_engine.get_duration.return_value = 120.0
        mock_engine.get_current_time.return_value = 0.0
        mock_engine.is_playing.return_value = False
        main_window.preview_panel.set_preview_engine(mock_engine)
        
        # Set up initial playing state
        main_window.action_play.setChecked(True)
        main_window.action_play.setText("&Pause")
        main_window.preview_panel._is_playing = True
        
        # The main window now calls preview panel methods directly
        main_window._handle_stop()
        
        assert not main_window.preview_panel._is_playing
        assert not main_window.action_play.isChecked()
        assert "Play" in main_window.action_play.text()
    
    @patch('PyQt6.QtWidgets.QMessageBox.about')
    def test_about_dialog(self, mock_about, main_window):
        """Test about dialog functionality."""
        main_window._show_about_dialog()
        
        mock_about.assert_called_once()
        args = mock_about.call_args[0]
        assert args[0] is main_window
        assert "About Subtitle Creator with Effects" in args[1]
        assert "Subtitle Creator with Effects" in args[2]