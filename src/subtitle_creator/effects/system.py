"""
Effect system for managing MoviePy clip composition and effect stacking.

This module provides the EffectSystem class that handles effect application,
composition, preset management, and parameter binding to MoviePy clips.
"""

import json
import pickle
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

# Optional import for MoviePy - will be available when dependencies are installed
try:
    from moviepy.editor import VideoClip, CompositeVideoClip, TextClip, ColorClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    # Create placeholders for development/testing
    class VideoClip:
        def __init__(self):
            self.duration = 0
            self.size = (1920, 1080)
        
        def set_duration(self, duration):
            self.duration = duration
            return self
        
        def set_position(self, position):
            return self
    
    class CompositeVideoClip:
        def __init__(self, clips):
            self.clips = clips
            self.duration = max(clip.duration for clip in clips) if clips else 0
            self.size = (1920, 1080)
    
    class TextClip(VideoClip):
        def __init__(self, text="", **kwargs):
            super().__init__()
            self.text = text
    
    class ColorClip(VideoClip):
        def __init__(self, size, color, duration=None):
            super().__init__()
            self.size = size
            self.color = color
            if duration:
                self.duration = duration
    
    MOVIEPY_AVAILABLE = False

from ..interfaces import Effect, SubtitleData, EffectError
from .base import BaseEffect


@dataclass
class EffectPreset:
    """Represents a saved effect preset with multiple effects and parameters."""
    name: str
    description: str
    effects: List[Dict[str, Any]]
    created_at: str
    version: str = "1.0"


@dataclass
class CompositionLayer:
    """Represents a single layer in the video composition."""
    clip: VideoClip
    effect: Effect
    layer_order: int
    blend_mode: str = "normal"
    opacity: float = 1.0


