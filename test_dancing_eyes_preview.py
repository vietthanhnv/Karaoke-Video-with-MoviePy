#!/usr/bin/env python3
"""
Test script to import Dancing in Your Eyes.json and show subtitle overlay preview
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from moviepy.editor import *
    from moviepy.video.tools.drawing import color_gradient
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.animation import FuncAnimation
    print("✓ All required libraries imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Installing required packages...")
    os.system("pip install moviepy pillow matplotlib numpy")
    sys.exit(1)

class DancingEyesSubtitleTest:
    def __init__(self, json_file="examples/Dancing in Your Eyes.json"):
        self.json_file = json_file
        self.subtitle_data = None
        self.video_width = 1280
        self.video_height = 720
        self.fps = 24
        
    def load_subtitle_data(self):
        """Load subtitle data from JSON file"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.subtitle_data = json.load(f)
            print(f"✓ Loaded subtitle data: {len(self.subtitle_data['segments'])} segments")
            print(f"  Audio duration: {self.subtitle_data['metadata']['audio_duration']:.2f}s")
            print(f"  Total words: {self.subtitle_data['metadata']['total_words']}")
            return True
        except Exception as e:
            print(f"✗ Error loading subtitle data: {e}")
            return False
    
    def create_background_video(self, duration=30):
        """Create a simple animated background for testing"""
        def make_frame(t):
            # Create gradient background that changes over time
            frame = np.zeros((self.video_height, self.video_width, 3), dtype=np.uint8)
            
            # Animated gradient
            for y in range(self.video_height):
                for x in range(self.video_width):
                    # Create moving gradient effect
                    r = int(128 + 127 * np.sin(t * 0.5 + x * 0.01))
                    g = int(128 + 127 * np.sin(t * 0.3 + y * 0.01))
                    b = int(64 + 64 * np.sin(t * 0.7))
                    frame[y, x] = [r, g, b]
            
            return frame
        
        return VideoClip(make_frame, duration=duration)
    
    def create_subtitle_clip(self, text, start_time, end_time, position='center'):
        """Create a subtitle text clip with styling"""
        duration = end_time - start_time
        
        def make_text_frame(t):
            # Create transparent background
            img = Image.new('RGBA', (self.video_width, self.video_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fallback to default
            try:
                font_size = 48
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.load_default()
                    font_size = 24
                except:
                    font = None
                    font_size = 24
            
            # Calculate text position
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                # Estimate text size
                text_width = len(text) * font_size * 0.6
                text_height = font_size
            
            # Position text
            if position == 'center':
                x = (self.video_width - text_width) // 2
                y = self.video_height - 150  # Bottom area
            else:
                x, y = position
            
            # Add text shadow for better visibility
            shadow_offset = 2
            if font:
                draw.text((x + shadow_offset, y + shadow_offset), text, 
                         fill=(0, 0, 0, 180), font=font)
                draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            else:
                # Fallback without font
                draw.text((x + shadow_offset, y + shadow_offset), text, 
                         fill=(0, 0, 0, 180))
                draw.text((x, y), text, fill=(255, 255, 255, 255))
            
            # Convert PIL image to numpy array
            frame = np.array(img)
            return frame
        
        return VideoClip(make_text_frame, duration=duration).set_start(start_time)
    
    def create_preview_video(self, duration=30, output_file="dancing_eyes_preview.mp4"):
        """Create a preview video with subtitle overlay"""
        if not self.subtitle_data:
            print("✗ No subtitle data loaded")
            return False
        
        print(f"Creating preview video ({duration}s)...")
        
        # Create background
        background = self.create_background_video(duration)
        
        # Create subtitle clips for the preview duration
        subtitle_clips = []
        segments = self.subtitle_data['segments']
        
        for segment in segments:
            start_time = segment['start_time']
            end_time = segment['end_time']
            text = segment['text']
            
            # Only include segments within our preview duration
            if start_time < duration and text != "[No text]":
                # Adjust end time if it exceeds preview duration
                actual_end_time = min(end_time, duration)
                
                if actual_end_time > start_time:
                    subtitle_clip = self.create_subtitle_clip(text, start_time, actual_end_time)
                    subtitle_clips.append(subtitle_clip)
                    print(f"  Added subtitle: {start_time:.1f}s-{actual_end_time:.1f}s: '{text[:50]}...'")
        
        # Composite all clips
        if subtitle_clips:
            final_video = CompositeVideoClip([background] + subtitle_clips)
        else:
            final_video = background
            print("⚠ No subtitles found in preview duration")
        
        # Export video
        try:
            print(f"Exporting to {output_file}...")
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio=False,
                verbose=False,
                logger=None
            )
            print(f"✓ Preview video created: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Error creating video: {e}")
            return False
    
    def create_static_preview_frames(self, times=[25, 30, 35, 40]):
        """Create static preview frames at specific times"""
        if not self.subtitle_data:
            print("✗ No subtitle data loaded")
            return False
        
        print("Creating static preview frames...")
        
        for time_point in times:
            # Find active subtitle at this time
            active_text = ""
            for segment in self.subtitle_data['segments']:
                if segment['start_time'] <= time_point <= segment['end_time']:
                    active_text = segment['text']
                    break
            
            # Create frame
            fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
            
            # Create gradient background
            gradient = np.linspace(0, 1, 256).reshape(1, -1)
            gradient = np.vstack((gradient, gradient))
            
            # Create colorful background
            x = np.linspace(0, 1, self.video_width)
            y = np.linspace(0, 1, self.video_height)
            X, Y = np.meshgrid(x, y)
            
            # Animated gradient based on time
            R = 0.5 + 0.5 * np.sin(time_point * 0.5 + X * 10)
            G = 0.5 + 0.5 * np.sin(time_point * 0.3 + Y * 10)
            B = 0.3 + 0.3 * np.sin(time_point * 0.7)
            
            background_img = np.stack([R, G, B], axis=2)
            
            ax.imshow(background_img, extent=[0, self.video_width, 0, self.video_height])
            
            # Add subtitle if active
            if active_text and active_text != "[No text]":
                # Add text with shadow effect
                ax.text(self.video_width/2, 150, active_text, 
                       fontsize=24, color='black', ha='center', va='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.3))
                ax.text(self.video_width/2, 150, active_text, 
                       fontsize=24, color='white', ha='center', va='center')
                
                print(f"  Frame at {time_point}s: '{active_text[:50]}...'")
            else:
                print(f"  Frame at {time_point}s: (no subtitle)")
            
            ax.set_xlim(0, self.video_width)
            ax.set_ylim(0, self.video_height)
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Save frame
            frame_file = f"dancing_eyes_frame_t{time_point}s.png"
            plt.savefig(frame_file, bbox_inches='tight', pad_inches=0, dpi=100)
            plt.close()
            
            print(f"✓ Saved frame: {frame_file}")
        
        return True
    
    def show_subtitle_timeline(self):
        """Display subtitle timeline visualization"""
        if not self.subtitle_data:
            print("✗ No subtitle data loaded")
            return False
        
        print("Creating subtitle timeline...")
        
        fig, ax = plt.subplots(figsize=(15, 8))
        
        segments = self.subtitle_data['segments']
        y_positions = []
        
        for i, segment in enumerate(segments):
            start_time = segment['start_time']
            end_time = segment['end_time']
            text = segment['text']
            confidence = segment['confidence']
            
            # Color based on confidence
            color = plt.cm.RdYlGn(confidence)
            
            # Create rectangle for segment
            rect = patches.Rectangle((start_time, i), end_time - start_time, 0.8,
                                   linewidth=1, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
            
            # Add text label
            ax.text(start_time + (end_time - start_time) / 2, i + 0.4, 
                   text[:30] + "..." if len(text) > 30 else text,
                   ha='center', va='center', fontsize=8, weight='bold')
            
            y_positions.append(f"Segment {i}")
        
        ax.set_xlim(0, max(seg['end_time'] for seg in segments))
        ax.set_ylim(-0.5, len(segments) - 0.5)
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Subtitle Segments')
        ax.set_title('Dancing in Your Eyes - Subtitle Timeline\n(Color indicates confidence: Red=Low, Green=High)')
        ax.set_yticks(range(len(segments)))
        ax.set_yticklabels(y_positions)
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, 
                                  norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Confidence Score')
        
        plt.tight_layout()
        timeline_file = "dancing_eyes_timeline.png"
        plt.savefig(timeline_file, dpi=150, bbox_inches='tight')
        plt.show()
        
        print(f"✓ Timeline saved: {timeline_file}")
        return True

def main():
    """Main test function"""
    print("=== Dancing in Your Eyes Subtitle Preview Test ===\n")
    
    # Initialize test
    test = DancingEyesSubtitleTest()
    
    # Load subtitle data
    if not test.load_subtitle_data():
        return False
    
    # Show some statistics
    segments = test.subtitle_data['segments']
    print(f"\nSubtitle Statistics:")
    print(f"  Total segments: {len(segments)}")
    print(f"  Duration range: {segments[0]['start_time']:.1f}s - {segments[-1]['end_time']:.1f}s")
    print(f"  Average confidence: {test.subtitle_data['metadata']['average_confidence']:.3f}")
    
    # Show first few segments
    print(f"\nFirst 5 segments:")
    for i, segment in enumerate(segments[:5]):
        print(f"  {i+1}. {segment['start_time']:.1f}s-{segment['end_time']:.1f}s: '{segment['text']}'")
    
    # Create timeline visualization
    print(f"\n--- Creating Timeline Visualization ---")
    test.show_subtitle_timeline()
    
    # Create static preview frames
    print(f"\n--- Creating Static Preview Frames ---")
    test.create_static_preview_frames()
    
    # Create video preview (shorter duration for testing)
    print(f"\n--- Creating Video Preview ---")
    success = test.create_preview_video(duration=45)  # First 45 seconds
    
    if success:
        print(f"\n✓ All tests completed successfully!")
        print(f"Generated files:")
        print(f"  - dancing_eyes_timeline.png (timeline visualization)")
        print(f"  - dancing_eyes_frame_t*.png (preview frames)")
        print(f"  - dancing_eyes_preview.mp4 (video with subtitles)")
    else:
        print(f"\n⚠ Some tests failed, but static previews should be available")
    
    return success

if __name__ == "__main__":
    main()