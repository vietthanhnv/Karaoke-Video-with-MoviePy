"""
Tests for core interfaces and data models.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from subtitle_creator.interfaces import (
    SubtitleData, SubtitleLine, WordTiming,
    SubtitleParser, Effect, MediaManager, PreviewEngine, ExportManager,
    SubtitleCreatorError, ParseError, ExportError, MediaError, AudioError, EffectError
)


def test_word_timing_creation():
    """Test WordTiming dataclass creation."""
    word_timing = WordTiming(word="hello", start_time=1.0, end_time=1.5)
    assert word_timing.word == "hello"
    assert word_timing.start_time == 1.0
    assert word_timing.end_time == 1.5


def test_subtitle_line_creation():
    """Test SubtitleLine dataclass creation."""
    words = [
        WordTiming(word="hello", start_time=1.0, end_time=1.3),
        WordTiming(word="world", start_time=1.3, end_time=1.8)
    ]
    line = SubtitleLine(
        start_time=1.0,
        end_time=1.8,
        text="hello world",
        words=words,
        style_overrides={"color": "red"}
    )
    assert line.start_time == 1.0
    assert line.end_time == 1.8
    assert line.text == "hello world"
    assert len(line.words) == 2
    assert line.style_overrides["color"] == "red"


def test_subtitle_data_creation():
    """Test SubtitleData dataclass creation."""
    words = [WordTiming(word="test", start_time=0.0, end_time=1.0)]
    lines = [SubtitleLine(
        start_time=0.0,
        end_time=1.0,
        text="test",
        words=words,
        style_overrides={}
    )]
    
    subtitle_data = SubtitleData(
        lines=lines,
        global_style={"font": "Arial"},
        metadata={"version": "1.0"}
    )
    
    assert len(subtitle_data.lines) == 1
    assert subtitle_data.global_style["font"] == "Arial"
    assert subtitle_data.metadata["version"] == "1.0"


def test_abstract_classes_cannot_be_instantiated():
    """Test that abstract base classes cannot be instantiated directly."""
    with pytest.raises(TypeError):
        SubtitleParser()
    
    with pytest.raises(TypeError):
        Effect("test", {})
    
    with pytest.raises(TypeError):
        MediaManager()
    
    with pytest.raises(TypeError):
        PreviewEngine()
    
    with pytest.raises(TypeError):
        ExportManager()


def test_custom_exceptions():
    """Test custom exception classes."""
    # Test base exception
    base_error = SubtitleCreatorError("Base error")
    assert str(base_error) == "Base error"
    assert isinstance(base_error, Exception)
    
    # Test specific exceptions
    parse_error = ParseError("Parse failed")
    assert isinstance(parse_error, SubtitleCreatorError)
    
    export_error = ExportError("Export failed")
    assert isinstance(export_error, SubtitleCreatorError)
    
    media_error = MediaError("Media failed")
    assert isinstance(media_error, SubtitleCreatorError)
    
    audio_error = AudioError("Audio failed")
    assert isinstance(audio_error, SubtitleCreatorError)
    
    effect_error = EffectError("Effect failed")
    assert isinstance(effect_error, SubtitleCreatorError)


class TestSubtitleParser(SubtitleParser):
    """Concrete implementation for testing."""
    
    def parse(self, file_path: str) -> SubtitleData:
        return SubtitleData(lines=[], global_style={}, metadata={})
    
    def export(self, subtitle_data: SubtitleData, output_path: str) -> None:
        pass
    
    def get_supported_extensions(self) -> list:
        return ['.test']


def test_concrete_subtitle_parser():
    """Test that concrete implementations work correctly."""
    parser = TestSubtitleParser()
    
    # Test parse method
    result = parser.parse("test.txt")
    assert isinstance(result, SubtitleData)
    assert len(result.lines) == 0
    
    # Test supported extensions
    extensions = parser.get_supported_extensions()
    assert extensions == ['.test']