"""
Tests for the PreviewPanel widget.

This module tests the PreviewPanel widget functionality including video display,
timeline controls, playback controls, and keyboard shortcuts.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QKeySequence

from subtitle_creator.gui.preview_panel import PreviewPanel, VideoDisplayWidget, TimelineSlider
from subtitle_creator.preview_engine import PreviewEngine

# Mock numpy for testing
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@pytest.fixture
def app():
    """Create QApplication for testing."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def preview_panel(app):
    """Create PreviewPanel for testing."""
    panel = PreviewPanel()
    return panel


@pytest.fixture
def mock_preview_engine():
    """Create mock PreviewEngine for testing."""
    engine = Mock(spec=PreviewEngine)
    engine.get_duration.return_value = 120.0  # 2 minutes
    engine.get_current_time.return_value = 0.0
    engine.is_playing.return_value = False
    engine.seek_to_time.return_value = None
    return engine


class TestVideoDisplayWidget:
    """Test VideoDisplayWidget functionality."""
    
    def test_initialization(self, app):
        """Test VideoDisplayWidget initialization."""
        widget = VideoDisplayWidget()
        
        assert widget.text() == "No video loaded"
        assert widget.maintain_aspect_ratio is True
        assert widget.minimumSize().width() == 320
        assert widget.minimumSize().height() == 180
    
    def test_clear_frame(self, app):
        """Test clearing video frame."""
        widget = VideoDisplayWidget()
        widget.clear_frame()
        
        assert widget.text() == "No video loaded"
        assert widget._current_frame is None
        assert widget._current_pixmap is None
    
    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_set_frame_rgb(self, app):
        """Test setting RGB frame."""
        widget = VideoDisplayWidget()
        
        # Create test frame (RGB)
        frame = np.zeros((180, 320, 3), dtype=np.uint8)
        frame[:, :, 0] = 255  # Red channel
        
        widget.set_frame(frame)
        
        assert widget._current_frame is not None
        assert widget._current_pixmap is not None
        assert widget.text() == ""  # Placeholder text should be cleared
    
    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_set_frame_rgba(self, app):
        """Test setting RGBA frame."""
        widget = VideoDisplayWidget()
        
        # Create test frame (RGBA)
        frame = np.zeros((180, 320, 4), dtype=np.uint8)
        frame[:, :, 1] = 255  # Green channel
        frame[:, :, 3] = 255  # Alpha channel
        
        widget.set_frame(frame)
        
        assert widget._current_frame is not None
        assert widget._current_pixmap is not None


class TestTimelineSlider:
    """Test TimelineSlider functionality."""
    
    def test_initialization(self, app):
        """Test TimelineSlider initialization."""
        slider = TimelineSlider()
        
        assert slider.minimum() == 0
        assert slider.maximum() == 1000
        assert slider.value() == 0
        assert slider.get_duration() == 0.0
        assert slider.get_current_time() == 0.0
    
    def test_set_duration(self, app):
        """Test setting duration."""
        slider = TimelineSlider()
        slider.set_duration(120.0)  # 2 minutes
        
        assert slider.get_duration() == 120.0
        assert slider.maximum() == 12000  # 120 * 100
    
    def test_set_current_time(self, app):
        """Test setting current time."""
        slider = TimelineSlider()
        slider.set_duration(120.0)
        slider.set_current_time(60.0)  # 1 minute
        
        assert slider.get_current_time() == 60.0
        assert slider.value() == 6000  # 60 / 120 * 12000
    
    def test_format_time(self, app):
        """Test time formatting."""
        slider = TimelineSlider()
        
        assert slider.format_time(0) == "00:00"
        assert slider.format_time(65) == "01:05"
        assert slider.format_time(3661) == "61:01"
    
    def test_seek_signal(self, app):
        """Test seek signal emission."""
        slider = TimelineSlider()
        slider.set_duration(120.0)
        
        # Mock signal connection
        mock_slot = Mock()
        slider.seek_requested.connect(mock_slot)
        
        # Simulate slider press and release
        slider._on_slider_pressed()
        slider.setValue(6000)  # 60 seconds
        slider._on_slider_released()
        
        mock_slot.assert_called_once_with(60.0)


