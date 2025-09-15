#!/usr/bin/env python3
"""
Configure default image duration in the Subtitle Creator application.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_image_duration_configuration():
    """Test the image duration configuration functionality."""
    print("🔧 Testing Image Duration Configuration")
    print("=" * 50)
    
    try:
        from subtitle_creator.media_manager import MediaManager
        
        # Create media manager
        media_manager = MediaManager(test_mode=True)
        
        print(f"📏 Current default image duration: {media_manager.get_default_image_duration()} seconds")
        
        # Test setting different durations
        test_durations = [30.0, 60.0, 120.0, 300.0]  # 30s, 1min, 2min, 5min
        
        for duration in test_durations:
            media_manager.set_default_image_duration(duration)
            current = media_manager.get_default_image_duration()
            print(f"✅ Set duration to {duration}s, confirmed: {current}s")
        
        print("\n🎯 USAGE IN APPLICATION:")
        print("1. The default image duration is now 60 seconds (changed from 10)")
        print("2. When you import an image, it will have a 60-second timeline")
        print("3. You can modify this by editing the MediaManager configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_image_with_custom_duration():
    """Create a video from an image with custom duration."""
    print("\n🎬 Creating Video from Image with Custom Duration")
    print("=" * 50)
    
    # Get user input
    image_path = input("Enter image file path: ").strip()
    if not image_path or not os.path.exists(image_path):
        print("❌ Invalid image path")
        return False
    
    duration_input = input("Enter duration in seconds (default: 120): ").strip()
    try:
        duration = float(duration_input) if duration_input else 120.0
    except ValueError:
        print("Invalid duration, using 120 seconds")
        duration = 120.0
    
    try:
        from moviepy import ImageClip
        
        print(f"📸 Loading image: {image_path}")
        print(f"⏱️  Setting duration: {duration} seconds")
        
        # Create video from image
        clip = ImageClip(image_path, duration=duration)
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = f"{base_name}_{int(duration)}s_video.mp4"
        
        print(f"📹 Exporting video: {output_path}")
        
        clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264'
        )
        
        print(f"✅ Video created successfully: {output_path}")
        print(f"   Duration: {duration} seconds")
        print(f"   Size: {clip.size}")
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Import '{output_path}' into the Subtitle Creator application")
        print(f"2. The timeline will show {duration} seconds")
        print(f"3. Add your subtitles with proper timing")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create video: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_solutions():
    """Show all available solutions for the image duration issue."""
    print("\n💡 SOLUTIONS FOR IMAGE DURATION ISSUE")
    print("=" * 50)
    
    print("\n🎯 PROBLEM:")
    print("When you import an image, it only shows 10 seconds in the timeline.")
    print("This is because images are converted to videos with a default duration.")
    
    print("\n✅ SOLUTION 1: Use the Modified Application")
    print("The default image duration has been increased from 10 to 60 seconds.")
    print("When you import an image now, it will have a 60-second timeline.")
    
    print("\n✅ SOLUTION 2: Create Custom Duration Video")
    print("Use the extend_image_duration.py script to create a video with any duration:")
    print("   python extend_image_duration.py")
    print("This creates an MP4 file that you can import with your desired timeline length.")
    
    print("\n✅ SOLUTION 3: Use Video Files Instead")
    print("Instead of images, use video files which have their natural duration.")
    print("You can create a video from an image using video editing software.")
    
    print("\n✅ SOLUTION 4: Modify Duration Programmatically")
    print("In the application code, you can set custom duration:")
    print("   media_manager.set_default_image_duration(300)  # 5 minutes")
    
    print("\n🔧 RECOMMENDED APPROACH:")
    print("1. For quick testing: Use the modified application (60s default)")
    print("2. For specific projects: Create custom duration videos with the script")
    print("3. For production: Use actual video files as backgrounds")

def main():
    """Main function."""
    print("🚀 IMAGE DURATION CONFIGURATION TOOL")
    print("=" * 50)
    
    # Test configuration
    if not test_image_duration_configuration():
        return
    
    # Show solutions
    show_solutions()
    
    # Ask if user wants to create a custom duration video
    print("\n" + "=" * 50)
    create_video = input("Do you want to create a video from an image with custom duration? (y/n): ").strip().lower()
    
    if create_video in ['y', 'yes']:
        create_image_with_custom_duration()
    
    print("\n🎉 SUMMARY:")
    print("- Default image duration changed from 10s to 60s")
    print("- You can create custom duration videos using the provided scripts")
    print("- Import the generated MP4 files for longer timelines")

if __name__ == "__main__":
    main()