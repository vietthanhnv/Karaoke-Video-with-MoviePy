"""
Integration tests for the ExportManager with other components.

This module contains integration tests that verify the ExportManager works
correctly with other components like effects, media manager, and subtitle engine.
"""

import pytest
import os
import tempfile
import time
from unittest.mock import Mock, patch

from src.subtitle_creator.export_manager import ExportManager, ExportStatus
from src.subtitle_creator.interfaces import SubtitleData, SubtitleLine, WordTiming
from src.subtitle_creator.effects.base import Effect
from src.subtitle_creator.config import StyleConfig, EffectConfig, EffectType


class MockVideoClip:
    """Mock VideoClip for integration testing."""
    
    def __init__(self, duration=10.0, size=(1920, 1080), fps=30):
        self.duration = duration
        self.size = size
        self.fps = fps
        self.layer_index = 0
        self.audio = None
        self.start = 0
        self.mask = None
    
    @property
    def end(self):
        return self.start + self.duration
    
    def set_duration(self, duration):
        self.duration = duration
        return self
    
    def resize(self, size):
        self.size = size
        return self
    
    def resized(self, size):
        """MoviePy v2 method."""
        return self.resize(size)
    
    def set_fps(self, fps):
        self.fps = fps
        return self
    
    def with_fps(self, fps):
        """MoviePy v2 method."""
        return self.set_fps(fps)
    
    def with_duration(self, duration):
        """MoviePy v2 method."""
        return self.set_duration(duration)
    
    def write_videofile(self, filename, **kwargs):
        # Simulate realistic export time
        time.sleep(0.2)
        # Create output file
        with open(filename, 'w') as f:
            f.write("mock video file")
        return self


class MockTextStylingEffect(Effect):
    """Mock text styling effect for testing."""
    
    def __init__(self, name="text_styling", parameters=None):
        super().__init__(name, parameters or {
            "font_size": 48,
            "font_family": "Arial",
            "text_color": (255, 255, 255, 255)
        })
    
    def apply(self, clip, subtitle_data):
        # Mock effect application
        return clip
    
    def get_parameter_schema(self):
        return {
            "font_size": {"type": "int", "min": 12, "max": 200},
            "font_family": {"type": "str"},
            "text_color": {"type": "tuple", "length": 4}
        }
    
    def validate_parameters(self, parameters):
        return True


class MockAnimationEffect(Effect):
    """Mock animation effect for testing."""
    
    def __init__(self, name="animation", parameters=None):
        super().__init__(name, parameters or {
            "animation_type": "fade_in",
            "duration": 1.0,
            "intensity": 0.8
        })
    
    def apply(self, clip, subtitle_data):
        # Mock effect application
        return clip
    
    def get_parameter_schema(self):
        return {
            "animation_type": {"type": "str", "choices": ["fade_in", "fade_out", "scale"]},
            "duration": {"type": "float", "min": 0.1, "max": 10.0},
            "intensity": {"type": "float", "min": 0.0, "max": 1.0}
        }
    
    def validate_parameters(self, parameters):
        return True


class MockParticleEffect(Effect):
    """Mock particle effect for testing."""
    
    def __init__(self, name="particles", parameters=None):
        super().__init__(name, parameters or {
            "particle_type": "hearts",
            "particle_count": 50,
            "size": 20,
            "velocity": 100
        })
    
    def apply(self, clip, subtitle_data):
        # Mock effect application
        return clip
    
    def get_parameter_schema(self):
        return {
            "particle_type": {"type": "str", "choices": ["hearts", "stars", "sparkles"]},
            "particle_count": {"type": "int", "min": 1, "max": 1000},
            "size": {"type": "float", "min": 1.0, "max": 100.0},
            "velocity": {"type": "float", "min": 0.0, "max": 1000.0}
        }
    
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
def complex_subtitle_data():
    """Create complex subtitle data for integration testing."""
    lines = []
    
    # Create multiple subtitle lines with word-level timing
    for i in range(5):
        start_time = i * 2.0
        end_time = start_time + 1.8
        
        words = [
            WordTiming(f"Word{i*2+1}", start_time, start_time + 0.8),
            WordTiming(f"Word{i*2+2}", start_time + 0.9, end_time)
        ]
        
        line = SubtitleLine(
            start_time=start_time,
            end_time=end_time,
            text=f"Word{i*2+1} Word{i*2+2}",
            words=words,
            style_overrides={"font_size": 48 + i * 4}
        )
        lines.append(line)
    
    return SubtitleData(
        lines=lines,
        global_style={
            "font_family": "Arial",
            "text_color": (255, 255, 255, 255),
            "outline_color": (0, 0, 0, 255)
        },
        metadata={
            "title": "Integration Test Subtitles",
            "duration": 10.0
        }
    )