class TestPreviewPanel:
    """Test PreviewPanel functionality."""
    
    def test_initialization(self, preview_panel):
        """Test PreviewPanel initialization."""
        assert preview_panel.preview_engine is None
        assert preview_panel._is_playing is False
        assert preview_panel._current_time == 0.0
        assert preview_panel._duration == 0.0
        
        # Check UI components exist
        assert preview_panel.video_display is not None
        assert preview_panel.timeline_slider is not None
        assert preview_panel.play_button is not None
        assert preview_panel.stop_button is not None
        assert preview_panel.current_time_label is not None
        assert preview_panel.duration_label is not None
    
    def test_set_preview_engine(self, preview_panel, mock_preview_engine):
        """Test setting preview engine."""
        preview_panel.set_preview_engine(mock_preview_engine)
        
        assert preview_panel.preview_engine == mock_preview_engine
        mock_preview_engine.add_frame_callback.assert_called_once()
        mock_preview_engine.add_time_callback.assert_called_once()
        mock_preview_engine.get_duration.assert_called_once()
    
    def test_set_duration(self, preview_panel):
        """Test setting duration."""
        preview_panel.set_duration(120.0)
        
        assert preview_panel._duration == 120.0
        assert preview_panel.timeline_slider.get_duration() == 120.0
        assert preview_panel.duration_label.text() == "02:00"
    
    def test_playback_controls(self, preview_panel, mock_preview_engine):
        """Test playback control buttons."""
        preview_panel.set_preview_engine(mock_preview_engine)
        
        # Test play
        preview_panel._handle_play()
        assert preview_panel._is_playing is True
        assert preview_panel.play_button.text() == "Pause"
        mock_preview_engine.start_playback.assert_called_once()
        
        # Test pause
        preview_panel._handle_pause()
        assert preview_panel._is_playing is False
        assert preview_panel.play_button.text() == "Play"
        mock_preview_engine.pause_playback.assert_called_once()
        
        # Test stop
        preview_panel._handle_stop()
        assert preview_panel._is_playing is False
        assert preview_panel.play_button.text() == "Play"
        mock_preview_engine.stop_playback.assert_called_once()
    
    def test_seek_functionality(self, preview_panel, mock_preview_engine):
        """Test seeking functionality."""
        preview_panel.set_preview_engine(mock_preview_engine)
        preview_panel.set_duration(120.0)
        
        # Test seek to time
        preview_panel._seek_to_time(60.0)
        
        assert preview_panel._current_time == 60.0
        mock_preview_engine.seek_to_time.assert_called_with(60.0)
        assert preview_panel.current_time_label.text() == "01:00"
    
    def test_relative_seeking(self, preview_panel, mock_preview_engine):
        """Test relative seeking."""
        preview_panel.set_preview_engine(mock_preview_engine)
        preview_panel.set_duration(120.0)
        preview_panel._current_time = 30.0
        
        # Test forward seek
        preview_panel._seek_relative(5.0)
        mock_preview_engine.seek_to_time.assert_called_with(35.0)
        
        # Test backward seek
        preview_panel._seek_relative(-10.0)
        mock_preview_engine.seek_to_time.assert_called_with(25.0)
    
    def test_keyboard_shortcuts(self, preview_panel, mock_preview_engine):
        """Test keyboard shortcuts."""
        preview_panel.set_preview_engine(mock_preview_engine)
        preview_panel.set_duration(120.0)
        
        # Test space bar (play/pause) by activating shortcut directly
        preview_panel.play_shortcut.activated.emit()
        assert preview_panel._is_playing is True
        
        preview_panel.play_shortcut.activated.emit()
        assert preview_panel._is_playing is False
        
        # Test arrow keys (seeking) by activating shortcuts directly
        preview_panel._current_time = 30.0
        initial_time = preview_panel._current_time
        
        preview_panel.seek_forward_shortcut.activated.emit()
        mock_preview_engine.seek_to_time.assert_called_with(35.0)  # +5 seconds
        
        preview_panel.seek_back_shortcut.activated.emit()
        # Should be called with 30.0 (35 - 5) but we need to set current time first
        preview_panel._current_time = 35.0
        preview_panel.seek_back_shortcut.activated.emit()
        mock_preview_engine.seek_to_time.assert_called_with(30.0)  # -5 seconds
    
    def test_clear_video(self, preview_panel):
        """Test clearing video."""
        preview_panel.set_duration(120.0)
        preview_panel._current_time = 60.0
        preview_panel._is_playing = True
        
        preview_panel.clear_video()
        
        assert preview_panel._duration == 0.0
        assert preview_panel._current_time == 0.0
        assert preview_panel._is_playing is False
        assert preview_panel.play_button.text() == "Play"
        assert preview_panel.current_time_label.text() == "00:00"
        assert preview_panel.duration_label.text() == "00:00"
    
    def test_enabled_state(self, preview_panel):
        """Test enabling/disabling controls."""
        # Test disable
        preview_panel.set_enabled_state(False)
        assert not preview_panel.play_button.isEnabled()
        assert not preview_panel.stop_button.isEnabled()
        assert not preview_panel.timeline_slider.isEnabled()
        
        # Test enable
        preview_panel.set_enabled_state(True)
        assert preview_panel.play_button.isEnabled()
        assert preview_panel.stop_button.isEnabled()
        assert preview_panel.timeline_slider.isEnabled()
    
    def test_signal_emissions(self, preview_panel, mock_preview_engine):
        """Test signal emissions."""
        preview_panel.set_preview_engine(mock_preview_engine)
        
        # Mock signal connections
        play_mock = Mock()
        pause_mock = Mock()
        stop_mock = Mock()
        seek_mock = Mock()
        
        preview_panel.play_requested.connect(play_mock)
        preview_panel.pause_requested.connect(pause_mock)
        preview_panel.stop_requested.connect(stop_mock)
        preview_panel.seek_requested.connect(seek_mock)
        
        # Test signal emissions through button clicks
        preview_panel.play_button.clicked.emit()
        play_mock.assert_called_once()
        
        # Set playing state and test pause
        preview_panel._is_playing = True
        preview_panel.play_button.clicked.emit()
        pause_mock.assert_called_once()
        
        preview_panel.stop_button.clicked.emit()
        stop_mock.assert_called_once()
        
        # Reset mock to test seek signal separately
        seek_mock.reset_mock()
        preview_panel._seek_to_time(30.0)
        seek_mock.assert_called_once_with(30.0)
    
    @pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
    def test_frame_callback(self, preview_panel):
        """Test frame update callback."""
        # Create test frame
        frame = np.zeros((180, 320, 3), dtype=np.uint8)
        
        # Call frame callback
        preview_panel._on_frame_update(frame, 30.0)
        
        # Check that video display was updated
        assert preview_panel.video_display._current_frame is not None
    
    def test_time_callback(self, preview_panel):
        """Test time update callback."""
        preview_panel.set_duration(120.0)
        
        # Call time callback
        preview_panel._on_time_update(45.0)
        
        assert preview_panel._current_time == 45.0
        assert preview_panel.current_time_label.text() == "00:45"
    
    def test_update_playback_state(self, preview_panel, mock_preview_engine):
        """Test playback state updates."""
        preview_panel.set_preview_engine(mock_preview_engine)
        preview_panel._is_playing = True
        
        # Simulate playback ending
        mock_preview_engine.is_playing.return_value = False
        mock_preview_engine.get_current_time.return_value = 120.0
        
        preview_panel._update_playback_state()
        
        assert preview_panel._is_playing is False
        assert preview_panel.play_button.text() == "Play"


if __name__ == "__main__":
    pytest.main([__file__])