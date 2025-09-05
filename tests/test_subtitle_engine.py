"""
Unit tests for the SubtitleEngine class.

Tests subtitle manipulation, timing calculations, and export functionality.
"""

import pytest
import tempfile
import os
import json
import copy
from unittest.mock import patch, MagicMock

from src.subtitle_creator.subtitle_engine import SubtitleEngine, SubtitleEngineError
from src.subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming, ValidationError
from src.subtitle_creator.interfaces import ParseError, ExportError


class TestSubtitleEngine:
    """Test cases for SubtitleEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SubtitleEngine()
        
        # Create sample subtitle data with non-overlapping timing
        self.sample_words = [
            WordTiming("Hello", 0.0, 0.5),
            WordTiming("world", 0.5, 1.0)
        ]
        
        self.sample_lines = [
            SubtitleLine(0.0, 1.0, "Hello world", self.sample_words, {}),
            SubtitleLine(2.0, 3.0, "Second line", [], {})  # Non-overlapping timing
        ]
        
        self.sample_data = SubtitleData(
            lines=self.sample_lines,
            global_style={'font_family': 'Arial', 'font_size': 20},
            metadata={'title': 'Test Subtitles'}
        )
    
    def test_init(self):
        """Test SubtitleEngine initialization."""
        engine = SubtitleEngine()
        assert engine.subtitle_data is None
        assert not engine.has_data
        assert not engine.has_changes
        assert not engine.can_undo
        assert not engine.can_redo
    
    def test_load_from_data(self):
        """Test loading subtitle data from SubtitleData object."""
        self.engine.load_from_data(self.sample_data)
        
        assert self.engine.has_data
        assert not self.engine.has_changes  # No changes yet
        assert self.engine.subtitle_data.lines[0].text == "Hello world"
        assert len(self.engine.subtitle_data.lines) == 2
    
    def test_create_new(self):
        """Test creating new empty subtitle data."""
        self.engine.create_new()
        
        assert self.engine.has_data
        assert not self.engine.has_changes
        assert len(self.engine.subtitle_data.lines) == 0
        assert 'font_family' in self.engine.subtitle_data.global_style
    
    def test_create_new_with_custom_style(self):
        """Test creating new subtitle data with custom style."""
        custom_style = {'font_family': 'Times', 'font_size': 24}
        custom_metadata = {'author': 'Test Author'}
        
        self.engine.create_new(custom_style, custom_metadata)
        
        assert self.engine.subtitle_data.global_style['font_family'] == 'Times'
        assert self.engine.subtitle_data.metadata['author'] == 'Test Author'
    
    @patch('src.subtitle_creator.subtitle_engine.SubtitleParserFactory')
    def test_load_from_file_success(self, mock_factory):
        """Test successful loading from file."""
        mock_parser = MagicMock()
        mock_parser.parse.return_value = self.sample_data
        mock_factory.create_parser.return_value = mock_parser
        
        self.engine.load_from_file('test.json')
        
        assert self.engine.has_data
        assert not self.engine.has_changes
        mock_factory.create_parser.assert_called_once_with('test.json')
        mock_parser.parse.assert_called_once_with('test.json')
    
    @patch('src.subtitle_creator.subtitle_engine.SubtitleParserFactory')
    def test_load_from_file_failure(self, mock_factory):
        """Test loading from file with parse error."""
        mock_factory.create_parser.side_effect = ParseError("Parse failed")
        
        with pytest.raises(SubtitleEngineError, match="Failed to load subtitle file"):
            self.engine.load_from_file('test.json')
    
    def test_add_line_success(self):
        """Test successful addition of subtitle line."""
        self.engine.load_from_data(self.sample_data)
        
        # Add line in chronological order with non-overlapping timing
        index = self.engine.add_line(1.2, 1.8, "Middle line")
        
        assert index == 1  # Should be inserted between existing lines
        assert len(self.engine.subtitle_data.lines) == 3
        assert self.engine.subtitle_data.lines[1].text == "Middle line"
        assert self.engine.has_changes
        assert self.engine.can_undo
    
    def test_add_line_with_words(self):
        """Test adding line with word timing."""
        self.engine.load_from_data(self.sample_data)
        
        words = [WordTiming("Test", 1.2, 1.5), WordTiming("word", 1.5, 1.8)]
        index = self.engine.add_line(1.2, 1.8, "Test word", words)
        
        assert len(self.engine.subtitle_data.lines[index].words) == 2
        assert self.engine.subtitle_data.lines[index].words[0].word == "Test"
    
    def test_add_line_at_specific_index(self):
        """Test adding line at specific index (will be reordered chronologically)."""
        self.engine.load_from_data(self.sample_data)
        
        # Insert at index 0, but with later timing - should end up at the end after sorting
        index = self.engine.add_line(5.0, 6.0, "Last line", insert_index=0)
        
        # Should be reordered to maintain chronological order
        assert index == 2  # Should be at the end after sorting
        assert self.engine.subtitle_data.lines[2].text == "Last line"
    
    def test_add_line_no_data(self):
        """Test adding line when no data is loaded."""
        with pytest.raises(SubtitleEngineError, match="No subtitle data loaded"):
            self.engine.add_line(0.0, 1.0, "Test")
    
    def test_add_line_validation_error(self):
        """Test adding line with validation error."""
        self.engine.load_from_data(self.sample_data)
        
        # Try to add line with invalid timing
        with pytest.raises(SubtitleEngineError, match="Failed to add subtitle line"):
            self.engine.add_line(2.0, 1.0, "Invalid timing")  # end < start
    
    def test_remove_line_success(self):
        """Test successful removal of subtitle line."""
        self.engine.load_from_data(self.sample_data)
        
        removed_line = self.engine.remove_line(0)
        
        assert removed_line.text == "Hello world"
        assert len(self.engine.subtitle_data.lines) == 1
        assert self.engine.has_changes
        assert self.engine.can_undo
    
    def test_remove_line_invalid_index(self):
        """Test removing line with invalid index."""
        self.engine.load_from_data(self.sample_data)
        
        with pytest.raises(SubtitleEngineError, match="Line index 5 out of range"):
            self.engine.remove_line(5)
    
    def test_update_line_success(self):
        """Test successful update of subtitle line."""
        self.engine.load_from_data(self.sample_data)
        
        # Update text only (this will clear word timing automatically)
        self.engine.update_line(0, text="Updated text", end_time=1.5)
        
        assert self.engine.subtitle_data.lines[0].text == "Updated text"
        assert self.engine.subtitle_data.lines[0].end_time == 1.5
        assert len(self.engine.subtitle_data.lines[0].words) == 0  # Words cleared when text changed
        assert self.engine.has_changes
        assert self.engine.can_undo
    
    def test_update_line_with_words(self):
        """Test updating line with new word timing."""
        self.engine.load_from_data(self.sample_data)
        
        new_words = [WordTiming("New", 0.0, 0.3), WordTiming("words", 0.3, 1.0)]
        self.engine.update_line(0, text="New words", words=new_words)
        
        assert self.engine.subtitle_data.lines[0].text == "New words"
        assert len(self.engine.subtitle_data.lines[0].words) == 2
        assert self.engine.subtitle_data.lines[0].words[0].word == "New"
    
    def test_update_line_timing_reorder(self):
        """Test that updating timing reorders lines chronologically."""
        self.engine.load_from_data(self.sample_data)
        
        # Move first line to after second line (clear words to avoid timing conflicts)
        self.engine.update_line(0, start_time=3.5, end_time=4.5, words=[])
        
        # Lines should be reordered
        assert self.engine.subtitle_data.lines[0].text == "Second line"
        assert self.engine.subtitle_data.lines[1].text == "Hello world"
    
    def test_shift_timing_success(self):
        """Test successful timing shift."""
        self.engine.load_from_data(self.sample_data)
        
        self.engine.shift_timing(1.0)  # Shift all lines by 1 second
        
        assert self.engine.subtitle_data.lines[0].start_time == 1.0
        assert self.engine.subtitle_data.lines[0].end_time == 2.0
        assert self.engine.subtitle_data.lines[1].start_time == 3.0
        assert self.engine.subtitle_data.lines[1].end_time == 4.0
        
        # Check word timing is also shifted
        assert self.engine.subtitle_data.lines[0].words[0].start_time == 1.0
        assert self.engine.subtitle_data.lines[0].words[0].end_time == 1.5
    
    def test_shift_timing_range(self):
        """Test timing shift for specific range."""
        self.engine.load_from_data(self.sample_data)
        
        self.engine.shift_timing(0.5, start_index=1, end_index=1)  # Shift only second line
        
        assert self.engine.subtitle_data.lines[0].start_time == 0.0  # Unchanged
        assert self.engine.subtitle_data.lines[1].start_time == 2.5  # Shifted
    
    def test_shift_timing_negative_result(self):
        """Test timing shift that would result in negative times."""
        self.engine.load_from_data(self.sample_data)
        
        with pytest.raises(SubtitleEngineError, match="negative start time"):
            self.engine.shift_timing(-1.0)
    
    def test_scale_timing_success(self):
        """Test successful timing scaling."""
        self.engine.load_from_data(self.sample_data)
        
        self.engine.scale_timing(2.0)  # Double the timing
        
        # First line should remain at 0.0 start (reference point)
        assert self.engine.subtitle_data.lines[0].start_time == 0.0
        assert self.engine.subtitle_data.lines[0].end_time == 2.0  # 1.0 * 2
        assert self.engine.subtitle_data.lines[1].start_time == 4.0  # 2.0 * 2
        assert self.engine.subtitle_data.lines[1].end_time == 6.0   # 3.0 * 2
    
    def test_scale_timing_invalid_factor(self):
        """Test timing scaling with invalid factor."""
        self.engine.load_from_data(self.sample_data)
        
        with pytest.raises(SubtitleEngineError, match="Scaling factor must be positive"):
            self.engine.scale_timing(-1.0)
    
    def test_generate_word_timing_equal(self):
        """Test generating equal word timing."""
        self.engine.load_from_data(self.sample_data)
        
        # Clear existing word timing and generate new
        self.engine.generate_word_timing(1, method='equal')
        
        line = self.engine.subtitle_data.lines[1]
        assert len(line.words) == 2  # "Second line" = 2 words
        assert line.words[0].word == "Second"
        assert line.words[1].word == "line"
        
        # Each word should have equal duration (1.0 / 2 = 0.5)
        assert line.words[0].duration == pytest.approx(0.5)
        assert line.words[1].duration == pytest.approx(0.5)
    
    def test_generate_word_timing_proportional(self):
        """Test generating proportional word timing."""
        self.engine.load_from_data(self.sample_data)
        
        self.engine.generate_word_timing(1, method='proportional')
        
        line = self.engine.subtitle_data.lines[1]
        assert len(line.words) == 2
        
        # "Second" (6 chars) should get more time than "line" (4 chars)
        assert line.words[0].duration > line.words[1].duration
    
    def test_generate_word_timing_empty_text(self):
        """Test generating word timing for line with no words."""
        # Add line with text that has no words after splitting
        self.engine.create_new()
        self.engine.add_line(0.0, 1.0, "Hello")  # Valid text
        
        # Manually set empty words list to test the edge case
        self.engine.subtitle_data.lines[0].words = []
        
        # Test with a line that would result in no words
        self.engine.generate_word_timing(0, method='equal')
        
        # Should handle the case gracefully
    
    def test_clear_word_timing(self):
        """Test clearing word timing."""
        self.engine.load_from_data(self.sample_data)
        
        assert len(self.engine.subtitle_data.lines[0].words) > 0  # Has words initially
        
        self.engine.clear_word_timing(0)
        
        assert len(self.engine.subtitle_data.lines[0].words) == 0
        assert self.engine.can_undo
    
    def test_undo_redo_operations(self):
        """Test undo and redo functionality."""
        self.engine.load_from_data(self.sample_data)
        
        # Make a change with non-overlapping timing
        self.engine.add_line(4.0, 5.0, "New line")
        assert len(self.engine.subtitle_data.lines) == 3
        assert self.engine.can_undo
        
        # Undo the change
        success = self.engine.undo()
        assert success
        assert len(self.engine.subtitle_data.lines) == 2
        assert self.engine.can_redo
        
        # Redo the change
        success = self.engine.redo()
        assert success
        assert len(self.engine.subtitle_data.lines) == 3
        assert not self.engine.can_redo
    
    def test_undo_redo_no_operations(self):
        """Test undo/redo when no operations are available."""
        self.engine.load_from_data(self.sample_data)
        
        # No operations to undo/redo
        assert not self.engine.undo()
        assert not self.engine.redo()
    
    def test_get_line_at_time(self):
        """Test getting line at specific time."""
        self.engine.load_from_data(self.sample_data)
        
        # Time within first line
        result = self.engine.get_line_at_time(0.5)
        assert result is not None
        index, line = result
        assert index == 0
        assert line.text == "Hello world"
        
        # Time within second line
        result = self.engine.get_line_at_time(2.5)
        assert result is not None
        index, line = result
        assert index == 1
        assert line.text == "Second line"
        
        # Time with no active line
        result = self.engine.get_line_at_time(1.5)
        assert result is None
    
    def test_get_word_at_time(self):
        """Test getting word at specific time."""
        self.engine.load_from_data(self.sample_data)
        
        # Time within first word
        result = self.engine.get_word_at_time(0.25)
        assert result is not None
        line_index, word_index, word = result
        assert line_index == 0
        assert word_index == 0
        assert word.word == "Hello"
        
        # Time within second word
        result = self.engine.get_word_at_time(0.75)
        assert result is not None
        line_index, word_index, word = result
        assert line_index == 0
        assert word_index == 1
        assert word.word == "world"
        
        # Time in line without word timing
        result = self.engine.get_word_at_time(2.5)
        assert result is None
    
    def test_get_statistics(self):
        """Test getting subtitle statistics."""
        self.engine.load_from_data(self.sample_data)
        
        stats = self.engine.get_statistics()
        
        assert stats['total_lines'] == 2
        assert stats['total_words'] == 2  # Only first line has word timing
        assert stats['has_word_timing'] is True
        assert stats['lines_with_word_timing'] == 1
        assert stats['word_timing_coverage'] == 0.5  # 1 out of 2 lines
    
    def test_get_statistics_no_data(self):
        """Test getting statistics when no data is loaded."""
        stats = self.engine.get_statistics()
        
        assert stats['total_lines'] == 0
        assert stats['has_word_timing'] is False
    
    def test_validate_data_success(self):
        """Test data validation with valid data."""
        self.engine.load_from_data(self.sample_data)
        
        issues = self.engine.validate_data()
        assert len(issues) == 0
    
    def test_validate_data_no_data(self):
        """Test data validation with no data loaded."""
        issues = self.engine.validate_data()
        
        assert len(issues) == 1
        assert "No subtitle data loaded" in issues[0]
    
    def test_validate_data_with_issues(self):
        """Test data validation with problematic data."""
        # Create data with issues - bypass validation during creation
        problematic_lines = [
            SubtitleLine(0.0, 0.05, "Too short", [], {}),  # Very short duration
            SubtitleLine(1.0, 15.0, "Too long", [], {}),   # Very long duration
        ]
        
        # Manually create problematic data without triggering validation
        problematic_data = SubtitleData.__new__(SubtitleData)
        problematic_data.lines = problematic_lines
        problematic_data.global_style = {}
        problematic_data.metadata = {}
        
        self.engine._subtitle_data = problematic_data
        self.engine._original_data = copy.deepcopy(problematic_data)
        
        issues = self.engine.validate_data()
        
        assert len(issues) >= 2  # Should find multiple issues
        assert any("Very short duration" in issue for issue in issues)
        assert any("Very long duration" in issue for issue in issues)
    
    @patch('src.subtitle_creator.subtitle_engine.JSONSubtitleParser')
    def test_export_to_file_json(self, mock_parser_class):
        """Test exporting to JSON file."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        self.engine.load_from_data(self.sample_data)
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_name = tmp.name
        
        try:
            self.engine.export_to_file(tmp_name)
            
            mock_parser.export.assert_called_once()
            assert not self.engine.has_changes  # Should be marked as saved
        finally:
            try:
                os.unlink(tmp_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors
    
    @patch('src.subtitle_creator.subtitle_engine.ASSSubtitleParser')
    def test_export_to_file_ass(self, mock_parser_class):
        """Test exporting to ASS file."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        self.engine.load_from_data(self.sample_data)
        
        with tempfile.NamedTemporaryFile(suffix='.ass', delete=False) as tmp:
            tmp_name = tmp.name
        
        try:
            self.engine.export_to_file(tmp_name)
            
            mock_parser.export.assert_called_once()
        finally:
            try:
                os.unlink(tmp_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors
    
    def test_export_to_file_no_data(self):
        """Test exporting when no data is loaded."""
        with pytest.raises(SubtitleEngineError, match="No subtitle data to export"):
            self.engine.export_to_file('test.json')
    
    def test_export_to_file_unknown_format(self):
        """Test exporting to unknown file format."""
        self.engine.load_from_data(self.sample_data)
        
        with pytest.raises(SubtitleEngineError, match="Cannot determine format"):
            self.engine.export_to_file('test.xyz')
    
    @patch('src.subtitle_creator.subtitle_engine.JSONSubtitleParser')
    def test_export_to_file_explicit_format(self, mock_parser_class):
        """Test exporting with explicit format specification."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        self.engine.load_from_data(self.sample_data)
        
        self.engine.export_to_file('output.txt', format_type='json')
        
        mock_parser.export.assert_called_once()
    
    def test_has_changes_tracking(self):
        """Test that changes are properly tracked."""
        self.engine.load_from_data(self.sample_data)
        assert not self.engine.has_changes
        
        # Make a change
        self.engine.add_line(5.0, 6.0, "New line")
        assert self.engine.has_changes
        
        # Undo the change
        self.engine.undo()
        assert not self.engine.has_changes  # Should be back to original state
    
    def test_error_recovery_on_validation_failure(self):
        """Test that state is restored when operations fail validation."""
        self.engine.load_from_data(self.sample_data)
        original_count = len(self.engine.subtitle_data.lines)
        
        # Try to add invalid line (this should fail and restore state)
        with pytest.raises(SubtitleEngineError):
            self.engine.add_line(-1.0, 0.5, "Invalid timing")
        
        # State should be unchanged
        assert len(self.engine.subtitle_data.lines) == original_count
        assert not self.engine.has_changes
    
    def test_undo_stack_limit(self):
        """Test that undo stack respects size limit."""
        self.engine.load_from_data(self.sample_data)
        
        # Make more changes than the undo limit
        for i in range(60):  # More than max_undo_levels (50)
            self.engine.add_line(float(i + 10), float(i + 11), f"Line {i}")
        
        # Should only be able to undo up to the limit
        undo_count = 0
        while self.engine.can_undo:
            self.engine.undo()
            undo_count += 1
        
        assert undo_count <= 50  # Should not exceed the limit


class TestSubtitleEngineIntegration:
    """Integration tests for SubtitleEngine with real file operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = SubtitleEngine()
    
    def test_json_roundtrip(self):
        """Test loading and exporting JSON format."""
        # Create test data
        words = [WordTiming("Test", 0.0, 0.5), WordTiming("word", 0.5, 1.0)]
        lines = [SubtitleLine(0.0, 1.0, "Test word", words, {})]
        data = SubtitleData(lines=lines, global_style={}, metadata={'test': True})
        
        self.engine.load_from_data(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp_name = tmp.name
        
        try:
            # Export to file
            self.engine.export_to_file(tmp_name)
            
            # Load back from file
            new_engine = SubtitleEngine()
            new_engine.load_from_file(tmp_name)
            
            # Verify data integrity
            assert len(new_engine.subtitle_data.lines) == 1
            assert new_engine.subtitle_data.lines[0].text == "Test word"
            assert len(new_engine.subtitle_data.lines[0].words) == 2
            assert new_engine.subtitle_data.lines[0].words[0].word == "Test"
            
        finally:
            try:
                os.unlink(tmp_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors
    
    def test_ass_roundtrip(self):
        """Test loading and exporting ASS format."""
        # Create test data
        lines = [SubtitleLine(0.0, 1.0, "Test line", [], {})]
        data = SubtitleData(lines=lines, global_style={}, metadata={})
        
        self.engine.load_from_data(data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False) as tmp:
            tmp_name = tmp.name
        
        try:
            # Export to file
            self.engine.export_to_file(tmp_name)
            
            # Verify file was created and has content
            assert os.path.exists(tmp_name)
            with open(tmp_name, 'r') as f:
                content = f.read()
                assert '[Events]' in content
                assert 'Test line' in content
            
        finally:
            try:
                os.unlink(tmp_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors