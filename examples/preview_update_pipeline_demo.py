#!/usr/bin/env python3
"""
Demo of the complete preview update pipeline implementation.

This demo shows how the preview update pipeline connects subtitle editing changes
to preview engine updates using Qt signals, integrates effect application with
real-time preview rendering, and implements performance optimization.
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer, pyqtSignal

from subtitle_creator.app_controller import AppController
from subtitle_creator.models import SubtitleData, SubtitleLine
from subtitle_creator.gui.main_window import MainWindow


class PreviewUpdatePipelineDemo(QMainWindow):
    """Demo window showing preview update pipeline functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preview Update Pipeline Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Status label
        self.status_label = QLabel("Preview Update Pipeline Demo")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Create app controller in test mode
        self.app_controller = AppController(test_mode=True)
        
        # Connect to app controller signals
        self.app_controller.preview_updated.connect(self.on_preview_updated)
        self.app_controller.status_message.connect(self.on_status_message)
        
        # Demo buttons
        self.create_demo_buttons(layout)
        
        # Create sample subtitle data
        self.create_sample_data()
        
        # Performance monitoring
        self.update_count = 0
        self.last_update_time = 0
        
        # Timer for demo updates
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.run_demo_cycle)
        
        self.log("Preview Update Pipeline Demo initialized")
    
    def create_demo_buttons(self, layout):
        """Create demo control buttons."""
        # Test subtitle data change
        btn_subtitle_change = QPushButton("Test Subtitle Data Change")
        btn_subtitle_change.clicked.connect(self.test_subtitle_data_change)
        layout.addWidget(btn_subtitle_change)
        
        # Test effects change
        btn_effects_change = QPushButton("Test Effects Change")
        btn_effects_change.clicked.connect(self.test_effects_change)
        layout.addWidget(btn_effects_change)
        
        # Test performance optimization
        btn_performance = QPushButton("Test Performance Optimization")
        btn_performance.clicked.connect(self.test_performance_optimization)
        layout.addWidget(btn_performance)
        
        # Test audio sync
        btn_audio_sync = QPushButton("Test Audio Sync Info")
        btn_audio_sync.clicked.connect(self.test_audio_sync)
        layout.addWidget(btn_audio_sync)
        
        # Test background processing
        btn_background = QPushButton("Test Background Processing")
        btn_background.clicked.connect(self.test_background_processing)
        layout.addWidget(btn_background)
        
        # Start continuous demo
        btn_start_demo = QPushButton("Start Continuous Demo")
        btn_start_demo.clicked.connect(self.start_continuous_demo)
        layout.addWidget(btn_start_demo)
        
        # Stop demo
        btn_stop_demo = QPushButton("Stop Demo")
        btn_stop_demo.clicked.connect(self.stop_demo)
        layout.addWidget(btn_stop_demo)
    
    def create_sample_data(self):
        """Create sample subtitle data for testing."""
        lines = [
            SubtitleLine(
                start_time=0.0,
                end_time=2.0,
                text="First subtitle line for testing",
                words=[]
            ),
            SubtitleLine(
                start_time=2.5,
                end_time=4.5,
                text="Second subtitle line with effects",
                words=[]
            ),
            SubtitleLine(
                start_time=5.0,
                end_time=7.0,
                text="Third line for performance testing",
                words=[]
            )
        ]
        self.sample_subtitle_data = SubtitleData(lines=lines, global_style={}, metadata={})
        self.log("Sample subtitle data created")
    
    def test_subtitle_data_change(self):
        """Test subtitle data change triggering preview update."""
        self.log("Testing subtitle data change...")
        
        # Modify subtitle data
        self.sample_subtitle_data.lines[0].text = f"Modified at {time.time():.2f}"
        
        # Trigger subtitle data change
        self.app_controller._on_subtitle_data_changed(self.sample_subtitle_data)
        
        self.log("Subtitle data change triggered")
    
    def test_effects_change(self):
        """Test effects change triggering preview update."""
        self.log("Testing effects change...")
        
        # Trigger effects change
        self.app_controller._on_effects_changed()
        
        self.log("Effects change triggered")
    
    def test_performance_optimization(self):
        """Test performance optimization for effects."""
        self.log("Testing performance optimization...")
        
        # Create mock effects
        from unittest.mock import Mock
        
        mock_effects = []
        # Add multiple particle effects
        for i in range(5):
            effect = Mock()
            effect.__class__.__name__ = 'HeartParticleEffect'
            effect.parameters = {'particle_count': 100}
            mock_effects.append(effect)
        
        # Add text effect
        text_effect = Mock()
        text_effect.__class__.__name__ = 'TypographyEffect'
        text_effect.parameters = {'font_size': 24}
        mock_effects.append(text_effect)
        
        # Test optimization
        optimized = self.app_controller._optimize_effects_for_preview(mock_effects)
        
        particle_count = len([e for e in optimized if 'Particle' in e.__class__.__name__])
        text_count = len([e for e in optimized if e.__class__.__name__ == 'TypographyEffect'])
        
        self.log(f"Original effects: {len(mock_effects)}, Optimized: {len(optimized)}")
        self.log(f"Particle effects limited to: {particle_count} (max 2)")
        self.log(f"Text effects preserved: {text_count}")
    
    def test_audio_sync(self):
        """Test audio synchronization info."""
        self.log("Testing audio sync info...")
        
        # Test performance modes
        preview_engine = self.app_controller.preview_engine
        
        # High performance mode
        preview_engine.set_performance_mode(True)
        self.log(f"High performance mode: quality={preview_engine.quality_factor}, fps={preview_engine.preview_fps}")
        
        # Normal mode
        preview_engine.set_performance_mode(False)
        self.log(f"Normal mode: quality={preview_engine.quality_factor}, fps={preview_engine.preview_fps}")
        
        # Audio sync info
        sync_info = preview_engine.get_audio_sync_info()
        self.log(f"Audio sync info: {sync_info}")
    
    def test_background_processing(self):
        """Test background processing for UI responsiveness."""
        self.log("Testing background processing...")
        
        # Set recent update time to trigger background processing
        self.app_controller._last_update_time = time.time()
        
        # Schedule multiple rapid updates
        for i in range(3):
            self.app_controller._schedule_preview_update()
            time.sleep(0.01)  # Small delay
        
        self.log("Background processing test completed")
    
    def start_continuous_demo(self):
        """Start continuous demo showing preview updates."""
        self.log("Starting continuous demo...")
        self.demo_timer.start(1000)  # Update every second
    
    def stop_demo(self):
        """Stop the continuous demo."""
        self.demo_timer.stop()
        self.log("Demo stopped")
    
    def run_demo_cycle(self):
        """Run one cycle of the demo."""
        cycle_type = self.update_count % 4
        
        if cycle_type == 0:
            self.test_subtitle_data_change()
        elif cycle_type == 1:
            self.test_effects_change()
        elif cycle_type == 2:
            self.test_performance_optimization()
        else:
            self.test_audio_sync()
        
        self.update_count += 1
        
        if self.update_count >= 20:  # Stop after 20 cycles
            self.stop_demo()
            self.log("Continuous demo completed")
    
    def on_preview_updated(self):
        """Handle preview updated signal."""
        current_time = time.time()
        if self.last_update_time > 0:
            delta = current_time - self.last_update_time
            self.log(f"Preview updated (Δt: {delta:.3f}s)")
        else:
            self.log("Preview updated")
        self.last_update_time = current_time
    
    def on_status_message(self, message: str, timeout: int):
        """Handle status message from app controller."""
        self.log(f"Status: {message}")
    
    def log(self, message: str):
        """Log a message to the status label."""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.status_label.setText(log_message)


def main():
    """Run the preview update pipeline demo."""
    app = QApplication(sys.argv)
    
    # Create and show demo window
    demo = PreviewUpdatePipelineDemo()
    demo.show()
    
    print("Preview Update Pipeline Demo")
    print("=" * 50)
    print("This demo shows the complete preview update pipeline:")
    print("- Subtitle editing changes trigger preview updates")
    print("- Effects changes trigger preview updates")
    print("- Performance optimization for complex effects")
    print("- Audio synchronization support")
    print("- Background processing for UI responsiveness")
    print("=" * 50)
    print("Use the buttons to test different aspects of the pipeline")
    print("Or start the continuous demo to see automatic updates")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()