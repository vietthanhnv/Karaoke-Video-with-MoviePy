"""
Data models for the Subtitle Creator application with validation.

This module contains the core data structures used throughout the application,
including validation methods for timing consistency and text content.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import re
from .interfaces import SubtitleCreatorError


class ValidationError(SubtitleCreatorError):
    """Raised when data validation fails."""
    pass


@dataclass
class WordTiming:
    """Represents timing information for a single word in a subtitle line."""
    word: str
    start_time: float
    end_time: float

    def __post_init__(self):
        """Validate word timing data after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate word timing data.
        
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(self.word, str):
            raise ValidationError("Word must be a string")
        
        if not self.word.strip():
            raise ValidationError("Word cannot be empty or whitespace only")
        
        if not isinstance(self.start_time, (int, float)):
            raise ValidationError("Start time must be a number")
        
        if not isinstance(self.end_time, (int, float)):
            raise ValidationError("End time must be a number")
        
        if self.start_time < 0:
            raise ValidationError("Start time cannot be negative")
        
        if self.end_time < 0:
            raise ValidationError("End time cannot be negative")
        
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be less than end time")

    @property
    def duration(self) -> float:
        """Get the duration of this word timing."""
        return self.end_time - self.start_time

    def overlaps_with(self, other: 'WordTiming') -> bool:
        """
        Check if this word timing overlaps with another.
        
        Args:
            other: Another WordTiming instance
            
        Returns:
            True if there is overlap, False otherwise
        """
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)


