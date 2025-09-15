#!/usr/bin/env python3
"""
Simple launcher for the karaoke video creator
Provides an easy way to get started with creating karaoke videos
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n=== Installing Dependencies ===")
    
    dependencies = [
        "matplotlib",
        "numpy", 
        "pillow",
        "moviepy"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✓ {dep} already installed")
        except ImportError:
            print(f"Installing {dep}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ {dep} installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {dep}")
                return False
    
    return True

def show_menu():
    """Show the main menu"""
    print("\n" + "="*50)
    print("🎤 KARAOKE VIDEO CREATOR")
    print("="*50)
    print()
    print("Choose an option:")
    print("1. Create karaoke video (with GUI)")
    print("2. Create karaoke video (automated script)")
    print("3. Create preview images only")
    print("4. View existing examples")
    print("5. Install/check dependencies")
    print("6. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return int(choice)
            else:
                print("Please enter a number between 1 and 6")
        except KeyboardInterrupt:
            print("\nExiting...")
            return 6

def launch_gui():
    """Launch the GUI application"""
    print("\n=== Launching GUI Application ===")
    
    gui_script = "src/subtitle_creator/main.py"
    if not os.path.exists(gui_script):
        print(f"❌ GUI script not found: {gui_script}")
        print("Make sure you're running this from the project root directory")
        return False
    
    try:
        print("Starting GUI application...")
        print("(Close the GUI window to return to this menu)")
        subprocess.run([sys.executable, gui_script])
        return True
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return False

def run_automated_script():
    """Run the automated karaoke creation script"""
    print("\n=== Automated Karaoke Creation ===")
    
    # Check if audio file exists
    audio_file = input("Enter path to audio file (or press Enter to skip): ").strip()
    if audio_file and not os.path.exists(audio_file):
        print(f"⚠ Audio file not found: {audio_file}")
        audio_file = ""
    
    # Get duration
    try:
        duration = int(input("Enter video duration in seconds (default 60): ") or "60")
    except ValueError:
        duration = 60
    
    # Build command
    cmd = [sys.executable, "create_karaoke_video.py", "--duration", str(duration)]
    if audio_file:
        cmd.extend(["--audio", audio_file])
    
    print(f"\nRunning: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd)
        return True
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def create_preview_only():
    """Create preview images only"""
    print("\n=== Creating Preview Images ===")
    
    cmd = [sys.executable, "create_karaoke_video.py", "--preview-only"]
    
    try:
        subprocess.run(cmd)
        return True
    except Exception as e:
        print(f"❌ Error creating previews: {e}")
        return False

def view_examples():
    """Show existing examples"""
    print("\n=== Existing Examples ===")
    
    # Check for generated files
    examples = []
    
    # Check for preview images
    if os.path.exists("karaoke_preview"):
        preview_files = list(Path("karaoke_preview").glob("*.png"))
        if preview_files:
            examples.append(f"Preview images: {len(preview_files)} files in karaoke_preview/")
    
    # Check for generated videos
    video_files = list(Path(".").glob("*.mp4"))
    if video_files:
        examples.append(f"Video files: {', '.join([f.name for f in video_files])}")
    
    # Check for subtitle files
    subtitle_files = list(Path(".").glob("*.srt")) + list(Path(".").glob("*.vtt"))
    if subtitle_files:
        examples.append(f"Subtitle files: {', '.join([f.name for f in subtitle_files])}")
    
    # Check for Dancing in Your Eyes data
    if os.path.exists("examples/Dancing in Your Eyes.json"):
        examples.append("Sample data: examples/Dancing in Your Eyes.json")
    
    if examples:
        print("Found examples:")
        for example in examples:
            print(f"  ✓ {example}")
    else:
        print("No examples found yet. Create some using options 1-3!")
    
    print("\nTo view preview images, open the files in karaoke_preview/ folder")
    print("To play videos, use any video player that supports MP4")

def main():
    """Main launcher function"""
    print("🎤 Karaoke Video Creator Launcher")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    while True:
        choice = show_menu()
        
        if choice == 1:
            # GUI Application
            launch_gui()
            
        elif choice == 2:
            # Automated script
            run_automated_script()
            
        elif choice == 3:
            # Preview only
            create_preview_only()
            
        elif choice == 4:
            # View examples
            view_examples()
            
        elif choice == 5:
            # Install dependencies
            install_dependencies()
            
        elif choice == 6:
            # Exit
            print("Goodbye! 🎵")
            break
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye! 🎵")
        sys.exit(0)