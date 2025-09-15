"""
Subtitle file parsers for the Subtitle Creator application.

This module contains implementations for parsing different subtitle formats
including custom JSON format with word-level timing and standard .ASS format.
"""

import json
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from .interfaces import SubtitleParser, ParseError
from .models import SubtitleData, SubtitleLine, WordTiming, ValidationError


class SubtitleParserFactory:
    """Factory class for creating appropriate subtitle parsers based on file format."""
    
    _parsers = {}
    
    @classmethod
    def register_parser(cls, parser_class: type) -> None:
        """Register a parser class for its supported extensions."""
        parser_instance = parser_class()
        for ext in parser_instance.get_supported_extensions():
            cls._parsers[ext.lower()] = parser_class
    
    @classmethod
    def create_parser(cls, file_path: str) -> SubtitleParser:
        """
        Create appropriate parser based on file extension.
        
        Args:
            file_path: Path to the subtitle file
            
        Returns:
            SubtitleParser instance for the file format
            
        Raises:
            ParseError: If no parser is available for the file format
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in cls._parsers:
            raise ParseError(f"No parser available for file extension: {ext}")
        
        return cls._parsers[ext]()
    
    @classmethod
    def detect_format(cls, file_path: str) -> str:
        """
        Detect subtitle format by examining file content.
        
        Args:
            file_path: Path to the subtitle file
            
        Returns:
            Detected format string ('json', 'ass', or 'unknown')
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Try to detect JSON format
            if content.startswith('{') and content.endswith('}'):
                try:
                    data = json.loads(content)
                    if 'segments' in data or 'word_segments' in data:
                        return 'json'
                except json.JSONDecodeError:
                    pass
            
            # Try to detect ASS format
            if '[Script Info]' in content and '[Events]' in content:
                return 'ass'
            
            return 'unknown'
            
        except Exception:
            return 'unknown'


