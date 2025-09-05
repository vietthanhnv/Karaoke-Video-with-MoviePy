"""
Tests for configuration management.
"""

import sys
import os
import tempfile
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from subtitle_creator.config import (
    AppConfig, get_config, update_config, reset_config,
    StyleConfig, EffectConfig, ProjectConfig, ExportSettings,
    ConfigurationError, EffectType, AnimationType, ParticleType,
    TextAlignment, VerticalAlignment
)


def test_app_config_defaults():
    """Test AppConfig default values."""
    config = AppConfig()
    
    assert config.app_name == "Subtitle Creator with Effects"
    assert config.app_version == "0.1.0"
    assert config.preview_resolution == (640, 360)
    assert config.preview_fps == 24
    assert config.default_export_resolution == (1920, 1080)
    assert config.default_export_fps == 30
    assert '.mp4' in config.supported_video_formats
    assert '.json' in config.supported_subtitle_formats


def test_get_config():
    """Test getting global configuration."""
    config = get_config()
    assert isinstance(config, AppConfig)
    assert config.app_name == "Subtitle Creator with Effects"


def test_update_config():
    """Test updating configuration values."""
    original_fps = get_config().preview_fps
    
    # Update a valid configuration key
    update_config(preview_fps=30)
    assert get_config().preview_fps == 30
    
    # Test invalid configuration key
    with pytest.raises(ValueError, match="Unknown configuration key"):
        update_config(invalid_key="value")
    
    # Reset for other tests
    update_config(preview_fps=original_fps)


def test_reset_config():
    """Test resetting configuration to defaults."""
    # Modify config
    update_config(preview_fps=60)
    assert get_config().preview_fps == 60
    
    # Reset config
    reset_config()
    assert get_config().preview_fps == 24


def test_temp_directory_creation():
    """Test that temp directory is created."""
    config = AppConfig()
    assert os.path.exists(config.temp_dir)


