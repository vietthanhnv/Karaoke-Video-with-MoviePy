"""
Integration tests for PreviewEngine with other system components.

This module tests the integration between PreviewEngine and other components
like MediaManager, EffectSystem, and SubtitleEngine.
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np

from src.subtitle_creator.preview_engine import PreviewEngine
from src.subtitle_creator.media_manager import MediaManager
from src.subtitle_creator.effects.system import EffectSystem
from src.subtitle_creator.effects.text_styling import TypographyEffect
from src.subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming


class TestPreviewEngineIntegration:
    """Integration tests for PreviewEngine with other components."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.preview_engine = PreviewEngine(
            preview_resolution=(640, 360),
            preview_fps=15
        )
        
        # Create test subtitle data
        self.subtitle_data = SubtitleData()
        self.subtitle_data.add_line(
            start_time=1.0,
            end_time=3.0,
            text="Test subtitle for preview",
            words=[
                WordTiming("Test", 1.0, 1.5),
                WordTiming("subtitle", 1.5, 2.0),
                WordTiming("for", 2.0, 2.3),
                WordTiming("preview", 2.3, 3.0)
            ]
        )
    
    @patch('src.subtitle_creator.preview_engine.MOVIEPY_AVAILABLE', True)
    def test_preview_with_media_manager_integration(self):
        """Test PreviewEngine integration with MediaManager."""
        # Mock MediaManager
        media_manager = Mock(spec=MediaManager)
        
        # Create mock background clip
        mock_background = Mock()
        mock_background.duration = 10.0
        mock_background.size = (1920, 1080)
        mock_background.fps = 24
        mock_background.resize.return_value = mock_background
        mock_background.set_fps.return_value = mock_background
        
        media_manager.load_background_media.return_value = mock_background
        
        # Test preview generation with media manager background
        background = media_manager.load_background_media("test_video.mp4")
        preview_clip = self.preview_engine.generate_preview(
            background, self.subtitle_data, []
        )
        
        assert preview_clip is not None
        media_manager.load_background_media.assert_called_once_with("test_video.mp4")
    
    def test_preview_with_effect_system_integration(self):
        """Test PreviewEngine integration with EffectSystem."""
        # Create effect system
        effect_system = EffectSystem()
        
        # Register and create a typography effect
        effect_system.register_effect(TypographyEffect)
        typography_effect = effect_system.create_effect(
            "TypographyEffect",
            {
                "font_family": "Arial",
                "font_size": 48,
                "text_color": (255, 255, 255, 255),
                "position": ("center", 0, 0)
            }
        )
        
        # Create mock background
        mock_background = Mock()
        mock_background.duration = 10.0
        mock_background.size = (640, 360)
        mock_background.fps = 15
        mock_background.resize.return_value = mock_background
        mock_background.set_fps.return_value = mock_background
        
        # Test preview generation with effects
        effects = [typography_effect]
        preview_clip = self.preview_engine.generate_preview(
            mock_background, self.subtitle_data, effects
        )
        
        assert preview_clip is not None
        # Effects are applied during preview generation, not stored in preview engine
    
    def test_preview_performance_optimization(self):
        """Test preview performance optimizations."""
        # Create mock background with high resolution
        mock_background = Mock()
        mock_background.duration = 30.0
        mock_background.size = (3840, 2160)  # 4K resolution
        mock_background.fps = 60
        
        # Mock resize method to return optimized clip
        optimized_background = Mock()
        optimized_background.duration = 30.0
        optimized_background.size = (640, 360)  # Preview resolution
        optimized_background.fps = 15
        optimized_background.set_fps.return_value = optimized_background
        
        mock_background.resize.return_value = optimized_background
        
        # Test that background is optimized for preview
        with patch('src.subtitle_creator.preview_engine.MOVIEPY_AVAILABLE', True):
            optimized = self.preview_engine._optimize_background_for_preview(mock_background)
            
            # Verify optimization was applied
            mock_background.resize.assert_called_once_with((640, 360))
            assert optimized == optimized_background
    
    def test_preview_with_complex_subtitle_timing(self):
        """Test preview with complex subtitle timing scenarios."""
        # Create subtitle data with overlapping word timings within lines
        complex_subtitle_data = SubtitleData()
        
        # Add line with precise word timing
        complex_subtitle_data.add_line(
            start_time=0.0,
            end_time=4.0,
            text="This is a complex subtitle line",
            words=[
                WordTiming("This", 0.0, 0.5),
                WordTiming("is", 0.5, 0.8),
                WordTiming("a", 0.8, 1.0),
                WordTiming("complex", 1.0, 1.8),
                WordTiming("subtitle", 1.8, 2.8),
                WordTiming("line", 2.8, 3.2)
            ]
        )
        
        # Add another line with different timing pattern
        complex_subtitle_data.add_line(
            start_time=5.0,
            end_time=8.0,
            text="With precise timing",
            words=[
                WordTiming("With", 5.0, 5.5),
                WordTiming("precise", 5.5, 6.5),
                WordTiming("timing", 6.5, 7.5)
            ]
        )
        
        # Create mock background
        mock_background = Mock()
        mock_background.duration = 10.0
        mock_background.size = (640, 360)
        mock_background.fps = 15
        mock_background.resize.return_value = mock_background
        mock_background.set_fps.return_value = mock_background
        
        # Test preview generation
        preview_clip = self.preview_engine.generate_preview(
            mock_background, complex_subtitle_data, []
        )
        
        assert preview_clip is not None
        
        # Test seeking to different subtitle timing points
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            # Seek to various points in subtitle timing
            seek_times = [0.5, 1.5, 2.5, 5.5, 6.5, 7.5]
            for seek_time in seek_times:
                frame = self.preview_engine.seek_to_time(seek_time)
                assert frame is not None
    
    def test_preview_callback_integration(self):
        """Test preview engine callbacks for UI integration."""
        frame_updates = []
        time_updates = []
        
        def frame_callback(frame, time):
            frame_updates.append((frame.shape if frame is not None else None, time))
        
        def time_callback(time):
            time_updates.append(time)
        
        # Register callbacks
        self.preview_engine.add_frame_callback(frame_callback)
        self.preview_engine.add_time_callback(time_callback)
        
        # Create mock background
        mock_background = Mock()
        mock_background.duration = 5.0
        mock_background.size = (640, 360)
        mock_background.fps = 15
        mock_background.resize.return_value = mock_background
        mock_background.set_fps.return_value = mock_background
        
        # Generate preview
        self.preview_engine.generate_preview(mock_background, self.subtitle_data, [])
        
        # Test seeking triggers callbacks
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            self.preview_engine.seek_to_time(2.5)
            
            # Verify callbacks were called
            assert len(time_updates) > 0
            assert 2.5 in time_updates
    
    def test_preview_error_recovery(self):
        """Test preview engine error recovery mechanisms."""
        # Create mock background that will cause errors
        failing_background = Mock()
        failing_background.duration = 10.0
        failing_background.size = (640, 360)
        failing_background.fps = 15
        failing_background.resize.side_effect = Exception("Resize failed")
        
        # Test that preview generation handles resize errors gracefully
        optimized = self.preview_engine._optimize_background_for_preview(failing_background)
        
        # Should return original background when optimization fails
        assert optimized == failing_background
    
    def test_preview_memory_management(self):
        """Test preview engine memory management."""
        # Create mock background
        mock_background = Mock()
        mock_background.duration = 60.0
        mock_background.size = (640, 360)
        mock_background.fps = 15
        mock_background.resize.return_value = mock_background
        mock_background.set_fps.return_value = mock_background
        
        # Generate preview
        self.preview_engine.generate_preview(mock_background, self.subtitle_data, [])
        
        # Fill frame cache
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            # Seek to many different times to fill cache
            for i in range(60):  # More than cache size
                self.preview_engine.seek_to_time(i * 1.0)
            
            # Verify cache size is limited
            cache_info = self.preview_engine.frame_cache.get_cache_info()
            assert cache_info['size'] <= self.preview_engine.frame_cache.max_size
        
        # Test cache clearing
        self.preview_engine.clear_cache()
        cache_info_after = self.preview_engine.frame_cache.get_cache_info()
        assert cache_info_after['size'] == 0
    
    def test_preview_quality_adaptation(self):
        """Test preview quality adaptation based on performance."""
        # Test different quality settings
        quality_levels = [0.2, 0.5, 0.8, 1.0]
        
        for quality in quality_levels:
            self.preview_engine.set_preview_quality(quality)
            assert self.preview_engine.quality_factor == quality
            
            # Test effect parameter adaptation
            mock_effect = Mock()
            mock_effect.parameters = {
                "particle_count": 100,
                "animation_steps": 50,
                "font_size": 48
            }
            
            preview_params = self.preview_engine._get_preview_effect_parameters(mock_effect)
            
            # Verify parameters are reduced for lower quality
            if quality < 1.0:
                assert preview_params["particle_count"] <= mock_effect.parameters["particle_count"]
                assert preview_params["animation_steps"] <= mock_effect.parameters["animation_steps"]
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'preview_engine'):
            self.preview_engine.stop_playback()
            self.preview_engine.clear_cache()


