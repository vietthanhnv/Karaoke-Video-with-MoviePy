"""
Unit tests for subtitle parsers.

Tests both JSON and ASS subtitle parsers with various file formats and edge cases.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import json
import tempfile
from unittest.mock import patch, mock_open

from subtitle_creator.parsers import (
    JSONSubtitleParser, ASSSubtitleParser, SubtitleParserFactory
)
from subtitle_creator.interfaces import ParseError, ExportError, SubtitleData, SubtitleLine, WordTiming
from subtitle_creator.models import ValidationError


class TestSubtitleParserFactory:
    """Test cases for SubtitleParserFactory."""
    
    def test_create_parser_json(self):
        """Test creating JSON parser from file extension."""
        parser = SubtitleParserFactory.create_parser('test.json')
        assert isinstance(parser, JSONSubtitleParser)
    
    def test_create_parser_ass(self):
        """Test creating ASS parser from file extension."""
        parser = SubtitleParserFactory.create_parser('test.ass')
        assert isinstance(parser, ASSSubtitleParser)
    
    def test_create_parser_ssa(self):
        """Test creating ASS parser for SSA extension."""
        parser = SubtitleParserFactory.create_parser('test.ssa')
        assert isinstance(parser, ASSSubtitleParser)
    
    def test_create_parser_unsupported(self):
        """Test error for unsupported file extension."""
        with pytest.raises(ParseError, match="No parser available for file extension"):
            SubtitleParserFactory.create_parser('test.txt')
    
    def test_detect_format_json(self):
        """Test format detection for JSON files."""
        json_content = '{"segments": [], "word_segments": []}'
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            format_type = SubtitleParserFactory.detect_format('test.json')
            assert format_type == 'json'
    
    def test_detect_format_ass(self):
        """Test format detection for ASS files."""
        ass_content = '[Script Info]\nTitle: Test\n\n[Events]\nDialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,Test'
        
        with patch('builtins.open', mock_open(read_data=ass_content)):
            format_type = SubtitleParserFactory.detect_format('test.ass')
            assert format_type == 'ass'
    
    def test_detect_format_unknown(self):
        """Test format detection for unknown files."""
        unknown_content = 'This is not a subtitle file'
        
        with patch('builtins.open', mock_open(read_data=unknown_content)):
            format_type = SubtitleParserFactory.detect_format('test.txt')
            assert format_type == 'unknown'
    
    def test_detect_format_file_error(self):
        """Test format detection when file cannot be read."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            format_type = SubtitleParserFactory.detect_format('nonexistent.txt')
            assert format_type == 'unknown'


