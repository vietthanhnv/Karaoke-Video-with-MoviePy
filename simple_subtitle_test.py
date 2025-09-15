#!/usr/bin/env python3
"""
Simple subtitle overlay test to verify functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_simple_test():
    """Create a simple test video with subtitles."""
    print("Creating simple subtitle test...")
    
    try:
        from moviepy import ColorClip, TextClip, CompositeVideoClip
        
        # Create background
        background = ColorClip(
            size=(640, 360),
            color=(0, 50, 100),  # Dark blue
            duration=6.0
        )
        
        # Create text clips
        text1 = TextClip(
            text="First subtitle line",
            font_size=32,
            color='yellow',
            duration=2.0
        ).with_position(('center', 300)).with_start(1.0)
        
        text2 = TextClip(
            text="Second subtitle line",
            font_size=32,
            color='white',
            duration=2.0
        ).with_position(('center', 300)).with_start(3.0)
        
        # Create composite
        final_video = CompositeVideoClip([background, text1, text2])
        
        print(f"Video created with {len(final_video.clips)} clips")
        
        # Export frames instead of video to avoid codec issues
        test_times = [1.5, 3.5]
        for i, t in enumerate(test_times):
            frame = final_video.get_frame(t)
            from PIL import Image
            img = Image.fromarray(frame)
            filename = f"simple_test_frame_{i+1}.png"
            img.save(filename)
            print(f"Frame saved: {filename}")
        
        # Try to export video with simpler parameters
        try:
            output_path = "simple_subtitle_test.mp4"
            final_video.write_videofile(output_path, fps=24)
            print(f"Video exported: {output_path}")
        except Exception as e:
            print(f"Video export failed (but frames were saved): {e}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_components():
    """Test the application components directly."""
    print("\nTesting application components...")
    
    try:
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect
        from moviepy import ColorClip
        
        # Create test data
        background = ColorClip(size=(640, 360), color=(50, 50, 50), duration=5.0)
        
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(1.0, 3.0, "Test subtitle text"),
        ]
        
        # Create and apply typography effect
        typography = TypographyEffect("Test", {
            'font_size': 40,
            'text_color': (255, 255, 0, 255),  # Yellow
            'outline_enabled': True,
            'outline_color': (0, 0, 0, 255),
            'outline_width': 2
        })
        
        result = typography.apply(background, subtitle_data)
        
        print(f"Typography effect applied successfully")
        print(f"Result type: {type(result)}")
        
        if hasattr(result, 'clips'):
            print(f"Number of clips in result: {len(result.clips)}")
            
            # Extract frame
            frame = result.get_frame(2.0)  # Should have subtitle
            from PIL import Image
            img = Image.fromarray(frame)
            img.save("app_component_test.png")
            print("App component test frame saved: app_component_test.png")
        
        return True
        
    except Exception as e:
        print(f"App component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests."""
    print("=== Simple Subtitle Overlay Test ===")
    
    # Test 1: Simple MoviePy test
    if create_simple_test():
        print("SUCCESS: Simple test passed")
    else:
        print("FAILED: Simple test failed")
        return
    
    # Test 2: App components
    if test_app_components():
        print("SUCCESS: App components test passed")
    else:
        print("FAILED: App components test failed")
        return
    
    print("\n=== RESULTS ===")
    print("Check the generated PNG files:")
    print("- simple_test_frame_1.png (should show yellow text)")
    print("- simple_test_frame_2.png (should show white text)")
    print("- app_component_test.png (should show yellow text with black outline)")
    print("\nIf you can see text in these images, the subtitle system works!")
    print("If not, the issue might be:")
    print("1. Font rendering problems on your system")
    print("2. Text positioning outside visible area")
    print("3. Color contrast issues")

if __name__ == "__main__":
    main()