"""
Configuration management for Subtitle Creator with Effects.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from .interfaces import SubtitleCreatorError


class ConfigurationError(SubtitleCreatorError):
    """Raised when configuration validation fails."""
    pass


class EffectType(Enum):
    """Enumeration of available effect types."""
    TEXT_STYLING = "text_styling"
    ANIMATION = "animation"
    PARTICLE = "particle"


class AnimationType(Enum):
    """Enumeration of available animation types."""
    KARAOKE_HIGHLIGHT = "karaoke_highlight"
    SCALE_BOUNCE = "scale_bounce"
    TYPEWRITER = "typewriter"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"


class ParticleType(Enum):
    """Enumeration of available particle types."""
    HEARTS = "hearts"
    STARS = "stars"
    MUSIC_NOTES = "music_notes"
    SPARKLES = "sparkles"
    CUSTOM_IMAGE = "custom_image"


class TextAlignment(Enum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlignment(Enum):
    """Vertical alignment options."""
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


@dataclass
class StyleConfig:
    """Configuration for text styling and positioning."""
    
    # Font properties
    font_family: str = "Arial"
    font_size: int = 48
    font_weight: str = "normal"  # normal, bold
    
    # Colors (RGBA tuples)
    text_color: Tuple[int, int, int, int] = (255, 255, 255, 255)  # White
    outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255)    # Black
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128)     # Semi-transparent black
    
    # Positioning
    horizontal_alignment: TextAlignment = TextAlignment.CENTER
    vertical_alignment: VerticalAlignment = VerticalAlignment.BOTTOM
    x_offset: int = 0  # Pixels from alignment position
    y_offset: int = -50  # Pixels from alignment position
    
    # Text effects
    outline_width: int = 2
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_blur: int = 3
    
    # Background
    background_enabled: bool = False
    background_color: Tuple[int, int, int, int] = (0, 0, 0, 128)  # Semi-transparent black
    background_padding: int = 10
    background_border_radius: int = 5
    
    def __post_init__(self):
        """Validate style configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate style configuration parameters.
        
        Raises:
            ConfigurationError: If validation fails
        """
        # Font validation
        if not isinstance(self.font_family, str) or not self.font_family.strip():
            raise ConfigurationError("Font family must be a non-empty string")
        
        if not isinstance(self.font_size, int) or self.font_size <= 0:
            raise ConfigurationError("Font size must be a positive integer")
        
        if self.font_weight not in ["normal", "bold"]:
            raise ConfigurationError("Font weight must be 'normal' or 'bold'")
        
        # Color validation
        for color_name, color in [
            ("text_color", self.text_color),
            ("outline_color", self.outline_color),
            ("shadow_color", self.shadow_color),
            ("background_color", self.background_color)
        ]:
            if not self._validate_color(color):
                raise ConfigurationError(f"{color_name} must be a tuple of 4 integers (0-255)")
        
        # Alignment validation
        if not isinstance(self.horizontal_alignment, TextAlignment):
            raise ConfigurationError("Horizontal alignment must be a TextAlignment enum")
        
        if not isinstance(self.vertical_alignment, VerticalAlignment):
            raise ConfigurationError("Vertical alignment must be a VerticalAlignment enum")
        
        # Offset validation
        if not isinstance(self.x_offset, int):
            raise ConfigurationError("X offset must be an integer")
        
        if not isinstance(self.y_offset, int):
            raise ConfigurationError("Y offset must be an integer")
        
        # Effect validation
        if not isinstance(self.outline_width, int) or self.outline_width < 0:
            raise ConfigurationError("Outline width must be a non-negative integer")
        
        if not isinstance(self.shadow_offset_x, int):
            raise ConfigurationError("Shadow offset X must be an integer")
        
        if not isinstance(self.shadow_offset_y, int):
            raise ConfigurationError("Shadow offset Y must be an integer")
        
        if not isinstance(self.shadow_blur, int) or self.shadow_blur < 0:
            raise ConfigurationError("Shadow blur must be a non-negative integer")
        
        # Background validation
        if not isinstance(self.background_enabled, bool):
            raise ConfigurationError("Background enabled must be a boolean")
        
        if not isinstance(self.background_padding, int) or self.background_padding < 0:
            raise ConfigurationError("Background padding must be a non-negative integer")
        
        if not isinstance(self.background_border_radius, int) or self.background_border_radius < 0:
            raise ConfigurationError("Background border radius must be a non-negative integer")
    
    def _validate_color(self, color: Union[Tuple[int, int, int, int], List[int]]) -> bool:
        """Validate RGBA color tuple or list."""
        if not isinstance(color, (tuple, list)) or len(color) != 4:
            return False
        return all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert enums to their values
        data['horizontal_alignment'] = self.horizontal_alignment.value
        data['vertical_alignment'] = self.vertical_alignment.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StyleConfig':
        """Create StyleConfig from dictionary."""
        # Convert enum values back to enums
        if 'horizontal_alignment' in data:
            data['horizontal_alignment'] = TextAlignment(data['horizontal_alignment'])
        if 'vertical_alignment' in data:
            data['vertical_alignment'] = VerticalAlignment(data['vertical_alignment'])
        
        # Convert color lists back to tuples
        for color_key in ['text_color', 'outline_color', 'shadow_color', 'background_color']:
            if color_key in data and isinstance(data[color_key], list):
                data[color_key] = tuple(data[color_key])
        
        return cls(**data)


@dataclass
class EffectConfig:
    """Configuration for visual effects."""
    
    effect_type: EffectType
    effect_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    layer_order: int = 0
    
    def __post_init__(self):
        """Validate effect configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate effect configuration parameters.
        
        Raises:
            ConfigurationError: If validation fails
        """
        # Basic validation
        if not isinstance(self.effect_type, EffectType):
            raise ConfigurationError("Effect type must be an EffectType enum")
        
        if not isinstance(self.effect_name, str) or not self.effect_name.strip():
            raise ConfigurationError("Effect name must be a non-empty string")
        
        if not isinstance(self.parameters, dict):
            raise ConfigurationError("Parameters must be a dictionary")
        
        if not isinstance(self.enabled, bool):
            raise ConfigurationError("Enabled must be a boolean")
        
        if not isinstance(self.layer_order, int):
            raise ConfigurationError("Layer order must be an integer")
        
        # Validate parameters based on effect type
        self._validate_effect_parameters()
    
    def _validate_effect_parameters(self) -> None:
        """Validate effect-specific parameters."""
        if self.effect_type == EffectType.TEXT_STYLING:
            self._validate_text_styling_parameters()
        elif self.effect_type == EffectType.ANIMATION:
            self._validate_animation_parameters()
        elif self.effect_type == EffectType.PARTICLE:
            self._validate_particle_parameters()
    
    def _validate_text_styling_parameters(self) -> None:
        """Validate text styling effect parameters."""
        # Text styling effects use StyleConfig parameters
        # Additional validation can be added here for specific styling effects
        pass
    
    def _validate_animation_parameters(self) -> None:
        """Validate animation effect parameters."""
        if 'animation_type' in self.parameters:
            try:
                AnimationType(self.parameters['animation_type'])
            except ValueError:
                raise ConfigurationError(f"Invalid animation type: {self.parameters['animation_type']}")
        
        # Validate common animation parameters
        if 'duration' in self.parameters:
            duration = self.parameters['duration']
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ConfigurationError("Animation duration must be a positive number")
        
        if 'intensity' in self.parameters:
            intensity = self.parameters['intensity']
            if not isinstance(intensity, (int, float)) or not 0 <= intensity <= 1:
                raise ConfigurationError("Animation intensity must be between 0 and 1")
    
    def _validate_particle_parameters(self) -> None:
        """Validate particle effect parameters."""
        if 'particle_type' in self.parameters:
            try:
                ParticleType(self.parameters['particle_type'])
            except ValueError:
                raise ConfigurationError(f"Invalid particle type: {self.parameters['particle_type']}")
        
        # Validate particle-specific parameters
        if 'count' in self.parameters:
            count = self.parameters['count']
            if not isinstance(count, int) or count < 0:
                raise ConfigurationError("Particle count must be a non-negative integer")
        
        if 'size' in self.parameters:
            size = self.parameters['size']
            if not isinstance(size, (int, float)) or size <= 0:
                raise ConfigurationError("Particle size must be a positive number")
        
        if 'velocity' in self.parameters:
            velocity = self.parameters['velocity']
            if not isinstance(velocity, (int, float)):
                raise ConfigurationError("Particle velocity must be a number")
        
        if 'custom_image_path' in self.parameters:
            path = self.parameters['custom_image_path']
            if not isinstance(path, str):
                raise ConfigurationError("Custom image path must be a string")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['effect_type'] = self.effect_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EffectConfig':
        """Create EffectConfig from dictionary."""
        if 'effect_type' in data:
            data['effect_type'] = EffectType(data['effect_type'])
        
        return cls(**data)


@dataclass
class ExportSettings:
    """Configuration for video export."""
    
    # Output format
    format: str = "mp4"
    codec: str = "libx264"
    
    # Quality settings
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    bitrate: str = "5000k"
    
    # Audio settings
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    
    # Output path
    output_path: str = ""
    
    def __post_init__(self):
        """Validate export settings after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate export settings.
        
        Raises:
            ConfigurationError: If validation fails
        """
        # Format validation
        if not isinstance(self.format, str) or self.format not in ["mp4", "avi", "mov"]:
            raise ConfigurationError("Format must be one of: mp4, avi, mov")
        
        if not isinstance(self.codec, str) or not self.codec.strip():
            raise ConfigurationError("Codec must be a non-empty string")
        
        # Resolution validation
        if not isinstance(self.resolution, (tuple, list)) or len(self.resolution) != 2:
            raise ConfigurationError("Resolution must be a tuple of two integers")
        
        width, height = self.resolution
        if not isinstance(width, int) or not isinstance(height, int):
            raise ConfigurationError("Resolution values must be integers")
        
        if width <= 0 or height <= 0:
            raise ConfigurationError("Resolution values must be positive")
        
        # FPS validation
        if not isinstance(self.fps, int) or self.fps <= 0:
            raise ConfigurationError("FPS must be a positive integer")
        
        # Bitrate validation
        if not isinstance(self.bitrate, str) or not self.bitrate.strip():
            raise ConfigurationError("Bitrate must be a non-empty string")
        
        # Audio settings validation
        if not isinstance(self.audio_codec, str) or not self.audio_codec.strip():
            raise ConfigurationError("Audio codec must be a non-empty string")
        
        if not isinstance(self.audio_bitrate, str) or not self.audio_bitrate.strip():
            raise ConfigurationError("Audio bitrate must be a non-empty string")
        
        # Output path validation
        if not isinstance(self.output_path, str):
            raise ConfigurationError("Output path must be a string")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExportSettings':
        """Create ExportSettings from dictionary."""
        # Convert resolution list back to tuple
        if 'resolution' in data and isinstance(data['resolution'], list):
            data['resolution'] = tuple(data['resolution'])
        
        return cls(**data)


@dataclass
class ProjectConfig:
    """Complete project configuration including all components."""
    
    # Media files
    background_media_path: str = ""
    audio_file_path: str = ""
    subtitle_file_path: str = ""
    
    # Configuration objects
    global_style: StyleConfig = field(default_factory=StyleConfig)
    effects: List[EffectConfig] = field(default_factory=list)
    export_settings: ExportSettings = field(default_factory=ExportSettings)
    
    # Project metadata
    project_name: str = "Untitled Project"
    created_at: str = ""
    modified_at: str = ""
    version: str = "1.0"
    
    def __post_init__(self):
        """Validate project configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate complete project configuration.
        
        Raises:
            ConfigurationError: If validation fails
        """
        # Path validation
        if not isinstance(self.background_media_path, str):
            raise ConfigurationError("Background media path must be a string")
        
        if not isinstance(self.audio_file_path, str):
            raise ConfigurationError("Audio file path must be a string")
        
        if not isinstance(self.subtitle_file_path, str):
            raise ConfigurationError("Subtitle file path must be a string")
        
        # Configuration object validation
        if not isinstance(self.global_style, StyleConfig):
            raise ConfigurationError("Global style must be a StyleConfig instance")
        
        self.global_style.validate()
        
        if not isinstance(self.effects, list):
            raise ConfigurationError("Effects must be a list")
        
        for i, effect in enumerate(self.effects):
            if not isinstance(effect, EffectConfig):
                raise ConfigurationError(f"Effect {i} must be an EffectConfig instance")
            effect.validate()
        
        if not isinstance(self.export_settings, ExportSettings):
            raise ConfigurationError("Export settings must be an ExportSettings instance")
        
        self.export_settings.validate()
        
        # Metadata validation
        if not isinstance(self.project_name, str) or not self.project_name.strip():
            raise ConfigurationError("Project name must be a non-empty string")
        
        if not isinstance(self.created_at, str):
            raise ConfigurationError("Created at must be a string")
        
        if not isinstance(self.modified_at, str):
            raise ConfigurationError("Modified at must be a string")
        
        if not isinstance(self.version, str) or not self.version.strip():
            raise ConfigurationError("Version must be a non-empty string")
    
    def add_effect(self, effect: EffectConfig) -> None:
        """
        Add an effect to the project.
        
        Args:
            effect: EffectConfig to add
        """
        effect.validate()
        self.effects.append(effect)
        # Sort effects by layer order
        self.effects.sort(key=lambda e: e.layer_order)
    
    def remove_effect(self, index: int) -> None:
        """
        Remove an effect by index.
        
        Args:
            index: Index of the effect to remove
            
        Raises:
            IndexError: If index is out of range
        """
        if 0 <= index < len(self.effects):
            del self.effects[index]
        else:
            raise IndexError(f"Effect index {index} out of range")
    
    def get_effects_by_type(self, effect_type: EffectType) -> List[EffectConfig]:
        """
        Get all effects of a specific type.
        
        Args:
            effect_type: Type of effects to retrieve
            
        Returns:
            List of EffectConfig objects of the specified type
        """
        return [effect for effect in self.effects if effect.effect_type == effect_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'background_media_path': self.background_media_path,
            'audio_file_path': self.audio_file_path,
            'subtitle_file_path': self.subtitle_file_path,
            'global_style': self.global_style.to_dict(),
            'effects': [effect.to_dict() for effect in self.effects],
            'export_settings': asdict(self.export_settings),
            'project_name': self.project_name,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Create ProjectConfig from dictionary."""
        # Convert nested objects
        if 'global_style' in data:
            data['global_style'] = StyleConfig.from_dict(data['global_style'])
        
        if 'effects' in data:
            data['effects'] = [EffectConfig.from_dict(effect_data) for effect_data in data['effects']]
        
        if 'export_settings' in data:
            data['export_settings'] = ExportSettings.from_dict(data['export_settings'])
        
        return cls(**data)
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save project configuration to JSON file.
        
        Args:
            file_path: Path to save the configuration file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ProjectConfig':
        """
        Load project configuration from JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            ProjectConfig instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # Application metadata
    app_name: str = "Subtitle Creator with Effects"
    app_version: str = "0.1.0"
    
    # Default directories
    assets_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))
    temp_dir: str = field(default_factory=lambda: os.path.join(os.path.expanduser('~'), '.subtitle_creator', 'temp'))
    
    # Supported file formats
    supported_video_formats: list = field(default_factory=lambda: ['.mp4', '.avi', '.mov', '.mkv'])
    supported_image_formats: list = field(default_factory=lambda: ['.jpg', '.jpeg', '.png', '.gif'])
    supported_audio_formats: list = field(default_factory=lambda: ['.mp3', '.wav', '.aac', '.ogg'])
    supported_subtitle_formats: list = field(default_factory=lambda: ['.json', '.ass'])
    
    # Preview settings
    preview_resolution: tuple = (640, 360)  # Reduced resolution for smooth preview
    preview_fps: int = 24
    
    # Export settings
    default_export_resolution: tuple = (1920, 1080)
    default_export_fps: int = 30
    default_export_bitrate: str = "5000k"
    
    # UI settings
    window_size: tuple = (1200, 800)
    preview_panel_width_ratio: float = 0.6
    effects_panel_width_ratio: float = 0.4
    
    # Performance settings
    max_preview_cache_size: int = 100  # Number of frames to cache
    background_thread_count: int = 2
    
    def __post_init__(self):
        """Ensure temp directory exists."""
        os.makedirs(self.temp_dir, exist_ok=True)


# Global configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def update_config(**kwargs) -> None:
    """Update configuration values."""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration key: {key}")


def reset_config() -> None:
    """Reset configuration to defaults."""
    global config
    config = AppConfig()