#!/usr/bin/env python3
"""
Export Manager Demo

This script demonstrates the ExportManager functionality including:
- Quality presets (High 1080p, Medium 720p, Low 480p)
- Custom export settings
- Format support (MP4, AVI, MOV)
- Progress tracking with ETA calculation
- Error handling
"""

import os
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from subtitle_creator.export_manager import ExportManager, ExportStatus
from subtitle_creator.interfaces import SubtitleData, SubtitleLine, WordTiming


class MockVideoClip:
    """Mock video clip for demonstration."""
    
    def __init__(self, duration=10.0, size=(1920, 1080), fps=30):
        self.duration = duration
        self.size = size
        self.fps = fps
    
    def resize(self, size):
        self.size = size
        return self
    
    def set_fps(self, fps):
        self.fps = fps
        return self
    
    def write_videofile(self, filename, **kwargs):
        # Simulate export process
        print(f"  Writing video file: {filename}")
        time.sleep(0.2)  # Simulate processing time
        # Create output file
        Path(filename).touch()
        return self


class MockEffect:
    """Mock effect for demonstration."""
    
    def __init__(self, name, parameters=None):
        self.name = name
        self.parameters = parameters or {}
    
    def apply(self, clip, subtitle_data):
        return clip


def create_sample_subtitle_data():
    """Create sample subtitle data for demonstration."""
    lines = []
    
    # Create sample subtitle lines
    subtitles = [
        ("Hello world", 0.0, 2.0),
        ("This is a demo", 2.5, 4.5),
        ("Export manager test", 5.0, 7.0),
        ("Quality and progress", 7.5, 9.5)
    ]
    
    for text, start, end in subtitles:
        words = []
        word_list = text.split()
        word_duration = (end - start) / len(word_list)
        
        for i, word in enumerate(word_list):
            word_start = start + i * word_duration
            word_end = word_start + word_duration
            words.append(WordTiming(word, word_start, word_end))
        
        line = SubtitleLine(start, end, text, words, {})
        lines.append(line)
    
    return SubtitleData(lines, {}, {"title": "Demo Subtitles"})


def progress_callback(progress):
    """Progress callback for export tracking."""
    status_symbols = {
        ExportStatus.IDLE: "⏸️",
        ExportStatus.PREPARING: "🔄",
        ExportStatus.RENDERING: "🎬",
        ExportStatus.FINALIZING: "✨",
        ExportStatus.COMPLETED: "✅",
        ExportStatus.FAILED: "❌",
        ExportStatus.CANCELLED: "🚫"
    }
    
    symbol = status_symbols.get(progress.status, "❓")
    percent = int(progress.progress * 100)
    
    print(f"  {symbol} {progress.status.value.title()}: {percent}% - {progress.current_operation}")
    
    if progress.estimated_time_remaining > 0:
        eta = int(progress.estimated_time_remaining)
        print(f"    ETA: {eta}s")


def demo_quality_presets():
    """Demonstrate quality presets."""
    print("\n🎯 Quality Presets Demo")
    print("=" * 50)
    
    export_manager = ExportManager()
    presets = export_manager.get_quality_presets()
    
    for quality, preset in presets.items():
        print(f"\n{quality.value.upper()}:")
        print(f"  Name: {preset.name}")
        print(f"  Resolution: {preset.resolution[0]}x{preset.resolution[1]}")
        print(f"  FPS: {preset.fps}")
        print(f"  Bitrate: {preset.bitrate}")
        print(f"  Codec: {preset.codec}")
        print(f"  Description: {preset.description}")


def demo_supported_formats():
    """Demonstrate supported formats and codecs."""
    print("\n📁 Supported Formats Demo")
    print("=" * 50)
    
    export_manager = ExportManager()
    formats = export_manager.get_supported_formats()
    
    for format_type in formats:
        codecs = export_manager.get_supported_codecs(format_type)
        print(f"\n{format_type.value.upper()}:")
        print(f"  Video codecs: {', '.join(codecs['video'])}")
        print(f"  Audio codecs: {', '.join(codecs['audio'])}")


