#!/usr/bin/env python3
"""
Test audio playback functionality using MoviePy's built-in audio preview.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_audio_playback():
    """Test audio playback using MoviePy's audio preview functionality."""
    print("Testing audio playback...")
    print("=" * 50)
    
    try:
        # Import MoviePy audio components
        from moviepy import AudioFileClip
        print("✓ MoviePy imported successfully")
        
        # Test with a sample audio file (you'll need to provide one)
        audio_files = [
            "test_media.txt",  # This might not be audio
            # Add your audio file paths here
        ]
        
        # Look for audio files in examples directory
        examples_dir = "examples"
        if os.path.exists(examples_dir):
            for file in os.listdir(examples_dir):
                if file.lower().endswith(('.mp3', '.wav', '.ogg', '.aac', '.m4a')):
                    audio_files.append(os.path.join(examples_dir, file))
        
        # Look for audio files in current directory
        for file in os.listdir('.'):
            if file.lower().endswith(('.mp3', '.wav', '.ogg', '.aac', '.m4a')):
                audio_files.append(file)
        
        if not audio_files:
            print("❌ No audio files found to test")
            print("Please add an audio file (.mp3, .wav, etc.) to test playback")
            return
        
        for audio_path in audio_files:
            if not os.path.exists(audio_path):
                continue
                
            # Check if it's actually an audio file
            if not audio_path.lower().endswith(('.mp3', '.wav', '.ogg', '.aac', '.m4a')):
                continue
                
            print(f"\nTesting audio file: {audio_path}")
            
            try:
                # Load audio file
                audio_clip = AudioFileClip(audio_path)
                print(f"✓ Audio loaded successfully")
                print(f"  Duration: {audio_clip.duration:.2f} seconds")
                print(f"  Sample rate: {audio_clip.fps} Hz")
                
                # Test audio preview (this should play the audio)
                print("🔊 Starting audio preview (press Ctrl+C to stop)...")
                print("   If you don't hear anything, check your system audio settings")
                
                # Preview first 10 seconds or full duration if shorter
                preview_duration = min(10.0, audio_clip.duration)
                audio_clip.subclipped(0, preview_duration).preview()
                
                print("✓ Audio preview completed")
                break
                
            except Exception as e:
                print(f"❌ Error with {audio_path}: {e}")
                continue
    
    except ImportError as e:
        print(f"❌ MoviePy not available: {e}")
        print("Install MoviePy with: pip install moviepy")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_system_audio():
    """Test system audio capabilities."""
    print("\nTesting system audio capabilities...")
    print("=" * 50)
    
    try:
        # Check if ffplay is available (required for audio preview)
        import subprocess
        result = subprocess.run(['ffplay', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ ffplay is available for audio preview")
        else:
            print("❌ ffplay not found - audio preview may not work")
            print("Install ffmpeg/ffplay to enable audio preview")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ ffplay not found - audio preview may not work")
        print("Install ffmpeg/ffplay to enable audio preview")
    except Exception as e:
        print(f"⚠️  Could not check ffplay: {e}")

if __name__ == "__main__":
    test_system_audio()
    test_audio_playback()