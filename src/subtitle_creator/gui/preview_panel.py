"""
Preview panel widget for video playback and timeline control.

This module provides the PreviewPanel widget that embeds video display,
timeline scrubber with playhead visualization, playback controls, and
keyboard shortcuts for common playback operations.
"""

import sys
from typing import Optional, Callable, Tuple
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton,
    QFrame, QSizePolicy, QSpacerItem, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QSize, QRect, QPoint
)
from PyQt6.QtGui import (
    QPainter, QPixmap, QImage, QPalette, QKeySequence, QShortcut,
    QFont, QFontMetrics, QPen, QBrush, QColor
)

# Optional imports for numpy - will be available when dependencies are installed
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from ..preview_engine import PreviewEngine
from ..interfaces import SubtitleData, Effect


class VideoDisplayWidget(QLabel):
    """
    Custom widget for displaying video frames with proper scaling and aspect ratio.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the video display widget."""
        super().__init__(parent)
        
        # Widget configuration
        self.setMinimumSize(320, 180)  # 16:9 aspect ratio minimum
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #444;
                border-radius: 4px;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)  # We'll handle scaling manually
        
        # Current frame data
        self._current_frame: Optional[np.ndarray] = None
        self._current_pixmap: Optional[QPixmap] = None
        
        # Display properties
        self.maintain_aspect_ratio = True
        self.background_color = QColor(26, 26, 26)
        
        # Show placeholder text initially
        self.setText("No video loaded")
        self.setStyleSheet(self.styleSheet() + """
            QLabel {
                color: #888;
                font-size: 14px;
            }
        """)
    
    def set_frame(self, frame: np.ndarray) -> None:
        """
        Set the current video frame to display.
        
        Args:
            frame: Video frame as numpy array (height, width, channels)
        """
        if not NUMPY_AVAILABLE or frame is None:
            return
        
        try:
            self._current_frame = frame
            
            # Convert numpy array to QImage
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # RGB format
                height, width, channels = frame.shape
                bytes_per_line = channels * width
                
                # Ensure frame is in correct format (uint8)
                if frame.dtype != np.uint8:
                    frame = (frame * 255).astype(np.uint8)
                
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
                )
            elif len(frame.shape) == 3 and frame.shape[2] == 4:
                # RGBA format
                height, width, channels = frame.shape
                bytes_per_line = channels * width
                
                if frame.dtype != np.uint8:
                    frame = (frame * 255).astype(np.uint8)
                
                q_image = QImage(
                    frame.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888
                )
            else:
                # Unsupported format
                print(f"Warning: Unsupported frame format: {frame.shape}")
                return
            
            # Convert to pixmap and scale
            pixmap = QPixmap.fromImage(q_image)
            self._current_pixmap = pixmap
            
            # Update display
            self._update_display()
            
        except Exception as e:
            print(f"Warning: Failed to set frame: {e}")
    
    def _update_display(self) -> None:
        """Update the displayed pixmap with proper scaling."""
        if self._current_pixmap is None:
            return
        
        # Calculate scaled size maintaining aspect ratio
        widget_size = self.size()
        pixmap_size = self._current_pixmap.size()
        
        if self.maintain_aspect_ratio:
            scaled_pixmap = self._current_pixmap.scaled(
                widget_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            scaled_pixmap = self._current_pixmap.scaled(
                widget_size,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        
        self.setPixmap(scaled_pixmap)
        self.setText("")  # Clear placeholder text
    
    def clear_frame(self) -> None:
        """Clear the current frame and show placeholder."""
        self._current_frame = None
        self._current_pixmap = None
        self.clear()
        self.setText("No video loaded")
    
    def resizeEvent(self, event) -> None:
        """Handle widget resize to update frame scaling."""
        super().resizeEvent(event)
        if self._current_pixmap is not None:
            self._update_display()


class TimelineSlider(QSlider):
    """
    Custom timeline slider with playhead visualization and time display.
    """
    
    # Signal emitted when user seeks to a specific time
    seek_requested = pyqtSignal(float)  # time in seconds
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the timeline slider."""
        super().__init__(Qt.Orientation.Horizontal, parent)
        
        # Slider configuration
        self.setMinimum(0)
        self.setMaximum(1000)  # Will be scaled to actual duration
        self.setValue(0)
        
        # Timeline properties
        self._duration: float = 0.0
        self._current_time: float = 0.0
        self._is_seeking: bool = False
        
        # Visual customization
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                border: 1px solid #2a5a8a;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5aa0f2, stop:1 #458acd);
            }
            
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3a80d2, stop:1 #2570ad);
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4a90e2, stop:1 #357abd);
                border: 1px solid #2a5a8a;
                height: 8px;
                border-radius: 4px;
            }
            
            QSlider::add-page:horizontal {
                background: #2a2a2a;
                border: 1px solid #555;
                height: 8px;
                border-radius: 4px;
            }
        """)
        
        # Connect signals
        self.sliderPressed.connect(self._on_slider_pressed)
        self.sliderReleased.connect(self._on_slider_released)
        self.valueChanged.connect(self._on_value_changed)
    
    def set_duration(self, duration: float) -> None:
        """
        Set the total duration of the timeline.
        
        Args:
            duration: Duration in seconds
        """
        self._duration = max(0.0, duration)
        self._update_slider_range()
    
    def set_current_time(self, time: float) -> None:
        """
        Set the current playback time.
        
        Args:
            time: Current time in seconds
        """
        if self._is_seeking:
            return  # Don't update during user seeking
        
        self._current_time = max(0.0, min(time, self._duration))
        self._update_slider_position()
    
    def get_current_time(self) -> float:
        """Get the current time in seconds."""
        return self._current_time
    
    def get_duration(self) -> float:
        """Get the total duration in seconds."""
        return self._duration
    
    def _update_slider_range(self) -> None:
        """Update slider range based on duration."""
        if self._duration > 0:
            # Use high resolution for smooth seeking
            self.setMaximum(int(self._duration * 100))  # 0.01 second precision
        else:
            self.setMaximum(1000)
    
    def _update_slider_position(self) -> None:
        """Update slider position based on current time."""
        if self._duration > 0:
            position = int((self._current_time / self._duration) * self.maximum())
            self.setValue(position)
    
    def _on_slider_pressed(self) -> None:
        """Handle slider press start."""
        self._is_seeking = True
    
    def _on_slider_released(self) -> None:
        """Handle slider release and emit seek signal."""
        self._is_seeking = False
        
        # Calculate time from slider position
        if self._duration > 0:
            time = (self.value() / self.maximum()) * self._duration
            self._current_time = time
            self.seek_requested.emit(time)
    
    def _on_value_changed(self, value: int) -> None:
        """Handle slider value change during seeking."""
        if self._is_seeking and self._duration > 0:
            # Update current time during seeking for immediate feedback
            time = (value / self.maximum()) * self._duration
            self._current_time = time
    
    def format_time(self, seconds: float) -> str:
        """
        Format time in seconds to MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"


class PreviewPanel(QWidget):
    """
    Preview panel widget with video display, timeline scrubber, and playback controls.
    
    Provides embedded video display, timeline scrubbing with playhead visualization,
    playback controls, keyboard shortcuts, and integration with PreviewEngine.
    """
    
    # Signals for playback control
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(float)  # time in seconds
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the preview panel."""
        super().__init__(parent)
        
        # Preview engine integration
        self.preview_engine: Optional[PreviewEngine] = None
        
        # Playback state
        self._is_playing: bool = False
        self._current_time: float = 0.0
        self._duration: float = 0.0
        
        # UI update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_playback_state)
        self.update_timer.setInterval(50)  # 20 FPS UI updates
        
        # Setup UI
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup the user interface layout and widgets."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Video display area
        self.video_display = VideoDisplayWidget()
        self.video_display.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.video_display)
        
        # Timeline and time display container
        timeline_container = QFrame()
        timeline_container.setFrameStyle(QFrame.Shape.StyledPanel)
        timeline_container.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setContentsMargins(8, 6, 8, 6)
        timeline_layout.setSpacing(4)
        
        # Time display
        time_layout = QHBoxLayout()
        
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        self.duration_label = QLabel("00:00")
        self.duration_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        
        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(QLabel("/"))
        time_layout.addWidget(self.duration_label)
        time_layout.addStretch()
        
        timeline_layout.addLayout(time_layout)
        
        # Timeline slider
        self.timeline_slider = TimelineSlider()
        self.timeline_slider.setMinimumHeight(20)
        timeline_layout.addWidget(self.timeline_slider)
        
        layout.addWidget(timeline_container)
        
        # Playback controls
        controls_container = QFrame()
        controls_container.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_container.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(8, 6, 8, 6)
        controls_layout.setSpacing(8)
        
        # Playback buttons
        button_style = """
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ccc;
                font-weight: bold;
                padding: 6px 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
                border-color: #444;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                border-color: #444;
                color: #666;
            }
        """
        
        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet(button_style)
        self.play_button.setToolTip("Play/Pause (Space)")
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(button_style)
        self.stop_button.setToolTip("Stop (Ctrl+.)")
        
        # Add buttons to layout
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addStretch()
        
        # Playback speed control (future enhancement)
        speed_label = QLabel("Speed: 1.0x")
        speed_label.setStyleSheet("color: #888; font-size: 11px;")
        controls_layout.addWidget(speed_label)
        
        layout.addWidget(controls_container)
        
        # Set layout proportions
        layout.setStretchFactor(self.video_display, 1)  # Video takes most space
        layout.setStretchFactor(timeline_container, 0)  # Timeline fixed height
        layout.setStretchFactor(controls_container, 0)  # Controls fixed height
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for playback control."""
        # Play/Pause - Space bar
        self.play_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.play_shortcut.activated.connect(self._toggle_play_pause)
        
        # Stop - Ctrl+.
        self.stop_shortcut = QShortcut(QKeySequence("Ctrl+."), self)
        self.stop_shortcut.activated.connect(self._handle_stop)
        
        # Seek shortcuts
        # Left arrow - seek backward 5 seconds
        self.seek_back_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self.seek_back_shortcut.activated.connect(lambda: self._seek_relative(-5.0))
        
        # Right arrow - seek forward 5 seconds
        self.seek_forward_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self.seek_forward_shortcut.activated.connect(lambda: self._seek_relative(5.0))
        
        # Shift+Left - seek backward 30 seconds
        self.seek_back_long_shortcut = QShortcut(QKeySequence("Shift+Left"), self)
        self.seek_back_long_shortcut.activated.connect(lambda: self._seek_relative(-30.0))
        
        # Shift+Right - seek forward 30 seconds
        self.seek_forward_long_shortcut = QShortcut(QKeySequence("Shift+Right"), self)
        self.seek_forward_long_shortcut.activated.connect(lambda: self._seek_relative(30.0))
        
        # Home - seek to beginning
        self.seek_start_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Home), self)
        self.seek_start_shortcut.activated.connect(lambda: self._seek_to_time(0.0))
        
        # End - seek to end
        self.seek_end_shortcut = QShortcut(QKeySequence(Qt.Key.Key_End), self)
        self.seek_end_shortcut.activated.connect(lambda: self._seek_to_time(self._duration))
    
    def _connect_signals(self) -> None:
        """Connect internal widget signals."""
        # Button connections
        self.play_button.clicked.connect(self._toggle_play_pause)
        self.stop_button.clicked.connect(self._handle_stop)
        
        # Timeline connections
        self.timeline_slider.seek_requested.connect(self._handle_seek)
    
    def set_preview_engine(self, engine: PreviewEngine) -> None:
        """
        Set the preview engine for video rendering and playback.
        
        Args:
            engine: PreviewEngine instance
        """
        # Disconnect from previous engine
        if self.preview_engine is not None:
            self.preview_engine.remove_frame_callback(self._on_frame_update)
            self.preview_engine.remove_time_callback(self._on_time_update)
        
        self.preview_engine = engine
        
        if engine is not None:
            # Connect to engine callbacks
            engine.add_frame_callback(self._on_frame_update)
            engine.add_time_callback(self._on_time_update)
            
            # Update duration
            duration = engine.get_duration()
            self.set_duration(duration)
    
    def _on_frame_update(self, frame: np.ndarray, time: float) -> None:
        """
        Handle frame updates from preview engine.
        
        Args:
            frame: Video frame array
            time: Current time in seconds
        """
        if NUMPY_AVAILABLE:
            self.video_display.set_frame(frame)
    
    def _on_time_update(self, time: float) -> None:
        """
        Handle time updates from preview engine.
        
        Args:
            time: Current time in seconds
        """
        self._current_time = time
        self.timeline_slider.set_current_time(time)
        self._update_time_display()
    
    def set_duration(self, duration: float) -> None:
        """
        Set the total duration of the video.
        
        Args:
            duration: Duration in seconds
        """
        self._duration = duration
        self.timeline_slider.set_duration(duration)
        self._update_time_display()
    
    def _update_time_display(self) -> None:
        """Update the time display labels."""
        current_text = self.timeline_slider.format_time(self._current_time)
        duration_text = self.timeline_slider.format_time(self._duration)
        
        self.current_time_label.setText(current_text)
        self.duration_label.setText(duration_text)
    
    def _toggle_play_pause(self) -> None:
        """Toggle between play and pause states."""
        if self._is_playing:
            self._handle_pause()
        else:
            self._handle_play()
    
    def _handle_play(self) -> None:
        """Handle play button press."""
        if self.preview_engine is None:
            return
        
        self._is_playing = True
        self.play_button.setText("Pause")
        self.update_timer.start()
        
        # Start playback from current time
        self.preview_engine.start_playback(self._current_time)
        self.play_requested.emit()
    
    def _handle_pause(self) -> None:
        """Handle pause button press."""
        if self.preview_engine is None:
            return
        
        self._is_playing = False
        self.play_button.setText("Play")
        self.update_timer.stop()
        
        self.preview_engine.pause_playback()
        self.pause_requested.emit()
    
    def _handle_stop(self) -> None:
        """Handle stop button press."""
        if self.preview_engine is None:
            return
        
        self._is_playing = False
        self.play_button.setText("Play")
        self.update_timer.stop()
        
        # Stop playback and seek to beginning
        self.preview_engine.stop_playback()
        self._seek_to_time(0.0)
        self.stop_requested.emit()
    
    def _handle_seek(self, time: float) -> None:
        """
        Handle seek request from timeline slider.
        
        Args:
            time: Time to seek to in seconds
        """
        self._seek_to_time(time)
    
    def _seek_to_time(self, time: float) -> None:
        """
        Seek to a specific time.
        
        Args:
            time: Time in seconds
        """
        if self.preview_engine is None:
            return
        
        time = max(0.0, min(time, self._duration))
        self._current_time = time
        
        # Update UI immediately
        self.timeline_slider.set_current_time(time)
        self._update_time_display()
        
        # Seek in preview engine
        frame = self.preview_engine.seek_to_time(time)
        if frame is not None and NUMPY_AVAILABLE:
            self.video_display.set_frame(frame)
        
        self.seek_requested.emit(time)
    
    def _seek_relative(self, delta: float) -> None:
        """
        Seek relative to current time.
        
        Args:
            delta: Time delta in seconds (positive for forward, negative for backward)
        """
        new_time = self._current_time + delta
        self._seek_to_time(new_time)
    
    def _update_playback_state(self) -> None:
        """Update playback state from preview engine."""
        if self.preview_engine is None:
            return
        
        # Check if playback is still active
        engine_playing = self.preview_engine.is_playing()
        if self._is_playing and not engine_playing:
            # Playback ended
            self._handle_pause()
        
        # Update current time
        current_time = self.preview_engine.get_current_time()
        if abs(current_time - self._current_time) > 0.1:  # Avoid jitter
            self._current_time = current_time
            self.timeline_slider.set_current_time(current_time)
            self._update_time_display()
    
    def get_current_time(self) -> float:
        """Get current playback time."""
        return self._current_time
    
    def get_duration(self) -> float:
        """Get total duration."""
        return self._duration
    
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self._is_playing
    
    def clear_video(self) -> None:
        """Clear the video display and reset state."""
        self.video_display.clear_frame()
        self._current_time = 0.0
        self._duration = 0.0
        self._is_playing = False
        
        self.play_button.setText("Play")
        self.timeline_slider.set_duration(0.0)
        self.timeline_slider.set_current_time(0.0)
        self._update_time_display()
        
        if self.update_timer.isActive():
            self.update_timer.stop()
    
    def set_enabled_state(self, enabled: bool) -> None:
        """
        Enable or disable the preview panel controls.
        
        Args:
            enabled: True to enable controls, False to disable
        """
        self.play_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)
        self.timeline_slider.setEnabled(enabled)
        
        # Enable/disable keyboard shortcuts
        self.play_shortcut.setEnabled(enabled)
        self.stop_shortcut.setEnabled(enabled)
        self.seek_back_shortcut.setEnabled(enabled)
        self.seek_forward_shortcut.setEnabled(enabled)
        self.seek_back_long_shortcut.setEnabled(enabled)
        self.seek_forward_long_shortcut.setEnabled(enabled)
        self.seek_start_shortcut.setEnabled(enabled)
        self.seek_end_shortcut.setEnabled(enabled)