"""
Subtitle engine for manipulation and editing of subtitle data.

This module provides the SubtitleEngine class which handles subtitle manipulation,
timing calculations, and export functionality for the Subtitle Creator application.
"""

import copy
from typing import Dict, Any, List, Optional, Tuple, Union
from .models import SubtitleData, SubtitleLine, WordTiming, ValidationError
from .parsers import SubtitleParserFactory, JSONSubtitleParser, ASSSubtitleParser
from .interfaces import SubtitleCreatorError, ParseError, ExportError


class SubtitleEngineError(SubtitleCreatorError):
    """Raised when subtitle engine operations fail."""
    pass


class SubtitleEngine:
    """
    Engine for subtitle manipulation and editing operations.
    
    Provides functionality for loading, editing, timing calculations,
    and exporting subtitle data with support for word-level timing.
    """
    
    def __init__(self):
        """Initialize the subtitle engine."""
        self._subtitle_data: Optional[SubtitleData] = None
        self._original_data: Optional[SubtitleData] = None
        self._undo_stack: List[SubtitleData] = []
        self._redo_stack: List[SubtitleData] = []
        self._max_undo_levels = 50
    
    @property
    def subtitle_data(self) -> Optional[SubtitleData]:
        """Get the current subtitle data."""
        return self._subtitle_data
    
    @property
    def has_data(self) -> bool:
        """Check if subtitle data is loaded."""
        return self._subtitle_data is not None
    
    @property
    def has_changes(self) -> bool:
        """Check if there are unsaved changes."""
        if not self.has_data or not self._original_data:
            return False
        return self._subtitle_data != self._original_data
    
    @property
    def can_undo(self) -> bool:
        """Check if undo operation is available."""
        return len(self._undo_stack) > 0
    
    @property
    def can_redo(self) -> bool:
        """Check if redo operation is available."""
        return len(self._redo_stack) > 0
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load subtitle data from a file.
        
        Args:
            file_path: Path to the subtitle file
            
        Raises:
            SubtitleEngineError: If loading fails
        """
        try:
            parser = SubtitleParserFactory.create_parser(file_path)
            self._subtitle_data = parser.parse(file_path)
            self._original_data = copy.deepcopy(self._subtitle_data)
            self._clear_undo_redo()
        except (ParseError, Exception) as e:
            raise SubtitleEngineError(f"Failed to load subtitle file: {e}")
    
    def load_from_data(self, subtitle_data: SubtitleData) -> None:
        """
        Load subtitle data from a SubtitleData object.
        
        Args:
            subtitle_data: The subtitle data to load
        """
        self._subtitle_data = copy.deepcopy(subtitle_data)
        self._original_data = copy.deepcopy(subtitle_data)
        self._clear_undo_redo()
    
    def create_new(self, global_style: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Create new empty subtitle data.
        
        Args:
            global_style: Optional global style configuration
            metadata: Optional metadata dictionary
        """
        if global_style is None:
            global_style = {
                'font_family': 'Arial',
                'font_size': 20,
                'font_weight': 'normal',
                'text_color': (255, 255, 255, 255),
                'outline_color': (0, 0, 0, 255),
                'shadow_color': (0, 0, 0, 128),
                'position': ('center', 0, 50),
            }
        
        if metadata is None:
            metadata = {}
        
        self._subtitle_data = SubtitleData(
            lines=[],
            global_style=global_style,
            metadata=metadata
        )
        self._original_data = copy.deepcopy(self._subtitle_data)
        self._clear_undo_redo()
    
    def export_to_file(self, output_path: str, format_type: Optional[str] = None) -> None:
        """
        Export subtitle data to a file.
        
        Args:
            output_path: Path where the file should be saved
            format_type: Optional format type ('json' or 'ass'). If None, detected from extension
            
        Raises:
            SubtitleEngineError: If export fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data to export")
        
        try:
            if format_type is None:
                # Detect format from file extension
                if output_path.lower().endswith('.json'):
                    format_type = 'json'
                elif output_path.lower().endswith(('.ass', '.ssa')):
                    format_type = 'ass'
                else:
                    raise SubtitleEngineError(f"Cannot determine format for file: {output_path}")
            
            if format_type.lower() == 'json':
                parser = JSONSubtitleParser()
            elif format_type.lower() == 'ass':
                parser = ASSSubtitleParser()
            else:
                raise SubtitleEngineError(f"Unsupported export format: {format_type}")
            
            parser.export(self._subtitle_data, output_path)
            
            # Update original data to reflect saved state
            self._original_data = copy.deepcopy(self._subtitle_data)
            
        except (ExportError, Exception) as e:
            raise SubtitleEngineError(f"Failed to export subtitle file: {e}")
    
    def _save_state(self) -> None:
        """Save current state to undo stack."""
        if self._subtitle_data:
            self._undo_stack.append(copy.deepcopy(self._subtitle_data))
            
            # Limit undo stack size
            if len(self._undo_stack) > self._max_undo_levels:
                self._undo_stack.pop(0)
            
            # Clear redo stack when new action is performed
            self._redo_stack.clear()
    
    def _clear_undo_redo(self) -> None:
        """Clear undo and redo stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()
    
    def undo(self) -> bool:
        """
        Undo the last operation.
        
        Returns:
            True if undo was successful, False if no undo available
        """
        if not self.can_undo:
            return False
        
        # Save current state to redo stack
        if self._subtitle_data:
            self._redo_stack.append(copy.deepcopy(self._subtitle_data))
        
        # Restore previous state
        self._subtitle_data = self._undo_stack.pop()
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone operation.
        
        Returns:
            True if redo was successful, False if no redo available
        """
        if not self.can_redo:
            return False
        
        # Save current state to undo stack
        if self._subtitle_data:
            self._undo_stack.append(copy.deepcopy(self._subtitle_data))
        
        # Restore next state
        self._subtitle_data = self._redo_stack.pop()
        return True
    
    def add_line(self, start_time: float, end_time: float, text: str,
                 words: Optional[List[WordTiming]] = None,
                 style_overrides: Optional[Dict[str, Any]] = None,
                 insert_index: Optional[int] = None) -> int:
        """
        Add a new subtitle line.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            text: The subtitle text
            words: Optional word-level timing
            style_overrides: Optional style overrides
            insert_index: Optional index to insert at. If None, adds at chronological position
            
        Returns:
            Index where the line was inserted
            
        Raises:
            SubtitleEngineError: If the operation fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data loaded")
        
        self._save_state()
        
        try:
            if words is None:
                words = []
            if style_overrides is None:
                style_overrides = {}
            
            line = SubtitleLine(start_time, end_time, text, words, style_overrides)
            
            if insert_index is not None:
                # Insert at specific index
                self._subtitle_data.lines.insert(insert_index, line)
                inserted_index = insert_index
                # Re-sort to maintain chronological order
                self._subtitle_data.lines.sort(key=lambda x: x.start_time)
                # Find the actual index after sorting
                for i, sorted_line in enumerate(self._subtitle_data.lines):
                    if sorted_line is line:
                        inserted_index = i
                        break
            else:
                # Find chronological position
                inserted_index = 0
                for i, existing_line in enumerate(self._subtitle_data.lines):
                    if start_time < existing_line.start_time:
                        inserted_index = i
                        break
                    inserted_index = i + 1
                
                self._subtitle_data.lines.insert(inserted_index, line)
            
            # Re-validate the entire data
            self._subtitle_data.validate()
            
            return inserted_index
            
        except (ValidationError, Exception) as e:
            # Restore previous state on error
            if self._undo_stack:
                self._subtitle_data = self._undo_stack.pop()
            raise SubtitleEngineError(f"Failed to add subtitle line: {e}")
    
    def remove_line(self, index: int) -> SubtitleLine:
        """
        Remove a subtitle line by index.
        
        Args:
            index: Index of the line to remove
            
        Returns:
            The removed SubtitleLine
            
        Raises:
            SubtitleEngineError: If the operation fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data loaded")
        
        if not (0 <= index < len(self._subtitle_data.lines)):
            raise SubtitleEngineError(f"Line index {index} out of range")
        
        self._save_state()
        
        try:
            removed_line = self._subtitle_data.lines.pop(index)
            return removed_line
        except Exception as e:
            # Restore previous state on error
            if self._undo_stack:
                self._subtitle_data = self._undo_stack.pop()
            raise SubtitleEngineError(f"Failed to remove subtitle line: {e}")
    
    def update_line(self, index: int, start_time: Optional[float] = None,
                   end_time: Optional[float] = None, text: Optional[str] = None,
                   words: Optional[List[WordTiming]] = None,
                   style_overrides: Optional[Dict[str, Any]] = None) -> None:
        """
        Update a subtitle line.
        
        Args:
            index: Index of the line to update
            start_time: New start time (if provided)
            end_time: New end time (if provided)
            text: New text content (if provided)
            words: New word timing list (if provided)
            style_overrides: New style overrides (if provided)
            
        Raises:
            SubtitleEngineError: If the operation fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data loaded")
        
        if not (0 <= index < len(self._subtitle_data.lines)):
            raise SubtitleEngineError(f"Line index {index} out of range")
        
        self._save_state()
        
        try:
            line = self._subtitle_data.lines[index]
            
            # Store original start time for word timing adjustment
            original_start_time = line.start_time
            
            # Update fields if provided
            if start_time is not None:
                line.start_time = start_time
                # If timing changed, also update word timing proportionally
                if line.words and end_time is None:
                    # Shift word timing to match new start time
                    time_offset = start_time - original_start_time
                    for word in line.words:
                        word.start_time += time_offset
                        word.end_time += time_offset
            
            if end_time is not None:
                line.end_time = end_time
            
            if text is not None:
                line.text = text
                # If text changed but words weren't explicitly provided, clear word timing
                if words is None and line.words:
                    line.words = []
            
            if words is not None:
                line.words = words
            
            if style_overrides is not None:
                line.style_overrides = style_overrides
            
            # Re-validate the line and entire data
            line.validate()
            
            # Re-sort lines if timing changed
            if start_time is not None:
                self._subtitle_data.lines.sort(key=lambda x: x.start_time)
            
            self._subtitle_data.validate()
            
        except (ValidationError, Exception) as e:
            # Restore previous state on error
            if self._undo_stack:
                self._subtitle_data = self._undo_stack.pop()
            raise SubtitleEngineError(f"Failed to update subtitle line: {e}")
    
    def shift_timing(self, offset: float, start_index: Optional[int] = None,
                    end_index: Optional[int] = None) -> None:
        """
        Shift timing of subtitle lines by a given offset.
        
        Args:
            offset: Time offset in seconds (positive or negative)
            start_index: Start index for range (inclusive). If None, starts from beginning
            end_index: End index for range (inclusive). If None, goes to end
            
        Raises:
            SubtitleEngineError: If the operation fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data loaded")
        
        if not self._subtitle_data.lines:
            return  # Nothing to shift
        
        self._save_state()
        
        try:
            if start_index is None:
                start_index = 0
            if end_index is None:
                end_index = len(self._subtitle_data.lines) - 1
            
            # Validate range
            if not (0 <= start_index <= end_index < len(self._subtitle_data.lines)):
                raise SubtitleEngineError("Invalid index range for timing shift")
            
            # Apply offset to lines in range
            for i in range(start_index, end_index + 1):
                line = self._subtitle_data.lines[i]
                
                # Shift line timing
                new_start = line.start_time + offset
                new_end = line.end_time + offset
                
                # Ensure times don't go negative
                if new_start < 0:
                    raise SubtitleEngineError(f"Timing shift would result in negative start time for line {i}")
                
                line.start_time = new_start
                line.end_time = new_end
                
                # Shift word timing if present
                for word in line.words:
                    word.start_time += offset
                    word.end_time += offset
            
            # Re-validate the entire data
            self._subtitle_data.validate()
            
        except (ValidationError, Exception) as e:
            # Restore previous state on error
            if self._undo_stack:
                self._subtitle_data = self._undo_stack.pop()
            raise SubtitleEngineError(f"Failed to shift timing: {e}")
    
    def scale_timing(self, factor: float, start_index: Optional[int] = None,
                    end_index: Optional[int] = None) -> None:
        """
        Scale timing of subtitle lines by a given factor.
        
        Args:
            factor: Scaling factor (e.g., 1.1 for 10% slower, 0.9 for 10% faster)
            start_index: Start index for range (inclusive). If None, starts from beginning
            end_index: End index for range (inclusive). If None, goes to end
            
        Raises:
            SubtitleEngineError: If the operation fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data loaded")
        
        if not self._subtitle_data.lines:
            return  # Nothing to scale
        
        if factor <= 0:
            raise SubtitleEngineError("Scaling factor must be positive")
        
        self._save_state()
        
        try:
            if start_index is None:
                start_index = 0
            if end_index is None:
                end_index = len(self._subtitle_data.lines) - 1
            
            # Validate range
            if not (0 <= start_index <= end_index < len(self._subtitle_data.lines)):
                raise SubtitleEngineError("Invalid index range for timing scaling")
            
            # Get reference point (start of first line in range)
            reference_time = self._subtitle_data.lines[start_index].start_time
            
            # Apply scaling to lines in range
            for i in range(start_index, end_index + 1):
                line = self._subtitle_data.lines[i]
                
                # Scale line timing relative to reference point
                line.start_time = reference_time + (line.start_time - reference_time) * factor
                line.end_time = reference_time + (line.end_time - reference_time) * factor
                
                # Scale word timing if present
                for word in line.words:
                    word.start_time = reference_time + (word.start_time - reference_time) * factor
                    word.end_time = reference_time + (word.end_time - reference_time) * factor
            
            # Re-validate the entire data
            self._subtitle_data.validate()
            
        except (ValidationError, Exception) as e:
            # Restore previous state on error
            if self._undo_stack:
                self._subtitle_data = self._undo_stack.pop()
            raise SubtitleEngineError(f"Failed to scale timing: {e}")
    
    def generate_word_timing(self, line_index: int, method: str = 'equal') -> None:
        """
        Generate word-level timing for a subtitle line.
        
        Args:
            line_index: Index of the line to generate word timing for
            method: Method to use ('equal' for equal distribution, 'proportional' for length-based)
            
        Raises:
            SubtitleEngineError: If the operation fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data loaded")
        
        if not (0 <= line_index < len(self._subtitle_data.lines)):
            raise SubtitleEngineError(f"Line index {line_index} out of range")
        
        self._save_state()
        
        try:
            line = self._subtitle_data.lines[line_index]
            words = line.text.split()
            
            if not words:
                line.words = []
                return
            
            line_duration = line.end_time - line.start_time
            
            if method == 'equal':
                # Equal time distribution
                word_duration = line_duration / len(words)
                word_timings = []
                
                for i, word in enumerate(words):
                    start_time = line.start_time + i * word_duration
                    end_time = start_time + word_duration
                    
                    word_timing = WordTiming(word, start_time, end_time)
                    word_timings.append(word_timing)
                
                line.words = word_timings
                
            elif method == 'proportional':
                # Proportional to word length
                total_chars = sum(len(word) for word in words)
                word_timings = []
                current_time = line.start_time
                
                for word in words:
                    word_duration = (len(word) / total_chars) * line_duration
                    end_time = current_time + word_duration
                    
                    word_timing = WordTiming(word, current_time, end_time)
                    word_timings.append(word_timing)
                    
                    current_time = end_time
                
                line.words = word_timings
                
            else:
                raise SubtitleEngineError(f"Unknown word timing method: {method}")
            
            # Re-validate the line
            line.validate()
            
        except (ValidationError, Exception) as e:
            # Restore previous state on error
            if self._undo_stack:
                self._subtitle_data = self._undo_stack.pop()
            raise SubtitleEngineError(f"Failed to generate word timing: {e}")
    
    def clear_word_timing(self, line_index: int) -> None:
        """
        Clear word-level timing for a subtitle line.
        
        Args:
            line_index: Index of the line to clear word timing for
            
        Raises:
            SubtitleEngineError: If the operation fails
        """
        if not self.has_data:
            raise SubtitleEngineError("No subtitle data loaded")
        
        if not (0 <= line_index < len(self._subtitle_data.lines)):
            raise SubtitleEngineError(f"Line index {line_index} out of range")
        
        self._save_state()
        
        try:
            self._subtitle_data.lines[line_index].words = []
        except Exception as e:
            # Restore previous state on error
            if self._undo_stack:
                self._subtitle_data = self._undo_stack.pop()
            raise SubtitleEngineError(f"Failed to clear word timing: {e}")
    
    def get_line_at_time(self, time: float) -> Optional[Tuple[int, SubtitleLine]]:
        """
        Get the subtitle line active at a specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            Tuple of (index, SubtitleLine) if found, None otherwise
        """
        if not self.has_data:
            return None
        
        for i, line in enumerate(self._subtitle_data.lines):
            if line.start_time <= time < line.end_time:
                return (i, line)
        
        return None
    
    def get_word_at_time(self, time: float) -> Optional[Tuple[int, int, WordTiming]]:
        """
        Get the word active at a specific time.
        
        Args:
            time: Time in seconds
            
        Returns:
            Tuple of (line_index, word_index, WordTiming) if found, None otherwise
        """
        line_result = self.get_line_at_time(time)
        if not line_result:
            return None
        
        line_index, line = line_result
        
        for word_index, word in enumerate(line.words):
            if word.start_time <= time < word.end_time:
                return (line_index, word_index, word)
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current subtitle data.
        
        Returns:
            Dictionary containing various statistics
        """
        if not self.has_data:
            return {
                'total_lines': 0,
                'total_duration': 0.0,
                'total_words': 0,
                'has_word_timing': False,
                'lines_with_word_timing': 0
            }
        
        stats = self._subtitle_data.get_statistics()
        
        # Add engine-specific statistics
        lines_with_word_timing = sum(1 for line in self._subtitle_data.lines if line.words)
        stats.update({
            'has_word_timing': lines_with_word_timing > 0,
            'lines_with_word_timing': lines_with_word_timing,
            'word_timing_coverage': lines_with_word_timing / len(self._subtitle_data.lines) if self._subtitle_data.lines else 0.0
        })
        
        return stats
    
    def validate_data(self) -> List[str]:
        """
        Validate the current subtitle data and return any issues found.
        
        Returns:
            List of validation issue descriptions (empty if no issues)
        """
        if not self.has_data:
            return ["No subtitle data loaded"]
        
        issues = []
        
        try:
            self._subtitle_data.validate()
        except ValidationError as e:
            issues.append(str(e))
        
        # Additional checks for common issues
        for i, line in enumerate(self._subtitle_data.lines):
            # Check for very short durations
            if line.duration < 0.1:
                issues.append(f"Line {i}: Very short duration ({line.duration:.2f}s)")
            
            # Check for very long durations
            if line.duration > 10.0:
                issues.append(f"Line {i}: Very long duration ({line.duration:.2f}s)")
            
            # Check for empty text
            if not line.text.strip():
                issues.append(f"Line {i}: Empty or whitespace-only text")
            
            # Check word timing consistency
            if line.words:
                word_text = ' '.join(word.word for word in line.words)
                if word_text.strip() != line.text.strip():
                    issues.append(f"Line {i}: Word timing text doesn't match line text")
        
        return issues