def demo_export_with_progress():
    """Demonstrate export with progress tracking."""
    print("\n🚀 Export with Progress Tracking Demo")
    print("=" * 50)
    
    # Create demo data
    clip = MockVideoClip(duration=5.0)
    subtitle_data = create_sample_subtitle_data()
    effects = [
        MockEffect("text_styling", {"font_size": 48}),
        MockEffect("animation", {"type": "fade_in"})
    ]
    
    # Create export manager
    export_manager = ExportManager()
    export_manager.add_progress_callback(progress_callback)
    
    # Test different quality settings
    test_cases = [
        {"name": "High Quality", "settings": {"format": "mp4", "quality": "high"}},
        {"name": "Medium Quality", "settings": {"format": "mp4", "quality": "medium"}},
        {"name": "Custom Settings", "settings": {
            "format": "mp4",
            "quality": "custom",
            "resolution": [1280, 720],
            "fps": 25,
            "bitrate": "3000k"
        }}
    ]
    
    for case in test_cases:
        print(f"\n📤 Exporting: {case['name']}")
        output_path = f"demo_output_{case['name'].lower().replace(' ', '_')}.mp4"
        
        try:
            # Start export
            export_manager.export_video(clip, subtitle_data, effects, output_path, case['settings'])
            
            # Wait for completion
            success = export_manager.wait_for_export_completion(timeout=10.0)
            
            if success:
                print(f"  ✅ Export completed successfully!")
                
                # Show file size estimation
                estimated_size = export_manager.estimate_file_size(clip.duration, case['settings'])
                print(f"  📊 Estimated file size: {estimated_size / 1024 / 1024:.1f} MB")
                
                # Clean up demo file
                if os.path.exists(output_path):
                    os.remove(output_path)
            else:
                print(f"  ❌ Export failed or timed out")
                
        except Exception as e:
            print(f"  ❌ Export error: {e}")


def demo_export_cancellation():
    """Demonstrate export cancellation."""
    print("\n🛑 Export Cancellation Demo")
    print("=" * 50)
    
    # Create demo data with longer duration
    clip = MockVideoClip(duration=20.0)  # Longer clip
    subtitle_data = create_sample_subtitle_data()
    effects = [MockEffect("complex_effect")]
    
    export_manager = ExportManager()
    export_manager.add_progress_callback(progress_callback)
    
    output_path = "demo_cancelled_export.mp4"
    settings = {"format": "mp4", "quality": "high"}
    
    print("📤 Starting export (will be cancelled)...")
    
    try:
        # Start export
        export_manager.export_video(clip, subtitle_data, effects, output_path, settings)
        
        # Wait a moment then cancel
        time.sleep(0.2)
        print("🛑 Cancelling export...")
        
        success = export_manager.cancel_export()
        if success:
            print("  ✅ Cancellation initiated")
        
        # Wait for cancellation to complete
        time.sleep(0.5)
        
        progress = export_manager.get_detailed_progress()
        if progress and progress.status == ExportStatus.CANCELLED:
            print("  ✅ Export successfully cancelled")
        
        # Clean up if file was created
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        print(f"  ❌ Cancellation error: {e}")


def demo_validation():
    """Demonstrate export settings validation."""
    print("\n✅ Export Settings Validation Demo")
    print("=" * 50)
    
    export_manager = ExportManager()
    
    # Test valid settings
    valid_settings = [
        {"format": "mp4", "quality": "high"},
        {"format": "avi", "quality": "medium"},
        {"format": "mov", "quality": "low"},
        {
            "format": "mp4",
            "quality": "custom",
            "resolution": [1920, 1080],
            "fps": 30,
            "bitrate": "5000k"
        }
    ]
    
    print("Valid settings:")
    for i, settings in enumerate(valid_settings, 1):
        errors = export_manager.validate_export_settings(settings)
        status = "✅ Valid" if not errors else f"❌ Invalid: {errors[0]}"
        print(f"  {i}. {settings} - {status}")
    
    # Test invalid settings
    invalid_settings = [
        {"format": "invalid"},  # Missing quality
        {"format": "mp4", "quality": "invalid"},  # Invalid quality
        {"format": "mp4", "quality": "custom", "resolution": [0, 1080]},  # Invalid resolution
        {"format": "mp4", "quality": "custom", "fps": 0},  # Invalid FPS
    ]
    
    print("\nInvalid settings:")
    for i, settings in enumerate(invalid_settings, 1):
        errors = export_manager.validate_export_settings(settings)
        status = "✅ Valid" if not errors else f"❌ Invalid: {errors[0]}"
        print(f"  {i}. {settings} - {status}")


def main():
    """Run all export manager demos."""
    print("🎬 Export Manager Demo")
    print("=" * 50)
    print("This demo showcases the ExportManager functionality including:")
    print("- Quality presets and custom settings")
    print("- Format support and codec options")
    print("- Progress tracking with ETA calculation")
    print("- Export cancellation")
    print("- Settings validation")
    
    try:
        demo_quality_presets()
        demo_supported_formats()
        demo_validation()
        demo_export_with_progress()
        demo_export_cancellation()
        
        print("\n🎉 Demo completed successfully!")
        print("\nThe ExportManager provides:")
        print("✅ Quality presets (High 1080p, Medium 720p, Low 480p)")
        print("✅ Custom export settings (resolution, FPS, bitrate)")
        print("✅ Format support (MP4, AVI, MOV) with codec selection")
        print("✅ Progress tracking with ETA calculation")
        print("✅ Comprehensive error handling")
        print("✅ Export cancellation")
        print("✅ Settings validation")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()