"""
Tests for particle effects system.

This module tests all particle effect classes including base functionality,
specific particle types, and integration with MoviePy timing.
"""

import pytest
import math
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.subtitle_creator.effects.particles import (
    ParticleEffect, HeartParticleEffect, StarParticleEffect,
    MusicNoteParticleEffect, SparkleParticleEffect, CustomImageParticleEffect,
    ParticleConfig
)
from src.subtitle_creator.interfaces import EffectError
from src.subtitle_creator.models import SubtitleLine, SubtitleData


class TestParticleConfig:
    """Test ParticleConfig dataclass."""
    
    def test_particle_config_creation(self):
        """Test creating a ParticleConfig instance."""
        config = ParticleConfig(
            position=(100, 200),
            velocity=(50, -30),
            size=1.5,
            rotation=45,
            rotation_speed=90,
            opacity=0.8,
            lifetime=2.0
        )
        
        assert config.position == (100, 200)
        assert config.velocity == (50, -30)
        assert config.size == 1.5
        assert config.rotation == 45
        assert config.rotation_speed == 90
        assert config.opacity == 0.8
        assert config.lifetime == 2.0
        assert config.color is None
    
    def test_particle_config_with_color(self):
        """Test ParticleConfig with color tint."""
        config = ParticleConfig(
            position=(0, 0),
            velocity=(0, 0),
            size=1.0,
            rotation=0,
            rotation_speed=0,
            opacity=1.0,
            lifetime=1.0,
            color=(255, 128, 64, 200)
        )
        
        assert config.color == (255, 128, 64, 200)


class TestParticleEffect:
    """Test base ParticleEffect class."""
    
    def test_particle_effect_creation(self):
        """Test creating a ParticleEffect instance."""
        effect = ParticleEffect("test_particles", {})
        
        assert effect.name == "test_particles"
        assert effect.get_parameter_value('particle_count') == 20
        assert effect.get_parameter_value('emission_rate') == 10.0
        assert effect.get_parameter_value('particle_lifetime') == 2.0
    
    def test_particle_effect_custom_parameters(self):
        """Test ParticleEffect with custom parameters."""
        params = {
            'particle_count': 50,
            'emission_rate': 25.0,
            'particle_lifetime': 3.0,
            'gravity': 100.0,
            'wind_force': -50.0
        }
        
        effect = ParticleEffect("custom_particles", params)
        
        assert effect.get_parameter_value('particle_count') == 50
        assert effect.get_parameter_value('emission_rate') == 25.0
        assert effect.get_parameter_value('particle_lifetime') == 3.0
        assert effect.get_parameter_value('gravity') == 100.0
        assert effect.get_parameter_value('wind_force') == -50.0
    
    def test_particle_effect_parameter_validation(self):
        """Test parameter validation in ParticleEffect."""
        # Test invalid particle count
        with pytest.raises(EffectError):
            ParticleEffect("test", {'particle_count': 0})
        
        # Test invalid emission rate
        with pytest.raises(EffectError):
            ParticleEffect("test", {'emission_rate': 0.5})
        
        # Test invalid lifetime
        with pytest.raises(EffectError):
            ParticleEffect("test", {'particle_lifetime': 0.1})
    
    def test_generate_particle_config(self):
        """Test particle configuration generation."""
        effect = ParticleEffect("test", {
            'emission_area': (200, 100),
            'velocity_range': (100, 200),
            'size_range': (0.8, 1.2)
        })
        
        config = effect._generate_particle_config()
        
        # Check position is within emission area
        assert -100 <= config.position[0] <= 100
        assert -50 <= config.position[1] <= 50
        
        # Check velocity magnitude is within range
        velocity_magnitude = math.sqrt(config.velocity[0]**2 + config.velocity[1]**2)
        assert 100 <= velocity_magnitude <= 200
        
        # Check size is within range
        assert 0.8 <= config.size <= 1.2
        
        # Check other properties
        assert 0 <= config.rotation <= 360
        assert -180 <= config.rotation_speed <= 180
        assert 0.7 <= config.opacity <= 1.0
        assert config.lifetime == 2.0  # Default value
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False)
    def test_apply_without_moviepy(self):
        """Test apply method when MoviePy is not available."""
        effect = ParticleEffect("test", {})
        
        # Create mock clip and subtitle data
        mock_clip = Mock()
        subtitle_data = SubtitleData(
            lines=[
                SubtitleLine(
                    start_time=0.0,
                    end_time=2.0,
                    text="Test line",
                    words=[]
                )
            ],
            global_style={}
        )
        
        result = effect.apply(mock_clip, subtitle_data)
        assert result == mock_clip  # Should return original clip
    
    def test_apply_with_empty_subtitle_data(self):
        """Test apply method with empty subtitle data."""
        effect = ParticleEffect("test", {})
        mock_clip = Mock()
        
        # Test with None
        result = effect.apply(mock_clip, None)
        assert result == mock_clip
        
        # Test with empty lines
        empty_data = SubtitleData(lines=[], global_style={})
        result = effect.apply(mock_clip, empty_data)
        assert result == mock_clip
    
    def test_get_particle_sprite_not_implemented(self):
        """Test that base class raises NotImplementedError for _get_particle_sprite."""
        effect = ParticleEffect("test", {})
        
        with pytest.raises(NotImplementedError):
            effect._get_particle_sprite()


