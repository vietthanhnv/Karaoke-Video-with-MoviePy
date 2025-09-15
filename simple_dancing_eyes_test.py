#!/usr/bin/env python3
"""
Simple test to import Dancing in Your Eyes.json and create preview frames
"""

import json
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def load_subtitle_data(json_file="examples/Dancing in Your Eyes.json"):
    """Load subtitle data from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded subtitle data: {len(data['segments'])} segments")
        print(f"  Audio duration: {data['metadata']['audio_duration']:.2f}s")
        print(f"  Total words: {data['metadata']['total_words']}")
        return data
    except Exception as e:
        print(f"✗ Error loading subtitle data: {e}")
        return None

def create_preview_frame(subtitle_data, time_point, output_file):
    """Create a preview frame with subtitle overlay at specific time"""
    
    # Find active subtitle at this time
    active_text = ""
    active_segment = None
    
    for segment in subtitle_data['segments']:
        if segment['start_time'] <= time_point <= segment['end_time']:
            active_text = segment['text']
            active_segment = segment
            break
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    
    # Create animated gradient background
    width, height = 1280, 720
    x = np.linspace(0, 1, width//4)  # Reduced resolution for performance
    y = np.linspace(0, 1, height//4)
    X, Y = np.meshgrid(x, y)
    
    # Create colorful animated background
    R = 0.3 + 0.4 * np.sin(time_point * 0.5 + X * 8)
    G = 0.2 + 0.5 * np.sin(time_point * 0.3 + Y * 6)
    B = 0.4 + 0.3 * np.sin(time_point * 0.7 + (X + Y) * 4)
    
    background_img = np.stack([R, G, B], axis=2)
    
    # Display background
    ax.imshow(background_img, extent=[0, width, 0, height], aspect='auto')
    
    # Add subtitle if active
    if active_text and active_text != "[No text]":
        # Create subtitle area background
        subtitle_y = 120
        subtitle_height = 80
        
        # Add semi-transparent background for subtitle
        rect = patches.Rectangle((50, subtitle_y - 20), width - 100, subtitle_height,
                               linewidth=0, facecolor='black', alpha=0.6)
        ax.add_patch(rect)
        
        # Add text with shadow effect for better visibility
        shadow_offset = 3
        
        # Shadow text
        ax.text(width/2 + shadow_offset, subtitle_y + shadow_offset, active_text, 
               fontsize=28, color='black', ha='center', va='center',
               weight='bold', alpha=0.8)
        
        # Main text
        ax.text(width/2, subtitle_y, active_text, 
               fontsize=28, color='white', ha='center', va='center',
               weight='bold')
        
        # Add timing info
        if active_segment:
            timing_text = f"Time: {time_point:.1f}s | Segment: {active_segment['start_time']:.1f}s - {active_segment['end_time']:.1f}s | Confidence: {active_segment['confidence']:.2f}"
            ax.text(width/2, 50, timing_text, 
                   fontsize=12, color='yellow', ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        print(f"  Frame at {time_point}s: '{active_text[:60]}...'")
    else:
        # No subtitle active
        ax.text(width/2, height/2, "No subtitle at this time", 
               fontsize=24, color='white', ha='center', va='center',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='red', alpha=0.7))
        print(f"  Frame at {time_point}s: (no subtitle)")
    
    # Add title
    ax.text(width/2, height - 50, "Dancing in Your Eyes - Subtitle Preview", 
           fontsize=20, color='white', ha='center', va='center',
           weight='bold',
           bbox=dict(boxstyle="round,pad=0.3", facecolor='purple', alpha=0.8))
    
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Save frame
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0, dpi=100)
    plt.close()
    
    print(f"✓ Saved frame: {output_file}")
    return True

def create_timeline_visualization(subtitle_data, output_file="dancing_eyes_timeline.png"):
    """Create timeline visualization of all subtitles"""
    
    print("Creating subtitle timeline...")
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    segments = subtitle_data['segments']
    
    for i, segment in enumerate(segments):
        start_time = segment['start_time']
        end_time = segment['end_time']
        text = segment['text']
        confidence = segment['confidence']
        
        # Color based on confidence (red=low, green=high)
        color = plt.cm.RdYlGn(confidence)
        
        # Create rectangle for segment
        rect = patches.Rectangle((start_time, i), end_time - start_time, 0.8,
                               linewidth=1, edgecolor='black', facecolor=color, alpha=0.8)
        ax.add_patch(rect)
        
        # Add text label (truncated if too long)
        display_text = text[:40] + "..." if len(text) > 40 else text
        ax.text(start_time + (end_time - start_time) / 2, i + 0.4, 
               display_text,
               ha='center', va='center', fontsize=9, weight='bold',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Set up the plot
    ax.set_xlim(0, max(seg['end_time'] for seg in segments) + 5)
    ax.set_ylim(-0.5, len(segments) - 0.5)
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('Subtitle Segments', fontsize=12)
    ax.set_title('Dancing in Your Eyes - Complete Subtitle Timeline\n(Color indicates confidence: Red=Low, Green=High)', 
                fontsize=14, weight='bold')
    
    # Add segment labels on y-axis
    y_labels = [f"Seg {i}" for i in range(len(segments))]
    ax.set_yticks(range(len(segments)))
    ax.set_yticklabels(y_labels, fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Add colorbar for confidence
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, 
                              norm=plt.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Confidence Score', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Timeline saved: {output_file}")
    return True

def show_subtitle_statistics(subtitle_data):
    """Display detailed statistics about the subtitle data"""
    
    segments = subtitle_data['segments']
    metadata = subtitle_data['metadata']
    
    print(f"\n=== Subtitle Statistics ===")
    print(f"Total segments: {len(segments)}")
    print(f"Total words: {metadata['total_words']}")
    print(f"Audio duration: {metadata['audio_duration']:.2f}s")
    print(f"Average confidence: {metadata['average_confidence']:.3f}")
    
    # Calculate additional stats
    durations = [seg['end_time'] - seg['start_time'] for seg in segments]
    confidences = [seg['confidence'] for seg in segments]
    
    print(f"\nSegment Duration Stats:")
    print(f"  Average: {np.mean(durations):.2f}s")
    print(f"  Min: {np.min(durations):.2f}s")
    print(f"  Max: {np.max(durations):.2f}s")
    
    print(f"\nConfidence Stats:")
    print(f"  Average: {np.mean(confidences):.3f}")
    print(f"  Min: {np.min(confidences):.3f}")
    print(f"  Max: {np.max(confidences):.3f}")
    
    # Show first few segments
    print(f"\nFirst 5 segments:")
    for i, segment in enumerate(segments[:5]):
        print(f"  {i+1}. {segment['start_time']:.1f}s-{segment['end_time']:.1f}s (conf: {segment['confidence']:.2f})")
        print(f"     '{segment['text']}'")
    
    return True

def main():
    """Main test function"""
    print("=== Dancing in Your Eyes Subtitle Preview Test ===\n")
    
    # Load subtitle data
    subtitle_data = load_subtitle_data()
    if not subtitle_data:
        return False
    
    # Show statistics
    show_subtitle_statistics(subtitle_data)
    
    # Create timeline visualization
    print(f"\n--- Creating Timeline Visualization ---")
    create_timeline_visualization(subtitle_data)
    
    # Create preview frames at key moments
    print(f"\n--- Creating Preview Frames ---")
    preview_times = [25, 30, 35, 40, 45, 55, 85, 95]  # Key moments with subtitles
    
    for time_point in preview_times:
        output_file = f"dancing_eyes_preview_t{time_point}s.png"
        create_preview_frame(subtitle_data, time_point, output_file)
    
    print(f"\n✓ All tests completed successfully!")
    print(f"\nGenerated files:")
    print(f"  - dancing_eyes_timeline.png (complete timeline)")
    for time_point in preview_times:
        print(f"  - dancing_eyes_preview_t{time_point}s.png")
    
    print(f"\nTo see the subtitle overlay in action:")
    print(f"  1. Open the timeline image to see all subtitles")
    print(f"  2. View the preview frames to see subtitles at different times")
    print(f"  3. The frames show how subtitles would appear over video")
    
    return True

if __name__ == "__main__":
    main()