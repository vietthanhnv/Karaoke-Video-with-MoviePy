#!/usr/bin/env python3
"""
Debug script to test SubtitleLine creation from ASS data
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subtitle_creator.models import SubtitleLine, WordTiming, ValidationError

def test_subtitle_line_creation():
    """Test creating SubtitleLine objects with ASS data."""
    print("Testing SubtitleLine creation...")
    print("=" * 40)
    
    # Test data from the first ASS line
    test_data = {
        'start_time': 21.3,
        'end_time': 29.44,
        'text': 'Under the glow of the silver moon, I find my heart in a tender tune.',
        'words': [],
        'style_overrides': {}
    }
    
    try:
        print(f"Creating SubtitleLine with:")
        print(f"  Start: {test_data['start_time']}")
        print(f"  End: {test_data['end_time']}")
        print(f"  Text: '{test_data['text']}'")
        
        line = SubtitleLine(
            start_time=test_data['start_time'],
            end_time=test_data['end_time'],
            text=test_data['text'],
            words=test_data['words'],
            style_overrides=test_data['style_overrides']
        )
        
        print(f"SUCCESS: SubtitleLine created!")
        print(f"  Duration: {line.duration}")
        print(f"  Word count: {len(line.words)}")
        
        # Test validation
        line.validate()
        print(f"SUCCESS: Validation passed!")
        
        return True
        
    except ValidationError as e:
        print(f"VALIDATION ERROR: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_karaoke_words():
    """Test creating SubtitleLine with karaoke word timing."""
    print("\nTesting with karaoke word timing...")
    print("=" * 40)
    
    try:
        # Create some word timings
        words = [
            WordTiming(word="Under", start_time=21.3, end_time=22.37),
            WordTiming(word="the", start_time=22.37, end_time=22.95),
            WordTiming(word="glow", start_time=22.95, end_time=23.34),
        ]
        
        line = SubtitleLine(
            start_time=21.3,
            end_time=29.44,
            text="Under the glow of the silver moon, I find my heart in a tender tune.",
            words=words,
            style_overrides={}
        )
        
        print(f"SUCCESS: SubtitleLine with words created!")
        print(f"  Word count: {len(line.words)}")
        for i, word in enumerate(line.words):
            print(f"    {i+1}. '{word.word}' ({word.start_time:.2f}-{word.end_time:.2f})")
        
        # Test validation
        line.validate()
        print(f"SUCCESS: Validation passed!")
        
        return True
        
    except ValidationError as e:
        print(f"VALIDATION ERROR: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_subtitle_line_creation()
    success2 = test_with_karaoke_words()
    
    if success1 and success2:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")