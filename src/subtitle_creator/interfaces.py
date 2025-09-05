"""
Core interfaces and abstract base classes for the Subtitle Creator application.

This module defines the contracts that all parsers, effects, and managers must implement
to ensure consistent behavior across the application.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Optional import for MoviePy - will be available when dependencies are installed
try:
    from moviepy.editor import VideoClip
except ImportError:
    # Create a placeholder for development/testing
    class VideoClip:
        pass


@dataclass
class WordTiming:
    """Represents timing information for a single word in a subtitle line."""
    word: str
    start_time: float
    end_time: float


@dataclass
class SubtitleLine:
    """Represents a single subtitle line with timing and content."""
    start_time: float
    end_time: float
    text: str
    words: List[WordTiming]
    style_overrides: Dict[str, Any]


@dataclass
class SubtitleData:
    """Container for complete subtitle information."""
    lines: List[SubtitleLine]
    global_style: Dict[str, Any]
    metadata: Dict[str, Any]


class SubtitleParser(ABC):
    """Abstract base class for subtitle file parsers."""
    
    @abstractmethod
    def parse(self, file_path: str) -> SubtitleData:
        """
        Parse a subtitle file and return structured subtitle data.
        
        Args:
            file_path: Path to the subtitle file
            
        Returns:
            SubtitleData object containing parsed subtitle information
            
        Raises:
            ParseError: If the file cannot be parsed
        """
        pass
    
    @abstractmethod
    def export(self, subtitle_data: SubtitleData, output_path: str) -> None:
        """
        Export subtitle data to a file.
        
        Args:
            subtitle_data: The subtitle data to export
            output_path: Path where the file should be saved
            
        Raises:
            ExportError: If the file cannot be exported
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions supported by this parser.
        
        Returns:
            List of supported file extensions (e.g., ['.json', '.ass'])
        """
        pass


class Effect(ABC):
    """Abstract base class for subtitle effects."""
    
    def __init__(self, name: str, parameters: Dict[str, Any]):
        """
        Initialize the effect with a name and parameters.
        
        Args:
            name: Human-readable name of the effect
            parameters: Dictionary of effect parameters
        """
        self.name = name
        self.parameters = parameters
    
    @abstractmethod
    def apply(self, clip: VideoClip, subtitle_data: SubtitleData) -> VideoClip:
        """
        Apply the effect to a video clip with subtitle data.
        
        Args:
            clip: The MoviePy VideoClip to apply the effect to
            subtitle_data: Subtitle timing and content information
            
        Returns:
            Modified VideoClip with the effect applied
        """
        pass
    
    @abstractmethod
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the parameter schema for this effect.
        
        Returns:
            Dictionary describing the parameters this effect accepts
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate that the provided parameters are valid for this effect.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        pass


class MediaManager(ABC):
    """Abstract base class for media file management."""
    
    @abstractmethod
    def load_background_media(self, file_path: str) -> VideoClip:
        """
        Load background media (image or video) as a VideoClip.
        
        Args:
            file_path: Path to the media file
            
        Returns:
            MoviePy VideoClip object
            
        Raises:
            MediaError: If the media cannot be loaded
        """
        pass
    
    @abstractmethod
    def load_audio(self, file_path: str) -> Any:
        """
        Load audio file for synchronization.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Audio object compatible with MoviePy
            
        Raises:
            AudioError: If the audio cannot be loaded
        """
        pass
    
    @abstractmethod
    def get_supported_video_formats(self) -> List[str]:
        """Get list of supported video file formats."""
        pass
    
    @abstractmethod
    def get_supported_image_formats(self) -> List[str]:
        """Get list of supported image file formats."""
        pass
    
    @abstractmethod
    def get_supported_audio_formats(self) -> List[str]:
        """Get list of supported audio file formats."""
        pass


class PreviewEngine(ABC):
    """Abstract base class for video preview functionality."""
    
    @abstractmethod
    def generate_preview(self, background: VideoClip, subtitle_data: SubtitleData, 
                        effects: List[Effect]) -> VideoClip:
        """
        Generate a preview video clip with reduced quality for real-time playback.
        
        Args:
            background: Background video clip
            subtitle_data: Subtitle information
            effects: List of effects to apply
            
        Returns:
            Preview VideoClip optimized for playback
        """
        pass
    
    @abstractmethod
    def seek_to_time(self, time: float) -> Any:
        """
        Seek to a specific time in the preview.
        
        Args:
            time: Time in seconds to seek to
        """
        pass


class ExportManager(ABC):
    """Abstract base class for video export functionality."""
    
    @abstractmethod
    def export_video(self, background: VideoClip, subtitle_data: SubtitleData,
                    effects: List[Effect], output_path: str, 
                    export_settings: Dict[str, Any]) -> None:
        """
        Export the final video with full quality.
        
        Args:
            background: Background video clip
            subtitle_data: Subtitle information
            effects: List of effects to apply
            output_path: Path where the video should be saved
            export_settings: Export configuration (quality, format, etc.)
            
        Raises:
            ExportError: If the export fails
        """
        pass
    
    @abstractmethod
    def get_export_progress(self) -> float:
        """
        Get the current export progress as a percentage.
        
        Returns:
            Progress value between 0.0 and 1.0
        """
        pass


# Custom exception classes
class SubtitleCreatorError(Exception):
    """Base exception class for Subtitle Creator errors."""
    pass


class ParseError(SubtitleCreatorError):
    """Raised when subtitle parsing fails."""
    pass


class ExportError(SubtitleCreatorError):
    """Raised when export operations fail."""
    pass


class MediaError(SubtitleCreatorError):
    """Raised when media loading fails."""
    pass


class AudioError(SubtitleCreatorError):
    """Raised when audio processing fails."""
    pass


class EffectError(SubtitleCreatorError):
    """Raised when effect application fails."""
    pass