class TestStyleConfig:
    """Test StyleConfig class."""
    
    def test_style_config_defaults(self):
        """Test StyleConfig default values."""
        style = StyleConfig()
        
        assert style.font_family == "Arial"
        assert style.font_size == 48
        assert style.font_weight == "normal"
        assert style.text_color == (255, 255, 255, 255)
        assert style.outline_color == (0, 0, 0, 255)
        assert style.shadow_color == (0, 0, 0, 128)
        assert style.horizontal_alignment == TextAlignment.CENTER
        assert style.vertical_alignment == VerticalAlignment.BOTTOM
        assert style.x_offset == 0
        assert style.y_offset == -50
        assert style.outline_width == 2
        assert style.shadow_offset_x == 2
        assert style.shadow_offset_y == 2
        assert style.shadow_blur == 3
        assert style.background_enabled == False
        assert style.background_color == (0, 0, 0, 128)
        assert style.background_padding == 10
        assert style.background_border_radius == 5
    
    def test_style_config_validation_valid(self):
        """Test StyleConfig validation with valid data."""
        style = StyleConfig(
            font_family="Times New Roman",
            font_size=36,
            font_weight="bold",
            text_color=(255, 0, 0, 255),
            horizontal_alignment=TextAlignment.LEFT,
            vertical_alignment=VerticalAlignment.TOP
        )
        # Should not raise any exception
        style.validate()
    
    def test_style_config_validation_invalid_font_family(self):
        """Test StyleConfig validation with invalid font family."""
        with pytest.raises(ConfigurationError, match="Font family must be a non-empty string"):
            StyleConfig(font_family="")
        
        with pytest.raises(ConfigurationError, match="Font family must be a non-empty string"):
            StyleConfig(font_family="   ")
    
    def test_style_config_validation_invalid_font_size(self):
        """Test StyleConfig validation with invalid font size."""
        with pytest.raises(ConfigurationError, match="Font size must be a positive integer"):
            StyleConfig(font_size=0)
        
        with pytest.raises(ConfigurationError, match="Font size must be a positive integer"):
            StyleConfig(font_size=-10)
        
        with pytest.raises(ConfigurationError, match="Font size must be a positive integer"):
            StyleConfig(font_size=12.5)
    
    def test_style_config_validation_invalid_font_weight(self):
        """Test StyleConfig validation with invalid font weight."""
        with pytest.raises(ConfigurationError, match="Font weight must be 'normal' or 'bold'"):
            StyleConfig(font_weight="italic")
    
    def test_style_config_validation_invalid_colors(self):
        """Test StyleConfig validation with invalid colors."""
        # Invalid color tuple length
        with pytest.raises(ConfigurationError, match="text_color must be a tuple of 4 integers"):
            StyleConfig(text_color=(255, 255, 255))
        
        # Invalid color values
        with pytest.raises(ConfigurationError, match="text_color must be a tuple of 4 integers"):
            StyleConfig(text_color=(256, 255, 255, 255))
        
        with pytest.raises(ConfigurationError, match="outline_color must be a tuple of 4 integers"):
            StyleConfig(outline_color=(-1, 0, 0, 255))
    
    def test_style_config_validation_invalid_offsets(self):
        """Test StyleConfig validation with invalid offsets."""
        with pytest.raises(ConfigurationError, match="X offset must be an integer"):
            StyleConfig(x_offset=10.5)
        
        with pytest.raises(ConfigurationError, match="Y offset must be an integer"):
            StyleConfig(y_offset="10")
    
    def test_style_config_validation_invalid_effects(self):
        """Test StyleConfig validation with invalid effect parameters."""
        with pytest.raises(ConfigurationError, match="Outline width must be a non-negative integer"):
            StyleConfig(outline_width=-1)
        
        with pytest.raises(ConfigurationError, match="Shadow blur must be a non-negative integer"):
            StyleConfig(shadow_blur=-5)
    
    def test_style_config_serialization(self):
        """Test StyleConfig serialization and deserialization."""
        original = StyleConfig(
            font_family="Helvetica",
            font_size=24,
            text_color=(255, 0, 0, 255),
            horizontal_alignment=TextAlignment.RIGHT
        )
        
        # Convert to dict
        data = original.to_dict()
        assert data['font_family'] == "Helvetica"
        assert data['font_size'] == 24
        assert data['text_color'] == (255, 0, 0, 255)
        assert data['horizontal_alignment'] == "right"
        
        # Convert back from dict
        restored = StyleConfig.from_dict(data)
        assert restored.font_family == original.font_family
        assert restored.font_size == original.font_size
        assert restored.text_color == original.text_color
        assert restored.horizontal_alignment == original.horizontal_alignment