class EffectSystem:
    """
    Manages MoviePy clip composition and effect stacking.
    
    This class handles the application of multiple effects to video clips,
    manages effect presets, and provides utilities for clip composition
    and parameter binding.
    """
    
    def __init__(self, preset_directory: Optional[Path] = None):
        """
        Initialize the effect system.
        
        Args:
            preset_directory: Directory to store effect presets
        """
        self.preset_directory = preset_directory or Path.cwd() / "presets"
        self.preset_directory.mkdir(exist_ok=True)
        
        self._registered_effects: Dict[str, type] = {}
        self._active_effects: List[Effect] = []
        self._composition_layers: List[CompositionLayer] = []
    
    def register_effect(self, effect_class: type) -> None:
        """
        Register an effect class for use in the system.
        
        Args:
            effect_class: Effect class to register
        """
        if not issubclass(effect_class, BaseEffect):
            raise EffectError(f"Effect class {effect_class.__name__} must inherit from BaseEffect")
        
        self._registered_effects[effect_class.__name__] = effect_class
    
    def create_effect(self, effect_name: str, parameters: Dict[str, Any]) -> Effect:
        """
        Create an effect instance by name.
        
        Args:
            effect_name: Name of the registered effect class
            parameters: Effect parameters
            
        Returns:
            Effect instance
            
        Raises:
            EffectError: If effect is not registered
        """
        if effect_name not in self._registered_effects:
            raise EffectError(f"Effect '{effect_name}' is not registered")
        
        effect_class = self._registered_effects[effect_name]
        return effect_class(effect_name, parameters)
    
    def add_effect(self, effect: Effect, layer_order: Optional[int] = None) -> None:
        """
        Add an effect to the active effects list.
        
        Args:
            effect: Effect to add
            layer_order: Optional layer order (defaults to next available)
        """
        if layer_order is None:
            layer_order = len(self._active_effects)
        
        self._active_effects.append(effect)
        
        # Sort effects by layer order if they have that attribute
        if hasattr(effect, 'layer_order'):
            effect.layer_order = layer_order
            self._active_effects.sort(key=lambda e: getattr(e, 'layer_order', 0))
    
    def remove_effect(self, effect: Effect) -> None:
        """
        Remove an effect from the active effects list.
        
        Args:
            effect: Effect to remove
        """
        if effect in self._active_effects:
            self._active_effects.remove(effect)
    
    def clear_effects(self) -> None:
        """Clear all active effects."""
        self._active_effects.clear()
        self._composition_layers.clear()
    
    def apply_effects(self, base_clip: VideoClip, subtitle_data: SubtitleData) -> VideoClip:
        """
        Apply all active effects to a base clip with subtitle data.
        
        Args:
            base_clip: Base video clip to apply effects to
            subtitle_data: Subtitle timing and content information
            
        Returns:
            Composite video clip with all effects applied
        """
        if not self._active_effects:
            return base_clip
        
        # Start with the base clip
        composition_clips = [base_clip]
        
        # Apply each effect and collect the resulting clips
        for effect in self._active_effects:
            try:
                effect_clip = effect.apply(base_clip, subtitle_data)
                if effect_clip is not None:
                    composition_clips.append(effect_clip)
            except Exception as e:
                raise EffectError(f"Failed to apply effect '{effect.name}': {str(e)}")
        
        # Create composite clip if we have multiple clips
        if len(composition_clips) == 1:
            return composition_clips[0]
        else:
            if not MOVIEPY_AVAILABLE:
                # Return the base clip for testing
                return base_clip
            
            return CompositeVideoClip(composition_clips)
    
    def create_composition_layer(self, clip: VideoClip, effect: Effect, 
                                layer_order: int, blend_mode: str = "normal", 
                                opacity: float = 1.0) -> CompositionLayer:
        """
        Create a composition layer for advanced clip stacking.
        
        Args:
            clip: Video clip for this layer
            effect: Effect associated with this layer
            layer_order: Stacking order (higher numbers on top)
            blend_mode: Blend mode for compositing
            opacity: Layer opacity (0.0 to 1.0)
            
        Returns:
            CompositionLayer object
        """
        return CompositionLayer(
            clip=clip,
            effect=effect,
            layer_order=layer_order,
            blend_mode=blend_mode,
            opacity=opacity
        )
    
    def compose_layers(self, layers: List[CompositionLayer]) -> VideoClip:
        """
        Compose multiple layers into a single video clip.
        
        Args:
            layers: List of composition layers
            
        Returns:
            Composite video clip
        """
        if not layers:
            raise EffectError("No layers provided for composition")
        
        # Sort layers by order
        sorted_layers = sorted(layers, key=lambda l: l.layer_order)
        
        # Extract clips and apply opacity
        clips = []
        for layer in sorted_layers:
            clip = layer.clip
            
            # Apply opacity if not 1.0
            if layer.opacity < 1.0 and MOVIEPY_AVAILABLE:
                clip = clip.set_opacity(layer.opacity)
            
            clips.append(clip)
        
        if not MOVIEPY_AVAILABLE:
            # Return the first clip for testing
            return clips[0] if clips else None
        
        return CompositeVideoClip(clips)
    
    def bind_parameter_to_clip_property(self, effect: Effect, param_name: str, 
                                       clip_property: str, 
                                       transform_func: Optional[callable] = None) -> None:
        """
        Bind an effect parameter to a MoviePy clip property.
        
        Args:
            effect: Effect containing the parameter
            param_name: Name of the effect parameter
            clip_property: Name of the clip property to bind to
            transform_func: Optional function to transform the parameter value
        """
        if not hasattr(effect, 'get_parameter_value'):
            raise EffectError(f"Effect '{effect.name}' does not support parameter binding")
        
        try:
            param_value = effect.get_parameter_value(param_name)
            
            # Apply transformation if provided
            if transform_func:
                param_value = transform_func(param_value)
            
            # Store binding information for later use
            if not hasattr(effect, '_parameter_bindings'):
                effect._parameter_bindings = {}
            
            effect._parameter_bindings[param_name] = {
                'clip_property': clip_property,
                'transform_func': transform_func,
                'value': param_value
            }
            
        except Exception as e:
            raise EffectError(f"Failed to bind parameter '{param_name}' to clip property '{clip_property}': {str(e)}")
    
    def save_preset(self, preset_name: str, description: str = "") -> None:
        """
        Save current effects configuration as a preset.
        
        Args:
            preset_name: Name for the preset
            description: Optional description
        """
        if not self._active_effects:
            raise EffectError("No active effects to save as preset")
        
        # Serialize effects
        effects_data = []
        for effect in self._active_effects:
            if hasattr(effect, 'to_dict'):
                effects_data.append(effect.to_dict())
            else:
                # Fallback serialization
                effects_data.append({
                    'name': effect.name,
                    'class': effect.__class__.__name__,
                    'parameters': effect.parameters
                })
        
        preset = EffectPreset(
            name=preset_name,
            description=description,
            effects=effects_data,
            created_at=str(Path.cwd())  # Placeholder for timestamp
        )
        
        # Save to file
        preset_file = self.preset_directory / f"{preset_name}.json"
        try:
            with open(preset_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(preset), f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise EffectError(f"Failed to save preset '{preset_name}': {str(e)}")
    
    def load_preset(self, preset_name: str) -> None:
        """
        Load an effects preset and apply it to the current system.
        
        Args:
            preset_name: Name of the preset to load
            
        Raises:
            EffectError: If preset cannot be loaded
        """
        preset_file = self.preset_directory / f"{preset_name}.json"
        
        if not preset_file.exists():
            raise EffectError(f"Preset '{preset_name}' not found")
        
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            preset = EffectPreset(**preset_data)
            
            # Clear current effects
            self.clear_effects()
            
            # Recreate effects from preset
            for effect_data in preset.effects:
                effect_class_name = effect_data.get('class')
                if effect_class_name in self._registered_effects:
                    effect = self.create_effect(effect_class_name, effect_data['parameters'])
                    self.add_effect(effect)
                else:
                    print(f"Warning: Effect class '{effect_class_name}' not registered, skipping")
            
        except Exception as e:
            raise EffectError(f"Failed to load preset '{preset_name}': {str(e)}")
    
    def list_presets(self) -> List[str]:
        """
        List all available presets.
        
        Returns:
            List of preset names
        """
        preset_files = self.preset_directory.glob("*.json")
        return [f.stem for f in preset_files]
    
    def get_preset_info(self, preset_name: str) -> Dict[str, Any]:
        """
        Get information about a specific preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Dictionary with preset information
        """
        preset_file = self.preset_directory / f"{preset_name}.json"
        
        if not preset_file.exists():
            raise EffectError(f"Preset '{preset_name}' not found")
        
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            return {
                'name': preset_data['name'],
                'description': preset_data['description'],
                'effect_count': len(preset_data['effects']),
                'effects': [e['name'] for e in preset_data['effects']],
                'created_at': preset_data['created_at'],
                'version': preset_data.get('version', '1.0')
            }
        except Exception as e:
            raise EffectError(f"Failed to get preset info for '{preset_name}': {str(e)}")
    
    def serialize_clip_state(self, clip: VideoClip) -> bytes:
        """
        Serialize a MoviePy clip state for preset storage.
        
        Args:
            clip: VideoClip to serialize
            
        Returns:
            Serialized clip data
        """
        # Note: Full MoviePy clip serialization is complex due to function references
        # This is a simplified version that stores basic properties
        clip_data = {
            'duration': getattr(clip, 'duration', 0),
            'size': getattr(clip, 'size', (1920, 1080)),
            'fps': getattr(clip, 'fps', 24)
        }
        
        return pickle.dumps(clip_data)
    
    def deserialize_clip_state(self, clip_data: bytes) -> Dict[str, Any]:
        """
        Deserialize clip state data.
        
        Args:
            clip_data: Serialized clip data
            
        Returns:
            Dictionary with clip properties
        """
        return pickle.loads(clip_data)
    
    def get_active_effects(self) -> List[Effect]:
        """
        Get list of currently active effects.
        
        Returns:
            List of active effects
        """
        return self._active_effects.copy()
    
    def get_registered_effects(self) -> Dict[str, type]:
        """
        Get dictionary of registered effect classes.
        
        Returns:
            Dictionary mapping effect names to classes
        """
        return self._registered_effects.copy()
    
    def validate_effect_stack(self) -> Tuple[bool, List[str]]:
        """
        Validate the current effect stack for potential issues.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for conflicting effects
        effect_types = [type(effect).__name__ for effect in self._active_effects]
        
        # Check for duplicate effects that might conflict
        seen_types = set()
        for effect_type in effect_types:
            if effect_type in seen_types:
                issues.append(f"Multiple instances of effect type '{effect_type}' may conflict")
            seen_types.add(effect_type)
        
        # Check for parameter conflicts
        for i, effect1 in enumerate(self._active_effects):
            for j, effect2 in enumerate(self._active_effects[i+1:], i+1):
                if hasattr(effect1, '_parameter_bindings') and hasattr(effect2, '_parameter_bindings'):
                    bindings1 = effect1._parameter_bindings
                    bindings2 = effect2._parameter_bindings
                    
                    # Check for conflicting clip property bindings
                    for param1, binding1 in bindings1.items():
                        for param2, binding2 in bindings2.items():
                            if binding1['clip_property'] == binding2['clip_property']:
                                issues.append(f"Effects '{effect1.name}' and '{effect2.name}' both bind to clip property '{binding1['clip_property']}'")
        
        return len(issues) == 0, issues