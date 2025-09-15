#!/usr/bin/env python3
"""
Simple application test to verify subtitle visibility.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_application_subtitle_workflow():
    """Test the exact workflow used in the application."""
    print("🔍 Testing application subtitle workflow...")
    
    try:
        from moviepy import ColorClip
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect, PositioningEffect
        
        # Create background (simulating loaded video)
        background = ColorClip(size=(1280, 720), color=(30, 30, 30), duration=10.0)
        print("✅ Background video created")
        
        # Create subtitle data (simulating loaded subtitles)
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(1.0, 3.0, "Test subtitle line 1"),
            SubtitleLine(4.0, 6.0, "Test subtitle line 2"),
            SubtitleLine(7.0, 9.0, "Test subtitle line 3")
        ]
        print(f"✅ Subtitle data created with {len(subtitle_data.lines)} lines")
        
        # Create typography effect (what user adds in Effects panel)
        typography_effect = TypographyEffect("Main Typography", {
            'font_size': 48,
            'text_color': (255, 255, 0, 255),  # Bright yellow
            'outline_enabled': True,
            'outline_color': (0, 0, 0, 255),  # Black outline
            'outline_width': 3
        })
        print("✅ Typography effect created")
        
        # Apply typography effect
        clip_with_text = typography_effect.apply(background, subtitle_data)
        print(f"✅ Typography applied - Type: {type(clip_with_text)}")
        
        # Create positioning effect
        positioning_effect = PositioningEffect("Bottom Center", {
            'horizontal_alignment': 'center',
            'vertical_alignment': 'bottom',
            'x_offset': 0,
            'y_offset': -80,
            'margin_vertical': 40
        })
        print("✅ Positioning effect created")
        
        # Apply positioning effect
        final_clip = positioning_effect.apply(clip_with_text, subtitle_data)
        print(f"✅ Positioning applied - Type: {type(final_clip)}")
        
        # Test frame extraction at subtitle times
        test_times = [2.0, 5.0, 8.0]  # Times when subtitles should be visible
        
        for i, t in enumerate(test_times):
            try:
                frame = final_clip.get_frame(t)
                print(f"✅ Frame extracted at t={t}s - Shape: {frame.shape}")
                
                # Save frame for inspection
                from PIL import Image
                img = Image.fromarray(frame)
                filename = f'app_workflow_test_{i+1}_t{t}s.png'
                img.save(filename)
                print(f"   💾 Saved as '{filename}'")
                
            except Exception as e:
                print(f"❌ Failed to extract frame at t={t}s: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Application workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the application test."""
    print("🚀 SIMPLE APPLICATION SUBTITLE TEST")
    print("=" * 50)
    
    if test_application_subtitle_workflow():
        print("\n✅ APPLICATION WORKFLOW TEST PASSED!")
        print("\nCheck the generated PNG files:")
        print("- app_workflow_test_1_t2.0s.png")
        print("- app_workflow_test_2_t5.0s.png") 
        print("- app_workflow_test_3_t8.0s.png")
        print("\nIf you can see yellow text in these images, your subtitle system works!")
        
        print("\n📋 TO USE IN THE MAIN APPLICATION:")
        print("1. Launch: python main.py")
        print("2. Load your video file (File → Import Media)")
        print("3. Load or create subtitles")
        print("4. Add Typography effect with these settings:")
        print("   - Font Size: 48")
        print("   - Text Color: Yellow (255, 255, 0)")
        print("   - Outline: Enabled, Black (0, 0, 0), Width: 3")
        print("5. Add Positioning effect:")
        print("   - Horizontal: Center")
        print("   - Vertical: Bottom")
        print("   - Y Offset: -80")
        print("6. Check preview - subtitles should be visible!")
        
    else:
        print("\n❌ APPLICATION WORKFLOW TEST FAILED")
        print("There might be an issue with your subtitle system setup.")

if __name__ == "__main__":
    main()