class TestEffectConfig:
    """Test EffectConfig class."""
    
    def test_effect_config_defaults(self):
        """Test EffectConfig default values."""
        effect = EffectConfig(
            effect_type=EffectType.TEXT_STYLING,
            effect_name="test_effect"
        )
        
        assert effect.effect_type == EffectType.TEXT_STYLING
        assert effect.effect_name == "test_effect"
        assert effect.parameters == {}
        assert effect.enabled == True
        assert effect.layer_order == 0
    
    def test_effect_config_validation_valid(self):
        """Test EffectConfig validation with valid data."""
        effect = EffectConfig(
            effect_type=EffectType.ANIMATION,
            effect_name="karaoke_highlight",
            parameters={
                "animation_type": "karaoke_highlight",
                "duration": 0.5,
                "intensity": 0.8
            },
            enabled=True,
            layer_order=1
        )
        # Should not raise any exception
        effect.validate()
    
    def test_effect_config_validation_invalid_basic(self):
        """Test EffectConfig validation with invalid basic parameters."""
        with pytest.raises(ConfigurationError, match="Effect name must be a non-empty string"):
            EffectConfig(effect_type=EffectType.TEXT_STYLING, effect_name="")
        
        with pytest.raises(ConfigurationError, match="Parameters must be a dictionary"):
            EffectConfig(
                effect_type=EffectType.TEXT_STYLING,
                effect_name="test",
                parameters="invalid"
            )
        
        with pytest.raises(ConfigurationError, match="Enabled must be a boolean"):
            EffectConfig(
                effect_type=EffectType.TEXT_STYLING,
                effect_name="test",
                enabled="true"
            )
        
        with pytest.raises(ConfigurationError, match="Layer order must be an integer"):
            EffectConfig(
                effect_type=EffectType.TEXT_STYLING,
                effect_name="test",
                layer_order=1.5
            )
    
    def test_effect_config_validation_animation_parameters(self):
        """Test EffectConfig validation with animation parameters."""
        # Valid animation parameters
        effect = EffectConfig(
            effect_type=EffectType.ANIMATION,
            effect_name="test_animation",
            parameters={
                "animation_type": "karaoke_highlight",
                "duration": 1.0,
                "intensity": 0.5
            }
        )
        effect.validate()  # Should not raise
        
        # Invalid animation type
        with pytest.raises(ConfigurationError, match="Invalid animation type"):
            EffectConfig(
                effect_type=EffectType.ANIMATION,
                effect_name="test_animation",
                parameters={"animation_type": "invalid_type"}
            )
        
        # Invalid duration
        with pytest.raises(ConfigurationError, match="Animation duration must be a positive number"):
            EffectConfig(
                effect_type=EffectType.ANIMATION,
                effect_name="test_animation",
                parameters={"duration": -1.0}
            )
        
        # Invalid intensity
        with pytest.raises(ConfigurationError, match="Animation intensity must be between 0 and 1"):
            EffectConfig(
                effect_type=EffectType.ANIMATION,
                effect_name="test_animation",
                parameters={"intensity": 1.5}
            )
    
    def test_effect_config_validation_particle_parameters(self):
        """Test EffectConfig validation with particle parameters."""
        # Valid particle parameters
        effect = EffectConfig(
            effect_type=EffectType.PARTICLE,
            effect_name="test_particles",
            parameters={
                "particle_type": "hearts",
                "count": 10,
                "size": 20.0,
                "velocity": 5.0
            }
        )
        effect.validate()  # Should not raise
        
        # Invalid particle type
        with pytest.raises(ConfigurationError, match="Invalid particle type"):
            EffectConfig(
                effect_type=EffectType.PARTICLE,
                effect_name="test_particles",
                parameters={"particle_type": "invalid_type"}
            )
        
        # Invalid count
        with pytest.raises(ConfigurationError, match="Particle count must be a non-negative integer"):
            EffectConfig(
                effect_type=EffectType.PARTICLE,
                effect_name="test_particles",
                parameters={"count": -1}
            )
        
        # Invalid size
        with pytest.raises(ConfigurationError, match="Particle size must be a positive number"):
            EffectConfig(
                effect_type=EffectType.PARTICLE,
                effect_name="test_particles",
                parameters={"size": 0}
            )
        
        # Invalid custom image path
        with pytest.raises(ConfigurationError, match="Custom image path must be a string"):
            EffectConfig(
                effect_type=EffectType.PARTICLE,
                effect_name="test_particles",
                parameters={"custom_image_path": 123}
            )
    
    def test_effect_config_serialization(self):
        """Test EffectConfig serialization and deserialization."""
        original = EffectConfig(
            effect_type=EffectType.ANIMATION,
            effect_name="bounce_effect",
            parameters={"duration": 2.0, "intensity": 0.7},
            enabled=False,
            layer_order=3
        )
        
        # Convert to dict
        data = original.to_dict()
        assert data['effect_type'] == "animation"
        assert data['effect_name'] == "bounce_effect"
        assert data['parameters'] == {"duration": 2.0, "intensity": 0.7}
        assert data['enabled'] == False
        assert data['layer_order'] == 3
        
        # Convert back from dict
        restored = EffectConfig.from_dict(data)
        assert restored.effect_type == original.effect_type
        assert restored.effect_name == original.effect_name
        assert restored.parameters == original.parameters
        assert restored.enabled == original.enabled
        assert restored.layer_order == original.layer_order