class TestPreviewEngineRealTimePerformance:
    """Test real-time performance characteristics of PreviewEngine."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.preview_engine = PreviewEngine(
            preview_resolution=(640, 360),
            preview_fps=15,
            cache_size=30
        )
    
    def test_frame_rate_consistency(self):
        """Test that preview maintains consistent frame rate."""
        # Create mock background
        mock_background = Mock()
        mock_background.duration = 10.0
        mock_background.size = (640, 360)
        mock_background.fps = 15
        mock_background.resize.return_value = mock_background
        mock_background.set_fps.return_value = mock_background
        
        # Generate preview
        subtitle_data = SubtitleData()
        subtitle_data.add_line(1.0, 3.0, "Test subtitle", [])
        
        self.preview_engine.generate_preview(mock_background, subtitle_data, [])
        
        # Test seeking performance
        import time
        seek_times = []
        
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            # Measure seek times
            for i in range(10):
                start_time = time.time()
                self.preview_engine.seek_to_time(i * 1.0)
                seek_time = time.time() - start_time
                seek_times.append(seek_time)
        
        # Verify seek times are reasonable for real-time playback
        average_seek_time = sum(seek_times) / len(seek_times)
        assert average_seek_time < 0.1  # Should seek in less than 100ms
        
        # Verify performance stats are tracked
        stats = self.preview_engine.get_performance_stats()
        assert stats['total_frames_rendered'] > 0
        assert stats['average_render_time'] >= 0
    
    def test_cache_hit_performance(self):
        """Test cache hit performance for smooth scrubbing."""
        # Create mock background
        mock_background = Mock()
        mock_background.duration = 10.0
        mock_background.size = (640, 360)
        mock_background.fps = 15
        mock_background.resize.return_value = mock_background
        mock_background.set_fps.return_value = mock_background
        
        subtitle_data = SubtitleData()
        subtitle_data.add_line(1.0, 3.0, "Test subtitle", [])
        
        self.preview_engine.generate_preview(mock_background, subtitle_data, [])
        
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            # First seek should render
            self.preview_engine.seek_to_time(5.0)
            first_render_count = mock_render.call_count
            
            # Second seek to same time should use cache
            self.preview_engine.seek_to_time(5.0)
            second_render_count = mock_render.call_count
            
            # Should not render again
            assert second_render_count == first_render_count
    
    def teardown_method(self):
        """Clean up after performance tests."""
        if hasattr(self, 'preview_engine'):
            self.preview_engine.stop_playback()
            self.preview_engine.clear_cache()