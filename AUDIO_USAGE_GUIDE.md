
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