class TestExportSettings:
    """Test ExportSettings class."""
    
    def test_export_settings_defaults(self):
        """Test ExportSettings default values."""
        settings = ExportSettings()
        
        assert settings.format == "mp4"
        assert settings.codec == "libx264"
        assert settings.resolution == (1920, 1080)
        assert settings.fps == 30
        assert settings.bitrate == "5000k"
        assert settings.audio_codec == "aac"
        assert settings.audio_bitrate == "128k"
        assert settings.output_path == ""
    
    def test_export_settings_validation_valid(self):
        """Test ExportSettings validation with valid data."""
        settings = ExportSettings(
            format="avi",
            codec="libx265",
            resolution=(1280, 720),
            fps=24,
            bitrate="3000k",
            audio_codec="mp3",
            audio_bitrate="192k",
            output_path="/path/to/output.avi"
        )
        # Should not raise any exception
        settings.validate()
    
    def test_export_settings_validation_invalid_format(self):
        """Test ExportSettings validation with invalid format."""
        with pytest.raises(ConfigurationError, match="Format must be one of: mp4, avi, mov"):
            ExportSettings(format="webm")
    
    def test_export_settings_validation_invalid_resolution(self):
        """Test ExportSettings validation with invalid resolution."""
        with pytest.raises(ConfigurationError, match="Resolution must be a tuple of two integers"):
            ExportSettings(resolution=(1920,))
        
        with pytest.raises(ConfigurationError, match="Resolution values must be integers"):
            ExportSettings(resolution=(1920.5, 1080))
        
        with pytest.raises(ConfigurationError, match="Resolution values must be positive"):
            ExportSettings(resolution=(0, 1080))
    
    def test_export_settings_validation_invalid_fps(self):
        """Test ExportSettings validation with invalid FPS."""
        with pytest.raises(ConfigurationError, match="FPS must be a positive integer"):
            ExportSettings(fps=0)
        
        with pytest.raises(ConfigurationError, match="FPS must be a positive integer"):
            ExportSettings(fps=24.5)


