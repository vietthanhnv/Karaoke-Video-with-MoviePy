"""
Integration tests for subtitle data models with real data formats.

Tests the models with actual JSON and ASS subtitle file formats to ensure
compatibility with the expected input data.
"""

import pytest
from src.subtitle_creator.models import (
    WordTiming, SubtitleLine, SubtitleData, ValidationError
)


class TestModelsIntegration:
    """Integration tests with real subtitle data formats."""

    def test_create_from_json_format(self):
        """Test creating models from JSON format like the example file."""
        # Simulate data from the JSON format
        segment_data = {
            "start_time": 21.3,
            "end_time": 29.44,
            "text": "Under the glow of the silver moon, I find my heart in a tender tune.",
            "segment_id": 0
        }
        
        word_data = [
            {"word": "Under", "start_time": 21.3, "end_time": 22.38, "segment_id": 0},
            {"word": "the", "start_time": 22.38, "end_time": 22.96, "segment_id": 0},
            {"word": "glow", "start_time": 22.96, "end_time": 23.36, "segment_id": 0},
            {"word": "of", "start_time": 23.36, "end_time": 24.0, "segment_id": 0},
            {"word": "the", "start_time": 24.0, "end_time": 24.16, "segment_id": 0},
            {"word": "silver", "start_time": 24.16, "end_time": 24.72, "segment_id": 0},
            {"word": "moon,", "start_time": 24.72, "end_time": 25.3, "segment_id": 0},
            {"word": "I", "start_time": 26.3, "end_time": 26.46, "segment_id": 0},
            {"word": "find", "start_time": 26.46, "end_time": 26.82, "segment_id": 0},
            {"word": "my", "start_time": 26.82, "end_time": 27.24, "segment_id": 0},
            {"word": "heart", "start_time": 27.24, "end_time": 27.98, "segment_id": 0},
            {"word": "in", "start_time": 27.98, "end_time": 28.34, "segment_id": 0},
            {"word": "a", "start_time": 28.34, "end_time": 28.44, "segment_id": 0},
            {"word": "tender", "start_time": 28.44, "end_time": 28.86, "segment_id": 0},
            {"word": "tune.", "start_time": 28.86, "end_time": 29.44, "segment_id": 0}
        ]
        
        # Create word timings
        words = [
            WordTiming(w["word"], w["start_time"], w["end_time"])
            for w in word_data
        ]
        
        # Create subtitle line
        line = SubtitleLine(
            segment_data["start_time"],
            segment_data["end_time"],
            segment_data["text"],
            words
        )
        
        assert line.start_time == 21.3
        assert line.end_time == 29.44
        assert len(line.words) == 15
        assert line.words[0].word == "Under"
        assert line.words[-1].word == "tune."

    def test_create_subtitle_data_from_multiple_segments(self):
        """Test creating SubtitleData from multiple segments."""
        # Create multiple lines
        line1 = SubtitleLine(21.3, 29.44, "Under the glow of the silver moon, I find my heart in a tender tune.")
        line2 = SubtitleLine(29.44, 38.32, "Every step brings me close to you, every moment feels so true.")
        line3 = SubtitleLine(39.06, 43.14, "Soft is the night as it holds our song.")
        
        # Create subtitle data
        data = SubtitleData([line1, line2, line3])
        
        assert len(data.lines) == 3
        assert data.total_duration == 43.14
        assert data.get_line_at_time(25.0).text.startswith("Under the glow")
        assert data.get_line_at_time(35.0).text.startswith("Every step")
        assert data.get_line_at_time(41.0).text.startswith("Soft is the night")

    def test_statistics_with_real_data(self):
        """Test statistics calculation with realistic data."""
        # Create lines with word timings
        words1 = [
            WordTiming("Hello", 1.0, 1.5),
            WordTiming("world", 1.5, 2.0)
        ]
        words2 = [
            WordTiming("This", 3.0, 3.3),
            WordTiming("is", 3.3, 3.5),
            WordTiming("a", 3.5, 3.6),
            WordTiming("test", 3.6, 4.0)
        ]
        
        lines = [
            SubtitleLine(1.0, 2.0, "Hello world", words1),
            SubtitleLine(3.0, 4.0, "This is a test", words2)
        ]
        
        data = SubtitleData(lines)
        stats = data.get_statistics()
        
        assert stats['total_lines'] == 2
        assert stats['total_duration'] == 4.0
        assert stats['total_words'] == 6
        assert stats['average_line_duration'] == 1.0
        assert stats['average_words_per_line'] == 3.0
        assert stats['earliest_start'] == 1.0
        assert stats['latest_end'] == 4.0

    def test_overlapping_detection_with_realistic_timing(self):
        """Test overlap detection with realistic subtitle timing."""
        # These should not overlap (common subtitle pattern)
        line1 = SubtitleLine(1.0, 3.0, "First subtitle line")
        line2 = SubtitleLine(3.5, 5.5, "Second subtitle line")
        line3 = SubtitleLine(6.0, 8.0, "Third subtitle line")
        
        data = SubtitleData([line1, line2, line3])
        assert len(data.lines) == 3  # Should validate successfully
        
        # These should overlap and fail validation
        overlapping_lines = [
            SubtitleLine(1.0, 3.0, "First line"),
            SubtitleLine(2.5, 4.5, "Overlapping line")  # Overlaps with first
        ]
        
        with pytest.raises(ValidationError, match="overlapping timing"):
            SubtitleData(overlapping_lines)

    def test_karaoke_style_word_timing(self):
        """Test word-level timing for karaoke-style synchronization."""
        # Simulate karaoke timing where each word is precisely timed
        words = [
            WordTiming("Dancing", 1.0, 1.8),
            WordTiming("in", 1.8, 2.0),
            WordTiming("your", 2.0, 2.4),
            WordTiming("eyes", 2.4, 3.0)
        ]
        
        line = SubtitleLine(1.0, 3.0, "Dancing in your eyes", words)
        
        # Test word retrieval at specific times
        assert line.get_word_at_time(1.4).word == "Dancing"
        assert line.get_word_at_time(1.9).word == "in"
        assert line.get_word_at_time(2.2).word == "your"
        assert line.get_word_at_time(2.7).word == "eyes"
        assert line.get_word_at_time(0.5) is None  # Before any word
        assert line.get_word_at_time(3.5) is None  # After all words

    def test_metadata_and_styling(self):
        """Test metadata and styling support."""
        global_style = {
            "font_family": "Arial",
            "font_size": 24,
            "color": (255, 255, 255, 255),
            "position": "bottom_center"
        }
        
        metadata = {
            "title": "Dancing in Your Eyes",
            "duration": 202.06,
            "format_version": "1.0"
        }
        
        style_overrides = {
            "color": (255, 255, 0, 255),  # Yellow for emphasis
            "font_weight": "bold"
        }
        
        line = SubtitleLine(1.0, 2.0, "Emphasized text", [], style_overrides)
        data = SubtitleData([line], global_style, metadata)
        
        assert data.global_style["font_family"] == "Arial"
        assert data.metadata["title"] == "Dancing in Your Eyes"
        assert data.lines[0].style_overrides["color"] == (255, 255, 0, 255)

    def test_edge_case_very_short_words(self):
        """Test handling of very short word durations."""
        # Some words might have very short durations
        words = [
            WordTiming("I", 1.0, 1.1),      # 0.1 second
            WordTiming("am", 1.1, 1.25),    # 0.15 seconds
            WordTiming("here", 1.25, 1.8)   # 0.55 seconds
        ]
        
        line = SubtitleLine(1.0, 1.8, "I am here", words)
        assert line.duration == 0.8
        assert all(word.duration > 0 for word in words)

    def test_long_subtitle_sequences(self):
        """Test handling of longer subtitle sequences."""
        # Create a longer sequence of subtitles
        lines = []
        for i in range(10):
            start_time = i * 2.0
            end_time = start_time + 1.5
            text = f"Subtitle line number {i + 1}"
            lines.append(SubtitleLine(start_time, end_time, text))
        
        data = SubtitleData(lines)
        assert len(data.lines) == 10
        assert data.total_duration == 19.5  # Last line ends at 19.5
        
        # Test range queries
        lines_in_range = data.get_lines_in_range(5.0, 10.0)
        assert len(lines_in_range) >= 2  # Should include multiple lines
        
        # Test statistics
        stats = data.get_statistics()
        assert stats['total_lines'] == 10
        assert stats['average_line_duration'] == 1.5