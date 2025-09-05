"""
Unit tests for the base effect framework.

Tests the BaseEffect class, EffectParameter validation, and core effect functionality
including parameter management, validation, and serialization.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.subtitle_creator.effects.base import (
    BaseEffect, EffectParameter, ease_in_out_cubic, ease_out_bounce, ease_in_out_sine
)
from src.subtitle_creator.interfaces import EffectError, SubtitleData, SubtitleLine, WordTiming


class TestEffectParameter:
    """Test cases for EffectParameter validation."""
    
    def test_float_parameter_validation(self):
        """Test float parameter validation with min/max constraints."""
        param = EffectParameter(
            name="opacity",
            value=0.5,
            param_type="float",
            min_value=0.0,
            max_value=1.0
        )
        assert param.validate() is True
        
        # Test invalid type
        param.value = "invalid"
        assert param.validate() is False
        
        # Test out of range
        param.value = 1.5
        assert param.validate() is False
        
        param.value = -0.1
        assert param.validate() is False
    
    def test_int_parameter_validation(self):
        """Test integer parameter validation."""
        param = EffectParameter(
            name="font_size",
            value=24,
            param_type="int",
            min_value=8,
            max_value=72
        )
        assert param.validate() is True
        
        # Test invalid type
        param.value = 24.5
        assert param.validate() is False
        
        # Test out of range
        param.value = 100
        assert param.validate() is False
    
    def test_string_parameter_validation(self):
        """Test string parameter validation."""
        param = EffectParameter(
            name="font_family",
            value="Arial",
            param_type="str"
        )
        assert param.validate() is True
        
        param.value = 123
        assert param.validate() is False
    
    def test_bool_parameter_validation(self):
        """Test boolean parameter validation."""
        param = EffectParameter(
            name="enabled",
            value=True,
            param_type="bool"
        )
        assert param.validate() is True
        
        param.value = "true"
        assert param.validate() is False
    
    def test_color_parameter_validation(self):
        """Test color parameter validation (RGBA tuple)."""
        param = EffectParameter(
            name="text_color",
            value=(255, 255, 255, 255),
            param_type="color"
        )
        assert param.validate() is True
        
        # Test invalid format
        param.value = (255, 255, 255)  # Missing alpha
        assert param.validate() is False
        
        # Test out of range values
        param.value = (256, 255, 255, 255)
        assert param.validate() is False
        
        param.value = (-1, 255, 255, 255)
        assert param.validate() is False
    
    def test_position_parameter_validation(self):
        """Test position parameter validation."""
        # Test string position
        param = EffectParameter(
            name="position",
            value="center",
            param_type="position"
        )
        assert param.validate() is True
        
        # Test invalid string position
        param.value = "invalid_position"
        assert param.validate() is False
        
        # Test tuple position
        param.value = (100, 200)
        assert param.validate() is True
        
        # Test invalid tuple
        param.value = (100,)  # Missing y coordinate
        assert param.validate() is False


class MockEffect(BaseEffect):
    """Mock effect class for testing BaseEffect functionality."""
    
    def _define_parameters(self) -> Dict[str, EffectParameter]:
        return {
            'opacity': EffectParameter(
                name='opacity',
                value=1.0,
                param_type='float',
                min_value=0.0,
                max_value=1.0,
                default_value=1.0,
                description='Effect opacity'
            ),
            'font_size': EffectParameter(
                name='font_size',
                value=24,
                param_type='int',
                min_value=8,
                max_value=72,
                default_value=24,
                description='Font size in pixels'
            ),
            'color': EffectParameter(
                name='color',
                value=(255, 255, 255, 255),
                param_type='color',
                default_value=(255, 255, 255, 255),
                description='Text color'
            )
        }
    
    def apply(self, clip, subtitle_data):
        """Mock apply method."""
        return clip


class TestBaseEffect:
    """Test cases for BaseEffect class."""
    
    def test_effect_initialization(self):
        """Test effect initialization with valid parameters."""
        parameters = {
            'opacity': 0.8,
            'font_size': 32,
            'color': (255, 0, 0, 255)
        }
        
        effect = MockEffect("test_effect", parameters)
        
        assert effect.name == "test_effect"
        assert effect.get_parameter_value('opacity') == 0.8
        assert effect.get_parameter_value('font_size') == 32
        assert effect.get_parameter_value('color') == (255, 0, 0, 255)
    
    def test_effect_initialization_with_defaults(self):
        """Test effect initialization using default parameter values."""
        parameters = {
            'opacity': 0.5
            # font_size and color should use defaults
        }
        
        effect = MockEffect("test_effect", parameters)
        
        assert effect.get_parameter_value('opacity') == 0.5
        assert effect.get_parameter_value('font_size') == 24  # default
        assert effect.get_parameter_value('color') == (255, 255, 255, 255)  # default
    
    def test_effect_initialization_missing_required_parameter(self):
        """Test effect initialization fails with missing required parameter."""
        # Create effect with required parameter (no default)
        class RequiredParamEffect(BaseEffect):
            def _define_parameters(self):
                return {
                    'required_param': EffectParameter(
                        name='required_param',
                        value=None,
                        param_type='str',
                        description='Required parameter'
                    )
                }
            
            def apply(self, clip, subtitle_data):
                return clip
        
        with pytest.raises(EffectError, match="Required parameter 'required_param' not provided"):
            RequiredParamEffect("test", {})
    
    def test_parameter_validation_on_initialization(self):
        """Test parameter validation during effect initialization."""
        parameters = {
            'opacity': 1.5,  # Invalid: out of range
            'font_size': 32,
            'color': (255, 255, 255, 255)
        }
        
        with pytest.raises(EffectError, match="Invalid value for parameter 'opacity'"):
            MockEffect("test_effect", parameters)
    
    def test_get_parameter_schema(self):
        """Test parameter schema generation."""
        effect = MockEffect("test", {'opacity': 0.5})
        schema = effect.get_parameter_schema()
        
        assert 'opacity' in schema
        assert schema['opacity']['type'] == 'float'
        assert schema['opacity']['min_value'] == 0.0
        assert schema['opacity']['max_value'] == 1.0
        assert schema['opacity']['default_value'] == 1.0
    
    def test_validate_parameters_method(self):
        """Test the validate_parameters method."""
        effect = MockEffect("test", {'opacity': 0.5})
        
        # Valid parameters
        valid_params = {'opacity': 0.8, 'font_size': 16}
        assert effect.validate_parameters(valid_params) is True
        
        # Invalid parameters
        invalid_params = {'opacity': 1.5}  # Out of range
        assert effect.validate_parameters(invalid_params) is False
    
    def test_get_parameter_value(self):
        """Test getting parameter values."""
        effect = MockEffect("test", {'opacity': 0.7})
        
        assert effect.get_parameter_value('opacity') == 0.7
        
        with pytest.raises(EffectError, match="Parameter 'nonexistent' not found"):
            effect.get_parameter_value('nonexistent')
    
    def test_set_parameter_value(self):
        """Test setting parameter values."""
        effect = MockEffect("test", {'opacity': 0.5})
        
        # Valid value
        effect.set_parameter_value('opacity', 0.8)
        assert effect.get_parameter_value('opacity') == 0.8
        
        # Invalid value
        with pytest.raises(EffectError, match="Invalid value for parameter 'opacity'"):
            effect.set_parameter_value('opacity', 1.5)
        
        # Nonexistent parameter
        with pytest.raises(EffectError, match="Parameter 'nonexistent' not defined"):
            effect.set_parameter_value('nonexistent', 0.5)
    
    @patch('src.subtitle_creator.effects.base.MOVIEPY_AVAILABLE', False)
    def test_create_text_clip_without_moviepy(self):
        """Test text clip creation when MoviePy is not available."""
        effect = MockEffect("test", {'opacity': 0.5})
        
        clip = effect._create_text_clip("Test text", 0.0, 5.0)
        
        assert clip.text == "Test text"
        assert clip.duration == 5.0
    
    def test_interpolate_value(self):
        """Test value interpolation utility."""
        effect = MockEffect("test", {'opacity': 0.5})
        
        # Linear interpolation
        result = effect._interpolate_value(0.0, 10.0, 0.5)
        assert result == 5.0
        
        # With easing function
        result = effect._interpolate_value(0.0, 10.0, 0.25, ease_in_out_cubic)
        assert result != 2.5  # Should be different due to easing
    
    def test_effect_serialization(self):
        """Test effect serialization to dictionary."""
        parameters = {'opacity': 0.8, 'font_size': 32}
        effect = MockEffect("test_effect", parameters)
        
        serialized = effect.to_dict()
        
        assert serialized['name'] == "test_effect"
        assert serialized['class'] == "MockEffect"
        assert serialized['parameters']['opacity'] == 0.8
        assert serialized['parameters']['font_size'] == 32
    
    def test_effect_deserialization(self):
        """Test effect creation from dictionary."""
        data = {
            'name': 'test_effect',
            'class': 'MockEffect',
            'parameters': {'opacity': 0.6, 'font_size': 28}
        }
        
        effect = MockEffect.from_dict(data)
        
        assert effect.name == "test_effect"
        assert effect.get_parameter_value('opacity') == 0.6
        assert effect.get_parameter_value('font_size') == 28


class TestEasingFunctions:
    """Test cases for easing functions."""
    
    def test_ease_in_out_cubic(self):
        """Test cubic ease-in-out function."""
        # Test boundary values
        assert ease_in_out_cubic(0.0) == 0.0
        assert ease_in_out_cubic(1.0) == 1.0
        
        # Test midpoint
        mid_result = ease_in_out_cubic(0.5)
        assert 0.0 < mid_result < 1.0
    
    def test_ease_out_bounce(self):
        """Test bounce ease-out function."""
        # Test boundary values
        assert ease_out_bounce(0.0) == 0.0
        assert abs(ease_out_bounce(1.0) - 1.0) < 0.001  # Close to 1.0
        
        # Test that it produces bounce-like values
        values = [ease_out_bounce(t) for t in [0.2, 0.4, 0.6, 0.8]]
        assert all(0.0 <= v <= 1.2 for v in values)  # Bounce can overshoot slightly
    
    def test_ease_in_out_sine(self):
        """Test sine ease-in-out function."""
        # Test boundary values
        assert abs(ease_in_out_sine(0.0) - 0.0) < 0.001
        assert abs(ease_in_out_sine(1.0) - 1.0) < 0.001
        
        # Test midpoint
        mid_result = ease_in_out_sine(0.5)
        assert abs(mid_result - 0.5) < 0.001  # Should be close to 0.5


class TestEffectIntegration:
    """Integration tests for effect functionality."""
    
    def test_effect_with_subtitle_data(self):
        """Test effect application with actual subtitle data."""
        # Create mock subtitle data
        word_timing = WordTiming(word="test", start_time=0.0, end_time=1.0)
        subtitle_line = SubtitleLine(
            start_time=0.0,
            end_time=5.0,
            text="Test subtitle",
            words=[word_timing],
            style_overrides={}
        )
        subtitle_data = SubtitleData(
            lines=[subtitle_line],
            global_style={},
            metadata={}
        )
        
        # Create mock clip
        mock_clip = Mock()
        mock_clip.duration = 5.0
        
        effect = MockEffect("test", {'opacity': 0.8})
        
        # Should not raise an exception
        result = effect.apply(mock_clip, subtitle_data)
        assert result == mock_clip  # Mock implementation returns input clip
    
    def test_parameter_edge_cases(self):
        """Test parameter handling edge cases."""
        effect = MockEffect("test", {'opacity': 0.5})
        
        # Test parameter with exact boundary values
        effect.set_parameter_value('opacity', 0.0)  # Min value
        assert effect.get_parameter_value('opacity') == 0.0
        
        effect.set_parameter_value('opacity', 1.0)  # Max value
        assert effect.get_parameter_value('opacity') == 1.0
        
        # Test integer parameter boundaries
        effect.set_parameter_value('font_size', 8)   # Min value
        effect.set_parameter_value('font_size', 72)  # Max value