#!/usr/bin/env python3
"""
Test the complete application workflow to identify subtitle overlay issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_workflow():
    """Test the complete subtitle creation workflow."""
    print("🔍 Testing complete subtitle creation workflow...")
    
    try:
        from moviepy import ColorClip
        from subtitle_creator.app_controller import AppController
        from subtitle_creator.models import SubtitleData, SubtitleLine
        
        # Create app controller in test mode
        app_controller = AppController(test_mode=True)
        
        print("✅ AppController created")
        
        # Create test background video
        background_clip = ColorClip(
            size=(640, 360),
            color=(50, 100, 150),  # Blue background
            duration=10.0
        )
        
        # Load background into media manager
        app_controller.media_manager._background_clip = background_clip
        print("✅ Background video loaded")
        
        # Create subtitle data
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(1.0, 3.0, "First subtitle line"),
            SubtitleLine(4.0, 6.0, "Second subtitle line"),
            SubtitleLine(7.0, 9.0, "Third subtitle line")
        ]
        
        # Load subtitle data
        app_controller.subtitle_engine.load_from_data(subtitle_data)
        print(f"✅ Subtitle data loaded with {len(subtitle_data.lines)} lines")
        
        # Add typography effect
        from subtitle_creator.effects.text_styling import TypographyEffect
        typography_effect = TypographyEffect("Main Typography", {
            'font_size': 42,
            'text_color': (255, 255, 0, 255),  # Yellow text
            'outline_enabled': True,
            'outline_color': (0, 0, 0, 255),
            'outline_width': 3
        })
        
        app_controller.effect_system.add_effect(typography_effect)
        print("✅ Typography effect added")
        
        # Generate preview
        effects = app_controller.effect_system.get_active_effects()
        preview_clip = app_controller.preview_engine.generate_preview(
            background_clip, 
            subtitle_data, 
            effects
        )
        
        print(f"✅ Preview generated")
        print(f"   - Type: {type(preview_clip)}")
        print(f"   - Duration: {preview_clip.duration}")
        
        if hasattr(preview_clip, 'clips'):
            print(f"   - Number of clips: {len(preview_clip.clips)}")
            for i, clip in enumerate(preview_clip.clips):
                clip_type = type(clip).__name__
                text_attr = getattr(clip, 'text', 'N/A')
                print(f"     Clip {i}: {clip_type} - Text: {text_attr}")
        
        # Test frame extraction at different times
        test_times = [0.5, 1.5, 4.5, 7.5]
        for t in test_times:
            try:
                frame = preview_clip.get_frame(t)
                print(f"✅ Frame extracted at t={t}s - Shape: {frame.shape}")
                
                # Save frame for inspection
                from PIL import Image
                img = Image.fromarray(frame)
                img.save(f'workflow_test_frame_t{t}.png')
                print(f"   - Saved as 'workflow_test_frame_t{t}.png'")
                
            except Exception as e:
                print(f"❌ Failed to extract frame at t={t}s: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_positioning_effect():
    """Test if positioning effect is working correctly."""
    print("\n🔍 Testing positioning effect...")
    
    try:
        from moviepy import ColorClip
        from subtitle_creator.models import SubtitleData, SubtitleLine
        from subtitle_creator.effects.text_styling import TypographyEffect, PositioningEffect
        
        # Create background
        background = ColorClip(size=(640, 360), color=(0, 0, 100), duration=5.0)
        
        # Create subtitle data
        subtitle_data = SubtitleData()
        subtitle_data.lines = [SubtitleLine(0.0, 5.0, "Positioned Text Test")]
        
        # Apply typography first
        typography = TypographyEffect("Typography", {
            'font_size': 48,
            'text_color': (255, 255, 255, 255)
        })
        
        clip_with_text = typography.apply(background, subtitle_data)
        print("✅ Typography applied")
        
        # Apply positioning
        positioning = PositioningEffect("Positioning", {
            'horizontal_alignment': 'center',
            'vertical_alignment': 'middle',  # Try middle instead of bottom
            'x_offset': 0,
            'y_offset': 0
        })
        
        final_clip = positioning.apply(clip_with_text, subtitle_data)
        print("✅ Positioning applied")
        
        # Extract frame
        frame = final_clip.get_frame(2.0)
        from PIL import Image
        img = Image.fromarray(frame)
        img.save('positioning_test_frame.png')
        print("✅ Positioning test frame saved as 'positioning_test_frame.png'")
        
        return True
        
    except Exception as e:
        print(f"❌ Positioning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_positions():
    """Test different text positions to see where text appears."""
    print("\n🔍 Testing different text positions...")
    
    try:
        from moviepy import ColorClip, TextClip, CompositeVideoClip
        
        # Create background
        background = ColorClip(size=(640, 360), color=(50, 50, 50), duration=3.0)
        
        # Test different positions
        positions = [
            ('center', 'top'),
            ('center', 'center'),
            ('center', 'bottom'),
            (50, 50),  # Top-left corner
            (320, 180),  # Center coordinates
            (320, 300),  # Bottom center coordinates
        ]
        
        for i, pos in enumerate(positions):
            text_clip = TextClip(
                text=f"Position: {pos}",
                font_size=24,
                color='yellow',
                duration=3.0
            ).with_position(pos)
            
            composite = CompositeVideoClip([background, text_clip])
            frame = composite.get_frame(1.0)
            
            from PIL import Image
            img = Image.fromarray(frame)
            img.save(f'position_test_{i}_{str(pos).replace(" ", "").replace(",", "_").replace("(", "").replace(")", "")}.png')
            print(f"✅ Position {pos} test saved")
        
        return True
        
    except Exception as e:
        print(f"❌ Position test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all workflow tests."""
    print("🚀 Starting Application Workflow Tests")
    print("=" * 50)
    
    # Test complete workflow
    if not test_complete_workflow():
        print("❌ Complete workflow test failed")
        return
    
    # Test positioning
    if not test_positioning_effect():
        print("❌ Positioning test failed")
        return
    
    # Test different positions
    if not test_different_positions():
        print("❌ Different positions test failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All workflow tests completed!")
    print("\nCheck the generated PNG files to see if subtitles are visible.")
    print("If subtitles are not visible in the images, the issue might be:")
    print("1. Text positioning outside the visible area")
    print("2. Text color matching background color")
    print("3. Font rendering issues")
    print("4. Text size too small or too large")

if __name__ == "__main__":
    main()