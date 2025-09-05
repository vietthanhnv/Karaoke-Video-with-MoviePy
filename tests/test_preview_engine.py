"""
Tests for the PreviewEngine class.

This module contains unit tests for the preview engine functionality including
real-time rendering, frame caching, timeline scrubbing, and performance optimization.
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.subtitle_creator.preview_engine import PreviewEngine, FrameCache
from src.subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming
from src.subtitle_creator.effects.base import BaseEffect
from src.subtitle_creator.interfaces import EffectError


class MockVideoClip:
    """Mock VideoClip for testing."""
    
    def __init__(self, duration=10.0, size=(1920, 1080), fps=24):
        self.duration = duration
        self.size = size
        self.fps = fps
    
    def resize(self, new_size):
        mock_clip = MockVideoClip(self.duration, new_size, self.fps)
        return mock_clip
    
    def set_fps(self, new_fps):
        mock_clip = MockVideoClip(self.duration, self.size, new_fps)
        return mock_clip
    
    def get_frame(self, t):
        # Return a simple test frame
        return np.zeros((self.size[1], self.size[0], 3), dtype=np.uint8)


class MockEffect(BaseEffect):
    """Mock effect for testing."""
    
    def __init__(self, name="test_effect", parameters=None):
        if parameters is None:
            parameters = {"intensity": 1.0}
        super().__init__(name, parameters)
    
    def apply(self, clip, subtitle_data):
        # Return the original clip for testing
        return clip
    
    def get_parameter_schema(self):
        return {
            "intensity": {"type": "float", "min": 0.0, "max": 2.0, "default": 1.0}
        }
    
    def validate_parameters(self, parameters):
        return "intensity" in parameters and 0.0 <= parameters["intensity"] <= 2.0


class TestFrameCache:
    """Test cases for FrameCache class."""
    
    def test_frame_cache_initialization(self):
        """Test frame cache initialization."""
        cache = FrameCache(max_size=50)
        assert cache.max_size == 50
        assert len(cache._cache) == 0
        assert len(cache._access_order) == 0
    
    def test_store_and_get_frame(self):
        """Test storing and retrieving frames."""
        cache = FrameCache(max_size=10)
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Store frame
        cache.store_frame(1.0, test_frame)
        
        # Retrieve exact frame
        retrieved_frame = cache.get_frame(1.0)
        assert retrieved_frame is not None
        np.testing.assert_array_equal(retrieved_frame, test_frame)
    
    def test_frame_cache_tolerance(self):
        """Test frame retrieval with tolerance."""
        cache = FrameCache(max_size=10)
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Store frame at time 1.0
        cache.store_frame(1.0, test_frame)
        
        # Retrieve with tolerance
        retrieved_frame = cache.get_frame(1.05, tolerance=0.1)
        assert retrieved_frame is not None
        np.testing.assert_array_equal(retrieved_frame, test_frame)
        
        # Should not retrieve with smaller tolerance
        retrieved_frame = cache.get_frame(1.15, tolerance=0.1)
        assert retrieved_frame is None
    
    def test_frame_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = FrameCache(max_size=2)
        
        frame1 = np.ones((10, 10, 3), dtype=np.uint8)
        frame2 = np.ones((10, 10, 3), dtype=np.uint8) * 2
        frame3 = np.ones((10, 10, 3), dtype=np.uint8) * 3
        
        # Fill cache
        cache.store_frame(1.0, frame1)
        cache.store_frame(2.0, frame2)
        
        # Add third frame (should evict first)
        cache.store_frame(3.0, frame3)
        
        # First frame should be evicted
        assert cache.get_frame(1.0) is None
        assert cache.get_frame(2.0) is not None
        assert cache.get_frame(3.0) is not None
    
    def test_frame_cache_clear(self):
        """Test clearing frame cache."""
        cache = FrameCache(max_size=10)
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        cache.store_frame(1.0, test_frame)
        assert len(cache._cache) == 1
        
        cache.clear()
        assert len(cache._cache) == 0
        assert len(cache._access_order) == 0
    
    def test_frame_cache_info(self):
        """Test cache info retrieval."""
        cache = FrameCache(max_size=10)
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        cache.store_frame(1.0, test_frame)
        cache.store_frame(2.0, test_frame)
        
        info = cache.get_cache_info()
        assert info['size'] == 2
        assert info['max_size'] == 10
        assert 1.0 in info['cached_times']
        assert 2.0 in info['cached_times']
        assert info['memory_usage_mb'] > 0


class TestPreviewEngine:
    """Test cases for PreviewEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.preview_engine = PreviewEngine(
            preview_resolution=(640, 360),
            preview_fps=15,
            cache_size=50
        )
        
        # Create test subtitle data
        self.subtitle_data = SubtitleData()
        self.subtitle_data.add_line(
            start_time=1.0,
            end_time=3.0,
            text="Test subtitle line",
            words=[
                WordTiming("Test", 1.0, 1.5),
                WordTiming("subtitle", 1.5, 2.0),
                WordTiming("line", 2.0, 2.5)
            ]
        )
    
    def test_preview_engine_initialization(self):
        """Test preview engine initialization."""
        assert self.preview_engine.preview_resolution == (640, 360)
        assert self.preview_engine.preview_fps == 15
        assert self.preview_engine.quality_factor == 0.5
        assert not self.preview_engine.skip_complex_effects
        assert not self.preview_engine.is_playing()
        assert self.preview_engine.get_current_time() == 0.0
    
    @patch('src.subtitle_creator.preview_engine.MOVIEPY_AVAILABLE', True)
    def test_generate_preview_basic(self):
        """Test basic preview generation."""
        background = MockVideoClip(duration=10.0)
        effects = []
        
        with patch('src.subtitle_creator.preview_engine.CompositeVideoClip') as mock_composite:
            preview_clip = self.preview_engine.generate_preview(
                background, self.subtitle_data, effects
            )
            
            assert preview_clip is not None
            assert self.preview_engine._current_clip is not None
    
    @patch('src.subtitle_creator.preview_engine.MOVIEPY_AVAILABLE', True)
    def test_generate_preview_with_effects(self):
        """Test preview generation with effects."""
        background = MockVideoClip(duration=10.0)
        effects = [MockEffect("test_effect", {"intensity": 1.5})]
        
        with patch('src.subtitle_creator.preview_engine.CompositeVideoClip') as mock_composite:
            preview_clip = self.preview_engine.generate_preview(
                background, self.subtitle_data, effects
            )
            
            assert preview_clip is not None
            assert self.preview_engine._current_clip is not None
    
    def test_optimize_background_for_preview(self):
        """Test background optimization for preview."""
        background = MockVideoClip(duration=10.0, size=(1920, 1080))
        
        with patch('src.subtitle_creator.preview_engine.MOVIEPY_AVAILABLE', True):
            optimized = self.preview_engine._optimize_background_for_preview(background)
            assert optimized.size == (640, 360)  # Should be resized to preview resolution
    
    def test_filter_effects_for_preview(self):
        """Test effect filtering for preview."""
        # Create mock effects with different types
        simple_effect = MockEffect("simple_effect")
        
        # Mock a complex effect
        complex_effect = Mock()
        complex_effect.__class__.__name__ = "ParticleEffect"
        complex_effect.name = "complex_particle_effect"
        
        effects = [simple_effect, complex_effect]
        
        # Test with complex effects enabled
        self.preview_engine.skip_complex_effects = False
        filtered = self.preview_engine._filter_effects_for_preview(effects)
        assert len(filtered) == 2
        
        # Test with complex effects disabled
        self.preview_engine.skip_complex_effects = True
        filtered = self.preview_engine._filter_effects_for_preview(effects)
        assert len(filtered) == 1
        assert filtered[0] == simple_effect
    
    def test_get_preview_effect_parameters(self):
        """Test preview effect parameter modification."""
        effect = MockEffect("test_effect", {
            "intensity": 1.0,
            "particle_count": 100,
            "animation_steps": 50,
            "font_size": 48
        })
        
        preview_params = self.preview_engine._get_preview_effect_parameters(effect)
        
        # Check parameter modifications
        assert preview_params["particle_count"] == 30  # 100 * 0.3
        assert preview_params["animation_steps"] == 25  # 50 * 0.5
        assert preview_params["font_size"] < 48  # Should be scaled down
    
    @patch('src.subtitle_creator.preview_engine.MOVIEPY_AVAILABLE', True)
    def test_seek_to_time(self):
        """Test seeking to specific time."""
        background = MockVideoClip(duration=10.0)
        self.preview_engine._current_clip = background
        
        # Test seeking to valid time
        frame = self.preview_engine.seek_to_time(5.0)
        assert frame is not None
        assert self.preview_engine.get_current_time() == 5.0
        
        # Test seeking beyond duration (should clamp)
        frame = self.preview_engine.seek_to_time(15.0)
        assert self.preview_engine.get_current_time() == 10.0
        
        # Test seeking to negative time (should clamp)
        frame = self.preview_engine.seek_to_time(-1.0)
        assert self.preview_engine.get_current_time() == 0.0
    
    def test_seek_to_time_with_cache(self):
        """Test seeking with frame caching."""
        background = MockVideoClip(duration=10.0)
        self.preview_engine._current_clip = background
        
        # First seek should render and cache
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            frame1 = self.preview_engine.seek_to_time(5.0)
            assert mock_render.call_count == 1
            
            # Second seek to same time should use cache
            frame2 = self.preview_engine.seek_to_time(5.0)
            assert mock_render.call_count == 1  # Should not render again
            
            np.testing.assert_array_equal(frame1, frame2)
    
    def test_playback_control(self):
        """Test playback start/stop/pause/resume."""
        background = MockVideoClip(duration=10.0)
        self.preview_engine._current_clip = background
        
        # Test start playback
        assert not self.preview_engine.is_playing()
        self.preview_engine.start_playback(2.0)
        
        # Give playback thread time to start
        time.sleep(0.1)
        assert self.preview_engine.is_playing()
        assert self.preview_engine.get_current_time() >= 2.0
        
        # Test pause
        self.preview_engine.pause_playback()
        assert not self.preview_engine.is_playing()
        
        # Test resume
        self.preview_engine.resume_playback()
        assert self.preview_engine.is_playing()
        
        # Test stop
        self.preview_engine.stop_playback()
        assert not self.preview_engine.is_playing()
    
    def test_callbacks(self):
        """Test frame and time callbacks."""
        frame_callback_called = False
        time_callback_called = False
        
        def frame_callback(frame, time):
            nonlocal frame_callback_called
            frame_callback_called = True
        
        def time_callback(time):
            nonlocal time_callback_called
            time_callback_called = True
        
        # Add callbacks
        self.preview_engine.add_frame_callback(frame_callback)
        self.preview_engine.add_time_callback(time_callback)
        
        # Trigger callbacks
        test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
        self.preview_engine._notify_frame_callbacks(test_frame, 1.0)
        self.preview_engine._notify_time_callbacks(1.0)
        
        assert frame_callback_called
        assert time_callback_called
        
        # Test callback removal
        self.preview_engine.remove_frame_callback(frame_callback)
        self.preview_engine.remove_time_callback(time_callback)
        
        frame_callback_called = False
        time_callback_called = False
        
        self.preview_engine._notify_frame_callbacks(test_frame, 2.0)
        self.preview_engine._notify_time_callbacks(2.0)
        
        assert not frame_callback_called
        assert not time_callback_called
    
    def test_performance_monitoring(self):
        """Test performance statistics tracking."""
        # Record some render times
        self.preview_engine._record_render_time(0.1)
        self.preview_engine._record_render_time(0.2)
        self.preview_engine._record_render_time(0.15)
        
        stats = self.preview_engine.get_performance_stats()
        
        assert stats['total_frames_rendered'] == 3
        assert stats['average_render_time'] == 0.15
        assert stats['max_render_time'] == 0.2
        assert stats['min_render_time'] == 0.1
        assert stats['target_fps'] == 15
        assert stats['preview_resolution'] == (640, 360)
    
    def test_quality_settings(self):
        """Test preview quality settings."""
        # Test quality factor setting
        self.preview_engine.set_preview_quality(0.8)
        assert self.preview_engine.quality_factor == 0.8
        
        # Test clamping
        self.preview_engine.set_preview_quality(1.5)  # Should clamp to 1.0
        assert self.preview_engine.quality_factor == 1.0
        
        self.preview_engine.set_preview_quality(0.05)  # Should clamp to 0.1
        assert self.preview_engine.quality_factor == 0.1
        
        # Test skip complex effects setting
        self.preview_engine.set_skip_complex_effects(True)
        assert self.preview_engine.skip_complex_effects
        
        self.preview_engine.set_skip_complex_effects(False)
        assert not self.preview_engine.skip_complex_effects
    
    @patch('src.subtitle_creator.preview_engine.MOVIEPY_AVAILABLE', True)
    def test_create_preview_thumbnail(self):
        """Test thumbnail creation."""
        background = MockVideoClip(duration=10.0)
        self.preview_engine._current_clip = background
        
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            thumbnail = self.preview_engine.create_preview_thumbnail(5.0, (160, 90))
            assert thumbnail is not None
            mock_render.assert_called_once_with(5.0)
    
    def test_export_preview_frame(self):
        """Test frame export functionality."""
        background = MockVideoClip(duration=10.0)
        self.preview_engine._current_clip = background
        
        with patch.object(self.preview_engine, 'seek_to_time') as mock_seek:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_seek.return_value = test_frame
            
            # Test without MoviePy (fallback mode)
            result = self.preview_engine.export_preview_frame(5.0, "test_frame.png")
            assert result is True
            mock_seek.assert_called_once_with(5.0)
    
    def test_clear_cache(self):
        """Test cache clearing."""
        # Add some data to cache and performance stats
        self.preview_engine._record_render_time(0.1)
        test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
        self.preview_engine.frame_cache.store_frame(1.0, test_frame)
        
        assert len(self.preview_engine._render_times) > 0
        assert len(self.preview_engine.frame_cache._cache) > 0
        
        self.preview_engine.clear_cache()
        
        assert len(self.preview_engine._render_times) == 0
        assert len(self.preview_engine.frame_cache._cache) == 0
    
    def test_error_handling(self):
        """Test error handling in preview generation."""
        # Test with invalid background
        with pytest.raises(EffectError):
            self.preview_engine.generate_preview(None, self.subtitle_data, [])
        
        # Test with failing effect
        failing_effect = Mock()
        failing_effect.apply.side_effect = Exception("Effect failed")
        failing_effect.name = "failing_effect"
        
        background = MockVideoClip(duration=10.0)
        
        # Should not raise exception, but handle gracefully
        preview_clip = self.preview_engine.generate_preview(
            background, self.subtitle_data, [failing_effect]
        )
        assert preview_clip is not None
    
    def test_duration_and_clip_properties(self):
        """Test duration and clip property methods."""
        # Test with no clip
        assert self.preview_engine.get_duration() == 0.0
        
        # Test with clip
        background = MockVideoClip(duration=15.0)
        self.preview_engine._current_clip = background
        assert self.preview_engine.get_duration() == 15.0
    
    def test_thread_safety(self):
        """Test thread safety of preview engine operations."""
        background = MockVideoClip(duration=10.0)
        self.preview_engine._current_clip = background
        
        # Test concurrent seeking
        def seek_worker(times):
            for t in times:
                self.preview_engine.seek_to_time(t)
        
        times1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        times2 = [6.0, 7.0, 8.0, 9.0, 10.0]
        
        thread1 = threading.Thread(target=seek_worker, args=(times1,))
        thread2 = threading.Thread(target=seek_worker, args=(times2,))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Should complete without errors
        assert True
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'preview_engine'):
            self.preview_engine.stop_playback()
            self.preview_engine.clear_cache()