class TestHeartParticleEffect:
    """Test HeartParticleEffect class."""
    
    def test_heart_particle_creation(self):
        """Test creating a HeartParticleEffect instance."""
        effect = HeartParticleEffect("hearts", {})
        
        assert effect.name == "hearts"
        assert effect.get_parameter_value('heart_color') == (255, 20, 147, 255)
        assert effect.get_parameter_value('heart_size') == 24
        assert effect.get_parameter_value('pulse_enabled') is True
        assert effect.get_parameter_value('pulse_rate') == 1.5
        assert effect.get_parameter_value('float_pattern') == 'rising'
    
    def test_heart_particle_custom_parameters(self):
        """Test HeartParticleEffect with custom parameters."""
        params = {
            'heart_color': (255, 0, 0, 255),
            'heart_size': 32,
            'pulse_enabled': False,
            'pulse_rate': 2.0,
            'float_pattern': 'spiral'
        }
        
        effect = HeartParticleEffect("custom_hearts", params)
        
        assert effect.get_parameter_value('heart_color') == (255, 0, 0, 255)
        assert effect.get_parameter_value('heart_size') == 32
        assert effect.get_parameter_value('pulse_enabled') is False
        assert effect.get_parameter_value('pulse_rate') == 2.0
        assert effect.get_parameter_value('float_pattern') == 'spiral'
    
    def test_heart_parameter_validation(self):
        """Test parameter validation for HeartParticleEffect."""
        # Test invalid heart size
        with pytest.raises(EffectError):
            HeartParticleEffect("test", {'heart_size': 4})  # Below minimum
        
        # Test invalid pulse rate
        with pytest.raises(EffectError):
            HeartParticleEffect("test", {'pulse_rate': 0.1})  # Below minimum
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False)
    def test_get_heart_sprite_without_moviepy(self):
        """Test heart sprite creation without MoviePy."""
        effect = HeartParticleEffect("hearts", {})
        sprite = effect._get_particle_sprite()
        assert sprite is None
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True)
    @patch('src.subtitle_creator.effects.particles.ColorClip')
    def test_get_heart_sprite_with_moviepy(self, mock_color_clip):
        """Test heart sprite creation with MoviePy."""
        mock_clip = Mock()
        mock_color_clip.return_value = mock_clip
        
        effect = HeartParticleEffect("hearts", {
            'heart_color': (255, 100, 150, 255),
            'heart_size': 20
        })
        
        sprite = effect._get_particle_sprite()
        
        mock_color_clip.assert_called_once_with(
            size=(20, 20),
            color=(255, 100, 150),  # RGB only
            duration=1
        )
        assert sprite == mock_clip


