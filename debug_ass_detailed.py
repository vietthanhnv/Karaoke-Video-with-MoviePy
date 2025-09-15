#!/usr/bin/env python3
"""
Detailed debug script to test ASS file parsing step by step
"""

import sys
import os
import re

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_ass_parsing():
    """Debug ASS parsing step by step."""
    ass_file = "examples/Dancing in Your Eyes.ass"
    
    print(f"Debugging ASS parsing for: {ass_file}")
    print("=" * 60)
    
    # Read the file content
    with open(ass_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"Total lines in file: {len(lines)}")
    
    # Parse sections manually
    current_section = None
    events = []
    line_count = 0
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith(';'):
            continue
        
        # Check for section headers
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].lower()
            print(f"Found section: {current_section}")
            continue
        
        if current_section == 'events':
            print(f"Line {line_num} in Events section: {line}")
            
            if line.startswith('Dialogue:'):
                print(f"  -> Found Dialogue line!")
                parts = line[9:].split(',', 9)  # Split into max 10 parts
                print(f"  -> Split into {len(parts)} parts")
                
                if len(parts) >= 10:
                    print(f"  -> Start time: '{parts[1]}'")
                    print(f"  -> End time: '{parts[2]}'")
                    print(f"  -> Text: '{parts[9]}'")
                    
                    # Try to parse times
                    try:
                        start_time = parse_ass_time(parts[1])
                        end_time = parse_ass_time(parts[2])
                        text = parts[9]
                        
                        print(f"  -> Parsed start: {start_time}")
                        print(f"  -> Parsed end: {end_time}")
                        
                        # Clean text
                        clean_text = clean_ass_text(text)
                        print(f"  -> Clean text: '{clean_text}'")
                        
                        if clean_text.strip():
                            events.append({
                                'start': start_time,
                                'end': end_time,
                                'text': clean_text
                            })
                            line_count += 1
                            print(f"  -> Added event #{line_count}")
                        else:
                            print(f"  -> Skipped empty text")
                            
                    except Exception as e:
                        print(f"  -> Error parsing: {e}")
                else:
                    print(f"  -> Not enough parts ({len(parts)} < 10)")
            else:
                print(f"  -> Not a Dialogue line")
    
    print(f"\nTotal events parsed: {len(events)}")
    
    if events:
        print("\nFirst few events:")
        for i, event in enumerate(events[:3]):
            print(f"  {i+1}. {event['start']:.2f}-{event['end']:.2f}: '{event['text']}'")

def parse_ass_time(time_str: str) -> float:
    """Parse ASS time format (H:MM:SS.CC) to seconds."""
    time_str = time_str.strip()
    
    # ASS format: H:MM:SS.CC
    match = re.match(r'(\d+):(\d{2}):(\d{2})\.(\d{2})', time_str)
    if not match:
        raise ValueError(f"Invalid ASS time format: {time_str}")
    
    hours, minutes, seconds, centiseconds = match.groups()
    
    total_seconds = (
        int(hours) * 3600 +
        int(minutes) * 60 +
        int(seconds) +
        int(centiseconds) / 100.0
    )
    
    return total_seconds

def clean_ass_text(text: str) -> str:
    """Remove ASS formatting tags from text."""
    # Remove karaoke tags
    text = re.sub(r'\{\\k\d+\}', '', text)
    
    # Remove other ASS tags
    text = re.sub(r'\{[^}]*\}', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

if __name__ == "__main__":
    debug_ass_parsing()