class TestJSONSubtitleParser:
    """Test cases for JSONSubtitleParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JSONSubtitleParser()
    
    def test_get_supported_extensions(self):
        """Test supported file extensions."""
        extensions = self.parser.get_supported_extensions()
        assert extensions == ['.json']
    
    def test_parse_valid_json_file(self):
        """Test parsing a valid JSON subtitle file."""
        # Create test data similar to the example file
        test_data = {
            "metadata": {
                "format_version": "1.0",
                "total_segments": 2,
                "total_words": 4
            },
            "segments": [
                {
                    "start_time": 1.0,
                    "end_time": 3.0,
                    "text": "Hello world",
                    "segment_id": 0
                },
                {
                    "start_time": 4.0,
                    "end_time": 6.0,
                    "text": "Test subtitle",
                    "segment_id": 1
                }
            ],
            "word_segments": [
                {
                    "word": "Hello",
                    "start_time": 1.0,
                    "end_time": 1.5,
                    "segment_id": 0
                },
                {
                    "word": "world",
                    "start_time": 1.5,
                    "end_time": 3.0,
                    "segment_id": 0
                },
                {
                    "word": "Test",
                    "start_time": 4.0,
                    "end_time": 4.5,
                    "segment_id": 1
                },
                {
                    "word": "subtitle",
                    "start_time": 4.5,
                    "end_time": 6.0,
                    "segment_id": 1
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            
            assert isinstance(result, SubtitleData)
            assert len(result.lines) == 2
            assert result.lines[0].text == "Hello world"
            assert result.lines[0].start_time == 1.0
            assert result.lines[0].end_time == 3.0
            assert len(result.lines[0].words) == 2
            assert result.lines[0].words[0].word == "Hello"
            assert result.lines[1].text == "Test subtitle"
            assert len(result.lines[1].words) == 2
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_json_with_no_text_segments(self):
        """Test parsing JSON with [No text] segments (should be skipped)."""
        test_data = {
            "segments": [
                {
                    "start_time": 1.0,
                    "end_time": 3.0,
                    "text": "Valid text",
                    "segment_id": 0
                },
                {
                    "start_time": 4.0,
                    "end_time": 6.0,
                    "text": "[No text]",
                    "segment_id": 1
                },
                {
                    "start_time": 7.0,
                    "end_time": 9.0,
                    "text": "",
                    "segment_id": 2
                }
            ],
            "word_segments": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            
            # Should only have one line (the valid text)
            assert len(result.lines) == 1
            assert result.lines[0].text == "Valid text"
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        with pytest.raises(ParseError, match="File not found"):
            self.parser.parse("nonexistent.json")
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json")
            temp_path = f.name
        
        try:
            with pytest.raises(ParseError, match="Invalid JSON format"):
                self.parser.parse(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_parse_json_missing_required_fields(self):
        """Test parsing JSON with missing required fields."""
        test_data = {
            "segments": [
                {
                    "start_time": 1.0,
                    # Missing end_time
                    "text": "Test",
                    "segment_id": 0
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ParseError, match="Error parsing segment"):
                self.parser.parse(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_export_to_json(self):
        """Test exporting subtitle data to JSON format."""
        # Create test subtitle data
        words1 = [
            WordTiming("Hello", 1.0, 1.5),
            WordTiming("world", 1.5, 3.0)
        ]
        words2 = [
            WordTiming("Test", 4.0, 4.5),
            WordTiming("subtitle", 4.5, 6.0)
        ]
        
        lines = [
            SubtitleLine(1.0, 3.0, "Hello world", words1, {}),
            SubtitleLine(4.0, 6.0, "Test subtitle", words2, {})
        ]
        
        subtitle_data = SubtitleData(
            lines=lines,
            global_style={'font_family': 'Arial'},
            metadata={'test': 'value'}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.parser.export(subtitle_data, temp_path)
            
            # Verify the exported file
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
            
            assert 'segments' in exported_data
            assert 'word_segments' in exported_data
            assert 'metadata' in exported_data
            assert len(exported_data['segments']) == 2
            assert len(exported_data['word_segments']) == 4
            assert exported_data['metadata']['test'] == 'value'
            
        finally:
            os.unlink(temp_path)


class TestASSSubtitleParser:
    """Test cases for ASSSubtitleParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ASSSubtitleParser()
    
    def test_get_supported_extensions(self):
        """Test supported file extensions."""
        extensions = self.parser.get_supported_extensions()
        assert '.ass' in extensions
        assert '.ssa' in extensions
    
    def test_parse_valid_ass_file(self):
        """Test parsing a valid ASS subtitle file."""
        ass_content = """[Script Info]
Title: Test Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.0,0.0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,Hello world
Dialogue: 0,0:00:04.00,0:00:06.00,Default,,0,0,0,,Test subtitle
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as f:
            f.write(ass_content)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            
            assert isinstance(result, SubtitleData)
            assert len(result.lines) == 2
            assert result.lines[0].text == "Hello world"
            assert result.lines[0].start_time == 1.0
            assert result.lines[0].end_time == 3.0
            assert result.lines[1].text == "Test subtitle"
            assert result.lines[1].start_time == 4.0
            assert result.lines[1].end_time == 6.0
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_ass_with_karaoke_timing(self):
        """Test parsing ASS file with karaoke timing."""
        ass_content = """[Script Info]
