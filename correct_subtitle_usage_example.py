#!/usr/bin/env python3
"""
Correct usage example for the Subtitle Creator application.
This demonstrates the proper way to create videos with visible subtitles.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_video_with_subtitles():
    """Create a video with properly configured subtitles."""
    print("Creating video with properly configured subtitles...")
    
    try:
        from moviepy import ColorClip, VideoFileClip
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect, PositioningEffect
        from subtitle_creator.app_controller import AppController
        
        # Step 1: Create or load background video
        # For this example, we'll create a simple colored background
        background_clip = ColorClip(
            size=(1280, 720),  # HD resolution
            color=(20, 40, 80),  # Dark blue background
            duration=15.0
        )
        print("✓ Background video created")
        
        # Step 2: Create subtitle data with proper timing
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(1.0, 4.0, "Welcome to the subtitle demo"),
            SubtitleLine(5.0, 8.0, "This text should be clearly visible"),
            SubtitleLine(9.0, 12.0, "With proper contrast and positioning"),
            SubtitleLine(13.0, 15.0, "Thank you for watching!")
        ]
        print(f"✓ Subtitle data created with {len(subtitle_data.lines)} lines")
        
        # Step 3: Create typography effect with high visibility settings
        typography_effect = TypographyEffect("High Visibility Typography", {
            'font_size': 48,                        # Large, readable size
            'text_color': (255, 255, 0, 255),      # Bright yellow text
            'outline_enabled': True,                 # Enable outline for contrast
            'outline_color': (0, 0, 0, 255),       # Black outline
            'outline_width': 3,                     # Thick outline
            'font_weight': 'normal'                 # Normal weight
        })
        print("✓ Typography effect configured")
        
        # Step 4: Create positioning effect for proper placement
        positioning_effect = PositioningEffect("Bottom Center Positioning", {
            'horizontal_alignment': 'center',       # Center horizontally
            'vertical_alignment': 'bottom',         # Bottom of screen
            'x_offset': 0,                          # No horizontal offset
            'y_offset': -100,                       # 100 pixels from bottom
            'margin_horizontal': 40,                # 40px margin from sides
            'margin_vertical': 40                   # 40px margin from top/bottom
        })
        print("✓ Positioning effect configured")
        
        # Step 5: Apply effects in correct order
        # First apply typography to create text clips
        clip_with_text = typography_effect.apply(background_clip, subtitle_data)
        print("✓ Typography effect applied")
        
        # Then apply positioning to place text correctly
        final_clip = positioning_effect.apply(clip_with_text, subtitle_data)
        print("✓ Positioning effect applied")
        
        # Step 6: Verify the composition
        print(f"✓ Final clip created:")
        print(f"  - Type: {type(final_clip)}")
        print(f"  - Duration: {final_clip.duration} seconds")
        print(f"  - Size: {final_clip.size}")
        
        if hasattr(final_clip, 'clips'):
            print(f"  - Number of clips: {len(final_clip.clips)}")
        
        # Step 7: Export frames for verification
        test_times = [2.0, 6.0, 10.0, 14.0]  # One frame per subtitle
        for i, t in enumerate(test_times):
            frame = final_clip.get_frame(t)
            from PIL import Image
            img = Image.fromarray(frame)
            filename = f"correct_usage_frame_{i+1}_t{t:.1f}s.png"
            img.save(filename)
            print(f"  - Frame saved: {filename}")
        
        # Step 8: Export final video
        output_path = "correct_subtitle_example.mp4"
        print(f"Exporting final video to {output_path}...")
        
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec=None,  # No audio for this example
            temp_audiofile=None,
            remove_temp=True
        )
        
        print(f"✓ Video exported successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to create video: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_common_mistakes():
    """Show common mistakes that cause invisible subtitles."""
    print("\nDemonstrating common mistakes...")
    
    try:
        from moviepy import ColorClip
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect
        
        background = ColorClip(size=(640, 360), color=(200, 200, 200), duration=5.0)  # Light gray
        subtitle_data = SubtitleData()
        subtitle_data.lines = [SubtitleLine(1.0, 4.0, "This text might be invisible")]
        
        # Mistake 1: Low contrast (white text on light background)
        bad_typography = TypographyEffect("Bad Contrast", {
            'font_size': 24,                        # Too small
            'text_color': (220, 220, 220, 255),    # Light gray text on light background
            'outline_enabled': False,               # No outline
        })
        
        bad_clip = bad_typography.apply(background, subtitle_data)
        frame = bad_clip.get_frame(2.0)
        
        from PIL import Image
        img = Image.fromarray(frame)
        img.save("mistake_example_low_contrast.png")
        print("✓ Low contrast example saved: mistake_example_low_contrast.png")
        
        # Mistake 2: Text positioned outside visible area
        # (This would require positioning effect, but demonstrates the concept)
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create mistake examples: {e}")
        return False

def main():
    """Run the complete example."""
    print("=== Correct Subtitle Usage Example ===")
    print("This demonstrates the proper way to create visible subtitles.\n")
    
    # Create correct example
    if create_video_with_subtitles():
        print("\n✓ SUCCESS: Correct usage example completed")
    else:
        print("\n✗ FAILED: Could not create correct example")
        return
    
    # Show common mistakes
    if demonstrate_common_mistakes():
        print("✓ Common mistakes examples created")
    
    print("\n=== RESULTS ===")
    print("Files created:")
    print("1. correct_subtitle_example.mp4 - Video with properly visible subtitles")
    print("2. correct_usage_frame_*.png - Individual frames showing subtitles")
    print("3. mistake_example_low_contrast.png - Example of what NOT to do")
    
    print("\n=== KEY POINTS FOR VISIBLE SUBTITLES ===")
    print("1. Use HIGH CONTRAST colors (bright text on dark background)")
    print("2. Use LARGE FONT SIZE (40-60px for HD video)")
    print("3. Enable OUTLINE with contrasting color")
    print("4. Position text in SAFE AREA (not too close to edges)")
    print("5. Apply effects in CORRECT ORDER (Typography first, then Positioning)")
    
    print("\nIf you follow these guidelines, your subtitles will be clearly visible!")

if __name__ == "__main__":
    main()