"""
Base effect classes and framework for MoviePy-based subtitle effects.

This module provides the foundation for all subtitle effects, including parameter
management, clip composition, and effect stacking capabilities.
"""

import json
import pickle
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# Optional import for MoviePy - will be available when dependencies are installed
try:
    from moviepy import VideoClip, CompositeVideoClip, TextClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    # Create placeholders for development/testing
    class VideoClip:
        def __init__(self):
            self.duration = 0
            self.size = (1920, 1080)
        
        def with_duration(self, duration):
            self.duration = duration
            return self
        
        def with_position(self, position):
            return self
    
    class CompositeVideoClip:
        def __init__(self, clips):
            self.clips = clips
    
    class TextClip(VideoClip):
        def __init__(self, text="", **kwargs):
            super().__init__()
            self.text = text
    
    MOVIEPY_AVAILABLE = False

from ..interfaces import Effect, SubtitleData, EffectError


@dataclass
class EffectParameter:
    """Represents a single effect parameter with validation and metadata."""
    name: str
    value: Any
    param_type: str  # 'float', 'int', 'str', 'color', 'position', 'bool'
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    default_value: Any = None
    description: str = ""
    
    def validate(self) -> bool:
        """Validate the parameter value against its constraints."""
        if self.param_type == 'float':
            if not isinstance(self.value, (int, float)):
                return False
            # Check for NaN and infinity
            import math
            if math.isnan(self.value) or math.isinf(self.value):
                return False
            if self.min_value is not None and self.value < self.min_value:
                return False
            if self.max_value is not None and self.value > self.max_value:
                return False
        elif self.param_type == 'int':
            if not isinstance(self.value, int):
                return False
            if self.min_value is not None and self.value < self.min_value:
                return False
            if self.max_value is not None and self.value > self.max_value:
                return False
        elif self.param_type == 'str':
            if not isinstance(self.value, str):
                return False
        elif self.param_type == 'bool':
            if not isinstance(self.value, bool):
                return False
        elif self.param_type == 'color':
            # Expect RGBA tuple (r, g, b, a) with values 0-255
            if not isinstance(self.value, (tuple, list)) or len(self.value) != 4:
                return False
            if not all(isinstance(v, int) and 0 <= v <= 255 for v in self.value):
                return False
        elif self.param_type == 'position':
            # Expect (x, y) tuple or string like 'center', 'left', 'right'
            if isinstance(self.value, str):
                valid_positions = ['center', 'left', 'right', 'top', 'bottom']
                if self.value not in valid_positions:
                    return False
            elif isinstance(self.value, (tuple, list)) and len(self.value) == 2:
                if not all(isinstance(v, (int, float)) for v in self.value):
                    return False
            else:
                return False
        
        return True


