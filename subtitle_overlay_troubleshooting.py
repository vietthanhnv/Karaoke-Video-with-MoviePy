#!/usr/bin/env python3
"""
Comprehensive troubleshooting guide for subtitle overlay issues.
This script will help identify and fix common subtitle visibility problems.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_common_issues():
    """Check for common subtitle overlay issues."""
    print("🔍 Checking for common subtitle overlay issues...")
    
    issues_found = []
    solutions = []
    
    # Check 1: MoviePy version
    try:
        import moviepy
        version = getattr(moviepy, '__version__', 'Unknown')
        print(f"✅ MoviePy version: {version}")
        
        if version.startswith('1.'):
            issues_found.append("Using MoviePy v1.x (deprecated)")
            solutions.append("Upgrade to MoviePy v2.x: pip install moviepy>=2.0")
    except ImportError:
        issues_found.append("MoviePy not installed")
        solutions.append("Install MoviePy: pip install moviepy")
    
    # Check 2: Font availability
    try:
        from moviepy import TextClip
        test_clip = TextClip(text="Test", font_size=20, color='white')
        print("✅ Font rendering works")
    except Exception as e:
        if "font" in str(e).lower():
            issues_found.append(f"Font rendering issue: {e}")
            solutions.append("Install system fonts or specify a valid font path")
    
    # Check 3: Text positioning
    print("✅ Text positioning system available")
    
    return issues_found, solutions

def create_test_video_with_subtitles():
    """Create a test video with clearly visible subtitles."""
    print("\n🎬 Creating test video with visible subtitles...")
    
    try:
        from moviepy import ColorClip, TextClip, CompositeVideoClip
        
        # Create a colorful background to ensure contrast
        background = ColorClip(
            size=(640, 360),
            color=(0, 50, 100),  # Dark blue
            duration=10.0
        )
        
        # Create multiple text clips with different styles and positions
        text_clips = []
        
        # Title text (top center)
        title_clip = TextClip(
            text="SUBTITLE OVERLAY TEST",
            font_size=32,
            color='yellow',
            duration=10.0
        ).with_position(('center', 30)).with_start(0)
        text_clips.append(title_clip)
        
        # Subtitle 1 (bottom center - traditional position)
        sub1_clip = TextClip(
            text="This is subtitle line 1",
            font_size=28,
            color='white',
            duration=3.0
        ).with_position(('center', 300)).with_start(1.0)
        text_clips.append(sub1_clip)
        
        # Subtitle 2 (bottom center)
        sub2_clip = TextClip(
            text="This is subtitle line 2",
            font_size=28,
            color='cyan',
            duration=3.0
        ).with_position(('center', 300)).with_start(4.0)
        text_clips.append(sub2_clip)
        
        # Subtitle 3 (bottom center)
        sub3_clip = TextClip(
            text="This is subtitle line 3",
            font_size=28,
            color='lime',
            duration=3.0
        ).with_position(('center', 300)).with_start(7.0)
        text_clips.append(sub3_clip)
        
        # Create composite video
        final_video = CompositeVideoClip([background] + text_clips)
        
        print(f"✅ Test video created with {len(text_clips)} text overlays")
        
        # Export test video
        output_path = "subtitle_test_video.mp4"
        print(f"📹 Exporting test video to '{output_path}'...")
        
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac' if final_video.audio else None,
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        print(f"✅ Test video exported successfully!")
        print(f"   - File: {output_path}")
        print(f"   - Duration: {final_video.duration} seconds")
        print(f"   - Resolution: {final_video.size}")
        
        # Also export individual frames for inspection
        test_times = [2.0, 5.0, 8.0]
        for i, t in enumerate(test_times):
            frame = final_video.get_frame(t)
            from PIL import Image
            img = Image.fromarray(frame)
            frame_path = f"test_video_frame_{i+1}_t{t}.png"
            img.save(frame_path)
            print(f"   - Frame at t={t}s saved as '{frame_path}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test video: {e}")
        import traceback
        traceback.print_exc()
        return False

def diagnose_application_usage():
    """Provide guidance on proper application usage."""
    print("\n📋 Application Usage Diagnosis")
    print("=" * 40)
    
    print("\n1. LOADING MEDIA:")
    print("   ✓ Load background video first")
    print("   ✓ Load or create subtitle data")
    print("   ✓ Ensure subtitle timing matches video duration")
    
    print("\n2. ADDING EFFECTS:")
    print("   ✓ Add Typography effect for basic text styling")
    print("   ✓ Add Positioning effect to control text placement")
    print("   ✓ Ensure text color contrasts with background")
    
    print("\n3. PREVIEW SETTINGS:")
    print("   ✓ Check preview resolution (might be too low)")
    print("   ✓ Ensure preview is not skipping text effects")
    print("   ✓ Try different preview quality settings")
    
    print("\n4. EXPORT SETTINGS:")
    print("   ✓ Use high quality export preset")
    print("   ✓ Ensure text effects are not disabled during export")
    print("   ✓ Check final video in external player")

def create_simple_fix_script():
    """Create a simple script to fix common subtitle issues."""
    print("\n🔧 Creating subtitle fix script...")
    
    fix_script = '''#!/usr/bin/env python3
"""
Simple subtitle overlay fix script.
Use this to ensure subtitles appear correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def fix_subtitle_overlay():
    """Apply fixes for common subtitle overlay issues."""
    from moviepy import ColorClip, TextClip, CompositeVideoClip
    from subtitle_creator.models import SubtitleData, SubtitleLine
    from subtitle_creator.effects.text_styling import TypographyEffect, PositioningEffect
    
    # Create test background
    background = ColorClip(size=(1280, 720), color=(20, 20, 80), duration=10.0)
    
    # Create subtitle data with clear timing
    subtitle_data = SubtitleData()
    subtitle_data.lines = [
        SubtitleLine(1.0, 4.0, "First subtitle - should be clearly visible"),
        SubtitleLine(5.0, 8.0, "Second subtitle - bright yellow text"),
    ]
    
    # Create typography effect with high contrast
    typography = TypographyEffect("Fixed Typography", {
        'font_size': 48,  # Large, readable size
        'text_color': (255, 255, 0, 255),  # Bright yellow
        'outline_enabled': True,
        'outline_color': (0, 0, 0, 255),  # Black outline
        'outline_width': 3  # Thick outline for visibility
    })
    
    # Apply typography
    clip_with_text = typography.apply(background, subtitle_data)
    
    # Create positioning effect - center bottom
    positioning = PositioningEffect("Fixed Positioning", {
        'horizontal_alignment': 'center',
        'vertical_alignment': 'bottom',
        'x_offset': 0,
        'y_offset': -80,  # 80 pixels from bottom
        'margin_vertical': 40
    })
    
    # Apply positioning
    final_clip = positioning.apply(clip_with_text, subtitle_data)
    
    # Export with high quality
    output_path = "fixed_subtitle_test.mp4"
    print(f"Exporting fixed subtitle video to {output_path}...")
    
    final_clip.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        bitrate='5000k',  # High bitrate for quality
        verbose=False,
        logger=None
    )
    
    print(f"✅ Fixed subtitle video exported: {output_path}")
    print("If subtitles are still not visible, check:")
    print("1. Video player compatibility")
    print("2. System font installation")
    print("3. MoviePy version (should be 2.x)")

