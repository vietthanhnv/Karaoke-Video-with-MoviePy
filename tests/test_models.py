"""
Unit tests for subtitle data models with validation.

Tests cover validation methods, timing consistency, text content validation,
and edge cases for all data model classes.
"""

import pytest
from src.subtitle_creator.models import (
    WordTiming, SubtitleLine, SubtitleData, ValidationError
)


class TestWordTiming:
    """Test cases for WordTiming data model."""

    def test_valid_word_timing(self):
        """Test creation of valid word timing."""
        word = WordTiming("hello", 1.0, 2.0)
        assert word.word == "hello"
        assert word.start_time == 1.0
        assert word.end_time == 2.0
        assert word.duration == 1.0

    def test_word_timing_validation_empty_word(self):
        """Test validation fails for empty word."""
        with pytest.raises(ValidationError, match="Word cannot be empty"):
            WordTiming("", 1.0, 2.0)

    def test_word_timing_validation_whitespace_word(self):
        """Test validation fails for whitespace-only word."""
        with pytest.raises(ValidationError, match="Word cannot be empty"):
            WordTiming("   ", 1.0, 2.0)

    def test_word_timing_validation_non_string_word(self):
        """Test validation fails for non-string word."""
        with pytest.raises(ValidationError, match="Word must be a string"):
            WordTiming(123, 1.0, 2.0)

    def test_word_timing_validation_non_numeric_times(self):
        """Test validation fails for non-numeric times."""
        with pytest.raises(ValidationError, match="Start time must be a number"):
            WordTiming("hello", "1.0", 2.0)
        
        with pytest.raises(ValidationError, match="End time must be a number"):
            WordTiming("hello", 1.0, "2.0")

    def test_word_timing_validation_negative_times(self):
        """Test validation fails for negative times."""
        with pytest.raises(ValidationError, match="Start time cannot be negative"):
            WordTiming("hello", -1.0, 2.0)
        
        with pytest.raises(ValidationError, match="End time cannot be negative"):
            WordTiming("hello", 1.0, -2.0)

    def test_word_timing_validation_start_after_end(self):
        """Test validation fails when start time >= end time."""
        with pytest.raises(ValidationError, match="Start time must be less than end time"):
            WordTiming("hello", 2.0, 1.0)
        
        with pytest.raises(ValidationError, match="Start time must be less than end time"):
            WordTiming("hello", 2.0, 2.0)

    def test_word_timing_overlaps_with(self):
        """Test overlap detection between word timings."""
        word1 = WordTiming("hello", 1.0, 3.0)
        word2 = WordTiming("world", 2.0, 4.0)  # Overlaps
        word3 = WordTiming("test", 3.0, 5.0)   # No overlap
        word4 = WordTiming("exact", 0.0, 1.0)  # Exact boundary, no overlap
        
        assert word1.overlaps_with(word2)
        assert word2.overlaps_with(word1)
        assert not word1.overlaps_with(word3)
        assert not word1.overlaps_with(word4)

    def test_word_timing_duration_property(self):
        """Test duration property calculation."""
        word = WordTiming("test", 1.5, 3.7)
        assert word.duration == 2.2