Title: Karaoke Test

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.0,0.0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\\k50}Hello {\\k100}world
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as f:
            f.write(ass_content)
            temp_path = f.name
        
        try:
            result = self.parser.parse(temp_path)
            
            assert len(result.lines) == 1
            assert result.lines[0].text == "Hello world"
            assert len(result.lines[0].words) == 2
            assert result.lines[0].words[0].word == "Hello"
            assert (result.lines[0].words[0].end_time - result.lines[0].words[0].start_time) == 0.5  # 50 centiseconds
            assert result.lines[0].words[1].word == "world"
            assert (result.lines[0].words[1].end_time - result.lines[0].words[1].start_time) == 1.0  # 100 centiseconds
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_ass_time_format(self):
        """Test parsing ASS time format."""
        # Test various time formats
        assert self.parser._parse_ass_time("0:00:01.50") == 1.5
        assert self.parser._parse_ass_time("0:01:30.25") == 90.25
        assert self.parser._parse_ass_time("1:23:45.67") == 5025.67
    
    def test_parse_ass_invalid_time_format(self):
        """Test parsing invalid ASS time format."""
        with pytest.raises(ValueError, match="Invalid ASS time format"):
            self.parser._parse_ass_time("invalid")
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        with pytest.raises(ParseError, match="File not found"):
            self.parser.parse("nonexistent.ass")
    
    def test_clean_ass_text(self):
        """Test cleaning ASS formatting tags from text."""
        # Test karaoke tag removal
        assert self.parser._clean_ass_text("{\\k50}Hello {\\k100}world") == "Hello world"
        
        # Test other tag removal
        assert self.parser._clean_ass_text("{\\b1}Bold{\\b0} text") == "Bold text"
        
        # Test multiple whitespace cleanup
        assert self.parser._clean_ass_text("Hello    world") == "Hello world"
    
    def test_export_to_ass(self):
        """Test exporting subtitle data to ASS format."""
        # Create test subtitle data with karaoke timing
        words = [
            WordTiming("Hello", 1.0, 1.5),
            WordTiming("world", 1.5, 3.0)
        ]
        
        lines = [
            SubtitleLine(1.0, 3.0, "Hello world", words, {}),
            SubtitleLine(4.0, 6.0, "Test subtitle", [], {})
        ]
        
        subtitle_data = SubtitleData(
            lines=lines,
            global_style={'font_family': 'Arial', 'font_size': 24},
            metadata={}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False) as f:
            temp_path = f.name
        
        try:
            self.parser.export(subtitle_data, temp_path)
            
            # Verify the exported file
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert '[Script Info]' in content
            assert '[V4+ Styles]' in content
            assert '[Events]' in content
            assert 'Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\\k50}Hello{\\k150}world' in content
            assert 'Dialogue: 0,0:00:04.00,0:00:06.00,Default,,0,0,0,,Test subtitle' in content
            
        finally:
            os.unlink(temp_path)
    
    def test_format_ass_time(self):
        """Test formatting seconds as ASS time string."""
        assert self.parser._format_ass_time(1.5) == "0:00:01.50"
        assert self.parser._format_ass_time(90.25) == "0:01:30.25"
        assert self.parser._format_ass_time(5025.67) == "1:23:45.67"
    
    def test_create_karaoke_text(self):
        """Test creating karaoke text with timing tags."""
        words = [
            WordTiming("Hello", 1.0, 1.5),  # 0.5 seconds = 50 centiseconds
            WordTiming("world", 1.5, 3.0)   # 1.5 seconds = 150 centiseconds
        ]
        
        line = SubtitleLine(1.0, 3.0, "Hello world", words, {})
        karaoke_text = self.parser._create_karaoke_text(line)
        
        assert karaoke_text == "{\\k50}Hello{\\k150}world"


class TestParserIntegration:
    """Integration tests for parser functionality."""
    
    def test_parse_real_example_files(self):
        """Test parsing the actual example files in the project."""
        # Test JSON example file
        json_parser = JSONSubtitleParser()
        try:
            json_result = json_parser.parse("examples/Dancing in Your Eyes.json")
            assert isinstance(json_result, SubtitleData)
            assert len(json_result.lines) > 0
            assert json_result.metadata.get('format_version') == '1.0'
        except FileNotFoundError:
            pytest.skip("Example JSON file not found")
        
        # Test ASS example file
        ass_parser = ASSSubtitleParser()
        try:
            ass_result = ass_parser.parse("examples/Dancing in Your Eyes.ass")
            assert isinstance(ass_result, SubtitleData)
            assert len(ass_result.lines) > 0
        except FileNotFoundError:
            pytest.skip("Example ASS file not found")
    
    def test_round_trip_conversion(self):
        """Test converting between JSON and ASS formats."""
        # Create test data
        words = [WordTiming("Test", 1.0, 2.0)]
        lines = [SubtitleLine(1.0, 2.0, "Test", words, {})]
        original_data = SubtitleData(lines=lines, global_style={}, metadata={})
        
        json_parser = JSONSubtitleParser()
        ass_parser = ASSSubtitleParser()
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as json_file, \
             tempfile.NamedTemporaryFile(suffix='.ass', delete=False) as ass_file:
            
            json_path = json_file.name
            ass_path = ass_file.name
        
        try:
            # Export to JSON
            json_parser.export(original_data, json_path)
            
            # Parse back from JSON
            json_result = json_parser.parse(json_path)
            
            # Export to ASS
            ass_parser.export(json_result, ass_path)
            
            # Parse back from ASS
            ass_result = ass_parser.parse(ass_path)
            
            # Verify data integrity
            assert len(ass_result.lines) == 1
            assert ass_result.lines[0].text == "Test"
            assert ass_result.lines[0].start_time == 1.0
            assert ass_result.lines[0].end_time == 2.0
            
        finally:
            os.unlink(json_path)
            os.unlink(ass_path)
    
    def test_error_handling_with_line_numbers(self):
        """Test that parsing errors include line numbers for debugging."""
        # Create ASS file with invalid time format
        invalid_ass = """[Script Info]
Title: Test

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,invalid_time,0:00:03.00,Default,,0,0,0,,Test
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as f:
            f.write(invalid_ass)
            temp_path = f.name
        
        try:
            parser = ASSSubtitleParser()
            with pytest.raises(ParseError, match="Error parsing line"):
                parser.parse(temp_path)
        finally:
            os.unlink(temp_path)