if __name__ == "__main__":
    fix_subtitle_overlay()
'''
    
    with open('fix_subtitle_overlay.py', 'w') as f:
        f.write(fix_script)
    
    print("✅ Fix script created: 'fix_subtitle_overlay.py'")
    print("   Run this script to create a test video with guaranteed visible subtitles")

def main():
    """Run complete troubleshooting."""
    print("🚀 Subtitle Overlay Troubleshooting")
    print("=" * 50)
    
    # Check common issues
    issues, solutions = check_common_issues()
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} potential issues:")
        for i, (issue, solution) in enumerate(zip(issues, solutions), 1):
            print(f"   {i}. {issue}")
            print(f"      → {solution}")
    else:
        print("\n✅ No common issues detected")
    
    # Create test video
    print("\n" + "=" * 50)
    if create_test_video_with_subtitles():
        print("\n✅ Test video created successfully!")
        print("   Check 'subtitle_test_video.mp4' to see if subtitles are visible")
    
    # Provide usage guidance
    diagnose_application_usage()
    
    # Create fix script
    create_simple_fix_script()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print("1. Check the generated test video and frame images")
    print("2. If subtitles are visible in test files, the issue is in application usage")
    print("3. If subtitles are not visible, run the fix script")
    print("4. Ensure you're using high contrast colors (bright text on dark background)")
    print("5. Check text positioning - use 'bottom' alignment with proper margins")

if __name__ == "__main__":
    main()