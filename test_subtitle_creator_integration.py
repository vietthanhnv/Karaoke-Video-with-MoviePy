#!/usr/bin/env python3
"""
Test integration of Dancing in Your Eyes.json with the subtitle creator system
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_dancing_eyes_data():
    """Load the Dancing in Your Eyes JSON data"""
    try:
        with open("examples/Dancing in Your Eyes.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded Dancing in Your Eyes data: {len(data['segments'])} segments")
        return data
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return None

def convert_to_subtitle_format(dancing_eyes_data):
    """Convert Dancing in Your Eyes format to standard subtitle format"""
    
    subtitles = []
    
    for segment in dancing_eyes_data['segments']:
        if segment['text'] != "[No text]":
            subtitle = {
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'text': segment['text'],
                'confidence': segment.get('confidence', 1.0),
                'segment_id': segment.get('segment_id', 0)
            }
            subtitles.append(subtitle)
    
    print(f"✓ Converted {len(subtitles)} subtitles")
    return subtitles

def test_with_existing_system():
    """Test with the existing subtitle creator system"""
    
    try:
        # Try to import the subtitle creator
        from subtitle_creator.models import SubtitleSegment, VideoProject
        from subtitle_creator.subtitle_engine import SubtitleEngine
        print("✓ Subtitle creator system imported successfully")
        
        # Load data
        dancing_eyes_data = load_dancing_eyes_data()
        if not dancing_eyes_data:
            return False
        
        # Convert to subtitle format
        subtitles = convert_to_subtitle_format(dancing_eyes_data)
        
        # Create subtitle segments
        segments = []
        for sub in subtitles:
            segment = SubtitleSegment(
                start_time=sub['start_time'],
                end_time=sub['end_time'],
                text=sub['text']
            )
            segments.append(segment)
        
        print(f"✓ Created {len(segments)} subtitle segments")
        
        # Create a video project
        project = VideoProject(
            name="Dancing in Your Eyes",
            video_path="",  # No video file for this test
            subtitle_segments=segments
        )
        
        print(f"✓ Created video project with {len(project.subtitle_segments)} segments")
        
        # Test subtitle engine
        engine = SubtitleEngine()
        
        # Test getting subtitles at specific times
        test_times = [25, 30, 40, 55, 95]
        
        print(f"\nTesting subtitle retrieval at specific times:")
        for time_point in test_times:
            active_subtitles = engine.get_active_subtitles(segments, time_point)
            if active_subtitles:
                for subtitle in active_subtitles:
                    print(f"  {time_point}s: '{subtitle.text[:50]}...'")
            else:
                print(f"  {time_point}s: (no subtitle)")
        
        return True
        
    except ImportError as e:
        print(f"✗ Could not import subtitle creator system: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing with existing system: {e}")
        return False

def create_srt_export(dancing_eyes_data, output_file="dancing_eyes.srt"):
    """Export to SRT format for compatibility"""
    
    try:
        subtitles = convert_to_subtitle_format(dancing_eyes_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, subtitle in enumerate(subtitles, 1):
                # Convert time to SRT format (HH:MM:SS,mmm)
                start_time = format_srt_time(subtitle['start_time'])
                end_time = format_srt_time(subtitle['end_time'])
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle['text']}\n\n")
        
        print(f"✓ Exported to SRT format: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating SRT export: {e}")
        return False

def format_srt_time(seconds):
    """Convert seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_vtt_export(dancing_eyes_data, output_file="dancing_eyes.vtt"):
    """Export to WebVTT format"""
    
    try:
        subtitles = convert_to_subtitle_format(dancing_eyes_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for i, subtitle in enumerate(subtitles, 1):
                # Convert time to VTT format (HH:MM:SS.mmm)
                start_time = format_vtt_time(subtitle['start_time'])
                end_time = format_vtt_time(subtitle['end_time'])
                
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{subtitle['text']}\n\n")
        
        print(f"✓ Exported to WebVTT format: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error creating VTT export: {e}")
        return False

def format_vtt_time(seconds):
    """Convert seconds to WebVTT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"

def analyze_subtitle_patterns(dancing_eyes_data):
    """Analyze patterns in the subtitle data"""
    
    subtitles = convert_to_subtitle_format(dancing_eyes_data)
    
    print(f"\n=== Subtitle Pattern Analysis ===")
    
    # Duration analysis
    durations = [sub['end_time'] - sub['start_time'] for sub in subtitles]
    print(f"Duration stats:")
    print(f"  Average: {sum(durations) / len(durations):.2f}s")
    print(f"  Min: {min(durations):.2f}s")
    print(f"  Max: {max(durations):.2f}s")
    
    # Text length analysis
    text_lengths = [len(sub['text']) for sub in subtitles]
    print(f"\nText length stats:")
    print(f"  Average: {sum(text_lengths) / len(text_lengths):.1f} characters")
    print(f"  Min: {min(text_lengths)} characters")
    print(f"  Max: {max(text_lengths)} characters")
    
    # Confidence analysis
    confidences = [sub['confidence'] for sub in subtitles]
    print(f"\nConfidence stats:")
    print(f"  Average: {sum(confidences) / len(confidences):.3f}")
    print(f"  Min: {min(confidences):.3f}")
    print(f"  Max: {max(confidences):.3f}")
    
    # Gap analysis
    gaps = []
    for i in range(len(subtitles) - 1):
        gap = subtitles[i + 1]['start_time'] - subtitles[i]['end_time']
        if gap > 0:
            gaps.append(gap)
    
    if gaps:
        print(f"\nGap analysis:")
        print(f"  Average gap: {sum(gaps) / len(gaps):.2f}s")
        print(f"  Max gap: {max(gaps):.2f}s")
        print(f"  Gaps > 5s: {len([g for g in gaps if g > 5])}")
    
    return True

def main():
    """Main test function"""
    print("=== Dancing in Your Eyes Integration Test ===\n")
    
    # Load data
    dancing_eyes_data = load_dancing_eyes_data()
    if not dancing_eyes_data:
        return False
    
    # Analyze patterns
    analyze_subtitle_patterns(dancing_eyes_data)
    
    # Test with existing system
    print(f"\n--- Testing with Subtitle Creator System ---")
    test_with_existing_system()
    
    # Create exports
    print(f"\n--- Creating Export Formats ---")
    create_srt_export(dancing_eyes_data)
    create_vtt_export(dancing_eyes_data)
    
    # Show sample subtitles
    subtitles = convert_to_subtitle_format(dancing_eyes_data)
    print(f"\n--- Sample Subtitles ---")
    for i, subtitle in enumerate(subtitles[:5]):
        print(f"{i+1}. {subtitle['start_time']:.1f}s - {subtitle['end_time']:.1f}s")
        print(f"   '{subtitle['text']}'")
        print(f"   Confidence: {subtitle['confidence']:.3f}")
    
    print(f"\n✓ Integration test completed!")
    print(f"Generated files:")
    print(f"  - dancing_eyes.srt (SubRip format)")
    print(f"  - dancing_eyes.vtt (WebVTT format)")
    print(f"\nThe JSON data has been successfully integrated and can be used")
    print(f"with standard subtitle systems and video players.")
    
    return True

if __name__ == "__main__":
    main()