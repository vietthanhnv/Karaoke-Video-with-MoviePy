#!/usr/bin/env python3
"""
Add audio playback functionality to the Subtitle Creator application.

This script demonstrates how to add audio preview/playback capabilities
to your existing application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def add_audio_playback_to_app_controller():
    """Add audio playback methods to the AppController class."""
    
    # Read the current app controller
    app_controller_path = "src/subtitle_creator/app_controller.py"
    
    # Audio playback methods to add
    audio_playback_methods = '''
    
    # Audio Playback Methods (Added for audio preview functionality)
    
    def preview_audio(self, start_time: float = 0.0, duration: float = 10.0) -> None:
        """
        Preview audio playback using MoviePy's built-in audio preview.
        
        Args:
            start_time: Start time in seconds (default: 0.0)
            duration: Duration to preview in seconds (default: 10.0)
        """
        if not self._audio_clip:
            self.status_message.emit("No audio loaded for preview", 2000)
            return
        
        try:
            # Calculate end time
            audio_duration = getattr(self._audio_clip, 'duration', 0)
            if audio_duration == 0:
                self.status_message.emit("Audio duration unknown", 2000)
                return
            
            end_time = min(start_time + duration, audio_duration)
            
            if start_time >= audio_duration:
                self.status_message.emit("Start time beyond audio duration", 2000)
                return
            
            # Create audio segment for preview
            if start_time > 0 or end_time < audio_duration:
                preview_clip = self._audio_clip.subclipped(start_time, end_time)
            else:
                preview_clip = self._audio_clip
            
            # Start audio preview in a separate thread to avoid blocking UI
            import threading
            
            def play_audio():
                try:
                    preview_clip.preview()
                except Exception as e:
                    print(f"Audio preview error: {e}")
            
            audio_thread = threading.Thread(target=play_audio, daemon=True)
            audio_thread.start()
            
            self.status_message.emit(f"Playing audio from {start_time:.1f}s to {end_time:.1f}s", 2000)
            
        except Exception as e:
            self.error_occurred.emit("Audio Preview Error", f"Failed to preview audio: {str(e)}")
    
    def stop_audio_preview(self) -> None:
        """
        Stop audio preview playback.
        Note: MoviePy's audio preview doesn't have a direct stop method,
        but this method can be extended to work with other audio libraries.
        """
        self.status_message.emit("Audio preview stopped", 1000)
    
    def get_audio_info(self) -> Dict[str, Any]:
        """
        Get information about the currently loaded audio.
        
        Returns:
            Dictionary with audio information or empty dict if no audio loaded
        """
        if not self._audio_clip:
            return {}
        
        try:
            info = {
                'has_audio': True,
                'duration': getattr(self._audio_clip, 'duration', 0),
                'sample_rate': getattr(self._audio_clip, 'fps', 0),
                'channels': getattr(self._audio_clip, 'nchannels', 0),
                'file_path': self.project_state.audio_file_path
            }
            return info
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return {'has_audio': False, 'error': str(e)}
'''
    
    print("Audio playback methods to add to AppController:")
    print("=" * 60)
    print(audio_playback_methods)
    print("=" * 60)
    
    return audio_playback_methods

def create_audio_test_gui():
    """Create a simple GUI test for audio playback."""
    
    gui_test_code = '''#!/usr/bin/env python3
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
'''
    
    return gui_test_code

def main():
    """Main function to demonstrate audio playback solutions."""
    print("Audio Playback Solutions for Subtitle Creator")
    print("=" * 50)
    
    print("\n1. The issue:")
    print("   Your application loads audio files but doesn't play them through speakers.")
    print("   The audio is only used for video synchronization during export.")
    
    print("\n2. The solution:")
    print("   Add audio preview functionality using MoviePy's built-in audio preview.")
    
    print("\n3. Methods to add:")
    add_audio_playback_to_app_controller()
    
    print("\n4. Creating a test GUI...")
    gui_code = create_audio_test_gui()
    
    # Write the test GUI to a file
    with open("audio_test_gui.py", "w") as f:
        f.write(gui_code)
    
    print("✓ Created audio_test_gui.py - run this to test audio playback")
    
    print("\n5. To integrate into your main application:")
    print("   - Add the audio playback methods to AppController")
    print("   - Add audio preview buttons to your GUI")
    print("   - Connect the buttons to the new audio methods")
    
    print("\n6. Quick test:")
    print("   Run: python audio_test_gui.py")
    print("   Then load an audio file and test playback")

if __name__ == "__main__":
    main()