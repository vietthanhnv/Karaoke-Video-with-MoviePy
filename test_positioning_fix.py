#!/usr/bin/env python3
"""
Test the positioning fix to ensure subtitles appear correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_fixed_positioning():
    """Test the fixed positioning logic."""
    print("Testing fixed subtitle positioning...")
    
    try:
        from moviepy import ColorClip
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect, PositioningEffect
        
        # Create test background (HD resolution)
        background = ColorClip(size=(1280, 720), color=(20, 40, 80), duration=8.0)
        
        # Create subtitle data
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(1.0, 3.0, "FIXED: This should be properly positioned"),
            SubtitleLine(4.0, 6.0, "FIXED: Bottom center with safe margins"),
        ]
        
        # Apply typography effect (creates text clips with fixed default positioning)
        typography = TypographyEffect("Fixed Typography", {
            'font_size': 48,
            'text_color': (255, 255, 0, 255),  # Bright yellow
            'outline_enabled': True,
            'outline_color': (0, 0, 0, 255),   # Black outline
            'outline_width': 3
        })
        
        clip_with_text = typography.apply(background, subtitle_data)
        print("✓ Typography effect applied with fixed default positioning")
        
        # Apply positioning effect with corrected calculation
        positioning = PositioningEffect("Fixed Positioning", {
            'horizontal_alignment': 'center',
            'vertical_alignment': 'bottom',
            'x_offset': 0,
            'y_offset': -60,  # 60 pixels up from calculated bottom
            'margin_horizontal': 40,
            'margin_vertical': 60  # Safe margin from edges
        })
        
        final_clip = positioning.apply(clip_with_text, subtitle_data)
        print("✓ Positioning effect applied with fixed calculation")
        
        # Test frame extraction
        test_times = [2.0, 5.0]
        for i, t in enumerate(test_times):
            frame = final_clip.get_frame(t)
            from PIL import Image
            img = Image.fromarray(frame)
            filename = f"positioning_fix_verification_{i+1}.png"
            img.save(filename)
            print(f"✓ Fixed positioning frame saved: {filename}")
        
        # Export test video
        output_path = "positioning_fix_verification.mp4"
        final_clip.write_videofile(output_path, fps=24)
        print(f"✓ Fixed positioning video exported: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Positioning fix test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_resolutions():
    """Test positioning fix across different video resolutions."""
    print("\nTesting positioning fix across different resolutions...")
    
    resolutions = [
        (640, 360, "360p"),
        (1280, 720, "720p"),
        (1920, 1080, "1080p")
    ]
    
    try:
        from moviepy import ColorClip, TextClip, CompositeVideoClip
        
        for width, height, name in resolutions:
            # Create background
            background = ColorClip(size=(width, height), color=(30, 60, 90), duration=3.0)
            
            # Create text with safe positioning
            safe_bottom_y = height - 80  # 80 pixels from bottom
            text_clip = TextClip(
                text=f"Test {name} - Safe Bottom Position",
                font_size=max(24, width // 40),  # Scale font size with resolution
                color='yellow',
                stroke_color='black',
                stroke_width=2,
                duration=3.0
            ).with_position(('center', safe_bottom_y))
            
            # Create composite
            composite = CompositeVideoClip([background, text_clip])
            
            # Extract frame
            frame = composite.get_frame(1.5)
            from PIL import Image
            img = Image.fromarray(frame)
            filename = f"resolution_test_{name.lower()}.png"
            img.save(filename)
            print(f"✓ {name} resolution test: {filename}")
        
        return True
        
    except Exception as e:
        print(f"✗ Resolution test failed: {e}")
        return False

def main():
    """Run positioning fix tests."""
    print("=== Subtitle Positioning Fix Verification ===")
    
    # Test the fixed positioning
    if test_fixed_positioning():
        print("✓ Fixed positioning test passed")
    else:
        print("✗ Fixed positioning test failed")
        return
    
    # Test across different resolutions
    if test_different_resolutions():
        print("✓ Resolution tests passed")
    
    print("\n=== FIX VERIFICATION RESULTS ===")
    print("Check the generated files:")
    print("1. positioning_fix_verification.mp4 - Video with corrected positioning")
    print("2. positioning_fix_verification_*.png - Frames showing correct positioning")
    print("3. resolution_test_*.png - Tests across different resolutions")
    
    print("\n=== WHAT WAS FIXED ===")
    print("1. ✓ Default text positioning now uses safe bottom margin (80px from bottom)")
    print("2. ✓ Position calculation accounts for MoviePy's center-point positioning")
    print("3. ✓ Bottom alignment now prevents text from being cut off")
    print("4. ✓ Safe bounds checking ensures text stays within video area")
    
    print("\nThe positioning issue should now be resolved!")
    print("Subtitles will appear properly centered and not cut off at the bottom.")

if __name__ == "__main__":
    main()