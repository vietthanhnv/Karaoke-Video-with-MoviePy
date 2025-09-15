#!/usr/bin/env python3
"""
Debug which lines are being filtered during ASS parsing
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subtitle_creator.parsers import ASSSubtitleParser
from subtitle_creator.models import SubtitleLine, SubtitleData, ValidationError

class DebugASSParser(ASSSubtitleParser):
    """Debug version of ASS parser with detailed logging."""
    
    def _parse_ass_content(self, content: str):
        """Override to add debug logging."""
        lines = content.split('\n')
        
        # Parse sections
        current_section = None
        styles = {}
        events = []
        metadata = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith(';'):
                continue
            
            # Check for section headers
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1].lower()
                continue
            
            try:
                if current_section == 'script info':
                    self._parse_script_info_line(line, metadata)
                elif current_section == 'v4+ styles':
                    self._parse_style_line(line, styles)
                elif current_section == 'events':
                    event = self._parse_event_line(line, line_num)
                    if event:
                        events.append(event)
            except Exception as e:
                print(f"Error parsing line {line_num}: {e}")
        
        print(f"Parsed {len(events)} events from ASS file")
        
        # Convert events to SubtitleLine objects
        subtitle_lines = []
        for i, event in enumerate(events):
            print(f"\nProcessing event {i+1}/{len(events)}:")
            print(f"  Start: {event['start']}, End: {event['end']}")
            print(f"  Text: '{event['text'][:50]}{'...' if len(event['text']) > 50 else ''}'")
            
            try:
                # Parse karaoke timing if present
                words = self._parse_karaoke_timing(event['text'], event['start'])
                print(f"  Parsed {len(words)} words")
                
                # Clean text of karaoke tags
                clean_text = self._clean_ass_text(event['text'])
                print(f"  Clean text: '{clean_text[:50]}{'...' if len(clean_text) > 50 else ''}'")
                
                if clean_text.strip():  # Skip empty lines
                    print(f"  Creating SubtitleLine...")
                    line = SubtitleLine(
                        start_time=event['start'],
                        end_time=event['end'],
                        text=clean_text,
                        words=words,
                        style_overrides={}
                    )
                    subtitle_lines.append(line)
                    print(f"  SUCCESS: Added line {len(subtitle_lines)}")
                else:
                    print(f"  SKIPPED: Empty text")
                    
            except ValidationError as e:
                print(f"  VALIDATION ERROR: {e}")
                # Try without words
                try:
                    print(f"  Trying without word timing...")
                    line = SubtitleLine(
                        start_time=event['start'],
                        end_time=event['end'],
                        text=clean_text,
                        words=[],
                        style_overrides={}
                    )
                    subtitle_lines.append(line)
                    print(f"  SUCCESS: Added line {len(subtitle_lines)} (no words)")
                except ValidationError as e2:
                    print(f"  STILL FAILED: {e2}")
            except Exception as e:
                print(f"  ERROR: {e}")
        
        print(f"\nCreated {len(subtitle_lines)} subtitle lines")
        
        # Sort lines by start time
        subtitle_lines.sort(key=lambda line: line.start_time)
        
        # Create global style from default style
        global_style = self._create_global_style(styles)
        
        print(f"Creating SubtitleData with {len(subtitle_lines)} lines...")
        try:
            subtitle_data = SubtitleData(
                lines=subtitle_lines,
                global_style=global_style,
                metadata=metadata
            )
            print(f"SUCCESS: SubtitleData created with {len(subtitle_data.lines)} lines")
            return subtitle_data
        except ValidationError as e:
            print(f"SUBTITLE DATA VALIDATION ERROR: {e}")
            raise

def test_debug_parser():
    """Test the debug parser."""
    print("Testing debug ASS parser...")
    print("=" * 60)
    
    parser = DebugASSParser()
    ass_file = "examples/Dancing in Your Eyes.ass"
    
    try:
        subtitle_data = parser.parse(ass_file)
        print(f"\nFINAL RESULT: {len(subtitle_data.lines)} lines imported")
        
        for i, line in enumerate(subtitle_data.lines):
            print(f"  {i+1}. {line.start_time:.2f}-{line.end_time:.2f}: '{line.text[:50]}{'...' if len(line.text) > 50 else ''}'")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_parser()