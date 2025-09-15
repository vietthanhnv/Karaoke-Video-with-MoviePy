#!/usr/bin/env python3
"""
Debug script to test ASS file import
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subtitle_creator.parsers import SubtitleParserFactory, ASSSubtitleParser
from subtitle_creator.subtitle_engine import SubtitleEngine

def test_ass_import():
    """Test importing the ASS file directly."""
    ass_file = "examples/Dancing in Your Eyes.ass"
    
    print(f"Testing ASS import from: {ass_file}")
    print("=" * 50)
    
    try:
        # Test 1: Direct parser test
        print("1. Testing direct ASS parser...")
        parser = ASSSubtitleParser()
        subtitle_data = parser.parse(ass_file)
        
        print(f"   Lines parsed: {len(subtitle_data.lines)}")
        print(f"   Global style: {subtitle_data.global_style}")
        print(f"   Metadata: {subtitle_data.metadata}")
        
        if subtitle_data.lines:
            print(f"   First line: {subtitle_data.lines[0].text}")
            print(f"   First line timing: {subtitle_data.lines[0].start_time} - {subtitle_data.lines[0].end_time}")
            print(f"   First line words: {len(subtitle_data.lines[0].words)}")
            if subtitle_data.lines[0].words:
                print(f"   First word: {subtitle_data.lines[0].words[0].word}")
        
        print("\n2. Testing subtitle engine...")
        engine = SubtitleEngine()
        engine.load_from_file(ass_file)
        
        print(f"   Engine has data: {engine.has_data}")
        if engine.has_data:
            stats = engine.get_statistics()
            print(f"   Statistics: {stats}")
        
        print("\n3. Testing factory parser...")
        factory_parser = SubtitleParserFactory.create_parser(ass_file)
        print(f"   Factory created parser: {type(factory_parser).__name__}")
        
        factory_data = factory_parser.parse(ass_file)
        print(f"   Factory parsed lines: {len(factory_data.lines)}")
        
        print("\nSUCCESS: ASS file imported successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ass_import()