class TestStarParticleEffect:
    """Test StarParticleEffect class."""
    
    def test_star_particle_creation(self):
        """Test creating a StarParticleEffect instance."""
        effect = StarParticleEffect("stars", {})
        
        assert effect.name == "stars"
        assert effect.get_parameter_value('star_color') == (255, 255, 0, 255)
        assert effect.get_parameter_value('star_points') == 5
        assert effect.get_parameter_value('twinkle_enabled') is True
        assert effect.get_parameter_value('twinkle_rate') == 2.0
        assert effect.get_parameter_value('trail_enabled') is False
    
    def test_star_particle_custom_parameters(self):
        """Test StarParticleEffect with custom parameters."""
        params = {
            'star_color': (0, 255, 255, 255),
            'star_points': 6,
            'twinkle_enabled': False,
            'twinkle_rate': 5.0,
            'trail_enabled': True
        }
        
        effect = StarParticleEffect("custom_stars", params)
        
        assert effect.get_parameter_value('star_color') == (0, 255, 255, 255)
        assert effect.get_parameter_value('star_points') == 6
        assert effect.get_parameter_value('twinkle_enabled') is False
        assert effect.get_parameter_value('twinkle_rate') == 5.0
        assert effect.get_parameter_value('trail_enabled') is True
    
    def test_star_parameter_validation(self):
        """Test parameter validation for StarParticleEffect."""
        # Test invalid star points
        with pytest.raises(EffectError):
            StarParticleEffect("test", {'star_points': 3})  # Below minimum
        
        # Test invalid twinkle rate
        with pytest.raises(EffectError):
            StarParticleEffect("test", {'twinkle_rate': 0.1})  # Below minimum
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True)
    @patch('src.subtitle_creator.effects.particles.ColorClip')
    def test_get_star_sprite_with_moviepy(self, mock_color_clip):
        """Test star sprite creation with MoviePy."""
        mock_clip = Mock()
        mock_color_clip.return_value = mock_clip
        
        effect = StarParticleEffect("stars", {
            'star_color': (255, 255, 100, 255)
        })
        
        sprite = effect._get_particle_sprite()
        
        mock_color_clip.assert_called_once_with(
            size=(20, 20),
            color=(255, 255, 100),  # RGB only
            duration=1
        )
        assert sprite == mock_clip


