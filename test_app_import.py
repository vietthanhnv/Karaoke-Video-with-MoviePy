#!/usr/bin/env python3
"""
Test ASS import in application context
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subtitle_creator.app_controller import AppController
from subtitle_creator.subtitle_engine import SubtitleEngine

def test_app_import():
    """Test ASS import through the application controller."""
    print("Testing ASS import through app controller...")
    print("=" * 50)
    
    # Create app controller in test mode
    controller = AppController(main_window=None, test_mode=True)
    
    # Test subtitle engine directly first
    print("1. Testing subtitle engine directly...")
    engine = SubtitleEngine()
    
    try:
        engine.load_from_file("examples/Dancing in Your Eyes.ass")
        print(f"   Engine loaded: {engine.has_data}")
        
        if engine.has_data:
            stats = engine.get_statistics()
            print(f"   Lines: {stats['total_lines']}")
            print(f"   Duration: {stats['total_duration']:.2f}s")
            print(f"   Words: {stats['total_words']}")
            print(f"   Word timing coverage: {stats['word_timing_coverage']:.1%}")
            
            # Show first few lines
            if engine.subtitle_data and engine.subtitle_data.lines:
                print(f"   First 3 lines:")
                for i, line in enumerate(engine.subtitle_data.lines[:3]):
                    print(f"     {i+1}. {line.start_time:.2f}-{line.end_time:.2f}: '{line.text}'")
                    print(f"        Words: {len(line.words)}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test through app controller
    print("\n2. Testing through app controller...")
    
    try:
        controller.load_subtitle_file("examples/Dancing in Your Eyes.ass")
        
        # Check if controller has subtitle data
        if controller.subtitle_engine.has_data:
            stats = controller.subtitle_engine.get_statistics()
            print(f"   Controller loaded: True")
            print(f"   Lines: {stats['total_lines']}")
            print(f"   Duration: {stats['total_duration']:.2f}s")
            print(f"   Words: {stats['total_words']}")
        else:
            print(f"   Controller loaded: False")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_import()