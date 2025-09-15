#!/usr/bin/env python3
"""
Debug script to test subtitle overlay functionality.
This script will help identify why subtitles aren't appearing on video.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_moviepy_imports():
    """Test if MoviePy is properly installed and working."""
    print("🔍 Testing MoviePy imports...")
    try:
        from moviepy.editor import VideoClip, TextClip, CompositeVideoClip, ColorClip
        print("✅ MoviePy imports successful")
        return True
    except ImportError as e:
        print(f"❌ MoviePy import failed: {e}")
        return False

def test_basic_text_clip():
    """Test creating a basic TextClip."""
    print("\n🔍 Testing basic TextClip creation...")
    try:
        from moviepy.editor import TextClip
        
        # Create a simple text clip
        text_clip = TextClip(
            text="Hello World",
            font_size=50,
            color='white',
            duration=3.0
        )
        
        print(f"✅ TextClip created successfully")
        print(f"   - Text: {text_clip.text}")
        print(f"   - Duration: {text_clip.duration}")
        print(f"   - Size: {getattr(text_clip, 'size', 'Unknown')}")
        
        return text_clip
    except Exception as e:
        print(f"❌ TextClip creation failed: {e}")
        return None

def test_composite_video():
    """Test creating a composite video with background and text."""
    print("\n🔍 Testing CompositeVideoClip with text overlay...")
    try:
        from moviepy import ColorClip, TextClip, CompositeVideoClip
        
        # Create background clip
        background = ColorClip(
            size=(640, 360),
            color=(50, 50, 50),  # Dark gray
            duration=5.0
        )
        
        # Create text clip
        text_clip = TextClip(
            text="Subtitle Test",
            font_size=40,
            color='white',
            duration=5.0
        ).with_position(('center', 'bottom')).with_start(0)
        
        # Create composite
        composite = CompositeVideoClip([background, text_clip])
        
        print(f"✅ CompositeVideoClip created successfully")
        print(f"   - Background size: {background.size}")
        print(f"   - Text position: {getattr(text_clip, 'pos', 'Unknown')}")
        print(f"   - Composite duration: {composite.duration}")
        print(f"   - Number of clips: {len(composite.clips)}")
        
        return composite
    except Exception as e:
        print(f"❌ CompositeVideoClip creation failed: {e}")
        return None

def test_subtitle_creator_components():
    """Test the subtitle creator components."""
    print("\n🔍 Testing Subtitle Creator components...")
    try:
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect
        from subtitle_creator.preview_engine import PreviewEngine
        
        # Create test subtitle data
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(0.0, 2.0, "First subtitle line"),
            SubtitleLine(2.5, 4.5, "Second subtitle line")
        ]
        
        print(f"✅ SubtitleData created with {len(subtitle_data.lines)} lines")
        
        # Test typography effect
        typography_effect = TypographyEffect("Test Typography", {
            'font_size': 48,
            'text_color': (255, 255, 255, 255)
        })
        
        print(f"✅ TypographyEffect created")
        
        # Test preview engine
        preview_engine = PreviewEngine()
        print(f"✅ PreviewEngine created")
        
        return True
    except Exception as e:
        print(f"❌ Subtitle Creator components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_subtitle_overlay():
    """Test the complete subtitle overlay process."""
    print("\n🔍 Testing complete subtitle overlay process...")
    try:
        from moviepy import ColorClip
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect
        from subtitle_creator.preview_engine import PreviewEngine
        
        # Create background video
        background = ColorClip(
            size=(640, 360),
            color=(100, 100, 100),
            duration=5.0
        )
        
        # Create subtitle data
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(0.0, 2.0, "Testing subtitle overlay"),
            SubtitleLine(2.5, 4.5, "This should appear on video")
        ]
        
        # Create typography effect
        typography_effect = TypographyEffect("Test", {
            'font_size': 36,
            'text_color': (255, 255, 0, 255),  # Yellow text
            'outline_enabled': True,
            'outline_color': (0, 0, 0, 255),
            'outline_width': 2
        })
        
        # Apply effect
        result_clip = typography_effect.apply(background, subtitle_data)
        
        print(f"✅ Typography effect applied")
        print(f"   - Result type: {type(result_clip)}")
        print(f"   - Has clips attribute: {hasattr(result_clip, 'clips')}")
        
        if hasattr(result_clip, 'clips'):
            print(f"   - Number of clips in composite: {len(result_clip.clips)}")
            for i, clip in enumerate(result_clip.clips):
                print(f"     Clip {i}: {type(clip)} - {getattr(clip, 'text', 'No text attr')}")
        
        return result_clip
    except Exception as e:
        print(f"❌ Full subtitle overlay test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_export_frame():
    """Test exporting a single frame to see if subtitles are visible."""
    print("\n🔍 Testing frame export to check subtitle visibility...")
    try:
        composite_clip = test_full_subtitle_overlay()
        if composite_clip is None:
            return False
        
        # Try to get a frame at 1 second (should have subtitle)
        if hasattr(composite_clip, 'get_frame'):
            frame = composite_clip.get_frame(1.0)
            print(f"✅ Frame extracted at t=1.0s")
            print(f"   - Frame shape: {frame.shape if hasattr(frame, 'shape') else 'Unknown'}")
            
            # Save frame as image for inspection
            try:
                from PIL import Image
                if hasattr(frame, 'shape') and len(frame.shape) == 3:
                    img = Image.fromarray(frame)
                    img.save('test_frame_with_subtitle.png')
                    print(f"✅ Frame saved as 'test_frame_with_subtitle.png'")
                    print(f"   - Check this image to see if subtitles are visible")
            except ImportError:
                print("   - PIL not available, cannot save frame image")
            except Exception as e:
                print(f"   - Could not save frame: {e}")
            
            return True
        else:
            print("❌ Composite clip doesn't have get_frame method")
            return False
            
    except Exception as e:
        print(f"❌ Frame export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests."""
    print("🚀 Starting Subtitle Overlay Diagnostic Tests")
    print("=" * 50)
    
    # Test 1: MoviePy imports
    if not test_moviepy_imports():
        print("\n❌ Cannot proceed without MoviePy. Please install it:")
        print("   pip install moviepy")
        return
    
    # Test 2: Basic TextClip
    text_clip = test_basic_text_clip()
    if text_clip is None:
        print("\n❌ Basic TextClip creation failed")
        return
    
    # Test 3: CompositeVideoClip
    composite = test_composite_video()
    if composite is None:
        print("\n❌ CompositeVideoClip creation failed")
        return
    
    # Test 4: Subtitle Creator components
    if not test_subtitle_creator_components():
        print("\n❌ Subtitle Creator components failed")
        return
    
    # Test 5: Full subtitle overlay
    full_test = test_full_subtitle_overlay()
    if full_test is None:
        print("\n❌ Full subtitle overlay test failed")
        return
    
    # Test 6: Export frame
    test_export_frame()
    
    print("\n" + "=" * 50)
    print("🎉 Diagnostic tests completed!")
    print("\nIf subtitles still don't appear, check:")
    print("1. Font availability on your system")
    print("2. Text color contrast (white text on white background won't show)")
    print("3. Text positioning (might be outside visible area)")
    print("4. MoviePy version compatibility")

if __name__ == "__main__":
    main()