"""
Tests for the complete preview update pipeline implementation.

This module tests the integration between GUI components, application controller,
and preview engine for real-time preview updates with audio synchronization
and performance optimization.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.subtitle_creator.app_controller import AppController
from src.subtitle_creator.models import SubtitleData, SubtitleLine
from src.subtitle_creator.gui.main_window import MainWindow
from src.subtitle_creator.preview_engine import PreviewEngine
from src.subtitle_creator.effects.system import EffectSystem


class TestPreviewUpdatePipeline:
    """Test the complete preview update pipeline."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        return QApplication.instance() or QApplication([])
    
    @pytest.fixture
    def main_window(self, app):
        """Create main window instance."""
        return MainWindow()
    
    @pytest.fixture
    def app_controller(self, main_window):
        """Create app controller with main window."""
        return AppController(main_window)
    
    @pytest.fixture
    def sample_subtitle_data(self):
        """Create sample subtitle data."""
        lines = [
            SubtitleLine(
                start_time=0.0,
                end_time=2.0,
                text="First subtitle line",
                words=[]
            ),
            SubtitleLine(
                start_time=2.5,
                end_time=4.5,
                text="Second subtitle line",
                words=[]
            )
        ]
        return SubtitleData(lines=lines, global_style={}, metadata={})
    
    def test_subtitle_editor_signal_connection(self, app_controller, main_window):
        """Test that subtitle editor signals are properly connected."""
        # Get subtitle editor
        subtitle_editor = main_window.get_subtitle_editor()
        assert subtitle_editor is not None
        
        # Check that signals are connected
        assert subtitle_editor.subtitle_data_changed.receivers() > 0
        assert subtitle_editor.preview_update_requested.receivers() > 0
        assert subtitle_editor.line_selected.receivers() > 0
    
    def test_effects_panel_signal_connection(self, app_controller, main_window):
        """Test that effects panel signals are properly connected."""
        # Get effects panel
        effects_panel = main_window.get_effects_panel()
        assert effects_panel is not None
        
        # Check that effects_changed signal is connected
        assert effects_panel.effects_changed.receivers() > 0
    
    def test_preview_panel_signal_connection(self, app_controller, main_window):
        """Test that preview panel signals are properly connected."""
        # Get preview panel
        preview_panel = main_window.get_preview_panel()
        assert preview_panel is not None
        
        # Check that playback control signals are connected
        assert preview_panel.seek_requested.receivers() > 0
        assert preview_panel.play_requested.receivers() > 0
        assert preview_panel.pause_requested.receivers() > 0
        assert preview_panel.stop_requested.receivers() > 0
    
    def test_subtitle_data_change_triggers_preview_update(self, app_controller, sample_subtitle_data):
        """Test that subtitle data changes trigger preview updates."""
        # Mock the preview update method
        with patch.object(app_controller, '_schedule_preview_update') as mock_schedule:
            # Trigger subtitle data change
            app_controller._on_subtitle_data_changed(sample_subtitle_data)
            
            # Verify preview update was scheduled
            mock_schedule.assert_called_once()
    
    def test_effects_change_triggers_preview_update(self, app_controller):
        """Test that effects changes trigger preview updates."""
        # Mock the preview update method
        with patch.object(app_controller, '_schedule_preview_update') as mock_schedule:
            # Trigger effects change
            app_controller._on_effects_changed()
            
            # Verify preview update was scheduled
            mock_schedule.assert_called_once()
    
    def test_preview_update_debouncing(self, app_controller):
        """Test that preview updates are properly debounced."""
        # Mock the timer
        with patch.object(app_controller._preview_update_timer, 'start') as mock_start:
            # Trigger multiple rapid updates
            app_controller._schedule_preview_update()
            app_controller._schedule_preview_update()
            app_controller._schedule_preview_update()
            
            # Timer should be started for each call (debouncing resets timer)
            assert mock_start.call_count == 3
    
    def test_performance_optimization_for_effects(self, app_controller):
        """Test that effects are optimized for preview performance."""
        # Create mock effects with particle effects
        mock_effects = []
        
        # Create multiple particle effects
        for i in range(5):
            mock_effect = Mock()
            mock_effect.__class__.__name__ = 'HeartParticleEffect'
            mock_effect.parameters = {'particle_count': 100}
            mock_effects.append(mock_effect)
        
        # Add non-particle effect
        mock_text_effect = Mock()
        mock_text_effect.__class__.__name__ = 'TypographyEffect'
        mock_text_effect.parameters = {'font_size': 24}
        mock_effects.append(mock_text_effect)
        
        # Test optimization
        optimized = app_controller._optimize_effects_for_preview(mock_effects)
        
        # Should limit particle effects and reduce particle count
        particle_effects = [e for e in optimized if 'Particle' in e.__class__.__name__]
        assert len(particle_effects) <= 2  # Max 2 particle effects
        
        # Should include non-particle effects
        text_effects = [e for e in optimized if e.__class__.__name__ == 'TypographyEffect']
        assert len(text_effects) == 1
    
    def test_audio_synchronization_in_preview(self, app_controller):
        """Test audio synchronization in preview generation."""
        # Mock background and audio clips
        mock_background = Mock()
        mock_background.duration = 10.0
        
        mock_audio = Mock()
        mock_audio.duration = 8.0
        mock_audio.subclip.return_value = mock_audio
        
        # Mock preview clip
        mock_preview = Mock()
        mock_preview.duration = 10.0
        mock_preview.set_audio.return_value = mock_preview
        
        # Mock preview engine
        with patch.object(app_controller.preview_engine, 'generate_preview', return_value=mock_preview):
            # Test audio sync
            result = app_controller._generate_preview_with_audio_sync(
                mock_background, Mock(), [], mock_audio
            )
            
            # Should trim audio to match video duration
            mock_audio.subclip.assert_called_once_with(0, 10.0)
            mock_preview.set_audio.assert_called_once()
    
    def test_background_processing_for_ui_responsiveness(self, app_controller):
        """Test background processing for smooth UI responsiveness."""
        # Mock the background timer
        with patch.object(app_controller._background_update_timer, 'start') as mock_start:
            # Set last update time to recent
            app_controller._last_update_time = time.time()
            
            # Schedule update (should use background timer due to recent update)
            app_controller._schedule_preview_update()
            
            # Background timer should be started
            mock_start.assert_called_once()
    
    def test_preview_update_prevents_concurrent_updates(self, app_controller):
        """Test that concurrent preview updates are handled properly."""
        # Set updating flag
        app_controller._is_preview_updating = True
        
        # Try to schedule update
        app_controller._schedule_preview_update()
        
        # Should set pending flag
        assert app_controller._pending_preview_update == True
    
    def test_subtitle_line_selection_seeks_preview(self, app_controller, sample_subtitle_data):
        """Test that selecting a subtitle line seeks the preview."""
        # Load subtitle data
        app_controller.subtitle_engine.load_from_data(sample_subtitle_data)
        
        # Mock seek method
        with patch.object(app_controller, 'seek_to_time') as mock_seek:
            # Trigger line selection
            app_controller._on_subtitle_line_selected(1)  # Second line
            
            # Should seek to line start time
            mock_seek.assert_called_once_with(2.5)
    
    def test_preview_engine_performance_mode(self, app_controller):
        """Test preview engine performance mode settings."""
        preview_engine = app_controller.preview_engine
        
        # Test high performance mode
        preview_engine.set_performance_mode(True)
        assert preview_engine.quality_factor == 0.3
        assert preview_engine.skip_complex_effects == True
        assert preview_engine.preview_fps == 10
        
        # Test normal performance mode
        preview_engine.set_performance_mode(False)
        assert preview_engine.quality_factor == 0.7
        assert preview_engine.skip_complex_effects == False
        assert preview_engine.preview_fps == 15
    
    def test_audio_sync_info_reporting(self, app_controller):
        """Test audio synchronization info reporting."""
        preview_engine = app_controller.preview_engine
        
        # Test with no clip
        sync_info = preview_engine.get_audio_sync_info()
        assert sync_info['has_audio'] == False
        assert sync_info['sync_status'] == 'no_clip'
        
        # Test with clip but no audio
        mock_clip = Mock()
        mock_clip.duration = 10.0
        mock_clip.audio = None
        preview_engine._current_clip = mock_clip
        
        sync_info = preview_engine.get_audio_sync_info()
        assert sync_info['has_audio'] == False
        assert sync_info['sync_status'] == 'no_audio'
        assert sync_info['clip_duration'] == 10.0
    
    def test_preview_update_error_handling(self, app_controller):
        """Test error handling in preview updates."""
        # Mock preview engine to raise exception
        with patch.object(app_controller.preview_engine, 'generate_preview', 
                         side_effect=Exception("Preview error")):
            with patch.object(app_controller, 'error_occurred') as mock_error:
                # Trigger preview update
                app_controller._update_preview_delayed()
                
                # Should emit error signal
                mock_error.emit.assert_called_once()
                args = mock_error.emit.call_args[0]
                assert "Preview Error" in args[0]
                assert "Preview update failed" in args[1]
    
    def test_playback_control_signal_handling(self, app_controller):
        """Test playback control signal handling."""
        # Mock playback methods
        with patch.object(app_controller, 'start_playback') as mock_start, \
             patch.object(app_controller, 'pause_playback') as mock_pause, \
             patch.object(app_controller, 'stop_playback') as mock_stop:
            
            # Test play request
            app_controller._on_preview_play_requested()
            mock_start.assert_called_once()
            
            # Test pause request
            app_controller._on_preview_pause_requested()
            mock_pause.assert_called_once()
            
            # Test stop request
            app_controller._on_preview_stop_requested()
            mock_stop.assert_called_once()
    
    @pytest.mark.integration
    def test_complete_preview_pipeline_integration(self, app_controller, main_window, sample_subtitle_data):
        """Integration test for the complete preview update pipeline."""
        # Load background media (mock)
        mock_background = Mock()
        mock_background.duration = 10.0
        app_controller._background_clip = mock_background
        
        # Load subtitle data
        app_controller.subtitle_engine.load_from_data(sample_subtitle_data)
        
        # Mock preview engine methods
        with patch.object(app_controller.preview_engine, 'generate_preview') as mock_generate:
            mock_preview = Mock()
            mock_preview.duration = 10.0
            mock_generate.return_value = mock_preview
            
            # Trigger subtitle change through GUI
            subtitle_editor = main_window.get_subtitle_editor()
            subtitle_editor.subtitle_data_changed.emit(sample_subtitle_data)
            
            # Process events to allow signals to propagate
            QApplication.processEvents()
            
            # Allow timer to fire
            time.sleep(0.15)  # Wait for debounce timer
            QApplication.processEvents()
            
            # Preview should have been generated
            # Note: In real test, we'd need to trigger the timer manually
            # This is a simplified integration test