class TestMusicNoteParticleEffect:
    """Test MusicNoteParticleEffect class."""
    
    def test_music_note_creation(self):
        """Test creating a MusicNoteParticleEffect instance."""
        effect = MusicNoteParticleEffect("notes", {})
        
        assert effect.name == "notes"
        assert effect.get_parameter_value('note_color') == (138, 43, 226, 255)
        assert effect.get_parameter_value('note_type') == 'eighth'
        assert effect.get_parameter_value('rhythm_sync') is False
        assert effect.get_parameter_value('beat_duration') == 0.5
        assert effect.get_parameter_value('bounce_on_beat') is True
        assert effect.get_parameter_value('staff_lines') is False
    
    def test_music_note_custom_parameters(self):
        """Test MusicNoteParticleEffect with custom parameters."""
        params = {
            'note_color': (100, 50, 200, 255),
            'note_type': 'quarter',
            'rhythm_sync': True,
            'beat_duration': 0.25,
            'bounce_on_beat': False,
            'staff_lines': True
        }
        
        effect = MusicNoteParticleEffect("custom_notes", params)
        
        assert effect.get_parameter_value('note_color') == (100, 50, 200, 255)
        assert effect.get_parameter_value('note_type') == 'quarter'
        assert effect.get_parameter_value('rhythm_sync') is True
        assert effect.get_parameter_value('beat_duration') == 0.25
        assert effect.get_parameter_value('bounce_on_beat') is False
        assert effect.get_parameter_value('staff_lines') is True
    
    def test_rhythm_sync_particle_generation(self):
        """Test rhythm-synchronized particle generation."""
        effect = MusicNoteParticleEffect("notes", {
            'rhythm_sync': True,
            'beat_duration': 0.5,
            'particle_lifetime': 1.0
        })
        
        # Create a subtitle line with 2 seconds duration (4 beats)
        line = Mock()
        line.start_time = 1.0
        line.duration = 2.0
        line.end_time = 3.0
        
        with patch.object(effect, '_generate_particle_config') as mock_config, \
             patch.object(effect, '_create_particle_clip') as mock_create:
            
            mock_config.return_value = Mock()
            mock_create.return_value = Mock()
            
            particles = effect._generate_rhythm_synced_particles(line)
            
            # Should generate 4 particles (2 seconds / 0.5 beat duration)
            assert mock_create.call_count == 4
            
            # Check timing of particle creation
            call_args = mock_create.call_args_list
            expected_times = [1.0, 1.5, 2.0, 2.5]  # Beat times
            
            for i, call in enumerate(call_args):
                args, kwargs = call
                assert args[1] == expected_times[i]  # start_time argument
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True)
    @patch('src.subtitle_creator.effects.particles.ColorClip')
    def test_get_note_sprite_with_moviepy(self, mock_color_clip):
        """Test music note sprite creation with MoviePy."""
        mock_clip = Mock()
        mock_color_clip.return_value = mock_clip
        
        effect = MusicNoteParticleEffect("notes", {
            'note_color': (150, 75, 200, 255)
        })
        
        sprite = effect._get_particle_sprite()
        
        mock_color_clip.assert_called_once_with(
            size=(16, 32),  # Notes are taller
            color=(150, 75, 200),  # RGB only
            duration=1
        )
        assert sprite == mock_clip


class TestSparkleParticleEffect:
    """Test SparkleParticleEffect class."""
    
    def test_sparkle_particle_creation(self):
        """Test creating a SparkleParticleEffect instance."""
        effect = SparkleParticleEffect("sparkles", {})
        
        assert effect.name == "sparkles"
        assert effect.get_parameter_value('sparkle_size_variation') == 0.8
        assert effect.get_parameter_value('flash_duration') == 0.1
        assert effect.get_parameter_value('burst_mode') is False
        assert effect.get_parameter_value('burst_interval') == 1.0
        assert effect.get_parameter_value('radial_spread') is True
    
    def test_sparkle_custom_parameters(self):
        """Test SparkleParticleEffect with custom parameters."""
        params = {
            'sparkle_size_variation': 1.5,
            'flash_duration': 0.2,
            'burst_mode': True,
            'burst_interval': 0.5,
            'radial_spread': False
        }
        
        effect = SparkleParticleEffect("custom_sparkles", params)
        
        assert effect.get_parameter_value('sparkle_size_variation') == 1.5
        assert effect.get_parameter_value('flash_duration') == 0.2
        assert effect.get_parameter_value('burst_mode') is True
        assert effect.get_parameter_value('burst_interval') == 0.5
        assert effect.get_parameter_value('radial_spread') is False
    
    def test_burst_mode_particle_generation(self):
        """Test burst mode particle generation."""
        effect = SparkleParticleEffect("sparkles", {
            'burst_mode': True,
            'burst_interval': 1.0,
            'particle_count': 20,
            'particle_lifetime': 0.5
        })
        
        # Create a subtitle line with 3 seconds duration (3 bursts)
        line = Mock()
        line.start_time = 0.0
        line.duration = 3.0
        line.end_time = 3.0
        
        with patch.object(effect, '_generate_sparkle_config') as mock_config, \
             patch.object(effect, '_create_particle_clip') as mock_create:
            
            mock_config.return_value = Mock()
            mock_create.return_value = Mock()
            
            particles = effect._generate_burst_sparkles(line)
            
            # Should generate particles for 3 bursts
            # Each burst has min(20//3, 10) = 6 particles
            assert mock_create.call_count == 18  # 3 bursts * 6 particles
    
    def test_radial_spread_config(self):
        """Test radial spread particle configuration."""
        effect = SparkleParticleEffect("sparkles", {
            'radial_spread': True
        })
        
        config = effect._generate_sparkle_config()
        
        # Check that position and velocity are radially distributed
        pos_distance = math.sqrt(config.position[0]**2 + config.position[1]**2)
        assert 20 <= pos_distance <= 100  # Within radial distance range
        
        # Velocity should be in same direction as position (away from center)
        pos_angle = math.atan2(config.position[1], config.position[0])
        vel_angle = math.atan2(config.velocity[1], config.velocity[0])
        
        # Angles should be similar (within some tolerance for randomness)
        angle_diff = abs(pos_angle - vel_angle)
        assert angle_diff < 0.5 or angle_diff > (2 * math.pi - 0.5)  # Account for wrap-around