class BaseEffect(Effect):
    """
    Base implementation of the Effect interface with MoviePy integration.
    
    This class provides common functionality for all effects including parameter
    management, validation, and basic clip manipulation utilities.
    """
    
    def __init__(self, name: str, parameters: Dict[str, Any]):
        """
        Initialize the base effect.
        
        Args:
            name: Human-readable name of the effect
            parameters: Dictionary of effect parameters
        """
        super().__init__(name, parameters)
        self._parameter_definitions = self._define_parameters()
        self._validated_parameters = self._validate_and_convert_parameters(parameters)
    
    def _define_parameters(self) -> Dict[str, EffectParameter]:
        """
        Define the parameters this effect accepts.
        
        Subclasses should override this method to define their specific parameters.
        
        Returns:
            Dictionary mapping parameter names to EffectParameter objects
        """
        return {}
    
    def _validate_and_convert_parameters(self, parameters: Dict[str, Any]) -> Dict[str, EffectParameter]:
        """
        Validate and convert raw parameters to EffectParameter objects.
        
        Args:
            parameters: Raw parameter dictionary
            
        Returns:
            Dictionary of validated EffectParameter objects
            
        Raises:
            EffectError: If parameter validation fails
        """
        validated = {}
        
        # Check for required parameters and set defaults
        for param_name, param_def in self._parameter_definitions.items():
            if param_name in parameters:
                # Create parameter with provided value
                param = EffectParameter(
                    name=param_name,
                    value=parameters[param_name],
                    param_type=param_def.param_type,
                    min_value=param_def.min_value,
                    max_value=param_def.max_value,
                    default_value=param_def.default_value,
                    description=param_def.description
                )
            else:
                # Use default value if available
                if param_def.default_value is not None:
                    param = EffectParameter(
                        name=param_name,
                        value=param_def.default_value,
                        param_type=param_def.param_type,
                        min_value=param_def.min_value,
                        max_value=param_def.max_value,
                        default_value=param_def.default_value,
                        description=param_def.description
                    )
                else:
                    raise EffectError(f"Required parameter '{param_name}' not provided for effect '{self.name}'")
            
            # Validate the parameter
            if not param.validate():
                raise EffectError(f"Invalid value for parameter '{param_name}' in effect '{self.name}': {param.value}")
            
            validated[param_name] = param
        
        return validated
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Get the parameter schema for this effect.
        
        Returns:
            Dictionary describing the parameters this effect accepts
        """
        schema = {}
        for param_name, param_def in self._parameter_definitions.items():
            schema[param_name] = {
                'type': param_def.param_type,
                'min_value': param_def.min_value,
                'max_value': param_def.max_value,
                'default_value': param_def.default_value,
                'description': param_def.description
            }
        return schema
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate that the provided parameters are valid for this effect.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        try:
            self._validate_and_convert_parameters(parameters)
            return True
        except EffectError:
            return False
    
    def get_parameter_value(self, param_name: str) -> Any:
        """
        Get the value of a specific parameter.
        
        Args:
            param_name: Name of the parameter
            
        Returns:
            Parameter value
            
        Raises:
            EffectError: If parameter doesn't exist
        """
        if param_name not in self._validated_parameters:
            raise EffectError(f"Parameter '{param_name}' not found in effect '{self.name}'")
        return self._validated_parameters[param_name].value
    
    def set_parameter_value(self, param_name: str, value: Any) -> None:
        """
        Set the value of a specific parameter.
        
        Args:
            param_name: Name of the parameter
            value: New parameter value
            
        Raises:
            EffectError: If parameter doesn't exist or value is invalid
        """
        if param_name not in self._parameter_definitions:
            raise EffectError(f"Parameter '{param_name}' not defined for effect '{self.name}'")
        
        # Create temporary parameter for validation
        param_def = self._parameter_definitions[param_name]
        temp_param = EffectParameter(
            name=param_name,
            value=value,
            param_type=param_def.param_type,
            min_value=param_def.min_value,
            max_value=param_def.max_value,
            default_value=param_def.default_value,
            description=param_def.description
        )
        
        if not temp_param.validate():
            raise EffectError(f"Invalid value for parameter '{param_name}' in effect '{self.name}': {value}")
        
        self._validated_parameters[param_name] = temp_param
    
    def apply(self, clip: VideoClip, subtitle_data: SubtitleData) -> VideoClip:
        """
        Apply the effect to a video clip with subtitle data.
        
        This is the main method that subclasses must implement to define their
        specific effect behavior.
        
        Args:
            clip: The MoviePy VideoClip to apply the effect to
            subtitle_data: Subtitle timing and content information
            
        Returns:
            Modified VideoClip with the effect applied
        """
        raise NotImplementedError("Subclasses must implement the apply method")
    
    def _create_text_clip(self, text: str, start_time: float, end_time: float, **kwargs) -> VideoClip:
        """
        Utility method to create a text clip with common settings.
        
        Args:
            text: Text content
            start_time: Start time in seconds
            end_time: End time in seconds
            **kwargs: Additional TextClip parameters
            
        Returns:
            Configured TextClip
        """
        if not MOVIEPY_AVAILABLE:
            # Return placeholder for testing
            clip = TextClip(text=text)
            clip.duration = end_time - start_time
            return clip
        
        # Default text clip settings
        default_kwargs = {
            'font_size': 50,
            'color': 'white'
        }
        default_kwargs.update(kwargs)
        
        text_clip = TextClip(text=text, **default_kwargs)
        text_clip = text_clip.with_duration(end_time - start_time)
        
        return text_clip
    
    def _interpolate_value(self, start_value: float, end_value: float, 
                          progress: float, easing_func: Optional[Callable] = None) -> float:
        """
        Interpolate between two values with optional easing function.
        
        Args:
            start_value: Starting value
            end_value: Ending value
            progress: Progress from 0.0 to 1.0
            easing_func: Optional easing function
            
        Returns:
            Interpolated value
        """
        if easing_func:
            progress = easing_func(progress)
        
        return start_value + (end_value - start_value) * progress
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the effect to a dictionary.
        
        Returns:
            Dictionary representation of the effect
        """
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'parameters': {name: param.value for name, param in self._validated_parameters.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEffect':
        """
        Create an effect instance from a dictionary.
        
        Args:
            data: Dictionary representation of the effect
            
        Returns:
            Effect instance
        """
        return cls(data['name'], data['parameters'])


# Common easing functions for smooth animations
def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out easing function."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_bounce(t: float) -> float:
    """Bounce ease-out easing function."""
    n1 = 7.5625
    d1 = 2.75
    
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_in_out_sine(t: float) -> float:
    """Sine ease-in-out easing function."""
    import math
    return -(math.cos(math.pi * t) - 1) / 2