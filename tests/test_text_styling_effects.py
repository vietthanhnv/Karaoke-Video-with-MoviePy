"""
Tests for text styling effects implementation.

This module tests the concrete text styling effects including typography,
positioning, backgrounds, and transitions.
"""

import pytest
from unittest.mock import Mock, patch
from src.subtitle_creator.effects.text_styling import (
    TypographyEffect, PositioningEffect, BackgroundEffect, TransitionEffect
)
from src.subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming
from src.subtitle_creator.interfaces import EffectError


class TestTypographyEffect:
    """Test cases for TypographyEffect class."""
    
    def test_typography_effect_initialization(self):
        """Test TypographyEffect initialization with default parameters."""
        effect = TypographyEffect("Typography Test", {})
        
        assert effect.name == "Typography Test"
        assert effect.get_parameter_value('font_family') == 'Arial'
        assert effect.get_parameter_value('font_size') == 48
        assert effect.get_parameter_value('font_weight') == 'normal'
        assert effect.get_parameter_value('text_color') == (255, 255, 255, 255)
        assert effect.get_parameter_value('outline_enabled') == True
        assert effect.get_parameter_value('outline_color') == (0, 0, 0, 255)
        assert effect.get_parameter_value('outline_width') == 2
    
    def test_typography_effect_custom_parameters(self):
        """Test TypographyEffect with custom parameters."""
        params = {
            'font_family': 'Times New Roman',
            'font_size': 64,
            'font_weight': 'bold',
            'text_color': (255, 0, 0, 255),
            'outline_enabled': False,
            'outline_width': 0
        }
        
        effect = TypographyEffect("Custom Typography", params)
        
        assert effect.get_parameter_value('font_family') == 'Times New Roman'
        assert effect.get_parameter_value('font_size') == 64
        assert effect.get_parameter_value('font_weight') == 'bold'
        assert effect.get_parameter_value('text_color') == (255, 0, 0, 255)
        assert effect.get_parameter_value('outline_enabled') == False
        assert effect.get_parameter_value('outline_width') == 0
    
    def test_typography_effect_parameter_validation(self):
        """Test parameter validation for TypographyEffect."""
        # Test invalid font size
        with pytest.raises(EffectError):
            TypographyEffect("Invalid Size", {'font_size': -10})
        
        # Test invalid color format
        with pytest.raises(EffectError):
            TypographyEffect("Invalid Color", {'text_color': (300, 0, 0, 255)})
        
        # Test invalid font weight
        with pytest.raises(EffectError):
            TypographyEffect("Invalid Weight", {'font_weight': 'invalid'})
    
    def test_typography_effect_apply_empty_subtitles(self):
        """Test applying typography effect with empty subtitle data."""
        effect = TypographyEffect("Empty Test", {})
        mock_clip = Mock()
        empty_subtitles = SubtitleData()
        
        result = effect.apply(mock_clip, empty_subtitles)
        assert result == mock_clip
    
    def test_typography_effect_apply_with_subtitles(self):
        """Test applying typography effect with subtitle data."""
        effect = TypographyEffect("Subtitle Test", {})
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        
        # Create test subtitle data
        subtitles = SubtitleData()
        subtitles.lines = [
            SubtitleLine(0.0, 2.0, "Hello World"),
            SubtitleLine(2.5, 4.5, "Second Line")
        ]
        
        result = effect.apply(mock_clip, subtitles)
        
        # Should return the original clip in test environment (no MoviePy)
        assert result == mock_clip
    
    def test_typography_effect_parameter_schema(self):
        """Test parameter schema generation."""
        effect = TypographyEffect("Schema Test", {})
        schema = effect.get_parameter_schema()
        
        assert 'font_family' in schema
        assert 'font_size' in schema
        assert 'font_weight' in schema
        assert 'text_color' in schema
        assert 'outline_enabled' in schema
        assert 'outline_color' in schema
        assert 'outline_width' in schema
        
        # Check parameter types
        assert schema['font_family']['type'] == 'str'
        assert schema['font_size']['type'] == 'int'
        assert schema['text_color']['type'] == 'color'
        assert schema['outline_enabled']['type'] == 'bool'