class TestSubtitleLine:
    """Test cases for SubtitleLine data model."""

    def test_valid_subtitle_line(self):
        """Test creation of valid subtitle line."""
        words = [WordTiming("hello", 1.0, 1.5), WordTiming("world", 1.5, 2.0)]
        line = SubtitleLine(1.0, 2.0, "hello world", words)
        
        assert line.start_time == 1.0
        assert line.end_time == 2.0
        assert line.text == "hello world"
        assert len(line.words) == 2
        assert line.duration == 1.0

    def test_subtitle_line_without_words(self):
        """Test subtitle line without word-level timing."""
        line = SubtitleLine(1.0, 2.0, "hello world")
        assert line.start_time == 1.0
        assert line.end_time == 2.0
        assert line.text == "hello world"
        assert len(line.words) == 0

    def test_subtitle_line_validation_non_string_text(self):
        """Test validation fails for non-string text."""
        with pytest.raises(ValidationError, match="Text must be a string"):
            SubtitleLine(1.0, 2.0, 123)

    def test_subtitle_line_validation_empty_text(self):
        """Test validation fails for empty text."""
        with pytest.raises(ValidationError, match="Text cannot be empty"):
            SubtitleLine(1.0, 2.0, "")
        
        with pytest.raises(ValidationError, match="Text cannot be empty"):
            SubtitleLine(1.0, 2.0, "   ")

    def test_subtitle_line_validation_invalid_timing(self):
        """Test validation fails for invalid timing."""
        with pytest.raises(ValidationError, match="Start time cannot be negative"):
            SubtitleLine(-1.0, 2.0, "hello")
        
        with pytest.raises(ValidationError, match="Start time must be less than end time"):
            SubtitleLine(2.0, 1.0, "hello")

    def test_subtitle_line_validation_word_timing_outside_line(self):
        """Test validation fails when word timing extends outside line timing."""
        words = [WordTiming("hello", 0.5, 1.5)]  # Starts before line
        with pytest.raises(ValidationError, match="Word timing starts before line start time"):
            SubtitleLine(1.0, 2.0, "hello", words)
        
        words = [WordTiming("hello", 1.5, 2.5)]  # Ends after line
        with pytest.raises(ValidationError, match="Word timing extends beyond line end time"):
            SubtitleLine(1.0, 2.0, "hello", words)

    def test_subtitle_line_validation_overlapping_words(self):
        """Test validation fails for overlapping word timings."""
        words = [
            WordTiming("hello", 1.0, 1.8),
            WordTiming("world", 1.5, 2.0)  # Overlaps with first word
        ]
        with pytest.raises(ValidationError, match="Words 0 and 1 have overlapping timing"):
            SubtitleLine(1.0, 2.0, "hello world", words)

    def test_subtitle_line_validation_word_text_mismatch(self):
        """Test validation fails when word list doesn't match text."""
        words = [WordTiming("hello", 1.0, 1.5), WordTiming("there", 1.5, 2.0)]
        with pytest.raises(ValidationError, match="Word list does not match line text content"):
            SubtitleLine(1.0, 2.0, "hello world", words)

    def test_subtitle_line_validation_word_text_whitespace_normalization(self):
        """Test that whitespace is normalized when comparing word text."""
        words = [WordTiming("hello", 1.0, 1.5), WordTiming("world", 1.5, 2.0)]
        # Should pass with extra whitespace
        line = SubtitleLine(1.0, 2.0, "  hello   world  ", words)
        assert line.text == "  hello   world  "

    def test_subtitle_line_overlaps_with(self):
        """Test overlap detection between subtitle lines."""
        line1 = SubtitleLine(1.0, 3.0, "first line")
        line2 = SubtitleLine(2.0, 4.0, "second line")  # Overlaps
        line3 = SubtitleLine(3.0, 5.0, "third line")   # No overlap
        line4 = SubtitleLine(0.0, 1.0, "fourth line")  # Exact boundary, no overlap
        
        assert line1.overlaps_with(line2)
        assert line2.overlaps_with(line1)
        assert not line1.overlaps_with(line3)
        assert not line1.overlaps_with(line4)

    def test_subtitle_line_get_word_at_time(self):
        """Test getting word active at specific time."""
        words = [
            WordTiming("hello", 1.0, 1.5),
            WordTiming("world", 1.5, 2.0)
        ]
        line = SubtitleLine(1.0, 2.0, "hello world", words)
        
        assert line.get_word_at_time(1.2).word == "hello"
        assert line.get_word_at_time(1.7).word == "world"
        assert line.get_word_at_time(0.5) is None
        assert line.get_word_at_time(2.5) is None

    def test_subtitle_line_add_word_timing(self):
        """Test adding word timing to a line."""
        # Create line with single word first
        line = SubtitleLine(1.0, 2.0, "hello")
        
        # Clear words and add the matching word timing
        line.words = []
        line.add_word_timing("hello", 1.0, 2.0)
        
        assert len(line.words) == 1
        assert line.words[0].word == "hello"
        assert line.words[0].start_time == 1.0
        assert line.words[0].end_time == 2.0

    def test_subtitle_line_add_invalid_word_timing(self):
        """Test adding invalid word timing fails validation."""
        line = SubtitleLine(1.0, 2.0, "hello")
        
        with pytest.raises(ValidationError):
            line.add_word_timing("hello", 0.5, 1.5)  # Starts before line


