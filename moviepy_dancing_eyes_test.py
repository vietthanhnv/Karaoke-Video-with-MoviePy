#!/usr/bin/env python3
"""
MoviePy test to create actual video with Dancing in Your Eyes subtitle overlay
"""

import json
import sys
import os
from pathlib import Path

def test_moviepy_import():
    """Test MoviePy import and create video with subtitles"""
    try:
        import moviepy.editor as mp
        import numpy as np
        print("✓ MoviePy imported successfully")
        return True
    except ImportError as e:
        print(f"✗ MoviePy import failed: {e}")
        return False

def load_subtitle_data(json_file="examples/Dancing in Your Eyes.json"):
    """Load subtitle data from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded subtitle data: {len(data['segments'])} segments")
        return data
    except Exception as e:
        print(f"✗ Error loading subtitle data: {e}")
        return None

def create_background_clip(duration=30, size=(1280, 720)):
    """Create animated background clip"""
    import moviepy.editor as mp
    import numpy as np
    
    def make_frame(t):
        # Create animated gradient background
        h, w = size[1], size[0]
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Create moving gradient effect
        for y in range(h):
            for x in range(w):
                # Animated colors based on time and position
                r = int(128 + 100 * np.sin(t * 0.5 + x * 0.005 + y * 0.003))
                g = int(128 + 100 * np.sin(t * 0.3 + x * 0.007 + y * 0.002))
                b = int(100 + 80 * np.sin(t * 0.7 + x * 0.004))
                
                # Clamp values to valid range
                frame[y, x] = [max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))]
        
        return frame
    
    return mp.VideoClip(make_frame, duration=duration)

def create_subtitle_clip(text, start_time, end_time, size=(1280, 720)):
    """Create subtitle text clip with MoviePy"""
    import moviepy.editor as mp
    
    duration = end_time - start_time
    
    # Create text clip with styling
    try:
        # Try to create text clip with custom font
        txt_clip = mp.TextClip(text, 
                           fontsize=48, 
                           color='white', 
                           font='Arial-Bold',
                           stroke_color='black',
                           stroke_width=2)
    except:
        # Fallback to default font
        txt_clip = mp.TextClip(text, 
                           fontsize=48, 
                           color='white')
    
    # Position at bottom center
    txt_clip = txt_clip.set_position(('center', size[1] - 150)).set_duration(duration)
    
    return txt_clip

def create_video_with_subtitles(subtitle_data, duration=45, output_file="dancing_eyes_with_subtitles.mp4"):
    """Create video with subtitle overlay using MoviePy"""
    
    if not test_moviepy_import():
        return False
    
    import moviepy.editor as mp
    
    print(f"Creating video with subtitles ({duration}s)...")
    
    # Create background
    background = create_background_clip(duration)
    
    # Create subtitle clips
    subtitle_clips = []
    segments = subtitle_data['segments']
    
    for segment in segments:
        start_time = segment['start_time']
        end_time = segment['end_time']
        text = segment['text']
        
        # Only include segments within our video duration
        if start_time < duration and text != "[No text]":
            # Adjust end time if it exceeds video duration
            actual_end_time = min(end_time, duration)
            
            if actual_end_time > start_time:
                try:
                    subtitle_clip = create_subtitle_clip(text, start_time, actual_end_time)
                    subtitle_clip = subtitle_clip.set_start(start_time)
                    subtitle_clips.append(subtitle_clip)
                    print(f"  Added subtitle: {start_time:.1f}s-{actual_end_time:.1f}s: '{text[:50]}...'")
                except Exception as e:
                    print(f"  ⚠ Failed to create subtitle for: '{text[:30]}...' - {e}")
    
    # Composite all clips
    if subtitle_clips:
        final_video = mp.CompositeVideoClip([background] + subtitle_clips)
        print(f"✓ Created composite video with {len(subtitle_clips)} subtitle clips")
    else:
        final_video = background
        print("⚠ No subtitles added to video")
    
    # Export video
    try:
        print(f"Exporting to {output_file}...")
        final_video.write_videofile(
            output_file,
            fps=24,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None,
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        print(f"✓ Video exported successfully: {output_file}")
        return True
    except Exception as e:
        print(f"✗ Error exporting video: {e}")
        return False

def create_simple_test_video():
    """Create a simple test video to verify MoviePy is working"""
    
    if not test_moviepy_import():
        return False
    
    import moviepy.editor as mp
    import numpy as np
    
    print("Creating simple test video...")
    
    try:
        # Create a simple colored background
        def make_frame(t):
            # Simple color animation
            color = [int(128 + 127 * np.sin(t)), 100, int(128 + 127 * np.cos(t))]
            frame = np.full((360, 640, 3), color, dtype=np.uint8)
            return frame
        
        # Create 5-second test clip
        clip = mp.VideoClip(make_frame, duration=5)
        
        # Add simple text
        txt = mp.TextClip("MoviePy Test", fontsize=50, color='white').set_duration(5).set_position('center')
        
        # Composite
        final = mp.CompositeVideoClip([clip, txt])
        
        # Export
        final.write_videofile("moviepy_test.mp4", fps=24, verbose=False, logger=None)
        print("✓ Simple test video created: moviepy_test.mp4")
        return True
        
    except Exception as e:
        print(f"✗ Error creating test video: {e}")
        return False

def main():
    """Main test function"""
    print("=== MoviePy Dancing in Your Eyes Test ===\n")
    
    # Test MoviePy import
    if not test_moviepy_import():
        print("MoviePy not available, creating simple preview instead...")
        os.system("python simple_dancing_eyes_test.py")
        return False
    
    # Load subtitle data
    subtitle_data = load_subtitle_data()
    if not subtitle_data:
        return False
    
    # Create simple test first
    print("\n--- Creating Simple Test Video ---")
    if not create_simple_test_video():
        print("Simple test failed, MoviePy may have issues")
        return False
    
    # Create video with subtitles
    print("\n--- Creating Video with Subtitles ---")
    success = create_video_with_subtitles(subtitle_data, duration=45)
    
    if success:
        print(f"\n✓ All tests completed successfully!")
        print(f"Generated files:")
        print(f"  - moviepy_test.mp4 (simple test)")
        print(f"  - dancing_eyes_with_subtitles.mp4 (with subtitle overlay)")
        print(f"\nYou can now play these videos to see the subtitle overlay in action!")
    else:
        print(f"\n⚠ Video creation failed, but you can still view the static previews")
        print(f"Run: python simple_dancing_eyes_test.py")
    
    return success

if __name__ == "__main__":
    main()