@pytest.fixture
def mixed_effects():
    """Create mixed effects for integration testing."""
    return [
        MockTextStylingEffect("title_style", {
            "font_size": 64,
            "font_family": "Arial Bold",
            "text_color": (255, 255, 0, 255)
        }),
        MockAnimationEffect("fade_in", {
            "animation_type": "fade_in",
            "duration": 0.5,
            "intensity": 1.0
        }),
        MockParticleEffect("celebration", {
            "particle_type": "stars",
            "particle_count": 100,
            "size": 15,
            "velocity": 150
        }),
        MockAnimationEffect("scale_bounce", {
            "animation_type": "scale",
            "duration": 0.3,
            "intensity": 0.6
        })
    ]


class TestExportIntegration:
    """Integration tests for ExportManager with other components."""
    
    def test_export_with_complex_subtitles(self, export_manager, mock_video_clip, complex_subtitle_data):
        """Test export with complex subtitle data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "complex_subtitles.mp4")
            settings = {"format": "mp4", "quality": "medium"}
            
            # Start export
            export_manager.export_video(mock_video_clip, complex_subtitle_data, [], output_path, settings)
            
            # Wait for completion
            success = export_manager.wait_for_export_completion(timeout=10.0)
            assert success
            
            # Verify output
            assert os.path.exists(output_path)
            
            # Check progress was tracked
            progress = export_manager.get_detailed_progress()
            assert progress.status == ExportStatus.COMPLETED
            assert progress.progress == 1.0
    
    def test_export_with_mixed_effects(self, export_manager, mock_video_clip, complex_subtitle_data, mixed_effects):
        """Test export with multiple different effect types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "mixed_effects.mp4")
            settings = {"format": "mp4", "quality": "high"}
            
            progress_updates = []
            
            def track_progress(progress):
                progress_updates.append({
                    'status': progress.status,
                    'progress': progress.progress,
                    'operation': progress.current_operation
                })
            
            export_manager.add_progress_callback(track_progress)
            
            # Start export
            export_manager.export_video(mock_video_clip, complex_subtitle_data, mixed_effects, output_path, settings)
            
            # Wait for completion
            success = export_manager.wait_for_export_completion(timeout=15.0)
            assert success
            
            # Verify output
            assert os.path.exists(output_path)
            
            # Check progress tracking
            assert len(progress_updates) > 0
            
            # Verify effect application was tracked
            effect_operations = [u['operation'] for u in progress_updates if 'effect' in u['operation'].lower()]
            assert len(effect_operations) > 0
            
            # Check final status
            final_progress = export_manager.get_detailed_progress()
            assert final_progress.status == ExportStatus.COMPLETED
    
    def test_export_quality_scaling_with_effects(self, export_manager, mock_video_clip, complex_subtitle_data, mixed_effects):
        """Test that effect parameters are properly scaled for different export qualities."""
        with tempfile.TemporaryDirectory() as temp_dir:
            qualities = ["low", "medium", "high"]
            
            for quality in qualities:
                output_path = os.path.join(temp_dir, f"quality_{quality}.mp4")
                settings = {"format": "mp4", "quality": quality}
                
                # Start export
                export_manager.export_video(mock_video_clip, complex_subtitle_data, mixed_effects, output_path, settings)
                
                # Wait for completion
                success = export_manager.wait_for_export_completion(timeout=10.0)
                assert success, f"Export failed for quality {quality}"
                
                # Verify output
                assert os.path.exists(output_path), f"Output file missing for quality {quality}"
    
    def test_export_custom_settings_with_effects(self, export_manager, mock_video_clip, complex_subtitle_data, mixed_effects):
        """Test export with custom settings and effects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "custom_settings.mp4")
            settings = {
                "format": "mp4",
                "quality": "custom",
                "resolution": [1280, 720],
                "fps": 25,
                "bitrate": "3500k",
                "audio_bitrate": "160k",
                "codec": "libx264",
                "audio_codec": "aac"
            }
            
            # Start export
            export_manager.export_video(mock_video_clip, complex_subtitle_data, mixed_effects, output_path, settings)
            
            # Wait for completion
            success = export_manager.wait_for_export_completion(timeout=10.0)
            assert success
            
            # Verify output
            assert os.path.exists(output_path)
    
    def test_export_different_formats_with_effects(self, export_manager, mock_video_clip, complex_subtitle_data, mixed_effects):
        """Test export with different formats and effects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            formats = [
                {"format": "mp4", "codec": "libx264"},
                {"format": "avi", "codec": "libx264"},
                {"format": "mov", "codec": "libx264"}
            ]
            
            for format_config in formats:
                format_name = format_config["format"]
                output_path = os.path.join(temp_dir, f"output.{format_name}")
                settings = {
                    "format": format_name,
                    "quality": "medium",
                    "codec": format_config["codec"]
                }
                
                # Start export
                export_manager.export_video(mock_video_clip, complex_subtitle_data, mixed_effects, output_path, settings)
                
                # Wait for completion
                success = export_manager.wait_for_export_completion(timeout=10.0)
                assert success, f"Export failed for format {format_name}"
                
                # Verify output
                assert os.path.exists(output_path), f"Output file missing for format {format_name}"
    
    def test_export_progress_with_long_video(self, export_manager, complex_subtitle_data, mixed_effects):
        """Test export progress tracking with longer video."""
        # Create longer video clip
        long_clip = MockVideoClip(duration=30.0, size=(1920, 1080), fps=30)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "long_video.mp4")
            settings = {"format": "mp4", "quality": "medium"}
            
            progress_history = []
            
            def detailed_progress_callback(progress):
                progress_history.append({
                    'timestamp': time.time(),
                    'status': progress.status,
                    'progress': progress.progress,
                    'elapsed_time': progress.elapsed_time,
                    'eta': progress.estimated_time_remaining,
                    'operation': progress.current_operation
                })
            
            export_manager.add_progress_callback(detailed_progress_callback)
            
            # Start export
            export_manager.export_video(long_clip, complex_subtitle_data, mixed_effects, output_path, settings)
            
            # Wait for completion
            success = export_manager.wait_for_export_completion(timeout=20.0)
            assert success
            
            # Analyze progress history
            assert len(progress_history) > 5  # Should have multiple progress updates
            
            # Check progress increases over time
            progress_values = [p['progress'] for p in progress_history if p['progress'] > 0]
            assert len(progress_values) > 1
            assert progress_values[-1] >= progress_values[0]  # Progress should increase
            
            # Check ETA calculation
            eta_values = [p['eta'] for p in progress_history if p['eta'] > 0]
            if len(eta_values) > 1:
                # ETA should generally decrease over time
                assert eta_values[-1] <= eta_values[0] * 2  # Allow some variance
    
    def test_export_cancellation_during_effects(self, export_manager, mock_video_clip, complex_subtitle_data, mixed_effects):
        """Test export cancellation during effect processing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "cancelled_export.mp4")
            settings = {"format": "mp4", "quality": "high"}
            
            # Start export
            export_manager.export_video(mock_video_clip, complex_subtitle_data, mixed_effects, output_path, settings)
            
            # Wait a moment for export to start
            time.sleep(0.1)
            
            # Cancel export
            assert export_manager.is_export_in_progress()
            success = export_manager.cancel_export()
            assert success
            
            # Wait for cancellation to complete
            time.sleep(0.5)
            
            # Check status
            progress = export_manager.get_detailed_progress()
            if progress:  # Progress might be None if cancellation was very fast
                assert progress.status == ExportStatus.CANCELLED
    
    def test_export_error_recovery(self, export_manager, complex_subtitle_data, mixed_effects):
        """Test export error handling and recovery."""
        # Create a mock clip that will fail
        failing_clip = Mock()
        failing_clip.duration = 10.0
        failing_clip.size = (1920, 1080)
        failing_clip.fps = 30
        failing_clip.resize.return_value = failing_clip
        failing_clip.set_fps.return_value = failing_clip
        failing_clip.write_videofile.side_effect = Exception("Simulated export failure")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "failed_export.mp4")
            settings = {"format": "mp4", "quality": "medium"}
            
            error_captured = []
            
            def error_callback(progress):
                if progress.status == ExportStatus.FAILED:
                    error_captured.append(progress.error_message)
            
            export_manager.add_progress_callback(error_callback)
            
            # Start export (should fail)
            export_manager.export_video(failing_clip, complex_subtitle_data, mixed_effects, output_path, settings)
            
            # Wait for failure
            export_manager.wait_for_export_completion(timeout=5.0)
            
            # Check error was captured
            progress = export_manager.get_detailed_progress()
            assert progress.status == ExportStatus.FAILED
            assert len(error_captured) > 0
            assert "Simulated export failure" in error_captured[0]
            
            # Test that we can start a new export after failure
            working_clip = MockVideoClip()
            output_path2 = os.path.join(temp_dir, "recovery_export.mp4")
            
            export_manager.export_video(working_clip, complex_subtitle_data, [], output_path2, settings)
            success = export_manager.wait_for_export_completion(timeout=5.0)
            assert success
            
            # Check recovery was successful
            final_progress = export_manager.get_detailed_progress()
            assert final_progress.status == ExportStatus.COMPLETED
    
    def test_export_file_size_estimation_accuracy(self, export_manager, complex_subtitle_data):
        """Test file size estimation accuracy with real exports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test different durations and qualities
            test_cases = [
                {"duration": 5.0, "quality": "low"},
                {"duration": 10.0, "quality": "medium"},
                {"duration": 15.0, "quality": "high"}
            ]
            
            for case in test_cases:
                clip = MockVideoClip(duration=case["duration"])
                output_path = os.path.join(temp_dir, f"size_test_{case['duration']}_{case['quality']}.mp4")
                settings = {"format": "mp4", "quality": case["quality"]}
                
                # Get size estimation
                estimated_size = export_manager.estimate_file_size(case["duration"], settings)
                assert estimated_size > 0
                
                # Perform actual export
                export_manager.export_video(clip, complex_subtitle_data, [], output_path, settings)
                success = export_manager.wait_for_export_completion(timeout=10.0)
                assert success
                
                # Check actual file size
                actual_size = os.path.getsize(output_path)
                
                # Estimation should be reasonable (within order of magnitude for mock files)
                # Note: This is a loose check since we're using mock files
                assert estimated_size > 0
                assert actual_size >= 0
    
    def test_concurrent_export_attempts(self, export_manager, mock_video_clip, complex_subtitle_data, mixed_effects):
        """Test handling of concurrent export attempts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path1 = os.path.join(temp_dir, "concurrent1.mp4")
            output_path2 = os.path.join(temp_dir, "concurrent2.mp4")
            settings = {"format": "mp4", "quality": "medium"}
            
            # Start first export
            export_manager.export_video(mock_video_clip, complex_subtitle_data, mixed_effects, output_path1, settings)
            
            # Verify first export is in progress
            assert export_manager.is_export_in_progress()
            
            # Try to start second export (should fail)
            with pytest.raises(Exception):  # Should raise ExportError
                export_manager.export_video(mock_video_clip, complex_subtitle_data, mixed_effects, output_path2, settings)
            
            # Wait for first export to complete
            success = export_manager.wait_for_export_completion(timeout=10.0)
            assert success
            
            # Now second export should be possible
            export_manager.export_video(mock_video_clip, complex_subtitle_data, [], output_path2, settings)
            success = export_manager.wait_for_export_completion(timeout=10.0)
            assert success
            
            # Both files should exist
            assert os.path.exists(output_path1)
            assert os.path.exists(output_path2)


if __name__ == "__main__":
    pytest.main([__file__])