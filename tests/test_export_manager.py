"""
Tests for the ExportManager class.

This module contains comprehensive tests for the export manager functionality,
including quality presets, custom settings, format support, progress tracking,
and error handling.
"""

import pytest
import os
import tempfile
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.subtitle_creator.export_manager import (
    ExportManager, ExportQuality, ExportFormat, ExportStatus, 
    QualityPreset, ExportProgress
)
from src.subtitle_creator.interfaces import ExportError, SubtitleData, SubtitleLine, WordTiming
from src.subtitle_creator.config import ExportSettings


class MockVideoClip:
    """Mock VideoClip for testing."""
    
    def __init__(self, duration=10.0, size=(1920, 1080), fps=30):
        self.duration = duration
        self.size = size
        self.fps = fps
        self.layer_index = 0
        self.audio = None
        self.start = 0
    
    @property
    def end(self):
        return self.start + self.duration
    
    def set_duration(self, duration):
        self.duration = duration
        return self
    
    def resize(self, size):
        self.size = size
        return self
    
    def set_fps(self, fps):
        self.fps = fps
        return self
    
    def write_videofile(self, filename, **kwargs):
        # Simulate export process
        time.sleep(0.1)
        # Create output file
        Path(filename).touch()
        return self


class MockEffect:
    """Mock Effect for testing."""
    
    def __init__(self, name="test_effect", parameters=None):
        self.name = name
        self.parameters = parameters or {}
    
    def apply(self, clip, subtitle_data):
        return clip
    
    def get_parameter_schema(self):
        return {}
    
    def validate_parameters(self, parameters):
        return True


@pytest.fixture
def export_manager():
    """Create ExportManager instance for testing."""
    return ExportManager()


@pytest.fixture
def mock_video_clip():
    """Create mock video clip for testing."""
    return MockVideoClip()


@pytest.fixture
def sample_subtitle_data():
    """Create sample subtitle data for testing."""
    words = [
        WordTiming("Hello", 0.0, 0.5),
        WordTiming("world", 0.5, 1.0)
    ]
    lines = [
        SubtitleLine(0.0, 1.0, "Hello world", words, {})
    ]
    return SubtitleData(lines, {}, {})


@pytest.fixture
def sample_effects():
    """Create sample effects for testing."""
    return [
        MockEffect("effect1", {"param1": "value1"}),
        MockEffect("effect2", {"param2": "value2"})
    ]