@dataclass
class SubtitleLine:
    """Represents a single subtitle line with timing and content."""
    start_time: float
    end_time: float
    text: str
    words: List[WordTiming] = field(default_factory=list)
    style_overrides: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate subtitle line data after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate subtitle line data including timing consistency.
        
        Raises:
            ValidationError: If validation fails
        """
        # Basic type validation
        if not isinstance(self.text, str):
            raise ValidationError("Text must be a string")
        
        if not isinstance(self.start_time, (int, float)):
            raise ValidationError("Start time must be a number")
        
        if not isinstance(self.end_time, (int, float)):
            raise ValidationError("End time must be a number")
        
        if not isinstance(self.words, list):
            raise ValidationError("Words must be a list")
        
        if not isinstance(self.style_overrides, dict):
            raise ValidationError("Style overrides must be a dictionary")
        
        # Timing validation
        if self.start_time < 0:
            raise ValidationError("Start time cannot be negative")
        
        if self.end_time < 0:
            raise ValidationError("End time cannot be negative")
        
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be less than end time")
        
        # Text content validation
        if not self.text.strip():
            raise ValidationError("Text cannot be empty or whitespace only")
        
        # Validate word timings
        for i, word in enumerate(self.words):
            try:
                word.validate()
            except ValidationError as e:
                raise ValidationError(f"Word {i} validation failed: {e}")
        
        # Check word timing consistency with line timing
        if self.words:
            first_word_start = min(word.start_time for word in self.words)
            last_word_end = max(word.end_time for word in self.words)
            
            if first_word_start < self.start_time:
                raise ValidationError("Word timing starts before line start time")
            
            if last_word_end > self.end_time:
                raise ValidationError("Word timing extends beyond line end time")
        
        # Check for overlapping words
        for i in range(len(self.words)):
            for j in range(i + 1, len(self.words)):
                if self.words[i].overlaps_with(self.words[j]):
                    raise ValidationError(f"Words {i} and {j} have overlapping timing")
        
        # Validate that words match the text content
        if self.words:
            word_text = ' '.join(word.word for word in self.words)
            # Normalize whitespace for comparison
            normalized_text = re.sub(r'\s+', ' ', self.text.strip())
            normalized_word_text = re.sub(r'\s+', ' ', word_text.strip())
            
            if normalized_text != normalized_word_text:
                raise ValidationError("Word list does not match line text content")

    @property
    def duration(self) -> float:
        """Get the duration of this subtitle line."""
        return self.end_time - self.start_time

    def overlaps_with(self, other: 'SubtitleLine') -> bool:
        """
        Check if this subtitle line overlaps with another.
        
        Args:
            other: Another SubtitleLine instance
            
        Returns:
            True if there is overlap, False otherwise
        """
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)

    def get_word_at_time(self, time: float) -> Optional[WordTiming]:
        """
        Get the word that should be active at a specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            WordTiming if a word is active at that time, None otherwise
        """
        for word in self.words:
            if word.start_time <= time < word.end_time:
                return word
        return None

    def add_word_timing(self, word: str, start_time: float, end_time: float) -> None:
        """
        Add a word timing to this line.
        
        Args:
            word: The word text
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Raises:
            ValidationError: If the word timing is invalid
        """
        word_timing = WordTiming(word, start_time, end_time)
        self.words.append(word_timing)
        # Re-validate the entire line to ensure consistency
        self.validate()


@dataclass
class SubtitleData:
    """Container for complete subtitle information with validation."""
    lines: List[SubtitleLine] = field(default_factory=list)
    global_style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate subtitle data after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate complete subtitle data including line consistency.
        
        Raises:
            ValidationError: If validation fails
        """
        # Basic type validation
        if not isinstance(self.lines, list):
            raise ValidationError("Lines must be a list")
        
        if not isinstance(self.global_style, dict):
            raise ValidationError("Global style must be a dictionary")
        
        if not isinstance(self.metadata, dict):
            raise ValidationError("Metadata must be a dictionary")
        
        # Validate each line
        for i, line in enumerate(self.lines):
            try:
                line.validate()
            except ValidationError as e:
                raise ValidationError(f"Line {i} validation failed: {e}")
        
        # Check for overlapping lines
        for i in range(len(self.lines)):
            for j in range(i + 1, len(self.lines)):
                if self.lines[i].overlaps_with(self.lines[j]):
                    raise ValidationError(f"Lines {i} and {j} have overlapping timing")
        
        # Validate chronological order
        for i in range(1, len(self.lines)):
            if self.lines[i].start_time < self.lines[i-1].start_time:
                raise ValidationError(f"Lines are not in chronological order: line {i} starts before line {i-1}")

    @property
    def total_duration(self) -> float:
        """Get the total duration of all subtitles."""
        if not self.lines:
            return 0.0
        return max(line.end_time for line in self.lines)

    def get_line_at_time(self, time: float) -> Optional[SubtitleLine]:
        """
        Get the subtitle line that should be active at a specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            SubtitleLine if a line is active at that time, None otherwise
        """
        for line in self.lines:
            if line.start_time <= time < line.end_time:
                return line
        return None

    def get_lines_in_range(self, start_time: float, end_time: float) -> List[SubtitleLine]:
        """
        Get all subtitle lines that are active within a time range.
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            List of SubtitleLine objects active in the range
        """
        result = []
        for line in self.lines:
            # Check if line overlaps with the time range
            if not (line.end_time <= start_time or line.start_time >= end_time):
                result.append(line)
        return result

    def add_line(self, start_time: float, end_time: float, text: str, 
                 words: Optional[List[WordTiming]] = None,
                 style_overrides: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a subtitle line to the data.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            text: The subtitle text
            words: Optional word-level timing
            style_overrides: Optional style overrides
            
        Raises:
            ValidationError: If the line data is invalid
        """
        if words is None:
            words = []
        if style_overrides is None:
            style_overrides = {}
        
        line = SubtitleLine(start_time, end_time, text, words, style_overrides)
        self.lines.append(line)
        
        # Sort lines by start time to maintain chronological order
        self.lines.sort(key=lambda x: x.start_time)
        
        # Re-validate the entire data to ensure consistency
        self.validate()

    def remove_line(self, index: int) -> None:
        """
        Remove a subtitle line by index.
        
        Args:
            index: Index of the line to remove
            
        Raises:
            IndexError: If index is out of range
        """
        if 0 <= index < len(self.lines):
            del self.lines[index]
        else:
            raise IndexError(f"Line index {index} out of range")

    def clear_lines(self) -> None:
        """Remove all subtitle lines."""
        self.lines.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the subtitle data.
        
        Returns:
            Dictionary containing various statistics
        """
        if not self.lines:
            return {
                'total_lines': 0,
                'total_duration': 0.0,
                'total_words': 0,
                'average_line_duration': 0.0,
                'average_words_per_line': 0.0
            }
        
        total_words = sum(len(line.words) for line in self.lines)
        total_duration = self.total_duration
        average_line_duration = sum(line.duration for line in self.lines) / len(self.lines)
        
        return {
            'total_lines': len(self.lines),
            'total_duration': total_duration,
            'total_words': total_words,
            'average_line_duration': average_line_duration,
            'average_words_per_line': total_words / len(self.lines) if self.lines else 0.0,
            'earliest_start': min(line.start_time for line in self.lines),
            'latest_end': max(line.end_time for line in self.lines)
        }