class TestCustomImageParticleEffect:
    """Test CustomImageParticleEffect class."""
    
    def test_custom_image_creation(self):
        """Test creating a CustomImageParticleEffect instance."""
        effect = CustomImageParticleEffect("custom", {})
        
        assert effect.name == "custom"
        assert effect.get_parameter_value('image_path') == ''
        assert effect.get_parameter_value('image_scale') == 1.0
        assert effect.get_parameter_value('color_tint') == (255, 255, 255, 255)
        assert effect.get_parameter_value('preserve_aspect') is True
        assert effect.get_parameter_value('random_flip') is False
        assert effect.get_parameter_value('blend_mode') == 'normal'
    
    def test_custom_image_parameters(self):
        """Test CustomImageParticleEffect with custom parameters."""
        params = {
            'image_path': '/path/to/image.png',
            'image_scale': 2.0,
            'color_tint': (255, 128, 64, 200),
            'preserve_aspect': False,
            'random_flip': True,
            'blend_mode': 'add'
        }
        
        effect = CustomImageParticleEffect("custom", params)
        
        assert effect.get_parameter_value('image_path') == '/path/to/image.png'
        assert effect.get_parameter_value('image_scale') == 2.0
        assert effect.get_parameter_value('color_tint') == (255, 128, 64, 200)
        assert effect.get_parameter_value('preserve_aspect') is False
        assert effect.get_parameter_value('random_flip') is True
        assert effect.get_parameter_value('blend_mode') == 'add'
    
    def test_validate_image_path(self):
        """Test image path validation."""
        effect = CustomImageParticleEffect("custom", {})
        
        # Test empty path
        assert not effect.validate_image_path('')
        
        # Test non-existent file
        assert not effect.validate_image_path('/nonexistent/file.png')
        
        # Test invalid extension
        with patch('pathlib.Path.exists', return_value=True):
            assert not effect.validate_image_path('/path/to/file.txt')
        
        # Test valid extension
        with patch('pathlib.Path.exists', return_value=True):
            assert effect.validate_image_path('/path/to/file.png')
    
    def test_get_supported_formats(self):
        """Test getting supported image formats."""
        effect = CustomImageParticleEffect("custom", {})
        formats = effect.get_supported_formats()
        
        expected_formats = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
        assert formats == expected_formats
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False)
    def test_get_sprite_without_moviepy(self):
        """Test sprite creation without MoviePy."""
        effect = CustomImageParticleEffect("custom", {
            'image_path': '/path/to/image.png'
        })
        
        sprite = effect._get_particle_sprite()
        assert sprite is None
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True)
    @patch('pathlib.Path.exists', return_value=False)
    @patch('src.subtitle_creator.effects.particles.ColorClip')
    def test_get_sprite_fallback_to_default(self, mock_color_clip, mock_exists):
        """Test fallback to default particle when image loading fails."""
        mock_clip = Mock()
        mock_color_clip.return_value = mock_clip
        
        effect = CustomImageParticleEffect("custom", {
            'image_path': '/nonexistent/image.png'
        })
        
        sprite = effect._get_particle_sprite()
        
        # Should create default particle
        mock_color_clip.assert_called_once_with(
            size=(16, 16),
            color=(255, 255, 255),
            duration=1
        )
        assert sprite == mock_clip
    
    @patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True)
    @patch('pathlib.Path.exists', return_value=True)
    @patch('src.subtitle_creator.effects.particles.ImageClip')
    def test_get_sprite_with_custom_image(self, mock_image_clip, mock_exists):
        """Test sprite creation with custom image."""
        mock_clip = Mock()
        mock_image_clip.return_value = mock_clip
        
        effect = CustomImageParticleEffect("custom", {
            'image_path': '/path/to/image.png',
            'image_scale': 1.5
        })
        
        sprite = effect._get_particle_sprite()
        
        mock_image_clip.assert_called_once_with('/path/to/image.png')
        mock_clip.resized.assert_called_once_with(1.5)
        # sprite should be the resized clip
        assert sprite == mock_clip.resized.return_value