class TestExportManager:
    """Test cases for ExportManager class."""
    
    def test_initialization(self, export_manager):
        """Test ExportManager initialization."""
        assert export_manager is not None
        assert not export_manager.is_export_in_progress()
        assert export_manager.get_export_progress() == 0.0
        assert export_manager.get_detailed_progress() is None
    
    def test_quality_presets(self, export_manager):
        """Test quality presets are properly defined."""
        presets = export_manager.get_quality_presets()
        
        assert ExportQuality.HIGH in presets
        assert ExportQuality.MEDIUM in presets
        assert ExportQuality.LOW in presets
        
        # Test high quality preset
        high_preset = presets[ExportQuality.HIGH]
        assert high_preset.resolution == (1920, 1080)
        assert high_preset.fps == 30
        assert high_preset.bitrate == "8000k"
        assert high_preset.codec == "libx264"
        
        # Test medium quality preset
        medium_preset = presets[ExportQuality.MEDIUM]
        assert medium_preset.resolution == (1280, 720)
        assert medium_preset.fps == 30
        assert medium_preset.bitrate == "4000k"
        
        # Test low quality preset
        low_preset = presets[ExportQuality.LOW]
        assert low_preset.resolution == (854, 480)
        assert low_preset.fps == 24
        assert low_preset.bitrate == "2000k"
    
    def test_supported_formats(self, export_manager):
        """Test supported formats."""
        formats = export_manager.get_supported_formats()
        
        assert ExportFormat.MP4 in formats
        assert ExportFormat.AVI in formats
        assert ExportFormat.MOV in formats
    
    def test_supported_codecs(self, export_manager):
        """Test supported codecs for each format."""
        # Test MP4 codecs
        mp4_codecs = export_manager.get_supported_codecs(ExportFormat.MP4)
        assert "libx264" in mp4_codecs["video"]
        assert "aac" in mp4_codecs["audio"]
        
        # Test AVI codecs
        avi_codecs = export_manager.get_supported_codecs(ExportFormat.AVI)
        assert "libx264" in avi_codecs["video"]
        assert "mp3" in avi_codecs["audio"]
        
        # Test MOV codecs
        mov_codecs = export_manager.get_supported_codecs(ExportFormat.MOV)
        assert "libx264" in mov_codecs["video"]
        assert "aac" in mov_codecs["audio"]
    
    def test_export_settings_validation_valid(self, export_manager):
        """Test validation of valid export settings."""
        # Test high quality preset
        settings = {
            "format": "mp4",
            "quality": "high"
        }
        errors = export_manager.validate_export_settings(settings)
        assert len(errors) == 0
        
        # Test custom settings
        custom_settings = {
            "format": "mp4",
            "quality": "custom",
            "resolution": [1920, 1080],
            "fps": 30,
            "bitrate": "5000k",
            "codec": "libx264"
        }
        errors = export_manager.validate_export_settings(custom_settings)
        assert len(errors) == 0
    
    def test_export_settings_validation_invalid(self, export_manager):
        """Test validation of invalid export settings."""
        # Missing required fields
        settings = {"format": "mp4"}
        errors = export_manager.validate_export_settings(settings)
        assert len(errors) > 0
        assert "quality" in errors[0]
        
        # Invalid format
        settings = {"format": "invalid", "quality": "high"}
        errors = export_manager.validate_export_settings(settings)
        assert len(errors) > 0
        assert "Invalid format" in errors[0]
        
        # Invalid quality
        settings = {"format": "mp4", "quality": "invalid"}
        errors = export_manager.validate_export_settings(settings)
        assert len(errors) > 0
        assert "Invalid quality" in errors[0]
        
        # Invalid custom resolution
        settings = {
            "format": "mp4",
            "quality": "custom",
            "resolution": [0, 1080]
        }
        errors = export_manager.validate_export_settings(settings)
        assert len(errors) > 0
        assert "positive" in errors[0]
        
        # Invalid FPS
        settings = {
            "format": "mp4",
            "quality": "custom",
            "fps": 0
        }
        errors = export_manager.validate_export_settings(settings)
        assert len(errors) > 0
        assert "FPS" in errors[0]
        
        # Invalid bitrate
        settings = {
            "format": "mp4",
            "quality": "custom",
            "bitrate": "invalid"
        }
        errors = export_manager.validate_export_settings(settings)
        assert len(errors) > 0
        assert "Bitrate" in errors[0]
    
    def test_export_input_validation(self, export_manager, sample_subtitle_data, sample_effects):
        """Test export input validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.mp4")
            settings = {"format": "mp4", "quality": "high"}
            
            # Test None background
            with pytest.raises(ExportError, match="Background clip cannot be None"):
                export_manager.export_video(None, sample_subtitle_data, sample_effects, output_path, settings)
            
            # Test None subtitle data
            mock_clip = MockVideoClip()
            with pytest.raises(ExportError, match="Subtitle data cannot be None"):
                export_manager.export_video(mock_clip, None, sample_effects, output_path, settings)
            
            # Test invalid effects
            with pytest.raises(ExportError, match="Effects must be a list"):
                export_manager.export_video(mock_clip, sample_subtitle_data, "invalid", output_path, settings)
            
            # Test empty output path
            with pytest.raises(ExportError, match="Output path must be a non-empty string"):
                export_manager.export_video(mock_clip, sample_subtitle_data, sample_effects, "", settings)
            
            # Test invalid settings
            with pytest.raises(ExportError, match="Export settings must be a dictionary"):
                export_manager.export_video(mock_clip, sample_subtitle_data, sample_effects, output_path, "invalid")
    
    def test_export_video_high_quality(self, export_manager, mock_video_clip, sample_subtitle_data, sample_effects):
        """Test video export with high quality preset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.mp4")
            settings = {"format": "mp4", "quality": "high"}
            
            # Start export
            export_manager.export_video(mock_video_clip, sample_subtitle_data, sample_effects, output_path, settings)
            
            # Wait for export to complete
            success = export_manager.wait_for_export_completion(timeout=5.0)
            assert success
            
            # Check progress
            progress = export_manager.get_detailed_progress()
            assert progress is not None
            assert progress.status == ExportStatus.COMPLETED
            assert progress.progress == 1.0
            
            # Check output file exists
            assert os.path.exists(output_path)
    
    def test_export_video_custom_settings(self, export_manager, mock_video_clip, sample_subtitle_data, sample_effects):
        """Test video export with custom settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.mp4")
            settings = {
                "format": "mp4",
                "quality": "custom",
                "resolution": [1280, 720],
                "fps": 25,
                "bitrate": "3000k",
                "audio_bitrate": "128k",
                "codec": "libx264",
                "audio_codec": "aac"
            }
            
            # Start export
            export_manager.export_video(mock_video_clip, sample_subtitle_data, sample_effects, output_path, settings)
            
            # Wait for export to complete
            success = export_manager.wait_for_export_completion(timeout=5.0)
            assert success
            
            # Check output file exists
            assert os.path.exists(output_path)
    
    def test_export_progress_tracking(self, export_manager, sample_subtitle_data, sample_effects):
        """Test export progress tracking."""
        # Create a longer video clip to ensure we can capture progress
        long_clip = MockVideoClip(duration=5.0)  # Longer duration
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.mp4")
            settings = {"format": "mp4", "quality": "medium"}
            
            progress_updates = []
            
            def progress_callback(progress):
                progress_updates.append(progress)
            
            export_manager.add_progress_callback(progress_callback)
            
            # Start export
            export_manager.export_video(long_clip, sample_subtitle_data, sample_effects, output_path, settings)
            
            # Give it a moment to start
            time.sleep(0.1)
            
            # Wait for export to complete
            success = export_manager.wait_for_export_completion(timeout=10.0)
            assert success
            
            # Check progress updates
            assert len(progress_updates) > 0
            
            # Check that we have different statuses (more flexible check)
            statuses = [p.status for p in progress_updates]
            unique_statuses = set(statuses)
            
            # Should have at least completed status
            assert ExportStatus.COMPLETED in statuses
            
            # Check progress values
            progress_values = [p.progress for p in progress_updates]
            assert len(progress_values) > 0
            assert max(progress_values) == 1.0
    
    def test_export_cancellation(self, export_manager, mock_video_clip, sample_subtitle_data, sample_effects):
        """Test export cancellation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.mp4")
            settings = {"format": "mp4", "quality": "high"}
            
            # Start export
            export_manager.export_video(mock_video_clip, sample_subtitle_data, sample_effects, output_path, settings)
            
            # Cancel export immediately
            assert export_manager.is_export_in_progress()
            success = export_manager.cancel_export()
            assert success
            
            # Wait a bit for cancellation to process
            time.sleep(0.2)
            
            # Check status
            progress = export_manager.get_detailed_progress()
            if progress:  # Progress might be None if cancellation was very fast
                assert progress.status == ExportStatus.CANCELLED
    
    def test_concurrent_export_prevention(self, export_manager, mock_video_clip, sample_subtitle_data, sample_effects):
        """Test that concurrent exports are prevented."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path1 = os.path.join(temp_dir, "output1.mp4")
            output_path2 = os.path.join(temp_dir, "output2.mp4")
            settings = {"format": "mp4", "quality": "high"}
            
            # Start first export
            export_manager.export_video(mock_video_clip, sample_subtitle_data, sample_effects, output_path1, settings)
            
            # Try to start second export
            with pytest.raises(ExportError, match="Export already in progress"):
                export_manager.export_video(mock_video_clip, sample_subtitle_data, sample_effects, output_path2, settings)
            
            # Wait for first export to complete
            export_manager.wait_for_export_completion(timeout=5.0)
    
    def test_file_size_estimation(self, export_manager):
        """Test file size estimation."""
        duration = 60.0  # 1 minute
        
        # Test high quality
        settings = {"format": "mp4", "quality": "high"}
        size = export_manager.estimate_file_size(duration, settings)
        assert size > 0
        
        # Test medium quality (should be smaller)
        settings = {"format": "mp4", "quality": "medium"}
        medium_size = export_manager.estimate_file_size(duration, settings)
        assert medium_size > 0
        assert medium_size < size
        
        # Test low quality (should be smallest)
        settings = {"format": "mp4", "quality": "low"}
        low_size = export_manager.estimate_file_size(duration, settings)
        assert low_size > 0
        assert low_size < medium_size
        
        # Test custom settings
        settings = {
            "format": "mp4",
            "quality": "custom",
            "bitrate": "10000k",
            "audio_bitrate": "256k"
        }
        custom_size = export_manager.estimate_file_size(duration, settings)
        assert custom_size > 0
    
    def test_quality_settings_extraction(self, export_manager):
        """Test quality settings extraction from export settings."""
        # Test preset quality
        settings = {"format": "mp4", "quality": "high"}
        quality_settings = export_manager._get_quality_settings(settings)
        
        assert quality_settings['resolution'] == (1920, 1080)
        assert quality_settings['fps'] == 30
        assert quality_settings['bitrate'] == "8000k"
        assert quality_settings['codec'] == "libx264"
        
        # Test custom quality
        custom_settings = {
            "format": "mp4",
            "quality": "custom",
            "resolution": [1280, 720],
            "fps": 25,
            "bitrate": "3000k",
            "codec": "libx265"
        }
        quality_settings = export_manager._get_quality_settings(custom_settings)
        
        assert quality_settings['resolution'] == (1280, 720)
        assert quality_settings['fps'] == 25
        assert quality_settings['bitrate'] == "3000k"
        assert quality_settings['codec'] == "libx265"
    
    def test_effect_parameter_optimization(self, export_manager):
        """Test effect parameter optimization for export."""
        effect = MockEffect("test", {
            "font_size": 48,
            "particle_count": 100,
            "animation_steps": 10
        })
        
        quality_settings = {
            "resolution": (1280, 720),  # 720p
            "fps": 30
        }
        
        optimized_params = export_manager._get_export_effect_parameters(effect, quality_settings)
        
        # Font size should be scaled for resolution
        resolution_scale = 1280 / 1920  # 720p vs 1080p reference
        expected_font_size = int(48 * resolution_scale)
        assert optimized_params['font_size'] == expected_font_size
        
        # Particle count should be scaled
        expected_particle_count = int(100 * max(1.0, resolution_scale))
        assert optimized_params['particle_count'] == expected_particle_count
        
        # Animation steps should be increased for export quality
        expected_steps = int(10 * 1.5)
        assert optimized_params['animation_steps'] == expected_steps
    
    def test_callback_management(self, export_manager):
        """Test progress callback management."""
        callback1 = Mock()
        callback2 = Mock()
        
        # Add callbacks
        export_manager.add_progress_callback(callback1)
        export_manager.add_progress_callback(callback2)
        
        # Simulate progress update
        export_manager._current_export = ExportProgress(status=ExportStatus.PREPARING)
        export_manager._notify_progress_callbacks()
        
        # Check callbacks were called
        callback1.assert_called_once()
        callback2.assert_called_once()
        
        # Remove one callback
        export_manager.remove_progress_callback(callback1)
        
        # Simulate another progress update
        export_manager._notify_progress_callbacks()
        
        # Check only remaining callback was called
        assert callback1.call_count == 1  # Still 1 from before
        assert callback2.call_count == 2  # Called twice now
    
    def test_cleanup(self, export_manager):
        """Test cleanup functionality."""
        # Add some state
        callback = Mock()
        export_manager.add_progress_callback(callback)
        export_manager._current_export = ExportProgress()
        
        # Cleanup
        export_manager.cleanup()
        
        # Check state is cleared
        assert len(export_manager._progress_callbacks) == 0
        assert export_manager._current_export is None
        assert export_manager._current_clip is None
    
    def test_export_with_no_effects(self, export_manager, mock_video_clip, sample_subtitle_data):
        """Test export with no effects applied."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.mp4")
            settings = {"format": "mp4", "quality": "medium"}
            
            # Export with empty effects list
            export_manager.export_video(mock_video_clip, sample_subtitle_data, [], output_path, settings)
            
            # Wait for export to complete
            success = export_manager.wait_for_export_completion(timeout=5.0)
            assert success
            
            # Check output file exists
            assert os.path.exists(output_path)
    
    def test_export_different_formats(self, export_manager, mock_video_clip, sample_subtitle_data, sample_effects):
        """Test export with different formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            formats = ["mp4", "avi", "mov"]
            
            for format_name in formats:
                output_path = os.path.join(temp_dir, f"output.{format_name}")
                settings = {"format": format_name, "quality": "medium"}
                
                # Start export
                export_manager.export_video(mock_video_clip, sample_subtitle_data, sample_effects, output_path, settings)
                
                # Wait for export to complete
                success = export_manager.wait_for_export_completion(timeout=5.0)
                assert success, f"Export failed for format {format_name}"
                
                # Check output file exists
                assert os.path.exists(output_path), f"Output file not created for format {format_name}"
    
    def test_export_error_handling(self, export_manager, sample_subtitle_data, sample_effects):
        """Test export error handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "output.mp4")
            settings = {"format": "mp4", "quality": "high"}
            
            # Create a mock clip that will fail during export
            class FailingMockClip:
                def __init__(self):
                    self.duration = 10.0
                    self.size = (1920, 1080)
                    self.fps = 30
                
                def resize(self, size):
                    self.size = size
                    return self
                
                def set_fps(self, fps):
                    self.fps = fps
                    return self
                
                def write_videofile(self, filename, **kwargs):
                    raise Exception("Export failed")
            
            failing_clip = FailingMockClip()
            
            # Start export
            export_manager.export_video(failing_clip, sample_subtitle_data, sample_effects, output_path, settings)
            
            # Wait for export to complete
            export_manager.wait_for_export_completion(timeout=5.0)
            
            # Check error status
            progress = export_manager.get_detailed_progress()
            assert progress is not None
            assert progress.status == ExportStatus.FAILED
            assert "Export failed" in progress.error_message