class TestPositioningEffect:
    """Test cases for PositioningEffect class."""
    
    def test_positioning_effect_initialization(self):
        """Test PositioningEffect initialization with default parameters."""
        effect = PositioningEffect("Position Test", {})
        
        assert effect.name == "Position Test"
        assert effect.get_parameter_value('horizontal_alignment') == 'center'
        assert effect.get_parameter_value('vertical_alignment') == 'bottom'
        assert effect.get_parameter_value('x_offset') == 0
        assert effect.get_parameter_value('y_offset') == -50
        assert effect.get_parameter_value('margin_horizontal') == 20
        assert effect.get_parameter_value('margin_vertical') == 20
    
    def test_positioning_effect_custom_parameters(self):
        """Test PositioningEffect with custom parameters."""
        params = {
            'horizontal_alignment': 'left',
            'vertical_alignment': 'top',
            'x_offset': 100,
            'y_offset': 50,
            'margin_horizontal': 30,
            'margin_vertical': 40
        }
        
        effect = PositioningEffect("Custom Position", params)
        
        assert effect.get_parameter_value('horizontal_alignment') == 'left'
        assert effect.get_parameter_value('vertical_alignment') == 'top'
        assert effect.get_parameter_value('x_offset') == 100
        assert effect.get_parameter_value('y_offset') == 50
        assert effect.get_parameter_value('margin_horizontal') == 30
        assert effect.get_parameter_value('margin_vertical') == 40
    
    def test_positioning_effect_calculate_position(self):
        """Test position calculation logic."""
        effect = PositioningEffect("Calc Test", {})
        
        # Test center-bottom positioning
        pos = effect._calculate_position('center', 'bottom', 0, -50, 20, 20, (1920, 1080))
        assert pos == (960, 1010)  # center x, bottom y with offset
        
        # Test left-top positioning
        pos = effect._calculate_position('left', 'top', 10, 10, 20, 20, (1920, 1080))
        assert pos == (30, 30)  # left margin + offset, top margin + offset
        
        # Test right-middle positioning
        pos = effect._calculate_position('right', 'middle', -10, 0, 20, 20, (1920, 1080))
        assert pos == (1890, 540)  # right margin + offset, middle y
    
    def test_positioning_effect_apply_empty_subtitles(self):
        """Test applying positioning effect with empty subtitle data."""
        effect = PositioningEffect("Empty Test", {})
        mock_clip = Mock()
        empty_subtitles = SubtitleData()
        
        result = effect.apply(mock_clip, empty_subtitles)
        assert result == mock_clip
    
    def test_positioning_effect_apply_with_composite_clip(self):
        """Test applying positioning effect with composite clip."""
        effect = PositioningEffect("Composite Test", {})
        
        # Mock composite clip with multiple clips
        mock_base_clip = Mock()
        mock_text_clip1 = Mock()
        mock_text_clip2 = Mock()
        
        mock_composite_clip = Mock()
        mock_composite_clip.clips = [mock_base_clip, mock_text_clip1, mock_text_clip2]
        mock_composite_clip.size = (1920, 1080)
        
        subtitles = SubtitleData()
        subtitles.lines = [
            SubtitleLine(0.0, 2.0, "Hello World"),
            SubtitleLine(2.5, 4.5, "Second Line")
        ]
        
        result = effect.apply(mock_composite_clip, subtitles)
        
        # Should return the original clip in test environment
        assert result == mock_composite_clip


