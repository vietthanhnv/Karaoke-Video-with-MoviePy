#!/usr/bin/env python3
"""
Step-by-step debug of the ASS parser
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subtitle_creator.parsers import ASSSubtitleParser
from subtitle_creator.models import SubtitleLine, WordTiming, ValidationError

def debug_ass_parser():
    """Debug the ASS parser step by step."""
    print("Debugging ASS parser step by step...")
    print("=" * 50)
    
    parser = ASSSubtitleParser()
    ass_file = "examples/Dancing in Your Eyes.ass"
    
    # Read file content
    with open(ass_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File content length: {len(content)} characters")
    
    # Call the internal parsing method with debug
    try:
        subtitle_data = parser._parse_ass_content(content)
        print(f"Parsing completed successfully!")
        print(f"Lines parsed: {len(subtitle_data.lines)}")
        
        if subtitle_data.lines:
            print(f"First line: '{subtitle_data.lines[0].text}'")
            print(f"First line timing: {subtitle_data.lines[0].start_time} - {subtitle_data.lines[0].end_time}")
            print(f"First line words: {len(subtitle_data.lines[0].words)}")
        
        return subtitle_data
        
    except Exception as e:
        print(f"Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_manual_parsing():
    """Manually parse and create SubtitleLine objects."""
    print("\nManual parsing test...")
    print("=" * 30)
    
    # Test data from first ASS line
    test_events = [
        {
            'start': 21.3,
            'end': 29.44,
            'text': r"{\k107}Under {\k58}the {\k39}glow {\k64}of {\k16}the {\k55}silver {\k58}moon, {\k16}I {\k35}find {\k41}my {\k74}heart {\k35}in {\k10}a {\k41}tender {\k58}tune."
        }
    ]
    
    parser = ASSSubtitleParser()
    
    for i, event in enumerate(test_events):
        print(f"Processing event {i+1}:")
        print(f"  Text: {event['text']}")
        
        try:
            # Parse karaoke timing
            words = parser._parse_karaoke_timing(event['text'])
            print(f"  Parsed {len(words)} words")
            
            # Clean text
            clean_text = parser._clean_ass_text(event['text'])
            print(f"  Clean text: '{clean_text}'")
            
            if clean_text.strip():
                print(f"  Text is not empty, creating SubtitleLine...")
                
                try:
                    line = SubtitleLine(
                        start_time=event['start'],
                        end_time=event['end'],
                        text=clean_text,
                        words=words,
                        style_overrides={}
                    )
                    print(f"  SUCCESS: SubtitleLine created!")
                    print(f"    Duration: {line.duration}")
                    print(f"    Word count: {len(line.words)}")
                    
                except ValidationError as e:
                    print(f"  VALIDATION ERROR: {e}")
                    
                    # Try without words
                    print(f"  Trying without word timing...")
                    try:
                        line = SubtitleLine(
                            start_time=event['start'],
                            end_time=event['end'],
                            text=clean_text,
                            words=[],
                            style_overrides={}
                        )
                        print(f"  SUCCESS: SubtitleLine created without words!")
                    except ValidationError as e2:
                        print(f"  STILL FAILED: {e2}")
                        
            else:
                print(f"  Text is empty, skipping...")
        
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    result = debug_ass_parser()
    debug_manual_parsing()