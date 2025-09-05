"""
Integration tests for text styling effects with the effects system.

This module tests the complete integration of text styling effects
with the effects system, including registration, application, and presets.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from src.subtitle_creator.effects.system import EffectSystem
from src.subtitle_creator.effects.text_styling import (
    TypographyEffect, PositioningEffect, BackgroundEffect, TransitionEffect
)
from src.subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming


class TestTextStylingIntegration:
    """Integration tests for text styling effects."""
    
    def test_register_all_text_styling_effects(self):
        """Test registering all text styling effects."""
        system = EffectSystem()
        
        # Register all text styling effects
        system.register_effect(TypographyEffect)
        system.register_effect(PositioningEffect)
        system.register_effect(BackgroundEffect)
        system.register_effect(TransitionEffect)
        
        registered = system.get_registered_effects()
        
        assert 'TypographyEffect' in registered
        assert 'PositioningEffect' in registered
        assert 'BackgroundEffect' in registered
        assert 'TransitionEffect' in registered
        assert len(registered) == 4
    
    def test_create_and_apply_typography_effect(self):
        """Test creating and applying typography effect."""
        system = EffectSystem()
        system.register_effect(TypographyEffect)
        
        # Create typography effect with custom parameters
        typography = system.create_effect('TypographyEffect', {
            'font_family': 'Helvetica',
            'font_size': 72,
            'font_weight': 'bold',
            'text_color': (255, 0, 0, 255),
            'outline_enabled': True,
            'outline_width': 3
        })
        
        system.add_effect(typography)
        
        # Create test data
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        mock_clip.duration = 10.0
        
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(0.0, 2.0, "Hello World"),
            SubtitleLine(3.0, 5.0, "Second Line")
        ]
        
        # Apply effects
        result = system.apply_effects(mock_clip, subtitle_data)
        
        # Should return the original clip in test environment
        assert result == mock_clip
        
        # Verify effect parameters
        assert typography.get_parameter_value('font_family') == 'Helvetica'
        assert typography.get_parameter_value('font_size') == 72
        assert typography.get_parameter_value('font_weight') == 'bold'
        assert typography.get_parameter_value('text_color') == (255, 0, 0, 255)
    
    def test_create_and_apply_positioning_effect(self):
        """Test creating and applying positioning effect."""
        system = EffectSystem()
        system.register_effect(PositioningEffect)
        
        # Create positioning effect
        positioning = system.create_effect('PositioningEffect', {
            'horizontal_alignment': 'left',
            'vertical_alignment': 'top',
            'x_offset': 50,
            'y_offset': 100,
            'margin_horizontal': 30,
            'margin_vertical': 40
        })
        
        system.add_effect(positioning)
        
        # Test position calculation
        pos = positioning._calculate_position('left', 'top', 50, 100, 30, 40, (1920, 1080))
        assert pos == (80, 140)  # margin + offset
        
        # Apply to mock clip
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        
        subtitle_data = SubtitleData()
        subtitle_data.lines = [SubtitleLine(0.0, 2.0, "Test")]
        
        result = system.apply_effects(mock_clip, subtitle_data)
        assert result == mock_clip
    
    def test_create_and_apply_background_effect(self):
        """Test creating and applying background effect."""
        system = EffectSystem()
        system.register_effect(BackgroundEffect)
        
        # Create background effect with both background and shadow enabled
        background = system.create_effect('BackgroundEffect', {
            'background_enabled': True,
            'background_color': (0, 0, 0, 180),
            'background_padding': 15,
            'background_border_radius': 8,
            'shadow_enabled': True,
            'shadow_color': (0, 0, 0, 100),
            'shadow_offset_x': 3,
            'shadow_offset_y': 3,
            'shadow_blur': 5
        })
        
        system.add_effect(background)
        
        # Apply to mock clip
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        
        subtitle_data = SubtitleData()
        subtitle_data.lines = [SubtitleLine(0.0, 2.0, "Test")]
        
        result = system.apply_effects(mock_clip, subtitle_data)
        assert result == mock_clip
        
        # Verify parameters
        assert background.get_parameter_value('background_enabled') == True
        assert background.get_parameter_value('shadow_enabled') == True
    
    def test_create_and_apply_transition_effect(self):
        """Test creating and applying transition effect."""
        system = EffectSystem()
        system.register_effect(TransitionEffect)
        
        # Create transition effect
        transition = system.create_effect('TransitionEffect', {
            'transition_type': 'fade_in',
            'transition_duration': 1.0,
            'easing_function': 'ease_out_bounce',
            'start_value': 0.0,
            'end_value': 1.0
        })
        
        system.add_effect(transition)
        
        # Test easing function retrieval
        easing_func = transition._get_easing_function('ease_out_bounce')
        assert callable(easing_func)
        
        # Apply to mock clip
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        
        subtitle_data = SubtitleData()
        subtitle_data.lines = [SubtitleLine(0.0, 2.0, "Test")]
        
        result = system.apply_effects(mock_clip, subtitle_data)
        assert result == mock_clip
    
    def test_combine_multiple_text_styling_effects(self):
        """Test combining multiple text styling effects."""
        system = EffectSystem()
        
        # Register all effects
        system.register_effect(TypographyEffect)
        system.register_effect(PositioningEffect)
        system.register_effect(BackgroundEffect)
        system.register_effect(TransitionEffect)
        
        # Create multiple effects
        typography = system.create_effect('TypographyEffect', {
            'font_size': 60,
            'text_color': (255, 255, 0, 255)
        })
        
        positioning = system.create_effect('PositioningEffect', {
            'horizontal_alignment': 'center',
            'vertical_alignment': 'middle'
        })
        
        background = system.create_effect('BackgroundEffect', {
            'background_enabled': True,
            'background_color': (0, 0, 0, 128)
        })
        
        transition = system.create_effect('TransitionEffect', {
            'transition_type': 'fade_in',
            'transition_duration': 0.8
        })
        
        # Add all effects
        system.add_effect(typography)
        system.add_effect(positioning)
        system.add_effect(background)
        system.add_effect(transition)
        
        assert len(system.get_active_effects()) == 4
        
        # Apply all effects
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        
        subtitle_data = SubtitleData()
        subtitle_data.lines = [
            SubtitleLine(0.0, 2.0, "Hello World"),
            SubtitleLine(3.0, 5.0, "Styled Text")
        ]
        
        result = system.apply_effects(mock_clip, subtitle_data)
        assert result == mock_clip
    
    def test_text_styling_effects_preset_management(self):
        """Test saving and loading presets with text styling effects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = EffectSystem(Path(temp_dir))
            
            # Register effects
            system.register_effect(TypographyEffect)
            system.register_effect(PositioningEffect)
            system.register_effect(BackgroundEffect)
            
            # Create a styled text preset
            typography = system.create_effect('TypographyEffect', {
                'font_family': 'Arial',
                'font_size': 48,
                'font_weight': 'bold',
                'text_color': (255, 255, 255, 255),
                'outline_enabled': True,
                'outline_color': (0, 0, 0, 255),
                'outline_width': 2
            })
            
            positioning = system.create_effect('PositioningEffect', {
                'horizontal_alignment': 'center',
                'vertical_alignment': 'bottom',
                'y_offset': -80
            })
            
            background = system.create_effect('BackgroundEffect', {
                'background_enabled': True,
                'background_color': (0, 0, 0, 150),
                'background_padding': 12
            })
            
            system.add_effect(typography)
            system.add_effect(positioning)
            system.add_effect(background)
            
            # Save preset
            system.save_preset('styled_subtitles', 'White text with black outline and background')
            
            # Verify preset was saved
            presets = system.list_presets()
            assert 'styled_subtitles' in presets
            
            # Get preset info
            info = system.get_preset_info('styled_subtitles')
            assert info['name'] == 'styled_subtitles'
            assert info['description'] == 'White text with black outline and background'
            assert info['effect_count'] == 3
            assert 'TypographyEffect' in info['effects']
            assert 'PositioningEffect' in info['effects']
            assert 'BackgroundEffect' in info['effects']
            
            # Clear effects and reload preset
            system.clear_effects()
            assert len(system.get_active_effects()) == 0
            
            system.load_preset('styled_subtitles')
            
            # Verify effects were loaded
            active_effects = system.get_active_effects()
            assert len(active_effects) == 3
            
            # Find and verify typography effect
            typography_effect = None
            for effect in active_effects:
                if isinstance(effect, TypographyEffect):
                    typography_effect = effect
                    break
            
            assert typography_effect is not None
            assert typography_effect.get_parameter_value('font_family') == 'Arial'
            assert typography_effect.get_parameter_value('font_size') == 48
            assert typography_effect.get_parameter_value('font_weight') == 'bold'
    
    def test_text_styling_effects_with_word_timing(self):
        """Test text styling effects with word-level timing data."""
        system = EffectSystem()
        system.register_effect(TypographyEffect)
        system.register_effect(TransitionEffect)
        
        # Create effects
        typography = system.create_effect('TypographyEffect', {
            'font_size': 54,
            'text_color': (0, 255, 0, 255)
        })
        
        transition = system.create_effect('TransitionEffect', {
            'transition_type': 'fade_in',
            'transition_duration': 0.3
        })
        
        system.add_effect(typography)
        system.add_effect(transition)
        
        # Create subtitle data with word-level timing
        subtitle_data = SubtitleData()
        words = [
            WordTiming("Hello", 0.0, 0.5),
            WordTiming("beautiful", 0.5, 1.2),
            WordTiming("world", 1.2, 2.0)
        ]
        subtitle_data.lines = [
            SubtitleLine(0.0, 2.0, "Hello beautiful world", words)
        ]
        
        # Apply effects
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        
        result = system.apply_effects(mock_clip, subtitle_data)
        assert result == mock_clip
        
        # Verify word timing data is preserved
        assert len(subtitle_data.lines[0].words) == 3
        assert subtitle_data.lines[0].words[0].word == "Hello"
        assert subtitle_data.lines[0].words[1].word == "beautiful"
        assert subtitle_data.lines[0].words[2].word == "world"
    
    def test_text_styling_effects_parameter_updates(self):
        """Test updating parameters of text styling effects."""
        system = EffectSystem()
        system.register_effect(TypographyEffect)
        
        # Create effect with initial parameters
        typography = system.create_effect('TypographyEffect', {
            'font_size': 48,
            'text_color': (255, 255, 255, 255)
        })
        
        system.add_effect(typography)
        
        # Verify initial parameters
        assert typography.get_parameter_value('font_size') == 48
        assert typography.get_parameter_value('text_color') == (255, 255, 255, 255)
        
        # Update parameters
        typography.set_parameter_value('font_size', 64)
        typography.set_parameter_value('text_color', (255, 0, 0, 255))
        
        # Verify updated parameters
        assert typography.get_parameter_value('font_size') == 64
        assert typography.get_parameter_value('text_color') == (255, 0, 0, 255)
        
        # Test invalid parameter update
        with pytest.raises(Exception):  # Should raise EffectError
            typography.set_parameter_value('font_size', -10)
    
    def test_text_styling_effects_serialization(self):
        """Test serialization and deserialization of text styling effects."""
        system = EffectSystem()
        system.register_effect(TypographyEffect)
        system.register_effect(BackgroundEffect)
        
        # Create effects
        typography = system.create_effect('TypographyEffect', {
            'font_family': 'Times New Roman',
            'font_size': 56,
            'font_weight': 'bold',
            'text_color': (0, 0, 255, 255)
        })
        
        background = system.create_effect('BackgroundEffect', {
            'background_enabled': True,
            'background_color': (255, 255, 255, 200),
            'shadow_enabled': True
        })
        
        # Test serialization
        typography_dict = typography.to_dict()
        background_dict = background.to_dict()
        
        assert typography_dict['class'] == 'TypographyEffect'
        assert typography_dict['parameters']['font_family'] == 'Times New Roman'
        assert typography_dict['parameters']['font_size'] == 56
        
        assert background_dict['class'] == 'BackgroundEffect'
        assert background_dict['parameters']['background_enabled'] == True
        assert background_dict['parameters']['shadow_enabled'] == True
        
        # Test deserialization
        recreated_typography = TypographyEffect.from_dict(typography_dict)
        recreated_background = BackgroundEffect.from_dict(background_dict)
        
        assert recreated_typography.get_parameter_value('font_family') == 'Times New Roman'
        assert recreated_typography.get_parameter_value('font_size') == 56
        assert recreated_typography.get_parameter_value('font_weight') == 'bold'
        
        assert recreated_background.get_parameter_value('background_enabled') == True
        assert recreated_background.get_parameter_value('shadow_enabled') == True