class JSONSubtitleParser(SubtitleParser):
    """Parser for custom JSON subtitle format with word-level timing."""
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.json']
    
    def parse(self, file_path: str) -> SubtitleData:
        """
        Parse a JSON subtitle file.
        
        Args:
            file_path: Path to the JSON subtitle file
            
        Returns:
            SubtitleData object containing parsed subtitle information
            
        Raises:
            ParseError: If the file cannot be parsed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ParseError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            raise ParseError(f"Error reading file {file_path}: {e}")
        
        try:
            return self._parse_json_data(data)
        except Exception as e:
            raise ParseError(f"Error parsing JSON subtitle data: {e}")
    
    def _parse_json_data(self, data: Dict[str, Any]) -> SubtitleData:
        """
        Parse JSON data structure into SubtitleData.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            SubtitleData object
        """
        # Extract metadata
        metadata = data.get('metadata', {})
        
        # Extract segments (subtitle lines)
        segments = data.get('segments', [])
        word_segments = data.get('word_segments', [])
        
        # Create word timing lookup by segment_id
        words_by_segment = {}
        for word_data in word_segments:
            segment_id = word_data.get('segment_id')
            if segment_id is not None:
                if segment_id not in words_by_segment:
                    words_by_segment[segment_id] = []
                
                try:
                    word_timing = WordTiming(
                        word=word_data['word'],
                        start_time=float(word_data['start_time']),
                        end_time=float(word_data['end_time'])
                    )
                    words_by_segment[segment_id].append(word_timing)
                except (KeyError, ValueError, ValidationError) as e:
                    # Skip invalid word timing but continue parsing
                    continue
        
        # Create subtitle lines
        lines = []
        for i, segment in enumerate(segments):
            try:
                segment_id = segment.get('segment_id', i)
                words = words_by_segment.get(segment_id, [])
                
                # Get segment timing
                segment_start = float(segment['start_time'])
                segment_end = float(segment['end_time'])
                
                # Filter words to only include those within the segment time range
                valid_words = []
                for word in words:
                    # Only include words that are within the segment time range
                    if (word.start_time >= segment_start and 
                        word.end_time <= segment_end):
                        valid_words.append(word)
                
                # Sort words by start time
                valid_words.sort(key=lambda w: w.start_time)
                
                # Skip lines with no text or "[No text]" placeholder
                text = segment.get('text', '').strip()
                if not text or text == '[No text]':
                    continue
                
                # Try to create line with word timings, fall back to no words if validation fails
                try:
                    line = SubtitleLine(
                        start_time=segment_start,
                        end_time=segment_end,
                        text=text,
                        words=valid_words,
                        style_overrides={}
                    )
                except ValidationError:
                    # If word timing validation fails, create line without word timings
                    line = SubtitleLine(
                        start_time=segment_start,
                        end_time=segment_end,
                        text=text,
                        words=[],
                        style_overrides={}
                    )
                lines.append(line)
                
            except (KeyError, ValueError, ValidationError) as e:
                raise ParseError(f"Error parsing segment {i}: {e}")
        
        # Sort lines by start time
        lines.sort(key=lambda line: line.start_time)
        
        # Create global style from metadata or defaults
        global_style = {
            'font_family': 'Arial',
            'font_size': 20,
            'font_weight': 'normal',
            'text_color': (255, 255, 255, 255),  # White
            'outline_color': (0, 0, 0, 255),     # Black
            'shadow_color': (0, 0, 0, 128),      # Semi-transparent black
            'position': ('center', 0, 50),       # Center, no offset, 50px from bottom
        }
        
        try:
            subtitle_data = SubtitleData(
                lines=lines,
                global_style=global_style,
                metadata=metadata
            )
            return subtitle_data
        except ValidationError as e:
            raise ParseError(f"Validation error in subtitle data: {e}")
    
    def export(self, subtitle_data: SubtitleData, output_path: str) -> None:
        """
        Export subtitle data to JSON format.
        
        Args:
            subtitle_data: The subtitle data to export
            output_path: Path where the file should be saved
            
        Raises:
            ExportError: If the file cannot be exported
        """
        try:
            # Build segments and word_segments
            segments = []
            word_segments = []
            
            for i, line in enumerate(subtitle_data.lines):
                # Create segment
                segment = {
                    'start_time': line.start_time,
                    'end_time': line.end_time,
                    'duration': line.end_time - line.start_time,
                    'text': line.text,
                    'segment_id': i
                }
                segments.append(segment)
                
                # Create word segments
                for word in line.words:
                    word_segment = {
                        'word': word.word,
                        'start_time': word.start_time,
                        'end_time': word.end_time,
                        'duration': word.end_time - word.start_time,
                        'segment_id': i
                    }
                    word_segments.append(word_segment)
            
            # Build complete data structure
            export_data = {
                'metadata': subtitle_data.metadata.copy(),
                'segments': segments,
                'word_segments': word_segments
            }
            
            # Update metadata with current statistics
            export_data['metadata'].update({
                'total_segments': len(segments),
                'total_words': len(word_segments),
                'format_version': '1.0'
            })
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            from .interfaces import ExportError
            raise ExportError(f"Error exporting to JSON: {e}")


class ASSSubtitleParser(SubtitleParser):
    """Parser for standard .ASS subtitle format."""
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.ass', '.ssa']
    
    def parse(self, file_path: str) -> SubtitleData:
        """
        Parse an ASS subtitle file.
        
        Args:
            file_path: Path to the ASS subtitle file
            
        Returns:
            SubtitleData object containing parsed subtitle information
            
        Raises:
            ParseError: If the file cannot be parsed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise ParseError(f"File not found: {file_path}")
        except Exception as e:
            raise ParseError(f"Error reading file {file_path}: {e}")
        
        try:
            return self._parse_ass_content(content)
        except Exception as e:
            raise ParseError(f"Error parsing ASS subtitle data: {e}")
    
    def _parse_ass_content(self, content: str) -> SubtitleData:
        """
        Parse ASS file content into SubtitleData.
        
        Args:
            content: ASS file content
            
        Returns:
            SubtitleData object
        """
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
                raise ParseError(f"Error parsing line {line_num}: {e}")
        
        # Convert events to SubtitleLine objects
        subtitle_lines = []
        for event in events:
            try:
                # Parse karaoke timing if present
                words = self._parse_karaoke_timing(event['text'], event['start'])
                
                # Clean text of karaoke tags
                clean_text = self._clean_ass_text(event['text'])
                
                if clean_text.strip():  # Skip empty lines
                    line = SubtitleLine(
                        start_time=event['start'],
                        end_time=event['end'],
                        text=clean_text,
                        words=words,
                        style_overrides={}
                    )
                    subtitle_lines.append(line)
                    
            except ValidationError as e:
                # Skip invalid lines but continue parsing
                continue
        
        # Sort lines by start time
        subtitle_lines.sort(key=lambda line: line.start_time)
        
        # Create global style from default style
        global_style = self._create_global_style(styles)
        
        try:
            subtitle_data = SubtitleData(
                lines=subtitle_lines,
                global_style=global_style,
                metadata=metadata
            )
            return subtitle_data
        except ValidationError as e:
            raise ParseError(f"Validation error in subtitle data: {e}")
    
    def _parse_script_info_line(self, line: str, metadata: Dict[str, Any]) -> None:
        """Parse a line from the Script Info section."""
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    def _parse_style_line(self, line: str, styles: Dict[str, Dict[str, Any]]) -> None:
        """Parse a style definition line."""
        if line.startswith('Style:'):
            parts = line[6:].split(',')
            if len(parts) >= 23:  # ASS style has 23 fields
                style_name = parts[0].strip()
                styles[style_name] = {
                    'fontname': parts[1].strip(),
                    'fontsize': int(parts[2]) if parts[2].isdigit() else 20,
                    'primary_colour': parts[3].strip(),
                    'secondary_colour': parts[4].strip(),
                    'outline_colour': parts[5].strip(),
                    'back_colour': parts[6].strip(),
                    'bold': parts[7] == '-1',
                    'italic': parts[8] == '-1',
                    'alignment': int(parts[18]) if parts[18].isdigit() else 2
                }
    
    def _parse_event_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse an event (dialogue) line."""
        if line.startswith('Dialogue:'):
            parts = line[9:].split(',', 9)  # Split into max 10 parts
            if len(parts) >= 10:
                try:
                    start_time = self._parse_ass_time(parts[1])
                    end_time = self._parse_ass_time(parts[2])
                    text = parts[9]  # Text is the last part
                    
                    return {
                        'start': start_time,
                        'end': end_time,
                        'style': parts[3].strip(),
                        'text': text
                    }
                except ValueError as e:
                    raise ParseError(f"Invalid time format in line {line_num}: {e}")
        
        return None
    
    def _parse_ass_time(self, time_str: str) -> float:
        """
        Parse ASS time format (H:MM:SS.CC) to seconds.
        
        Args:
            time_str: Time string in ASS format
            
        Returns:
            Time in seconds as float
        """
        time_str = time_str.strip()
        
        # ASS format: H:MM:SS.CC
        match = re.match(r'(\d+):(\d{2}):(\d{2})\.(\d{2})', time_str)
        if not match:
            raise ValueError(f"Invalid ASS time format: {time_str}")
        
        hours, minutes, seconds, centiseconds = match.groups()
        
        total_seconds = (
            int(hours) * 3600 +
            int(minutes) * 60 +
            int(seconds) +
            int(centiseconds) / 100.0
        )
        
        return total_seconds
    
    def _parse_karaoke_timing(self, text: str, line_start_time: float = 0.0) -> List[WordTiming]:
        """
        Parse karaoke timing tags from ASS text.
        
        Args:
            text: ASS text with karaoke tags
            line_start_time: Start time of the line to offset word timing
            
        Returns:
            List of WordTiming objects
        """
        words = []
        current_time = line_start_time  # Start from line start time
        
        # Find all karaoke tags {\kXX} where XX is centiseconds
        parts = re.split(r'\{\\k(\d+)\}', text)
        
        for i in range(1, len(parts), 2):  # Every odd index has timing
            if i + 1 < len(parts):
                duration_cs = int(parts[i])  # Duration in centiseconds
                word_text = parts[i + 1].strip()
                
                if word_text:  # Skip empty words
                    duration_s = duration_cs / 100.0  # Convert to seconds
                    
                    try:
                        word = WordTiming(
                            word=word_text,
                            start_time=current_time,
                            end_time=current_time + duration_s
                        )
                        words.append(word)
                        current_time += duration_s
                    except ValidationError:
                        # Skip invalid word timing
                        continue
        
        return words
    
    def _clean_ass_text(self, text: str) -> str:
        """
        Remove ASS formatting tags from text.
        
        Args:
            text: Text with ASS tags
            
        Returns:
            Clean text without tags
        """
        # Remove karaoke tags
        text = re.sub(r'\{\\k\d+\}', '', text)
        
        # Remove other ASS tags
        text = re.sub(r'\{[^}]*\}', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _create_global_style(self, styles: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create global style from ASS styles."""
        # Use Default style if available, otherwise create default
        default_style = styles.get('Default', {})
        
        return {
            'font_family': default_style.get('fontname', 'Arial'),
            'font_size': default_style.get('fontsize', 20),
            'font_weight': 'bold' if default_style.get('bold', False) else 'normal',
            'text_color': (255, 255, 255, 255),  # White (simplified)
            'outline_color': (0, 0, 0, 255),     # Black
            'shadow_color': (0, 0, 0, 128),      # Semi-transparent black
            'position': ('center', 0, 50),       # Center, no offset, 50px from bottom
        }
    
    def export(self, subtitle_data: SubtitleData, output_path: str) -> None:
        """
        Export subtitle data to ASS format.
        
        Args:
            subtitle_data: The subtitle data to export
            output_path: Path where the file should be saved
            
        Raises:
            ExportError: If the file cannot be exported
        """
        try:
            lines = []
            
            # Script Info section
            lines.append('[Script Info]')
            lines.append('Title: Subtitle Creator Export')
            lines.append('ScriptType: v4.00+')
            lines.append('WrapStyle: 0')
            lines.append('ScaledBorderAndShadow: yes')
            lines.append('PlayResX: 1920')
            lines.append('PlayResY: 1080')
            lines.append('')
            
            # V4+ Styles section
            lines.append('[V4+ Styles]')
            lines.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding')
            
            # Create style from global_style
            style = subtitle_data.global_style
            font_family = style.get('font_family', 'Arial')
            font_size = style.get('font_size', 20)
            font_weight = style.get('font_weight', 'normal')
            bold = -1 if font_weight == 'bold' else 0
            
            lines.append(f'Style: Default,{font_family},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,{bold},0,0,0,100,100,0,0,1,2.0,0.0,2,10,10,10,1')
            lines.append('')
            
            # Events section
            lines.append('[Events]')
            lines.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')
            
            for line_data in subtitle_data.lines:
                start_time = self._format_ass_time(line_data.start_time)
                end_time = self._format_ass_time(line_data.end_time)
                
                # Create karaoke text if word timing is available
                if line_data.words:
                    text = self._create_karaoke_text(line_data)
                else:
                    text = line_data.text
                
                lines.append(f'Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}')
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
        except Exception as e:
            from .interfaces import ExportError
            raise ExportError(f"Error exporting to ASS: {e}")
    
    def _format_ass_time(self, seconds: float) -> str:
        """
        Format seconds as ASS time string (H:MM:SS.CC).
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)
        
        return f'{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}'
    
    def _create_karaoke_text(self, line: SubtitleLine) -> str:
        """
        Create karaoke text with timing tags from word timing.
        
        Args:
            line: SubtitleLine with word timing
            
        Returns:
            Text with karaoke timing tags
        """
        if not line.words:
            return line.text
        
        parts = []
        for word in line.words:
            duration_cs = int((word.end_time - word.start_time) * 100)  # Convert to centiseconds
            parts.append(f'{{\\k{duration_cs}}}{word.word}')
        
        return ''.join(parts)


# Register parsers with factory
SubtitleParserFactory.register_parser(JSONSubtitleParser)
SubtitleParserFactory.register_parser(ASSSubtitleParser)