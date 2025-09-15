#!/usr/bin/env python3
"""
Test the new audio preview functionality.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_audio_preview():
    """Test the audio preview functionality."""
    print("Testing Audio Preview Functionality")
    print("=" * 40)
    
    try:
        from subtitle_creator.app_controller import AppController
        
        # Create app controller in test mode
        controller = AppController(main_window=None, test_mode=True)
        
        print("✓ AppController created successfully")
        
        # Test audio info when no audio is loaded
        audio_info = controller.get_audio_info()
        print(f"Audio info (no audio): {audio_info}")
        
        # Try to preview audio when none is loaded
        print("\nTesting preview with no audio loaded...")
        controller.preview_audio()  # Should show a message
        
        print("\n" + "=" * 40)
        print("To test with actual audio:")
        print("1. Get an audio file (.mp3, .wav, etc.)")
        print("2. Run: controller.load_audio_file('path/to/your/audio.mp3')")
        print("3. Run: controller.preview_audio(0, 5)  # Play first 5 seconds")
        print("4. Check audio info: controller.get_audio_info()")
        
        return controller
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def interactive_test():
    """Interactive test for audio preview."""
    controller = test_audio_preview()
    
    if not controller:
        return
    
    print("\n" + "=" * 40)
    print("Interactive Audio Test")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Load audio file")
        print("2. Preview audio (first 10 seconds)")
        print("3. Preview audio (custom range)")
        print("4. Show audio info")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            file_path = input("Enter audio file path: ").strip()
            if file_path and os.path.exists(file_path):
                try:
                    controller.load_audio_file(file_path)
                    print("✓ Audio loaded successfully")
                except Exception as e:
                    print(f"❌ Error loading audio: {e}")
            else:
                print("❌ File not found or invalid path")
        
        elif choice == '2':
            try:
                controller.preview_audio(0, 10)
                print("🔊 Audio preview started (first 10 seconds)")
            except Exception as e:
                print(f"❌ Error previewing audio: {e}")
        
        elif choice == '3':
            try:
                start = float(input("Start time (seconds): "))
                duration = float(input("Duration (seconds): "))
                controller.preview_audio(start, duration)
                print(f"🔊 Audio preview started ({start}s to {start+duration}s)")
            except ValueError:
                print("❌ Invalid time values")
            except Exception as e:
                print(f"❌ Error previewing audio: {e}")
        
        elif choice == '4':
            info = controller.get_audio_info()
            if info:
                print("Audio Information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            else:
                print("No audio loaded")
        
        elif choice == '5':
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        test_audio_preview()
        print("\nRun with --interactive flag for interactive testing:")
        print("python test_audio_preview.py --interactive")