class TestPreviewEngineIntegration:
    """Integration tests for PreviewEngine with other components."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.preview_engine = PreviewEngine()
        
        # Create more complex subtitle data
        self.subtitle_data = SubtitleData()
        self.subtitle_data.add_line(
            start_time=0.0,
            end_time=2.0,
            text="First line of subtitles",
            words=[
                WordTiming("First", 0.0, 0.5),
                WordTiming("line", 0.5, 1.0),
                WordTiming("of", 1.0, 1.2),
                WordTiming("subtitles", 1.2, 2.0)
            ]
        )
        self.subtitle_data.add_line(
            start_time=3.0,
            end_time=5.0,
            text="Second line with effects",
            words=[
                WordTiming("Second", 3.0, 3.5),
                WordTiming("line", 3.5, 4.0),
                WordTiming("with", 4.0, 4.3),
                WordTiming("effects", 4.3, 5.0)
            ]
        )
    
    def test_preview_with_multiple_effects(self):
        """Test preview generation with multiple effects."""
        background = MockVideoClip(duration=10.0)
        
        effects = [
            MockEffect("effect1", {"intensity": 1.0}),
            MockEffect("effect2", {"intensity": 0.5}),
            MockEffect("effect3", {"intensity": 1.5})
        ]
        
        preview_clip = self.preview_engine.generate_preview(
            background, self.subtitle_data, effects
        )
        
        assert preview_clip is not None
        assert self.preview_engine._current_clip is not None
    
    def test_preview_performance_with_complex_subtitles(self):
        """Test preview performance with complex subtitle data."""
        background = MockVideoClip(duration=60.0)  # Longer clip
        
        # Create fresh subtitle data for this test to avoid overlaps
        test_subtitle_data = SubtitleData()
        
        # Add many subtitle lines with proper spacing
        for i in range(20):
            start_time = i * 3.0 + 5.0  # Start after existing subtitles
            end_time = start_time + 2.5
            test_subtitle_data.add_line(
                start_time=start_time,
                end_time=end_time,
                text=f"Subtitle line {i+1}",
                words=[
                    WordTiming(f"Subtitle", start_time, start_time + 0.8),
                    WordTiming(f"line", start_time + 0.8, start_time + 1.3),
                    WordTiming(f"{i+1}", start_time + 1.3, end_time)
                ]
            )
        
        effects = [MockEffect("performance_test", {"intensity": 1.0})]
        
        start_time = time.time()
        preview_clip = self.preview_engine.generate_preview(
            background, test_subtitle_data, effects
        )
        generation_time = time.time() - start_time
        
        assert preview_clip is not None
        assert generation_time < 5.0  # Should generate quickly
        
        # Test seeking performance
        seek_times = [5.0, 15.0, 25.0, 35.0, 45.0]
        start_time = time.time()
        
        with patch.object(self.preview_engine, '_render_frame_at_time') as mock_render:
            test_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            mock_render.return_value = test_frame
            
            for seek_time in seek_times:
                frame = self.preview_engine.seek_to_time(seek_time)
                assert frame is not None
        
        seek_time_total = time.time() - start_time
        assert seek_time_total < 2.0  # Should seek quickly
    
    def test_preview_memory_usage(self):
        """Test memory usage during preview operations."""
        background = MockVideoClip(duration=30.0)
        effects = [MockEffect("memory_test", {"intensity": 1.0})]
        
        # Generate preview
        preview_clip = self.preview_engine.generate_preview(
            background, self.subtitle_data, effects
        )
        
        # Perform many seek operations to fill cache
        for i in range(100):
            seek_time = (i / 100.0) * 30.0
            self.preview_engine.seek_to_time(seek_time)
        
        # Check cache info
        cache_info = self.preview_engine.frame_cache.get_cache_info()
        assert cache_info['size'] <= self.preview_engine.frame_cache.max_size
        
        # Clear cache and verify memory is freed
        self.preview_engine.clear_cache()
        cache_info_after = self.preview_engine.frame_cache.get_cache_info()
        assert cache_info_after['size'] == 0
        assert cache_info_after['memory_usage_mb'] == 0
    
    def teardown_method(self):
        """Clean up after integration tests."""
        if hasattr(self, 'preview_engine'):
            self.preview_engine.stop_playback()
            self.preview_engine.clear_cache()