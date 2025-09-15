#!/usr/bin/env python3
"""
Simple script to create a karaoke video from Dancing in Your Eyes data
This provides an automated way to generate karaoke videos without the GUI
"""

import json
import os
import sys
from pathlib import Path
import argparse

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    try:
        import matplotlib.pyplot as plt
        print("✓ matplotlib available")
    except ImportError:
        missing.append("matplotlib")
    
    try:
        import numpy as np
        print("✓ numpy available")
    except ImportError:
        missing.append("numpy")
    
    try:
        import PIL
        print("✓ Pillow available")
    except ImportError:
        missing.append("pillow")
    
    # Check for MoviePy (optional for video creation)
    try:
        import moviepy.editor as mp
        print("✓ MoviePy available - video creation enabled")
        return missing, True
    except ImportError:
        print("⚠ MoviePy not available - will create preview images only")
        return missing, False

def load_subtitle_data(json_file):
    """Load subtitle data from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded subtitle data: {len(data['segments'])} segments")
        return data
    except Exception as e:
        print(f"✗ Error loading subtitle data: {e}")
        return None

def create_karaoke_video_with_moviepy(subtitle_data, audio_file=None, output_file="karaoke_video.mp4", duration=60):
    """Create karaoke video using MoviePy"""
    
    try:
        import moviepy.editor as mp
        import numpy as np
        
        print(f"Creating karaoke video ({duration}s)...")
        
        # Create animated background
        def make_background_frame(t):
            # Create gradient background that changes over time
            width, height = 1280, 720
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Animated gradient
            for y in range(0, height, 4):  # Skip pixels for performance
                for x in range(0, width, 4):
                    r = int(128 + 100 * np.sin(t * 0.3 + x * 0.003 + y * 0.002))
                    g = int(128 + 100 * np.sin(t * 0.2 + x * 0.004 + y * 0.001))
                    b = int(100 + 80 * np.sin(t * 0.5 + x * 0.002))
                    
                    # Fill 4x4 blocks for performance
                    frame[y:y+4, x:x+4] = [
                        max(0, min(255, r)), 
                        max(0, min(255, g)), 
                        max(0, min(255, b))
                    ]
            
            return frame
        
        # Create background video
        background = mp.VideoClip(make_background_frame, duration=duration)
        
        # Create subtitle clips
        subtitle_clips = []
        segments = subtitle_data['segments']
        
        for segment in segments:
            start_time = segment['start_time']
            end_time = segment['end_time']
            text = segment['text']
            
            # Only include segments within video duration
            if start_time < duration and text != "[No text]":
                actual_end_time = min(end_time, duration)
                
                if actual_end_time > start_time:
                    try:
                        # Create text clip
                        txt_clip = mp.TextClip(
                            text,
                            fontsize=50,
                            color='white',
                            stroke_color='black',
                            stroke_width=3,
                            method='caption',
                            size=(1200, None)
                        ).set_position(('center', 'bottom')).set_duration(actual_end_time - start_time).set_start(start_time)
                        
                        subtitle_clips.append(txt_clip)
                        print(f"  Added: {start_time:.1f}s-{actual_end_time:.1f}s: '{text[:40]}...'")
                        
                    except Exception as e:
                        print(f"  ⚠ Failed to create subtitle: {e}")
        
        # Composite video
        if subtitle_clips:
            final_video = mp.CompositeVideoClip([background] + subtitle_clips)
        else:
            final_video = background
        
        # Add audio if provided
        if audio_file and os.path.exists(audio_file):
            try:
                audio = mp.AudioFileClip(audio_file).subclip(0, duration)
                final_video = final_video.set_audio(audio)
                print(f"✓ Added audio from: {audio_file}")
            except Exception as e:
                print(f"⚠ Could not add audio: {e}")
        
        # Export video
        print(f"Exporting to {output_file}...")
        final_video.write_videofile(
            output_file,
            fps=24,
            codec='libx264',
            verbose=False,
            logger=None
        )
        
        print(f"✓ Karaoke video created: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating video: {e}")
        return False

def create_preview_images(subtitle_data, output_dir="karaoke_preview"):
    """Create preview images showing subtitle overlay"""
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating preview images in {output_dir}/...")
    
    # Select key time points
    segments = [s for s in subtitle_data['segments'] if s['text'] != "[No text]"]
    preview_times = []
    
    # Take every 3rd segment for preview
    for i in range(0, min(len(segments), 12), 2):
        preview_times.append(segments[i]['start_time'] + 1)  # 1 second into segment
    
    for i, time_point in enumerate(preview_times):
        # Find active subtitle
        active_text = ""
        for segment in segments:
            if segment['start_time'] <= time_point <= segment['end_time']:
                active_text = segment['text']
                break
        
        # Create preview frame
        fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
        
        # Create background
        width, height = 1280, 720
        x = np.linspace(0, 1, 64)
        y = np.linspace(0, 1, 36)
        X, Y = np.meshgrid(x, y)
        
        # Animated gradient
        R = 0.3 + 0.4 * np.sin(time_point * 0.3 + X * 5)
        G = 0.2 + 0.5 * np.sin(time_point * 0.2 + Y * 4)
        B = 0.4 + 0.3 * np.sin(time_point * 0.5 + (X + Y) * 3)
        
        background = np.stack([R, G, B], axis=2)
        ax.imshow(background, extent=[0, width, 0, height], aspect='auto')
        
        # Add subtitle if active
        if active_text:
            # Subtitle background
            subtitle_y = 120
            rect = patches.Rectangle((40, subtitle_y - 30), width - 80, 80,
                                   linewidth=0, facecolor='black', alpha=0.7)
            ax.add_patch(rect)
            
            # Subtitle text with word wrapping
            words = active_text.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 50:  # Wrap at ~50 characters
                    if len(current_line) > 1:
                        lines.append(' '.join(current_line[:-1]))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Display lines
            for j, line in enumerate(lines):
                y_pos = subtitle_y + (len(lines) - 1 - j) * 25
                ax.text(width/2, y_pos, line, 
                       fontsize=24, color='white', ha='center', va='center',
                       weight='bold', 
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.3))
            
            # Time info
            ax.text(width/2, 40, f"Time: {time_point:.1f}s", 
                   fontsize=14, color='yellow', ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='purple', alpha=0.8))
        
        # Title
        ax.text(width/2, height - 40, "Dancing in Your Eyes - Karaoke Preview", 
               fontsize=18, color='white', ha='center', va='center',
               weight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='darkblue', alpha=0.8))
        
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.axis('off')
        
        # Save frame
        output_file = f"{output_dir}/karaoke_frame_{i+1:02d}_t{time_point:.1f}s.png"
        plt.savefig(output_file, bbox_inches='tight', pad_inches=0, dpi=100)
        plt.close()
        
        print(f"  ✓ Created: {output_file}")
    
    print(f"✓ Created {len(preview_times)} preview images")
    return True

def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(description="Create karaoke video from Dancing in Your Eyes data")
    parser.add_argument("--audio", "-a", help="Audio file path (MP3, WAV, etc.)")
    parser.add_argument("--output", "-o", default="dancing_eyes_karaoke.mp4", help="Output video file")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Video duration in seconds")
    parser.add_argument("--preview-only", "-p", action="store_true", help="Create preview images only")
    parser.add_argument("--json", "-j", default="examples/Dancing in Your Eyes.json", help="Subtitle JSON file")
    
    args = parser.parse_args()
    
    print("=== Karaoke Video Creator ===\n")
    
    # Check dependencies
    missing_deps, has_moviepy = check_dependencies()
    
    if missing_deps:
        print(f"\n⚠ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        if not args.preview_only:
            return 1
    
    # Load subtitle data
    subtitle_data = load_subtitle_data(args.json)
    if not subtitle_data:
        return 1
    
    print(f"\nSubtitle info:")
    print(f"  Duration: {subtitle_data['metadata']['audio_duration']:.1f}s")
    print(f"  Segments: {len(subtitle_data['segments'])}")
    print(f"  Words: {subtitle_data['metadata']['total_words']}")
    
    # Create preview images
    print(f"\n--- Creating Preview Images ---")
    create_preview_images(subtitle_data)
    
    # Create video if MoviePy is available and not preview-only
    if has_moviepy and not args.preview_only:
        print(f"\n--- Creating Karaoke Video ---")
        success = create_karaoke_video_with_moviepy(
            subtitle_data, 
            args.audio, 
            args.output, 
            args.duration
        )
        
        if success:
            print(f"\n✓ Karaoke video creation completed!")
            print(f"Output files:")
            print(f"  - {args.output} (karaoke video)")
            print(f"  - karaoke_preview/ (preview images)")
            
            if args.audio:
                print(f"  - Audio: {args.audio}")
            else:
                print(f"  - No audio added (use --audio to add audio track)")
        else:
            print(f"\n⚠ Video creation failed, but preview images are available")
    else:
        print(f"\n✓ Preview images created successfully!")
        print(f"To create video: pip install moviepy, then run again without --preview-only")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())