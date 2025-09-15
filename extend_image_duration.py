#!/usr/bin/env python3
"""
Script to extend image duration for subtitle creation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def extend_image_duration(image_path, desired_duration=60.0):
    """
    Create a video from an image with specified duration.
    
    Args:
        image_path: Path to the image file
        desired_duration: Duration in seconds (default: 60 seconds)
    """
    try:
        from moviepy import ImageClip
        
        print(f"🖼️  Loading image: {image_path}")
        print(f"⏱️  Setting duration: {desired_duration} seconds")
        
        # Create ImageClip with custom duration
        clip = ImageClip(image_path, duration=desired_duration)
        
        print(f"✅ Image loaded successfully")
        print(f"   - Size: {clip.size}")
        print(f"   - Duration: {clip.duration} seconds")
        
        # Export as video for use in the application
        output_path = f"extended_{os.path.splitext(os.path.basename(image_path))[0]}_{int(desired_duration)}s.mp4"
        
        print(f"📹 Exporting as video: {output_path}")
        
        clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264'
        )
        
        print(f"✅ Video created: {output_path}")
        print(f"   You can now import this video file into the application")
        print(f"   It will have a timeline of {desired_duration} seconds")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Failed to extend image duration: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function to extend image duration."""
    print("🚀 IMAGE DURATION EXTENDER")
    print("=" * 50)
    
    # Example usage
    print("This script converts an image to a video with custom duration.")
    print("Usage examples:")
    print("1. For 30 seconds: extend_image_duration('image.jpg', 30)")
    print("2. For 2 minutes: extend_image_duration('image.jpg', 120)")
    print("3. For 5 minutes: extend_image_duration('image.jpg', 300)")
    
    # You can modify these values
    image_file = input("\nEnter image file path (or press Enter for example): ").strip()
    
    if not image_file:
        print("No image file specified. Creating example...")
        # Create a test image if none specified
        try:
            from PIL import Image
            import numpy as np
            
            # Create a simple gradient image
            width, height = 1280, 720
            image_array = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Create gradient
            for y in range(height):
                for x in range(width):
                    image_array[y, x] = [
                        int(255 * x / width),  # Red gradient
                        int(255 * y / height),  # Green gradient
                        100  # Blue constant
                    ]
            
            img = Image.fromarray(image_array)
            img.save('test_background.png')
            image_file = 'test_background.png'
            print(f"✅ Created test image: {image_file}")
            
        except Exception as e:
            print(f"❌ Could not create test image: {e}")
            return
    
    if not os.path.exists(image_file):
        print(f"❌ Image file not found: {image_file}")
        return
    
    # Get desired duration
    duration_input = input("Enter desired duration in seconds (default: 60): ").strip()
    
    try:
        duration = float(duration_input) if duration_input else 60.0
    except ValueError:
        print("Invalid duration, using default 60 seconds")
        duration = 60.0
    
    # Extend the image duration
    result = extend_image_duration(image_file, duration)
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"Import '{result}' into your subtitle application")
        print(f"It will have a {duration}-second timeline for your subtitles")

if __name__ == "__main__":
    main()