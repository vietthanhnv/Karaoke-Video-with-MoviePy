#!/usr/bin/env python3
"""
Improved karaoke video creator that doesn't rely on ImageMagick
Uses PIL/Pillow for text rendering instead of MoviePy's TextClip
"""

import json
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse

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

def create_text_image(text, width=1280, height=720, font_size=48):
    """Create an image with text overlay using PIL"""
    
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fall back to default if not available
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except:
            # Fall back to default font
            font = ImageFont.load_default()
    
    # Word wrap the text
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= width - 100:  # Leave margin
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)  # Single word too long
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Calculate total text height
    line_height = font_size + 10
    total_height = len(lines) * line_height
    
    # Position text at bottom center
    start_y = height - total_height - 50
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = start_y + i * line_height
        
        # Draw text with outline for better visibility
        outline_width = 3
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
        
        # Draw main text
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    
    return img

def create_background_frame(t, width=1280, height=720):
    """Create animated background frame"""
    
    # Create gradient background
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            # Animated gradient
            r = int(128 + 100 * np.sin(t * 0.3 + x * 0.003 + y * 0.002))
            g = int(128 + 100 * np.sin(t * 0.2 + x * 0.004 + y * 0.001))
            b = int(100 + 80 * np.sin(t * 0.5 + x * 0.002))
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            pixels[x, y] = (r, g, b)
    
    return img

def create_karaoke_video_pil(subtitle_data, audio_file=None, output_file="karaoke_video.mp4", duration=60, fps=24):
    """Create karaoke video using PIL for text and MoviePy for video composition"""
    
    try:
        import moviepy.editor as mp
        
        print(f"Creating karaoke video with PIL text rendering ({duration}s)...")
        
        # Create frame generator function
        def make_frame(t):
            # Create background
            bg_img = create_background_frame(t)
            
            # Find active subtitle
            active_text = ""
            for segment in subtitle_data['segments']:
                if segment['start_time'] <= t <= segment['end_time'] and segment['text'] != "[No text]":
                    active_text = segment['text']
                    break
            
            # Add subtitle if active
            if active_text:
                text_img = create_text_image(active_text)
                # Composite text over background
                bg_img.paste(text_img, (0, 0), text_img)
            
            # Convert PIL image to numpy array for MoviePy
            return np.array(bg_img)
        
        # Create video clip
        video_clip = mp.VideoClip(make_frame, duration=duration)
        
        # Add audio if provided
        if audio_file and os.path.exists(audio_file):
            try:
                audio = mp.AudioFileClip(audio_file).subclip(0, duration)
                video_clip = video_clip.set_audio(audio)
                print(f"✓ Added audio from: {audio_file}")
            except Exception as e:
                print(f"⚠ Could not add audio: {e}")
        
        # Export video
        print(f"Exporting to {output_file}...")
        video_clip.write_videofile(
            output_file,
            fps=fps,
            codec='libx264',
            verbose=False,
            logger=None
        )
        
        print(f"✓ Karaoke video created successfully: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(description="Create karaoke video with improved text rendering")
    parser.add_argument("--json", "-j", default="examples/Dancing in Your Eyes.json", help="Subtitle JSON file")
    parser.add_argument("--audio", "-a", help="Audio file path")
    parser.add_argument("--output", "-o", default="improved_karaoke.mp4", help="Output video file")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Video duration in seconds")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second")
    
    args = parser.parse_args()
    
    print("=== Improved Karaoke Video Creator ===\n")
    
    # Check MoviePy
    try:
        import moviepy.editor as mp
        print("✓ MoviePy available")
    except ImportError:
        print("✗ MoviePy not available")
        return 1
    
    # Load subtitle data
    subtitle_data = load_subtitle_data(args.json)
    if not subtitle_data:
        return 1
    
    print(f"\nSubtitle info:")
    print(f"  Duration: {subtitle_data['metadata']['audio_duration']:.1f}s")
    print(f"  Segments: {len(subtitle_data['segments'])}")
    
    # Create video
    success = create_karaoke_video_pil(
        subtitle_data,
        args.audio,
        args.output,
        args.duration,
        args.fps
    )
    
    if success:
        print(f"\n✓ Video creation completed!")
        print(f"Output: {args.output}")
        if args.audio:
            print(f"Audio: {args.audio}")
    else:
        print(f"\n✗ Video creation failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())