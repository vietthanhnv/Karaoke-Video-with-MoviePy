#!/usr/bin/env python3
"""
Fix for subtitle positioning issues.
This script demonstrates the correct way to position subtitles.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_positioning_fix():
    """Test the corrected positioning logic."""
    print("Testing corrected subtitle positioning...")
    
    try:
        from moviepy import ColorClip, TextClip, CompositeVideoClip
        
        # Create test background
        background = ColorClip(size=(1280, 720), color=(0, 50, 100), duration=5.0)
        
        # Test different positioning approaches
        test_cases = [
            {
                'name': 'MoviePy String Position (center, bottom)',
                'position': ('center', 'bottom'),
                'description': 'Using MoviePy built-in string positioning'
            },
            {
                'name': 'Safe Bottom Center (calculated)',
                'position': (640, 620),  # Center X, 100px from bottom
                'description': 'Calculated safe position for 720p video'
            },
            {
                'name': 'Bottom with margin (calculated)',
                'position': (640, 650),  # Center X, 70px from bottom
                'description': 'Bottom position with proper margin'
            },
            {
                'name': 'Middle Center (calculated)',
                'position': (640, 360),  # Exact center
                'description': 'Exact center positioning'
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            # Create text clip with specific positioning
            text_clip = TextClip(
                text=f"Test {i+1}: {test_case['name']}",
                font_size=36,
                color='yellow',
                stroke_color='black',
                stroke_width=2,
                duration=5.0
            ).with_position(test_case['position'])
            
            # Create composite
            composite = CompositeVideoClip([background, text_clip])
            
            # Extract frame
            frame = composite.get_frame(2.0)
            
            # Save frame
            from PIL import Image
            img = Image.fromarray(frame)
            filename = f"positioning_fix_test_{i+1}.png"
            img.save(filename)
            
            print(f"✓ {test_case['name']}: {filename}")
            print(f"  Position: {test_case['position']}")
            print(f"  Description: {test_case['description']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Positioning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_corrected_positioning_effect():
    """Create a corrected version of the positioning effect."""
    print("\nCreating corrected positioning effect...")
    
    corrected_code = '''
def _calculate_position_corrected(self, h_align: str, v_align: str, x_offset: int, y_offset: int,
                                margin_h: int, margin_v: int, video_size: Tuple[int, int]) -> Union[str, Tuple]:
    """
    CORRECTED position calculation that accounts for MoviePy text positioning behavior.
    
    MoviePy positions text clips by their CENTER point, not top-left corner.
    This method calculates the correct center position for the text.
    """
    width, height = video_size
    
    # For MoviePy, we can use string-based positioning which is more reliable
    # than pixel coordinates for text alignment
    
    if h_align == 'center' and v_align == 'bottom':
        # Use MoviePy's built-in positioning with offset
        if y_offset != 0:
            # Calculate bottom position with offset
            bottom_y = height + y_offset - margin_v
            return ('center', bottom_y)
        else:
            # Use built-in bottom positioning with margin
            return ('center', height - margin_v)
    
    elif h_align == 'center' and v_align == 'middle':
        center_y = height // 2 + y_offset
        return ('center', center_y)
    
    elif h_align == 'center' and v_align == 'top':
        top_y = margin_v + y_offset
        return ('center', top_y)
    
    else:
        # For other alignments, calculate pixel positions
        if h_align == 'left':
            x_pos = margin_h + x_offset
        elif h_align == 'right':
            x_pos = width - margin_h + x_offset
        else:  # center
            x_pos = width // 2 + x_offset
        
        if v_align == 'top':
            y_pos = margin_v + y_offset
        elif v_align == 'bottom':
            # Account for text height by using a safe margin
            y_pos = height - margin_v + y_offset
        else:  # middle
            y_pos = height // 2 + y_offset
        
        return (x_pos, y_pos)
'''
    
    with open('corrected_positioning_logic.py', 'w') as f:
        f.write(corrected_code)
    
    print("✓ Corrected positioning logic saved to 'corrected_positioning_logic.py'")

def create_working_subtitle_example():
    """Create a subtitle example with guaranteed correct positioning."""
    print("\nCreating working subtitle example...")
    
    try:
        from moviepy import ColorClip, TextClip, CompositeVideoClip
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect
        
        # Create background
        background = ColorClip(size=(1280, 720), color=(20, 40, 80), duration=10.0)
        
        # Create subtitle data
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(1.0, 4.0, "Correctly positioned subtitle 1"),
            SubtitleLine(5.0, 8.0, "Correctly positioned subtitle 2"),
        ]
        
        # Apply typography effect (this creates the text clips)
        typography = TypographyEffect("Working Typography", {
            'font_size': 48,
            'text_color': (255, 255, 0, 255),  # Yellow
            'outline_enabled': True,
            'outline_color': (0, 0, 0, 255),   # Black outline
            'outline_width': 3
        })
        
        clip_with_text = typography.apply(background, subtitle_data)
        
        # Now manually fix the positioning by recreating the composite with correct positions
        if hasattr(clip_with_text, 'clips') and len(clip_with_text.clips) > 1:
            base_clip = clip_with_text.clips[0]
            text_clips = clip_with_text.clips[1:]
            
            # Reposition text clips with corrected logic
            corrected_clips = [base_clip]
            
            for text_clip in text_clips:
                # Use MoviePy's reliable string positioning
                corrected_clip = text_clip.with_position(('center', 620))  # 100px from bottom for 720p
                corrected_clips.append(corrected_clip)
            
            final_clip = CompositeVideoClip(corrected_clips)
        else:
            final_clip = clip_with_text
        
        # Export test frames
        test_times = [2.0, 6.0]
        for i, t in enumerate(test_times):
            frame = final_clip.get_frame(t)
            from PIL import Image
            img = Image.fromarray(frame)
            filename = f"working_subtitle_example_{i+1}.png"
            img.save(filename)
            print(f"✓ Working example frame saved: {filename}")
        
        # Export video
        output_path = "working_subtitle_example.mp4"
        final_clip.write_videofile(output_path, fps=24)
        print(f"✓ Working subtitle video exported: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Working example creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run positioning fix tests."""
    print("=== Subtitle Positioning Fix ===")
    
    # Test different positioning approaches
    if test_positioning_fix():
        print("✓ Positioning tests completed")
    
    # Create corrected positioning logic
    create_corrected_positioning_effect()
    
    # Create working example
    if create_working_subtitle_example():
        print("✓ Working example created")
    
    print("\n=== POSITIONING FIX SUMMARY ===")
    print("The issue was in the positioning calculation logic:")
    print("1. MoviePy positions text by CENTER point, not top-left")
    print("2. 'bottom' alignment needs proper margin calculation")
    print("3. String positions ('center', 'bottom') are more reliable than pixel coordinates")
    
    print("\n=== RECOMMENDED FIX ===")
    print("For reliable bottom-center positioning, use:")
    print("  position = ('center', video_height - 100)  # 100px from bottom")
    print("  OR")
    print("  position = ('center', 'bottom')  # Let MoviePy handle it")
    
    print("\nCheck the generated files to see the difference!")

if __name__ == "__main__":
    main()