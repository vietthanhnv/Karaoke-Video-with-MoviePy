#!/usr/bin/env python3
"""
Preview Panel Demo

This demo shows the PreviewPanel widget functionality including:
- Video display widget with frame rendering
- Timeline scrubber with playhead visualization
- Playback controls (play/pause/stop/seek)
- Keyboard shortcuts for common operations
- Integration with PreviewEngine for real-time rendering

Usage:
    python examples/preview_panel_demo.py
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

# Optional imports for numpy - will be available when dependencies are installed
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from subtitle_creator.gui.preview_panel import PreviewPanel
from subtitle_creator.preview_engine import PreviewEngine
from subtitle_creator.models import SubtitleData, SubtitleLine


class PreviewPanelDemo(QMainWindow):
    """Demo application for PreviewPanel widget."""
    
    def __init__(self):
        """Initialize the demo application."""
        super().__init__()
        
        self.setWindowTitle("Preview Panel Demo")
        self.setGeometry(100, 100, 900, 700)
        
        # Create preview engine
        self.preview_engine = PreviewEngine(
            preview_resolution=(640, 360),
            preview_fps=15
        )
        
        # Setup demo properties first
        self.demo_time = 0.0
        self.demo_duration = 30.0  # 30 seconds demo
        self.demo_playing = False
        
        # Setup demo timer for simulated playback
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self._update_demo_playback)
        self.demo_timer.setInterval(100)  # 10 FPS updates
        
        # Setup UI
        self._setup_ui()
        
        # Create demo content
        self._create_demo_content()
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Preview Panel Demo")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "This demo shows the PreviewPanel widget with simulated video content.\n"
            "Use the controls below or keyboard shortcuts:\n"
            "• Space: Play/Pause\n"
            "• Left/Right arrows: Seek ±5 seconds\n"
            "• Shift+Left/Right: Seek ±30 seconds\n"
            "• Home/End: Go to start/end\n"
            "• Ctrl+.: Stop"
        )
        description.setStyleSheet("color: #666; font-size: 12px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        # Preview panel
        self.preview_panel = PreviewPanel()
        self.preview_panel.set_preview_engine(self.preview_engine)
        layout.addWidget(self.preview_panel)
        
        # Demo controls
        controls_layout = QHBoxLayout()
        
        self.start_demo_button = QPushButton("Start Demo Playback")
        self.start_demo_button.clicked.connect(self._start_demo)
        controls_layout.addWidget(self.start_demo_button)
        
        self.stop_demo_button = QPushButton("Stop Demo")
        self.stop_demo_button.clicked.connect(self._stop_demo)
        controls_layout.addWidget(self.stop_demo_button)
        
        controls_layout.addStretch()
        
        # Performance info
        self.perf_label = QLabel("Performance: Ready")
        self.perf_label.setStyleSheet("color: #888; font-size: 11px;")
        controls_layout.addWidget(self.perf_label)
        
        layout.addLayout(controls_layout)
        
        # Connect preview panel signals
        self.preview_panel.play_requested.connect(self._on_play_requested)
        self.preview_panel.pause_requested.connect(self._on_pause_requested)
        self.preview_panel.stop_requested.connect(self._on_stop_requested)
        self.preview_panel.seek_requested.connect(self._on_seek_requested)
        
        # Set layout proportions
        layout.setStretchFactor(title, 0)
        layout.setStretchFactor(description, 0)
        layout.setStretchFactor(self.preview_panel, 1)
        layout.setStretchFactor(controls_layout, 0)
    
    def _create_demo_content(self):
        """Create demo video content."""
        # Set duration
        self.preview_panel.set_duration(self.demo_duration)
        
        # Create initial frame
        self._generate_demo_frame(0.0)
        
        # Show performance stats
        self._update_performance_info()
    
    def _generate_demo_frame(self, time: float):
        """Generate a demo frame for the given time."""
        if not NUMPY_AVAILABLE:
            return
        
        # Create a colorful demo frame
        width, height = 640, 360
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create animated background
        t = time * 2  # Speed up animation
        
        # Gradient background
        for y in range(height):
            for x in range(width):
                r = int(128 + 127 * np.sin(t + x * 0.01))
                g = int(128 + 127 * np.sin(t + y * 0.01 + 2))
                b = int(128 + 127 * np.sin(t + (x + y) * 0.005 + 4))
                
                frame[y, x] = [max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))]
        
        # Add time indicator
        time_text_y = height // 2
        time_text_x = width // 2 - 50
        
        # Simple text rendering (just a white rectangle for demo)
        text_width = 100
        text_height = 20
        frame[time_text_y:time_text_y+text_height, time_text_x:time_text_x+text_width] = [255, 255, 255]
        
        # Add progress bar
        progress = time / self.demo_duration
        bar_width = int(width * 0.8)
        bar_height = 10
        bar_x = (width - bar_width) // 2
        bar_y = height - 50
        
        # Background bar
        frame[bar_y:bar_y+bar_height, bar_x:bar_x+bar_width] = [64, 64, 64]
        
        # Progress bar
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            frame[bar_y:bar_y+bar_height, bar_x:bar_x+progress_width] = [100, 200, 100]
        
        # Set frame in video display
        self.preview_panel.video_display.set_frame(frame)
    
    def _start_demo(self):
        """Start demo playback."""
        self.demo_playing = True
        self.demo_timer.start()
        self.start_demo_button.setEnabled(False)
        self.stop_demo_button.setEnabled(True)
        
        # Update preview panel state
        self.preview_panel._is_playing = True
        self.preview_panel.play_button.setText("Pause")
        self.preview_panel.update_timer.start()
    
    def _stop_demo(self):
        """Stop demo playback."""
        self.demo_playing = False
        self.demo_timer.stop()
        self.demo_time = 0.0
        
        self.start_demo_button.setEnabled(True)
        self.stop_demo_button.setEnabled(False)
        
        # Update preview panel state
        self.preview_panel._is_playing = False
        self.preview_panel.play_button.setText("Play")
        self.preview_panel.update_timer.stop()
        
        # Reset to beginning
        self.preview_panel._current_time = 0.0
        self.preview_panel.timeline_slider.set_current_time(0.0)
        self.preview_panel._update_time_display()
        self._generate_demo_frame(0.0)
    
    def _update_demo_playback(self):
        """Update demo playback state."""
        if not self.demo_playing:
            return
        
        # Advance time
        self.demo_time += 0.1  # 100ms increment
        
        if self.demo_time >= self.demo_duration:
            # End of demo
            self._stop_demo()
            return
        
        # Update preview panel
        self.preview_panel._current_time = self.demo_time
        self.preview_panel.timeline_slider.set_current_time(self.demo_time)
        self.preview_panel._update_time_display()
        
        # Generate new frame
        self._generate_demo_frame(self.demo_time)
        
        # Update performance info
        self._update_performance_info()
    
    def _update_performance_info(self):
        """Update performance information display."""
        if hasattr(self.preview_engine, 'get_performance_stats'):
            stats = self.preview_engine.get_performance_stats()
            avg_render_time = stats.get('average_render_time', 0.0)
            cache_size = stats.get('cache_info', {}).get('size', 0)
            
            self.perf_label.setText(
                f"Performance: {avg_render_time*1000:.1f}ms avg render, "
                f"{cache_size} cached frames"
            )
        else:
            self.perf_label.setText(f"Performance: Demo time {self.demo_time:.1f}s")
    
    def _on_play_requested(self):
        """Handle play request from preview panel."""
        if not self.demo_playing:
            self._start_demo()
        print(f"Play requested at time {self.preview_panel.get_current_time():.1f}s")
    
    def _on_pause_requested(self):
        """Handle pause request from preview panel."""
        self.demo_playing = False
        self.demo_timer.stop()
        print(f"Pause requested at time {self.preview_panel.get_current_time():.1f}s")
    
    def _on_stop_requested(self):
        """Handle stop request from preview panel."""
        self._stop_demo()
        print("Stop requested")
    
    def _on_seek_requested(self, time: float):
        """Handle seek request from preview panel."""
        self.demo_time = max(0.0, min(time, self.demo_duration))
        self._generate_demo_frame(self.demo_time)
        print(f"Seek requested to time {time:.1f}s")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self._stop_demo()
        event.accept()


def main():
    """Run the preview panel demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Preview Panel Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show demo window
    demo = PreviewPanelDemo()
    demo.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()