class TestBackgroundEffect:
    """Test cases for BackgroundEffect class."""
    
    def test_background_effect_initialization(self):
        """Test BackgroundEffect initialization with default parameters."""
        effect = BackgroundEffect("Background Test", {})
        
        assert effect.name == "Background Test"
        assert effect.get_parameter_value('background_enabled') == False
        assert effect.get_parameter_value('background_color') == (0, 0, 0, 128)
        assert effect.get_parameter_value('background_padding') == 10
        assert effect.get_parameter_value('background_border_radius') == 5
        assert effect.get_parameter_value('shadow_enabled') == False
        assert effect.get_parameter_value('shadow_color') == (0, 0, 0, 128)
        assert effect.get_parameter_value('shadow_offset_x') == 2
        assert effect.get_parameter_value('shadow_offset_y') == 2
        assert effect.get_parameter_value('shadow_blur') == 3
    
    def test_background_effect_custom_parameters(self):
        """Test BackgroundEffect with custom parameters."""
        params = {
            'background_enabled': True,
            'background_color': (255, 255, 255, 200),
            'background_padding': 15,
            'background_border_radius': 10,
            'shadow_enabled': True,
            'shadow_color': (0, 0, 255, 100),
            'shadow_offset_x': 5,
            'shadow_offset_y': 5,
            'shadow_blur': 8
        }
        
        effect = BackgroundEffect("Custom Background", params)
        
        assert effect.get_parameter_value('background_enabled') == True
        assert effect.get_parameter_value('background_color') == (255, 255, 255, 200)
        assert effect.get_parameter_value('background_padding') == 15
        assert effect.get_parameter_value('background_border_radius') == 10
        assert effect.get_parameter_value('shadow_enabled') == True
        assert effect.get_parameter_value('shadow_color') == (0, 0, 255, 100)
        assert effect.get_parameter_value('shadow_offset_x') == 5
        assert effect.get_parameter_value('shadow_offset_y') == 5
        assert effect.get_parameter_value('shadow_blur') == 8
    
    def test_background_effect_apply_disabled(self):
        """Test applying background effect when both background and shadow are disabled."""
        effect = BackgroundEffect("Disabled Test", {
            'background_enabled': False,
            'shadow_enabled': False
        })
        
        mock_clip = Mock()
        subtitles = SubtitleData()
        subtitles.lines = [SubtitleLine(0.0, 2.0, "Test")]
        
        result = effect.apply(mock_clip, subtitles)
        assert result == mock_clip
    
    def test_background_effect_apply_empty_subtitles(self):
        """Test applying background effect with empty subtitle data."""
        effect = BackgroundEffect("Empty Test", {'background_enabled': True})
        mock_clip = Mock()
        empty_subtitles = SubtitleData()
        
        result = effect.apply(mock_clip, empty_subtitles)
        assert result == mock_clip
    
    def test_background_effect_parameter_validation(self):
        """Test parameter validation for BackgroundEffect."""
        # Test invalid padding
        with pytest.raises(EffectError):
            BackgroundEffect("Invalid Padding", {'background_padding': -5})
        
        # Test invalid color format
        with pytest.raises(EffectError):
            BackgroundEffect("Invalid Color", {'background_color': (300, 0, 0, 255)})
        
        # Test invalid shadow offset
        with pytest.raises(EffectError):
            BackgroundEffect("Invalid Offset", {'shadow_offset_x': 25})


class TestTransitionEffect:
    """Test cases for TransitionEffect class."""
    
    def test_transition_effect_initialization(self):
        """Test TransitionEffect initialization with default parameters."""
        effect = TransitionEffect("Transition Test", {})
        
        assert effect.name == "Transition Test"
        assert effect.get_parameter_value('transition_type') == 'fade_in'
        assert effect.get_parameter_value('transition_duration') == 0.5
        assert effect.get_parameter_value('easing_function') == 'ease_in_out'
        assert effect.get_parameter_value('start_value') == 0.0
        assert effect.get_parameter_value('end_value') == 1.0
    
    def test_transition_effect_custom_parameters(self):
        """Test TransitionEffect with custom parameters."""
        params = {
            'transition_type': 'fade_out',
            'transition_duration': 1.0,
            'easing_function': 'ease_out_bounce',
            'start_value': 0.2,
            'end_value': 0.8
        }
        
        effect = TransitionEffect("Custom Transition", params)
        
        assert effect.get_parameter_value('transition_type') == 'fade_out'
        assert effect.get_parameter_value('transition_duration') == 1.0
        assert effect.get_parameter_value('easing_function') == 'ease_out_bounce'
        assert effect.get_parameter_value('start_value') == 0.2
        assert effect.get_parameter_value('end_value') == 0.8
    
    def test_transition_effect_get_easing_function(self):
        """Test easing function retrieval."""
        effect = TransitionEffect("Easing Test", {})
        
        # Test linear easing
        linear_func = effect._get_easing_function('linear')
        assert linear_func(0.5) == 0.5
        
        # Test ease_in_out easing
        ease_func = effect._get_easing_function('ease_in_out')
        assert callable(ease_func)
        
        # Test unknown easing (should default to linear)
        unknown_func = effect._get_easing_function('unknown')
        assert unknown_func(0.5) == 0.5
    
    def test_transition_effect_apply_empty_subtitles(self):
        """Test applying transition effect with empty subtitle data."""
        effect = TransitionEffect("Empty Test", {})
        mock_clip = Mock()
        empty_subtitles = SubtitleData()
        
        result = effect.apply(mock_clip, empty_subtitles)
        assert result == mock_clip
    
    def test_transition_effect_apply_with_subtitles(self):
        """Test applying transition effect with subtitle data."""
        effect = TransitionEffect("Subtitle Test", {})
        
        # Mock composite clip
        mock_base_clip = Mock()
        mock_text_clip = Mock()
        mock_composite_clip = Mock()
        mock_composite_clip.clips = [mock_base_clip, mock_text_clip]
        
        subtitles = SubtitleData()
        subtitles.lines = [SubtitleLine(0.0, 2.0, "Test")]
        
        result = effect.apply(mock_composite_clip, subtitles)
        
        # Should return the original clip in test environment
        assert result == mock_composite_clip
    
    def test_transition_effect_parameter_validation(self):
        """Test parameter validation for TransitionEffect."""
        # Test invalid duration
        with pytest.raises(EffectError):
            TransitionEffect("Invalid Duration", {'transition_duration': 0.05})
        
        # Test invalid start value
        with pytest.raises(EffectError):
            TransitionEffect("Invalid Start", {'start_value': -0.5})
        
        # Test invalid end value
        with pytest.raises(EffectError):
            TransitionEffect("Invalid End", {'end_value': 1.5})