class TestSubtitleData:
    """Test cases for SubtitleData container."""

    def test_valid_subtitle_data(self):
        """Test creation of valid subtitle data."""
        lines = [
            SubtitleLine(1.0, 2.0, "first line"),
            SubtitleLine(3.0, 4.0, "second line")
        ]
        data = SubtitleData(lines)
        
        assert len(data.lines) == 2
        assert data.total_duration == 4.0

    def test_empty_subtitle_data(self):
        """Test creation of empty subtitle data."""
        data = SubtitleData()
        assert len(data.lines) == 0
        assert data.total_duration == 0.0

    def test_subtitle_data_validation_non_list_lines(self):
        """Test validation fails for non-list lines."""
        with pytest.raises(ValidationError, match="Lines must be a list"):
            SubtitleData("not a list")

    def test_subtitle_data_validation_overlapping_lines(self):
        """Test validation fails for overlapping lines."""
        lines = [
            SubtitleLine(1.0, 3.0, "first line"),
            SubtitleLine(2.0, 4.0, "second line")  # Overlaps
        ]
        with pytest.raises(ValidationError, match="Lines 0 and 1 have overlapping timing"):
            SubtitleData(lines)

    def test_subtitle_data_validation_non_chronological_order(self):
        """Test validation fails for non-chronological order."""
        lines = [
            SubtitleLine(3.0, 4.0, "second line"),
            SubtitleLine(1.0, 2.0, "first line")  # Starts before previous
        ]
        with pytest.raises(ValidationError, match="Lines are not in chronological order"):
            SubtitleData(lines)

    def test_subtitle_data_get_line_at_time(self):
        """Test getting line active at specific time."""
        lines = [
            SubtitleLine(1.0, 2.0, "first line"),
            SubtitleLine(3.0, 4.0, "second line")
        ]
        data = SubtitleData(lines)
        
        assert data.get_line_at_time(1.5).text == "first line"
        assert data.get_line_at_time(3.5).text == "second line"
        assert data.get_line_at_time(2.5) is None

    def test_subtitle_data_get_lines_in_range(self):
        """Test getting lines active in time range."""
        lines = [
            SubtitleLine(1.0, 2.0, "first line"),
            SubtitleLine(2.5, 3.5, "second line"),
            SubtitleLine(4.0, 5.0, "third line")
        ]
        data = SubtitleData(lines)
        
        # Range that includes first two lines
        result = data.get_lines_in_range(1.5, 3.0)
        assert len(result) == 2
        assert result[0].text == "first line"
        assert result[1].text == "second line"
        
        # Range that includes no lines
        result = data.get_lines_in_range(5.5, 6.0)
        assert len(result) == 0

    def test_subtitle_data_add_line(self):
        """Test adding line to subtitle data."""
        data = SubtitleData()
        data.add_line(1.0, 2.0, "first line")
        data.add_line(3.0, 4.0, "second line")
        
        assert len(data.lines) == 2
        assert data.lines[0].text == "first line"
        assert data.lines[1].text == "second line"

    def test_subtitle_data_add_line_maintains_order(self):
        """Test that adding lines maintains chronological order."""
        data = SubtitleData()
        data.add_line(3.0, 4.0, "second line")
        data.add_line(1.0, 2.0, "first line")  # Added out of order
        
        assert len(data.lines) == 2
        assert data.lines[0].text == "first line"  # Should be first due to sorting
        assert data.lines[1].text == "second line"

    def test_subtitle_data_remove_line(self):
        """Test removing line from subtitle data."""
        lines = [
            SubtitleLine(1.0, 2.0, "first line"),
            SubtitleLine(3.0, 4.0, "second line")
        ]
        data = SubtitleData(lines)
        
        data.remove_line(0)
        assert len(data.lines) == 1
        assert data.lines[0].text == "second line"

    def test_subtitle_data_remove_line_invalid_index(self):
        """Test removing line with invalid index."""
        data = SubtitleData()
        
        with pytest.raises(IndexError):
            data.remove_line(0)

    def test_subtitle_data_clear_lines(self):
        """Test clearing all lines."""
        lines = [
            SubtitleLine(1.0, 2.0, "first line"),
            SubtitleLine(3.0, 4.0, "second line")
        ]
        data = SubtitleData(lines)
        
        data.clear_lines()
        assert len(data.lines) == 0

    def test_subtitle_data_statistics_empty(self):
        """Test statistics for empty subtitle data."""
        data = SubtitleData()
        stats = data.get_statistics()
        
        assert stats['total_lines'] == 0
        assert stats['total_duration'] == 0.0
        assert stats['total_words'] == 0
        assert stats['average_line_duration'] == 0.0
        assert stats['average_words_per_line'] == 0.0

    def test_subtitle_data_statistics_with_data(self):
        """Test statistics calculation with data."""
        words1 = [WordTiming("hello", 1.0, 1.5), WordTiming("world", 1.5, 2.0)]
        words2 = [WordTiming("test", 3.0, 4.0)]
        
        lines = [
            SubtitleLine(1.0, 2.0, "hello world", words1),
            SubtitleLine(3.0, 4.0, "test", words2)
        ]
        data = SubtitleData(lines)
        stats = data.get_statistics()
        
        assert stats['total_lines'] == 2
        assert stats['total_duration'] == 4.0
        assert stats['total_words'] == 3
        assert stats['average_line_duration'] == 1.0
        assert stats['average_words_per_line'] == 1.5
        assert stats['earliest_start'] == 1.0
        assert stats['latest_end'] == 4.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_duration_word_timing(self):
        """Test that zero duration word timing fails validation."""
        with pytest.raises(ValidationError, match="Start time must be less than end time"):
            WordTiming("test", 1.0, 1.0)

    def test_very_small_duration(self):
        """Test very small but valid duration."""
        word = WordTiming("test", 1.0, 1.001)
        assert abs(word.duration - 0.001) < 1e-10  # Account for floating point precision

    def test_large_time_values(self):
        """Test handling of large time values."""
        word = WordTiming("test", 3600.0, 7200.0)  # 1-2 hours
        assert word.duration == 3600.0

    def test_floating_point_precision(self):
        """Test floating point precision in timing."""
        word = WordTiming("test", 1.123456789, 2.987654321)
        assert abs(word.duration - 1.864197532) < 1e-9

    def test_unicode_text_content(self):
        """Test handling of unicode text content."""
        line = SubtitleLine(1.0, 2.0, "Hello 世界 🌍")
        assert line.text == "Hello 世界 🌍"

    def test_special_characters_in_words(self):
        """Test handling of special characters in words."""
        words = [
            WordTiming("don't", 1.0, 1.5),
            WordTiming("stop!", 1.5, 2.0)
        ]
        line = SubtitleLine(1.0, 2.0, "don't stop!", words)
        assert len(line.words) == 2

    def test_multiple_spaces_in_text(self):
        """Test handling of multiple spaces in text."""
        words = [WordTiming("hello", 1.0, 1.5), WordTiming("world", 1.5, 2.0)]
        line = SubtitleLine(1.0, 2.0, "hello     world", words)
        # Should pass validation due to whitespace normalization
        assert line.text == "hello     world"