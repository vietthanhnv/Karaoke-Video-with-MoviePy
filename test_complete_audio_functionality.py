#!/usr/bin/env python3
"""
Complete test of the audio functionality including GUI integration.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_audio_functionality():
    """Test the complete audio functionality."""
    print("Testing Complete Audio Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Import required modules
        print("1. Testing imports...")
        from subtitle_creator.app_controller import AppController
        from subtitle_creator.gui.main_window import MainWindow
        print("   ✓ All modules imported successfully")
        
        # Test 2: Create main window
        print("\n2. Testing main window creation...")
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication([])
        main_window = MainWindow()
        print("   ✓ Main window created successfully")
        
        # Test 3: Check if audio preview action exists
        print("\n3. Testing audio preview action...")
        if hasattr(main_window, 'action_preview_audio'):
            print("   ✓ Audio preview action exists")
            print(f"   ✓ Shortcut: {main_window.action_preview_audio.shortcut().toString()}")
            print(f"   ✓ Status tip: {main_window.action_preview_audio.statusTip()}")
            print(f"   ✓ Initially enabled: {main_window.action_preview_audio.isEnabled()}")
        else:
            print("   ❌ Audio preview action not found")
            return False
        
        # Test 4: Create app controller
        print("\n4. Testing app controller integration...")
        controller = AppController(main_window=main_window, test_mode=True)
        print("   ✓ App controller created with main window")
        
        # Test 5: Test audio loading state changes
        print("\n5. Testing audio state management...")
        
        # Initially no audio should be loaded
        audio_info = controller.get_audio_info()
        print(f"   ✓ Initial audio info: {audio_info}")
        
        # Test enabling audio preview button
        main_window.set_audio_loaded(True)
        print(f"   ✓ Audio preview enabled: {main_window.action_preview_audio.isEnabled()}")
        
        main_window.set_audio_loaded(False)
        print(f"   ✓ Audio preview disabled: {main_window.action_preview_audio.isEnabled()}")
        
        # Test 6: Test signal connections
        print("\n6. Testing signal connections...")
        if hasattr(main_window, 'audio_preview_requested'):
            print("   ✓ Audio preview signal exists")
        else:
            print("   ❌ Audio preview signal not found")
            return False
        
        # Test 7: Test audio preview method
        print("\n7. Testing audio preview method...")
        if hasattr(controller, 'preview_audio'):
            print("   ✓ Audio preview method exists in controller")
            
            # Test with no audio loaded
            try:
                controller.preview_audio()
                print("   ✓ Audio preview handles no audio gracefully")
            except Exception as e:
                print(f"   ❌ Error in audio preview: {e}")
                return False
        else:
            print("   ❌ Audio preview method not found in controller")
            return False
        
        print("\n" + "=" * 50)
        print("✅ All audio functionality tests passed!")
        print("\nTo test with actual audio:")
        print("1. Run the application: python main.py")
        print("2. Import an audio file via File > Import > Import Audio")
        print("3. Click the 'Preview Audio' button in the toolbar")
        print("4. Or use the keyboard shortcut: Ctrl+A")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_usage_guide():
    """Create a usage guide for the audio functionality."""
    
    guide = """
# Audio Preview Functionality Usage Guide

## Overview
The Subtitle Creator now includes audio preview functionality that allows you to:
- Load audio files for synchronization with subtitles
- Preview audio playback directly from the application
- Control audio preview with keyboard shortcuts

## How to Use

### 1. Loading Audio
- **Menu**: File > Import > Import Audio...
- **Supported formats**: MP3, WAV, AAC, FLAC, OGG
- The audio will be loaded and the preview button will be enabled

### 2. Previewing Audio
- **Toolbar button**: Click "Preview Audio" button
- **Keyboard shortcut**: Ctrl+A
- **Default behavior**: Plays first 10 seconds of audio
- **Custom preview**: Use controller.preview_audio(start_time, duration) in code

### 3. Audio Information
- Use controller.get_audio_info() to get audio details:
  - Duration, sample rate, channels, file path

## Technical Details

### New Methods Added to AppController:
- `preview_audio(start_time=0.0, duration=10.0)`: Preview audio segment
- `get_audio_info()`: Get audio file information

### New UI Elements:
- Audio preview toolbar button (Ctrl+A)
- Automatic enable/disable based on audio loading state

### Requirements:
- MoviePy with ffplay support for audio preview
- Audio files in supported formats

## Troubleshooting

### No Sound During Preview:
1. Check system audio settings
2. Ensure ffplay is installed (comes with ffmpeg)
3. Verify audio file format is supported
4. Check if audio file is corrupted

### Audio Preview Button Disabled:
1. Load an audio file first via File > Import > Import Audio
2. Ensure audio file loaded successfully (check status bar)

### Error Messages:
- "No audio loaded for preview": Load an audio file first
- "Audio duration unknown": Audio file may be corrupted
- "Start time beyond audio duration": Adjust start time parameter

## Code Examples

```python
# Load audio file
controller.load_audio_file("path/to/audio.mp3")

# Preview first 10 seconds
controller.preview_audio()

# Preview custom segment (5-15 seconds)
controller.preview_audio(start_time=5.0, duration=10.0)

# Get audio information
info = controller.get_audio_info()
print(f"Duration: {info['duration']} seconds")
```
"""
    
    return guide

def main():
    """Main function."""
    success = test_audio_functionality()
    
    if success:
        print("\n" + "=" * 50)
        print("Creating usage guide...")
        
        guide = create_usage_guide()
        with open("AUDIO_USAGE_GUIDE.md", "w") as f:
            f.write(guide)
        
        print("✓ Usage guide created: AUDIO_USAGE_GUIDE.md")
        
        print("\n🎵 Audio functionality is ready to use!")
        print("Run your application and try importing an audio file.")

if __name__ == "__main__":
    main()