class TestTextStylingEffectsIntegration:
    """Integration tests for text styling effects."""
    
    def test_effects_can_be_combined(self):
        """Test that multiple text styling effects can be created and configured."""
        typography = TypographyEffect("Typography", {
            'font_size': 60,
            'text_color': (255, 0, 0, 255)
        })
        
        positioning = PositioningEffect("Positioning", {
            'horizontal_alignment': 'left',
            'x_offset': 50
        })
        
        background = BackgroundEffect("Background", {
            'background_enabled': True,
            'background_color': (0, 0, 0, 128)
        })
        
        transition = TransitionEffect("Transition", {
            'transition_type': 'fade_in',
            'transition_duration': 1.0
        })
        
        # All effects should be properly initialized
        assert typography.get_parameter_value('font_size') == 60
        assert positioning.get_parameter_value('horizontal_alignment') == 'left'
        assert background.get_parameter_value('background_enabled') == True
        assert transition.get_parameter_value('transition_type') == 'fade_in'
    
    def test_effects_serialization(self):
        """Test that text styling effects can be serialized and deserialized."""
        typography = TypographyEffect("Typography", {
            'font_family': 'Helvetica',
            'font_size': 72,
            'text_color': (0, 255, 0, 255)
        })
        
        # Test serialization
        effect_dict = typography.to_dict()
        assert effect_dict['name'] == 'Typography'
        assert effect_dict['class'] == 'TypographyEffect'
        assert effect_dict['parameters']['font_family'] == 'Helvetica'
        assert effect_dict['parameters']['font_size'] == 72
        assert effect_dict['parameters']['text_color'] == (0, 255, 0, 255)
        
        # Test deserialization
        recreated_effect = TypographyEffect.from_dict(effect_dict)
        assert recreated_effect.name == 'Typography'
        assert recreated_effect.get_parameter_value('font_family') == 'Helvetica'
        assert recreated_effect.get_parameter_value('font_size') == 72
        assert recreated_effect.get_parameter_value('text_color') == (0, 255, 0, 255)
    
    def test_effects_with_word_level_timing(self):
        """Test text styling effects with word-level timing data."""
        effect = TypographyEffect("Word Timing Test", {})
        
        # Create subtitle data with word-level timing
        subtitles = SubtitleData()
        words = [
            WordTiming("Hello", 0.0, 0.5),
            WordTiming("World", 0.5, 1.0)
        ]
        subtitles.lines = [SubtitleLine(0.0, 1.0, "Hello World", words)]
        
        mock_clip = Mock()
        mock_clip.size = (1920, 1080)
        
        # Should not raise any errors
        result = effect.apply(mock_clip, subtitles)
        assert result is not None