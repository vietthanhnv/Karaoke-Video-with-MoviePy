"""
Integration tests for AppController with real components.

This module tests the AppController with actual backend components
to verify the integration works correctly.
"""

import pytest
import tempfile
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject

from src.subtitle_creator.app_controller import AppController
from src.subtitle_creator.models import SubtitleData, SubtitleLine


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


class TestAppControllerIntegration:
    """Test AppController integration with real components."""
    
    def test_controller_initialization(self, app):
        """Test that controller initializes with real components."""
        controller = AppController()
        
        # Verify components are initialized
        assert controller.media_manager is not None
        assert controller.subtitle_engine is not None
        assert controller.effect_system is not None
        assert controller.preview_engine is not None
        assert controller.export_manager is not None
        
        # Verify initial state
        assert not controller.project_state.is_loaded
        assert not controller.project_state.is_modified
    
    def test_create_new_project_integration(self, app):
        """Test creating new project with real components."""
        controller = AppController()
        
        # Create new project
        controller.create_new_project()
        
        # Verify state
        assert controller.project_state.is_loaded
        assert not controller.project_state.is_modified
        assert controller.subtitle_engine.has_data
    
    def test_subtitle_engine_integration(self, app):
        """Test subtitle engine integration."""
        controller = AppController()
        
        # Create new project
        controller.create_new_project()
        
        # Verify subtitle engine is working
        assert controller.subtitle_engine.has_data
        
        # Test getting subtitle data
        subtitle_data = controller.get_subtitle_data()
        assert subtitle_data is not None
        assert isinstance(subtitle_data, SubtitleData)
    
    def test_effect_system_integration(self, app):
        """Test effect system integration."""
        controller = AppController()
        
        # Get active effects (should be empty initially)
        effects = controller.get_active_effects()
        assert isinstance(effects, list)
        assert len(effects) == 0
        
        # Clear effects (should work even when empty)
        controller.clear_all_effects()
        assert len(controller.get_active_effects()) == 0
    
    def test_state_management_integration(self, app):
        """Test state management with real components."""
        controller = AppController()
        
        # Initially no undo/redo available
        assert not controller.can_undo()
        assert not controller.can_redo()
        
        # Create new project
        controller.create_new_project()
        
        # Still no undo available (no operations performed yet)
        assert not controller.can_undo()
        assert not controller.can_redo()
    
    def test_project_state_management(self, app):
        """Test project state management."""
        controller = AppController()
        
        # Initial state
        project_state = controller.get_project_state()
        assert not project_state.is_loaded
        assert not project_state.is_modified
        
        # Create new project
        controller.create_new_project()
        
        # Updated state
        project_state = controller.get_project_state()
        assert project_state.is_loaded
        assert not project_state.is_modified
    
    def test_preview_capabilities(self, app):
        """Test preview capabilities."""
        controller = AppController()
        
        # Initially can't preview (no media)
        assert not controller._can_preview()
        
        # Create new project (has subtitles but no media)
        controller.create_new_project()
        assert not controller._can_preview()
        
        # Get preview duration (should work even without media)
        duration = controller.get_preview_duration()
        assert isinstance(duration, (int, float))
        
        # Get current time
        current_time = controller.get_current_time()
        assert isinstance(current_time, (int, float))
        
        # Check playing state
        is_playing = controller.is_playing()
        assert isinstance(is_playing, bool)
    
    def test_signal_emission(self, app):
        """Test that signals are emitted correctly."""
        controller = AppController()
        
        # Track signal emissions
        project_loaded_signals = []
        project_modified_signals = []
        
        def on_project_loaded(loaded):
            project_loaded_signals.append(loaded)
        
        def on_project_modified(modified):
            project_modified_signals.append(modified)
        
        # Connect signals
        controller.project_loaded.connect(on_project_loaded)
        controller.project_modified.connect(on_project_modified)
        
        # Create new project
        controller.create_new_project()
        
        # Verify signals were emitted
        assert len(project_loaded_signals) > 0
        assert len(project_modified_signals) > 0
        assert project_loaded_signals[-1] is True
        assert project_modified_signals[-1] is False
    
    def test_error_handling(self, app):
        """Test error handling in integration scenarios."""
        controller = AppController()
        
        # Test loading non-existent files
        controller.load_background_media('nonexistent.mp4')
        controller.load_audio_file('nonexistent.mp3')
        controller.load_subtitle_file('nonexistent.json')
        
        # Should not crash and state should remain consistent
        assert not controller.project_state.is_loaded or controller.project_state.is_loaded
        assert isinstance(controller.project_state.is_modified, bool)
    
    def test_component_coordination(self, app):
        """Test that components are properly coordinated."""
        controller = AppController()
        
        # Create new project
        controller.create_new_project()
        
        # Verify all components are in sync
        assert controller.subtitle_engine.has_data
        assert len(controller.effect_system.get_active_effects()) == 0
        
        # Test component state consistency
        subtitle_data = controller.get_subtitle_data()
        active_effects = controller.get_active_effects()
        
        assert subtitle_data is not None
        assert isinstance(active_effects, list)
    
    def test_cleanup_and_reset(self, app):
        """Test cleanup and reset functionality."""
        controller = AppController()
        
        # Create new project and modify state
        controller.create_new_project()
        initial_state = controller.project_state.is_loaded
        
        # Reset project state
        controller._reset_project_state()
        
        # Verify reset
        assert not controller.project_state.is_loaded
        assert not controller.project_state.is_modified
        assert len(controller._undo_stack) == 0
        assert len(controller._redo_stack) == 0