class TestParticleEffectsIntegration:
    """Test integration between particle effects and subtitle system."""
    
    def test_particle_timing_integration(self):
        """Test particle timing integration with subtitle lines."""
        effect = HeartParticleEffect("hearts", {
            'particle_count': 10,
            'emission_rate': 5.0,
            'particle_lifetime': 2.0
        })
        
        # Create subtitle data with multiple lines
        subtitle_data = SubtitleData(
            lines=[
                SubtitleLine(
                    start_time=0.0,
                    end_time=2.0,
                    text="First line",
                    words=[]
                ),
                SubtitleLine(
                    start_time=2.5,
                    end_time=4.5,
                    text="Second line",
                    words=[]
                )
            ],
            global_style={}
        )
        
        mock_clip = Mock()
        
        with patch.object(effect, '_generate_particles_for_line') as mock_generate:
            mock_generate.return_value = [Mock(), Mock()]  # Return 2 particles per line
            
            result = effect.apply(mock_clip, subtitle_data)
            
            # Should generate particles for both lines
            assert mock_generate.call_count == 2
            
            # Check that lines were passed correctly
            call_args = mock_generate.call_args_list
            assert call_args[0][0][0].text == "First line"
            assert call_args[1][0][0].text == "Second line"
    
    def test_particle_physics_simulation(self):
        """Test particle physics simulation with gravity and wind."""
        effect = ParticleEffect("physics_test", {
            'gravity': 100.0,
            'wind_force': 50.0
        })
        
        config = ParticleConfig(
            position=(0, 0),
            velocity=(10, -20),
            size=1.0,
            rotation=0,
            rotation_speed=0,
            opacity=1.0,
            lifetime=2.0
        )
        
        # Mock clip for testing
        mock_clip = Mock()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True):
            result_clip = effect._apply_particle_animation(mock_clip, config, 2.0)
            
            # Verify that with_position was called (physics animation applied)
            mock_clip.with_position.assert_called_once()
    
    def test_multiple_particle_effects_composition(self):
        """Test compositing multiple particle effects together."""
        from src.subtitle_creator.effects.system import EffectSystem
        
        # Create effect system and register particle effects
        system = EffectSystem()
        system.register_effect(HeartParticleEffect)
        system.register_effect(StarParticleEffect)
        
        # Create effects
        hearts = system.create_effect("HeartParticleEffect", {'particle_count': 5})
        stars = system.create_effect("StarParticleEffect", {'particle_count': 8})
        
        system.add_effect(hearts)
        system.add_effect(stars)
        
        # Create test data
        mock_clip = Mock()
        subtitle_data = SubtitleData(
            lines=[
                SubtitleLine(
                    start_time=0.0,
                    end_time=3.0,
                    text="Test line",
                    words=[]
                )
            ],
            global_style={}
        )
        
        # Apply effects
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False):
            result = system.apply_effects(mock_clip, subtitle_data)
            
            # Should return the base clip when MoviePy is not available
            assert result == mock_clip