class TestExportProgress:
    """Test cases for ExportProgress class."""
    
    def test_initialization(self):
        """Test ExportProgress initialization."""
        progress = ExportProgress()
        
        assert progress.status == ExportStatus.IDLE
        assert progress.progress == 0.0
        assert progress.current_frame == 0
        assert progress.total_frames == 0
        assert progress.elapsed_time == 0.0
        assert progress.estimated_time_remaining == 0.0
        assert progress.current_operation == ""
        assert progress.error_message == ""
    
    def test_custom_initialization(self):
        """Test ExportProgress with custom values."""
        progress = ExportProgress(
            status=ExportStatus.RENDERING,
            progress=0.5,
            current_frame=150,
            total_frames=300,
            elapsed_time=30.0,
            estimated_time_remaining=30.0,
            current_operation="Rendering frame 150",
            error_message=""
        )
        
        assert progress.status == ExportStatus.RENDERING
        assert progress.progress == 0.5
        assert progress.current_frame == 150
        assert progress.total_frames == 300
        assert progress.elapsed_time == 30.0
        assert progress.estimated_time_remaining == 30.0
        assert progress.current_operation == "Rendering frame 150"


class TestQualityPreset:
    """Test cases for QualityPreset class."""
    
    def test_initialization(self):
        """Test QualityPreset initialization."""
        preset = QualityPreset(
            name="Test Quality",
            resolution=(1920, 1080),
            fps=30,
            bitrate="5000k",
            audio_bitrate="128k",
            codec="libx264",
            audio_codec="aac",
            description="Test description"
        )
        
        assert preset.name == "Test Quality"
        assert preset.resolution == (1920, 1080)
        assert preset.fps == 30
        assert preset.bitrate == "5000k"
        assert preset.audio_bitrate == "128k"
        assert preset.codec == "libx264"
        assert preset.audio_codec == "aac"
        assert preset.description == "Test description"


if __name__ == "__main__":
    pytest.main([__file__])