class TestProjectConfig:
    """Test ProjectConfig class."""
    
    def test_project_config_defaults(self):
        """Test ProjectConfig default values."""
        project = ProjectConfig()
        
        assert project.background_media_path == ""
        assert project.audio_file_path == ""
        assert project.subtitle_file_path == ""
        assert isinstance(project.global_style, StyleConfig)
        assert project.effects == []
        assert isinstance(project.export_settings, ExportSettings)
        assert project.project_name == "Untitled Project"
        assert project.created_at == ""
        assert project.modified_at == ""
        assert project.version == "1.0"
    
    def test_project_config_validation_valid(self):
        """Test ProjectConfig validation with valid data."""
        project = ProjectConfig(
            background_media_path="/path/to/background.mp4",
            audio_file_path="/path/to/audio.mp3",
            subtitle_file_path="/path/to/subtitles.json",
            project_name="Test Project",
            created_at="2023-01-01T00:00:00Z",
            modified_at="2023-01-01T00:00:00Z",
            version="1.1"
        )
        # Should not raise any exception
        project.validate()
    
    def test_project_config_validation_invalid_paths(self):
        """Test ProjectConfig validation with invalid paths."""
        with pytest.raises(ConfigurationError, match="Background media path must be a string"):
            ProjectConfig(background_media_path=123)
        
        with pytest.raises(ConfigurationError, match="Audio file path must be a string"):
            ProjectConfig(audio_file_path=None)
        
        with pytest.raises(ConfigurationError, match="Subtitle file path must be a string"):
            ProjectConfig(subtitle_file_path=[])
    
    def test_project_config_validation_invalid_metadata(self):
        """Test ProjectConfig validation with invalid metadata."""
        with pytest.raises(ConfigurationError, match="Project name must be a non-empty string"):
            ProjectConfig(project_name="")
        
        with pytest.raises(ConfigurationError, match="Created at must be a string"):
            ProjectConfig(created_at=123)
        
        with pytest.raises(ConfigurationError, match="Version must be a non-empty string"):
            ProjectConfig(version="")
    
    def test_project_config_add_effect(self):
        """Test adding effects to project configuration."""
        project = ProjectConfig()
        
        effect1 = EffectConfig(
            effect_type=EffectType.TEXT_STYLING,
            effect_name="style1",
            layer_order=2
        )
        
        effect2 = EffectConfig(
            effect_type=EffectType.ANIMATION,
            effect_name="anim1",
            layer_order=1
        )
        
        project.add_effect(effect1)
        project.add_effect(effect2)
        
        # Effects should be sorted by layer order
        assert len(project.effects) == 2
        assert project.effects[0].effect_name == "anim1"  # layer_order=1
        assert project.effects[1].effect_name == "style1"  # layer_order=2
    
    def test_project_config_remove_effect(self):
        """Test removing effects from project configuration."""
        project = ProjectConfig()
        
        effect = EffectConfig(
            effect_type=EffectType.TEXT_STYLING,
            effect_name="test_effect"
        )
        
        project.add_effect(effect)
        assert len(project.effects) == 1
        
        project.remove_effect(0)
        assert len(project.effects) == 0
        
        # Test invalid index
        with pytest.raises(IndexError, match="Effect index 0 out of range"):
            project.remove_effect(0)
    
    def test_project_config_get_effects_by_type(self):
        """Test getting effects by type."""
        project = ProjectConfig()
        
        text_effect = EffectConfig(
            effect_type=EffectType.TEXT_STYLING,
            effect_name="text_effect"
        )
        
        anim_effect = EffectConfig(
            effect_type=EffectType.ANIMATION,
            effect_name="anim_effect"
        )
        
        particle_effect = EffectConfig(
            effect_type=EffectType.PARTICLE,
            effect_name="particle_effect"
        )
        
        project.add_effect(text_effect)
        project.add_effect(anim_effect)
        project.add_effect(particle_effect)
        
        text_effects = project.get_effects_by_type(EffectType.TEXT_STYLING)
        assert len(text_effects) == 1
        assert text_effects[0].effect_name == "text_effect"
        
        anim_effects = project.get_effects_by_type(EffectType.ANIMATION)
        assert len(anim_effects) == 1
        assert anim_effects[0].effect_name == "anim_effect"
        
        particle_effects = project.get_effects_by_type(EffectType.PARTICLE)
        assert len(particle_effects) == 1
        assert particle_effects[0].effect_name == "particle_effect"
    
    def test_project_config_serialization(self):
        """Test ProjectConfig serialization and deserialization."""
        # Create a complex project configuration
        style = StyleConfig(font_family="Helvetica", font_size=36)
        
        effect = EffectConfig(
            effect_type=EffectType.ANIMATION,
            effect_name="test_effect",
            parameters={"duration": 1.0}
        )
        
        export_settings = ExportSettings(
            format="avi",
            resolution=(1280, 720)
        )
        
        original = ProjectConfig(
            background_media_path="/path/to/bg.mp4",
            audio_file_path="/path/to/audio.mp3",
            subtitle_file_path="/path/to/subs.json",
            global_style=style,
            export_settings=export_settings,
            project_name="Test Project"
        )
        
        original.add_effect(effect)
        
        # Convert to dict
        data = original.to_dict()
        assert data['background_media_path'] == "/path/to/bg.mp4"
        assert data['global_style']['font_family'] == "Helvetica"
        assert len(data['effects']) == 1
        assert data['effects'][0]['effect_name'] == "test_effect"
        assert data['export_settings']['format'] == "avi"
        
        # Convert back from dict
        restored = ProjectConfig.from_dict(data)
        assert restored.background_media_path == original.background_media_path
        assert restored.global_style.font_family == original.global_style.font_family
        assert len(restored.effects) == 1
        assert restored.effects[0].effect_name == original.effects[0].effect_name
        assert restored.export_settings.format == original.export_settings.format
    
    def test_project_config_file_operations(self):
        """Test saving and loading project configuration from file."""
        # Create a project configuration
        style = StyleConfig(font_family="Times", font_size=24)
        
        effect = EffectConfig(
            effect_type=EffectType.PARTICLE,
            effect_name="hearts",
            parameters={"count": 5}
        )
        
        original = ProjectConfig(
            background_media_path="/test/bg.jpg",
            project_name="File Test Project",
            global_style=style
        )
        
        original.add_effect(effect)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            original.save_to_file(temp_path)
            
            # Load from file
            restored = ProjectConfig.load_from_file(temp_path)
            
            # Verify the loaded configuration
            assert restored.background_media_path == original.background_media_path
            assert restored.project_name == original.project_name
            assert restored.global_style.font_family == original.global_style.font_family
            assert len(restored.effects) == 1
            assert restored.effects[0].effect_name == original.effects[0].effect_name
            assert restored.effects[0].parameters == original.effects[0].parameters
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)