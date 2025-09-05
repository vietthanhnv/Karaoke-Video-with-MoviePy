"""
Tests for the AppController class.

This module tests the central application controller that coordinates
all components and manages project state.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from src.subtitle_creator.app_controller import AppController, ProjectState
from src.subtitle_creator.models import SubtitleData, SubtitleLine
from src.subtitle_creator.interfaces import MediaError, AudioError, EffectError, ExportError


class MockMainWindow(QObject):
    """Mock main window for testing."""
    
    # Signals that the controller expects
    project_new_requested = pyqtSignal()
    project_open_requested = pyqtSignal(str)
    project_save_requested = pyqtSignal()
    project_save_as_requested = pyqtSignal(str)
    project_export_requested = pyqtSignal()
    playback_play_requested = pyqtSignal()
    playback_pause_requested = pyqtSignal()
    playback_stop_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.set_project_loaded = Mock()
        self.set_project_modified = Mock()
        self.set_playback_state = Mock()
        self.show_status_message = Mock()
        
        # Mock GUI components
        self.preview_panel = Mock()
        self.subtitle_editor = Mock()
        self.effects_panel = Mock()
        
        # Mock component signals with proper connect methods
        self.preview_panel.seek_requested = Mock()
        self.preview_panel.seek_requested.connect = Mock()
        
        self.subtitle_editor.subtitle_changed = Mock()
        self.subtitle_editor.subtitle_changed.connect = Mock()
        self.subtitle_editor.timing_changed = Mock()
        self.subtitle_editor.timing_changed.connect = Mock()
        
        self.effects_panel.effects_changed = Mock()
        self.effects_panel.effects_changed.connect = Mock()
    
    def get_preview_panel(self):
        return self.preview_panel
    
    def get_subtitle_editor(self):
        return self.subtitle_editor
    
    def get_effects_panel(self):
        return self.effects_panel


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def mock_main_window():
    """Create mock main window."""
    return MockMainWindow()


@pytest.fixture
def app_controller(app, mock_main_window):
    """Create AppController instance for testing."""
    with patch('src.subtitle_creator.app_controller.MediaManager') as mock_media_manager, \
         patch('src.subtitle_creator.app_controller.SubtitleEngine') as mock_subtitle_engine, \
         patch('src.subtitle_creator.app_controller.EffectSystem') as mock_effect_system, \
         patch('src.subtitle_creator.app_controller.PreviewEngine') as mock_preview_engine, \
         patch('src.subtitle_creator.app_controller.ExportManager') as mock_export_manager:
        
        controller = AppController(mock_main_window)
        
        # Store mock references for testing
        controller._mock_media_manager = mock_media_manager.return_value
        controller._mock_subtitle_engine = mock_subtitle_engine.return_value
        controller._mock_effect_system = mock_effect_system.return_value
        controller._mock_preview_engine = mock_preview_engine.return_value
        controller._mock_export_manager = mock_export_manager.return_value
        
        return controller


class TestAppControllerInitialization:
    """Test AppController initialization."""
    
    def test_initialization_without_main_window(self, app):
        """Test controller initialization without main window."""
        with patch('src.subtitle_creator.app_controller.MediaManager'), \
             patch('src.subtitle_creator.app_controller.SubtitleEngine'), \
             patch('src.subtitle_creator.app_controller.EffectSystem'), \
             patch('src.subtitle_creator.app_controller.PreviewEngine'), \
             patch('src.subtitle_creator.app_controller.ExportManager'):
            
            controller = AppController()
            
            assert controller.main_window is None
            assert isinstance(controller.project_state, ProjectState)
            assert not controller.project_state.is_loaded
            assert not controller.project_state.is_modified
    
    def test_initialization_with_main_window(self, app_controller, mock_main_window):
        """Test controller initialization with main window."""
        assert app_controller.main_window is mock_main_window
        assert hasattr(app_controller, 'media_manager')
        assert hasattr(app_controller, 'subtitle_engine')
        assert hasattr(app_controller, 'effect_system')
        assert hasattr(app_controller, 'preview_engine')
        assert hasattr(app_controller, 'export_manager')
    
    def test_signal_connections(self, app_controller, mock_main_window):
        """Test that signals are properly connected."""
        # Test that main window signals are connected (simplified check)
        assert hasattr(app_controller, 'main_window')
        assert app_controller.main_window is mock_main_window


class TestProjectManagement:
    """Test project management functionality."""
    
    def test_create_new_project(self, app_controller):
        """Test creating a new project."""
        # Reset the mock to clear any calls from initialization
        app_controller._mock_subtitle_engine.create_new.reset_mock()
        
        # Create new project
        app_controller.create_new_project()
        
        # Verify state
        assert app_controller.project_state.is_loaded
        assert not app_controller.project_state.is_modified
        app_controller._mock_subtitle_engine.create_new.assert_called_once()
    
    def test_create_new_project_with_unsaved_changes(self, app_controller):
        """Test creating new project with unsaved changes."""
        # Set project as modified
        app_controller.project_state.is_modified = True
        
        # Mock confirmation dialog to return False (don't discard)
        with patch.object(app_controller, '_confirm_discard_changes', return_value=False):
            app_controller.create_new_project()
        
        # Verify project wasn't reset
        assert app_controller.project_state.is_modified
    
    def test_load_project_success(self, app_controller):
        """Test successful project loading."""
        # Create temporary project file
        project_data = {
            'version': '1.0',
            'background_media': 'test_bg.mp4',
            'audio_file': 'test_audio.mp3',
            'subtitle_data': {
                'lines': [],
                'global_style': {},
                'metadata': {}
            },
            'effects': []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(project_data, f)
            temp_path = f.name
        
        try:
            # Mock file loading methods
            app_controller.load_background_media = Mock()
            app_controller.load_audio_file = Mock()
            app_controller._mock_subtitle_engine.load_from_data = Mock()
            
            # Load project
            app_controller.load_project(temp_path)
            
            # Verify state
            assert app_controller.project_state.is_loaded
            assert not app_controller.project_state.is_modified
            assert app_controller.project_state.project_file_path == temp_path
            
        finally:
            os.unlink(temp_path)
    
    def test_load_project_file_not_found(self, app_controller):
        """Test loading non-existent project file."""
        with patch('src.subtitle_creator.app_controller.QMessageBox'):
            app_controller.load_project('nonexistent.json')
        
        # Verify error was emitted
        assert not app_controller.project_state.is_loaded
    
    def test_save_project_new_file(self, app_controller):
        """Test saving project to new file."""
        # Set up project state
        app_controller.project_state.is_loaded = True
        app_controller.project_state.is_modified = True
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_subtitle_engine.subtitle_data = Mock()
        app_controller._mock_subtitle_engine.subtitle_data.to_dict = Mock(return_value={})
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Save project
            app_controller._save_project_to_file(temp_path)
            
            # Verify state
            assert not app_controller.project_state.is_modified
            assert app_controller.project_state.project_file_path == temp_path
            assert os.path.exists(temp_path)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestMediaLoading:
    """Test media loading functionality."""
    
    def test_load_background_media_success(self, app_controller):
        """Test successful background media loading."""
        # Mock media manager
        mock_clip = Mock()
        app_controller._mock_media_manager.load_background_media = Mock(return_value=mock_clip)
        
        # Create temporary media file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            temp_path = f.name
        
        try:
            # Load media
            app_controller.load_background_media(temp_path)
            
            # Verify state
            assert app_controller.project_state.background_media_path == temp_path
            assert app_controller.project_state.is_modified
            assert app_controller._background_clip is mock_clip
            
        finally:
            os.unlink(temp_path)
    
    def test_load_background_media_file_not_found(self, app_controller):
        """Test loading non-existent media file."""
        with patch('src.subtitle_creator.app_controller.QMessageBox'):
            app_controller.load_background_media('nonexistent.mp4')
        
        # Verify error handling
        assert app_controller.project_state.background_media_path is None
        assert app_controller._background_clip is None
    
    def test_load_audio_file_success(self, app_controller):
        """Test successful audio file loading."""
        # Mock media manager
        mock_audio = Mock()
        app_controller._mock_media_manager.load_audio = Mock(return_value=mock_audio)
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_path = f.name
        
        try:
            # Load audio
            app_controller.load_audio_file(temp_path)
            
            # Verify state
            assert app_controller.project_state.audio_file_path == temp_path
            assert app_controller.project_state.is_modified
            assert app_controller._audio_clip is mock_audio
            
        finally:
            os.unlink(temp_path)
    
    def test_load_subtitle_file_success(self, app_controller):
        """Test successful subtitle file loading."""
        # Mock subtitle engine
        app_controller._mock_subtitle_engine.load_from_file = Mock()
        
        # Create temporary subtitle file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Load subtitles
            app_controller.load_subtitle_file(temp_path)
            
            # Verify state
            assert app_controller.project_state.subtitle_file_path == temp_path
            assert app_controller.project_state.is_modified
            app_controller._mock_subtitle_engine.load_from_file.assert_called_once_with(temp_path)
            
        finally:
            os.unlink(temp_path)


class TestEffectManagement:
    """Test effect management functionality."""
    
    def test_apply_effect_success(self, app_controller):
        """Test successful effect application."""
        # Mock effect system
        mock_effect = Mock()
        mock_effect.name = 'TestEffect'
        app_controller._mock_effect_system.create_effect = Mock(return_value=mock_effect)
        app_controller._mock_effect_system.add_effect = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[mock_effect])
        
        # Apply effect
        app_controller.apply_effect('TestEffect', {'param1': 'value1'})
        
        # Verify effect was applied
        app_controller._mock_effect_system.create_effect.assert_called_once_with('TestEffect', {'param1': 'value1'})
        app_controller._mock_effect_system.add_effect.assert_called_once_with(mock_effect)
        assert app_controller.project_state.is_modified
    
    def test_remove_effect_success(self, app_controller):
        """Test successful effect removal."""
        # Mock effect system
        mock_effect = Mock()
        mock_effect.name = 'TestEffect'
        app_controller._mock_effect_system.remove_effect = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        
        # Remove effect
        app_controller.remove_effect(mock_effect)
        
        # Verify effect was removed
        app_controller._mock_effect_system.remove_effect.assert_called_once_with(mock_effect)
        assert app_controller.project_state.is_modified
    
    def test_clear_all_effects(self, app_controller):
        """Test clearing all effects."""
        # Mock effect system
        app_controller._mock_effect_system.clear_effects = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        
        # Clear effects
        app_controller.clear_all_effects()
        
        # Verify effects were cleared
        app_controller._mock_effect_system.clear_effects.assert_called_once()
        assert app_controller.project_state.is_modified


class TestPlaybackControl:
    """Test playback control functionality."""
    
    def test_start_playback_with_media(self, app_controller):
        """Test starting playback with media loaded."""
        # Set up media
        app_controller._background_clip = Mock()
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_preview_engine.get_current_time = Mock(return_value=0.0)
        app_controller._mock_preview_engine.start_playback = Mock()
        
        # Start playback
        app_controller.start_playback()
        
        # Verify playback started
        app_controller._mock_preview_engine.start_playback.assert_called_once_with(0.0)
    
    def test_start_playback_without_media(self, app_controller):
        """Test starting playback without media loaded."""
        # No media loaded
        app_controller._background_clip = None
        
        # Start playback
        app_controller.start_playback()
        
        # Verify playback didn't start
        app_controller._mock_preview_engine.start_playback.assert_not_called()
    
    def test_pause_playback(self, app_controller):
        """Test pausing playback."""
        app_controller._mock_preview_engine.pause_playback = Mock()
        
        # Pause playback
        app_controller.pause_playback()
        
        # Verify playback paused
        app_controller._mock_preview_engine.pause_playback.assert_called_once()
    
    def test_stop_playback(self, app_controller):
        """Test stopping playback."""
        app_controller._mock_preview_engine.stop_playback = Mock()
        
        # Stop playback
        app_controller.stop_playback()
        
        # Verify playback stopped
        app_controller._mock_preview_engine.stop_playback.assert_called_once()
    
    def test_seek_to_time(self, app_controller):
        """Test seeking to specific time."""
        # Set up media
        app_controller._background_clip = Mock()
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_preview_engine.seek_to_time = Mock()
        
        # Seek to time
        app_controller.seek_to_time(5.0)
        
        # Verify seek was called
        app_controller._mock_preview_engine.seek_to_time.assert_called_once_with(5.0)


class TestStateManagement:
    """Test undo/redo state management."""
    
    def test_save_state_for_undo(self, app_controller):
        """Test saving state for undo."""
        # Set up some state
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_subtitle_engine.subtitle_data = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        
        # Save state
        app_controller._save_state_for_undo()
        
        # Verify state was saved
        assert len(app_controller._undo_stack) == 1
        assert len(app_controller._redo_stack) == 0
    
    def test_undo_operation(self, app_controller):
        """Test undo operation."""
        # Set up initial state
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_subtitle_engine.subtitle_data = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        app_controller._mock_subtitle_engine.load_from_data = Mock()
        app_controller._mock_effect_system.clear_effects = Mock()
        
        # Save initial state
        app_controller._save_state_for_undo()
        
        # Perform undo
        result = app_controller.undo()
        
        # Verify undo was successful
        assert result is True
        assert len(app_controller._undo_stack) == 0
        assert len(app_controller._redo_stack) == 1
    
    def test_undo_without_history(self, app_controller):
        """Test undo without history."""
        # Perform undo without history
        result = app_controller.undo()
        
        # Verify undo failed
        assert result is False
    
    def test_redo_operation(self, app_controller):
        """Test redo operation."""
        # Set up state and perform undo first
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_subtitle_engine.subtitle_data = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        app_controller._mock_subtitle_engine.load_from_data = Mock()
        app_controller._mock_effect_system.clear_effects = Mock()
        
        app_controller._save_state_for_undo()
        app_controller.undo()
        
        # Perform redo
        result = app_controller.redo()
        
        # Verify redo was successful
        assert result is True
        assert len(app_controller._undo_stack) == 1
        assert len(app_controller._redo_stack) == 0
    
    def test_can_undo_redo(self, app_controller):
        """Test undo/redo availability checks."""
        # Initially no undo/redo available
        assert not app_controller.can_undo()
        assert not app_controller.can_redo()
        
        # Save state
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_subtitle_engine.subtitle_data = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        app_controller._save_state_for_undo()
        
        # Now undo is available
        assert app_controller.can_undo()
        assert not app_controller.can_redo()


class TestExportFunctionality:
    """Test video export functionality."""
    
    def test_export_video_success(self, app_controller):
        """Test successful video export."""
        # Set up media and subtitles
        app_controller._background_clip = Mock()
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_subtitle_engine.subtitle_data = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        app_controller._mock_export_manager.export_video = Mock()
        
        # Export video
        app_controller.export_video('output.mp4', {'format': 'mp4', 'quality': 'high'})
        
        # Verify export was called
        app_controller._mock_export_manager.export_video.assert_called_once()
    
    def test_export_video_without_media(self, app_controller):
        """Test export without media loaded."""
        # No media loaded
        app_controller._background_clip = None
        
        # Export video
        with patch('src.subtitle_creator.app_controller.QMessageBox'):
            app_controller.export_video('output.mp4')
        
        # Verify export wasn't called
        app_controller._mock_export_manager.export_video.assert_not_called()


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_mark_project_modified(self, app_controller):
        """Test marking project as modified."""
        # Initially not modified
        assert not app_controller.project_state.is_modified
        
        # Mark as modified
        app_controller._mark_project_modified()
        
        # Verify state changed
        assert app_controller.project_state.is_modified
    
    def test_reset_project_state(self, app_controller):
        """Test resetting project state."""
        # Set up some state
        app_controller.project_state.is_loaded = True
        app_controller.project_state.is_modified = True
        app_controller._background_clip = Mock()
        app_controller._undo_stack.append({})
        
        # Mock component methods
        app_controller._mock_subtitle_engine.create_new = Mock()
        app_controller._mock_effect_system.clear_effects = Mock()
        app_controller._mock_preview_engine.clear_cache = Mock()
        
        # Reset state
        app_controller._reset_project_state()
        
        # Verify state was reset
        assert not app_controller.project_state.is_loaded
        assert not app_controller.project_state.is_modified
        assert app_controller._background_clip is None
        assert len(app_controller._undo_stack) == 0
    
    def test_can_preview(self, app_controller):
        """Test preview capability check."""
        # Initially can't preview
        assert not app_controller._can_preview()
        
        # Set up media and subtitles
        app_controller._background_clip = Mock()
        app_controller._mock_subtitle_engine.has_data = True
        
        # Now can preview
        assert app_controller._can_preview()
    
    def test_public_api_methods(self, app_controller):
        """Test public API methods."""
        # Test getter methods
        project_state = app_controller.get_project_state()
        assert isinstance(project_state, ProjectState)
        
        # Mock return values
        app_controller._mock_subtitle_engine.has_data = True
        app_controller._mock_subtitle_engine.subtitle_data = Mock()
        app_controller._mock_effect_system.get_active_effects = Mock(return_value=[])
        app_controller._mock_preview_engine.get_duration = Mock(return_value=10.0)
        app_controller._mock_preview_engine.get_current_time = Mock(return_value=5.0)
        app_controller._mock_preview_engine.is_playing = Mock(return_value=True)
        
        # Test API methods
        subtitle_data = app_controller.get_subtitle_data()
        assert subtitle_data is not None
        
        effects = app_controller.get_active_effects()
        assert isinstance(effects, list)
        
        duration = app_controller.get_preview_duration()
        assert duration == 10.0
        
        current_time = app_controller.get_current_time()
        assert current_time == 5.0
        
        is_playing = app_controller.is_playing()
        assert is_playing is True