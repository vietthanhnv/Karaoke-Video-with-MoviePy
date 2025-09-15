#!/usr/bin/env python3
"""
Simple GUI test for audio playback functionality.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QHBoxLayout, QWidget, QPushButton, QLabel, 
                            QFileDialog, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class AudioTestWindow(QMainWindow):
    """Simple window to test audio playback functionality."""
    
    def __init__(self):
        super().__init__()
        self.audio_clip = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Audio Playback Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No audio file selected")
        self.browse_button = QPushButton("Browse Audio File")
        self.browse_button.clicked.connect(self.browse_audio_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)
        
        # Playback controls
        controls_layout = QHBoxLayout()
        
        # Start time
        controls_layout.addWidget(QLabel("Start (s):"))
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0, 3600)
        self.start_time_spin.setValue(0)
        controls_layout.addWidget(self.start_time_spin)
        
        # Duration
        controls_layout.addWidget(QLabel("Duration (s):"))
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1, 60)
        self.duration_spin.setValue(10)
        controls_layout.addWidget(self.duration_spin)
        
        layout.addLayout(controls_layout)
        
        # Play button
        self.play_button = QPushButton("Play Audio Preview")
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setEnabled(False)
        layout.addWidget(self.play_button)
        
        # Info label
        self.info_label = QLabel("Load an audio file to test playback")
        layout.addWidget(self.info_label)
    
    def browse_audio_file(self):
        """Browse for an audio file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.aac *.m4a);;All Files (*)"
        )
        
        if file_path:
            self.load_audio_file(file_path)
    
    def load_audio_file(self, file_path):
        """Load an audio file."""
        try:
            from moviepy import AudioFileClip
            
            self.audio_clip = AudioFileClip(file_path)
            
            # Update UI
            self.file_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.play_button.setEnabled(True)
            
            # Update info
            duration = getattr(self.audio_clip, 'duration', 0)
            sample_rate = getattr(self.audio_clip, 'fps', 0)
            
            self.info_label.setText(
                f"Duration: {duration:.2f}s, Sample Rate: {sample_rate}Hz"
            )
            
            # Update start time range
            self.start_time_spin.setRange(0, max(0, duration - 1))
            
        except Exception as e:
            self.info_label.setText(f"Error loading audio: {e}")
            self.play_button.setEnabled(False)
    
    def play_audio(self):
        """Play audio preview."""
        if not self.audio_clip:
            return
        
        try:
            start_time = self.start_time_spin.value()
            duration = self.duration_spin.value()
            
            # Calculate end time
            audio_duration = getattr(self.audio_clip, 'duration', 0)
            end_time = min(start_time + duration, audio_duration)
            
            if start_time >= audio_duration:
                self.info_label.setText("Start time beyond audio duration")
                return
            
            # Create preview clip
            if start_time > 0 or end_time < audio_duration:
                preview_clip = self.audio_clip.subclipped(start_time, end_time)
            else:
                preview_clip = self.audio_clip
            
            # Play audio in separate thread
            import threading
            
            def play_audio_thread():
                try:
                    self.info_label.setText(f"Playing {start_time:.1f}s to {end_time:.1f}s...")
                    preview_clip.preview()
                    self.info_label.setText("Playback completed")
                except Exception as e:
                    self.info_label.setText(f"Playback error: {e}")
            
            audio_thread = threading.Thread(target=play_audio_thread, daemon=True)
            audio_thread.start()
            
        except Exception as e:
            self.info_label.setText(f"Error: {e}")

def main():
    """Run the audio test application."""
    app = QApplication(sys.argv)
    window = AudioTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
