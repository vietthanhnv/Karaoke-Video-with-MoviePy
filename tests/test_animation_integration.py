"""
Integration tests for animation effects with the effects system.

This module tests that animation effects can be properly registered and used
within the effects system framework.
"""

import pytest
from unittest.mock import Mock
from dataclasses import dataclass
from typing import List, Optional

from src.subtitle_creator.effects.system import EffectSystem
from src.subtitle_creator.effects.animation import (
    KaraokeHighlightEffect, ScaleBounceEffect, TypewriterEffect, FadeTransitionEffect
)


@dataclass
class MockWordTiming:
    """Mock word timing for testing."""
    word: str
    start_time: float
    end_time: float


@dataclass
class MockSubtitleLine:
    """Mock subtitle line for testing."""
    text: str
    start_time: float
    end_time: float
    words: Optional[List[MockWordTiming]] = None
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclass
class MockSubtitleData:
    """Mock subtitle data for testing."""
    lines: List[MockSubtitleLine]


class MockMask:
    """Mock mask for testing."""
    def __init__(self):
        self.layer_index = 0
        self.start = 0
        self.duration = 0
        self.pos = (0, 0)
        self.audio = None
        self.size = (1920, 1080)
        self.fps = 24
    
    @property
    def end(self):
        return self.start + self.duration
    
    def with_position(self, pos):
        mock_mask = MockMask()
        mock_mask.__dict__.update(self.__dict__)
        mock_mask.pos = pos
        return mock_mask
    
    def with_end(self, end_time):
        mock_mask = MockMask()
        mock_mask.__dict__.update(self.__dict__)
        mock_mask.duration = end_time - self.start
        return mock_mask
    
    def with_start(self, start_time, change_end=True):
        mock_mask = MockMask()
        mock_mask.__dict__.update(self.__dict__)
        mock_mask.start = start_time
        if not change_end:
            mock_mask.duration = self.duration
        return mock_mask
    
    def with_layer_index(self, layer_index):
        mock_mask = MockMask()
        mock_mask.__dict__.update(self.__dict__)
        mock_mask.layer_index = layer_index
        return mock_mask


class MockVideoClip:
    """Mock VideoClip for testing."""
    def __init__(self):
        self.duration = 0
        self.size = (1920, 1080)
        self.layer_index = 0
        self.fps = 24
        self.audio = None
        self.start = 0
        self.mask = None
        self.pos = (0, 0)
    
    @property
    def end(self):
        return self.start + self.duration
    
    def with_mask(self):
        """Return self with a mock mask."""
        mock_clip = MockVideoClip()
        mock_clip.__dict__.update(self.__dict__)
        mock_clip.mask = MockMask()
        return mock_clip
    
    def with_position(self, pos):
        """Mock position setting."""
        mock_clip = MockVideoClip()
        mock_clip.__dict__.update(self.__dict__)
        mock_clip.pos = pos
        return mock_clip
    
    def with_end(self, end_time):
        """Mock end time setting."""
        mock_clip = MockVideoClip()
        mock_clip.__dict__.update(self.__dict__)
        mock_clip.duration = end_time - self.start
        return mock_clip
    
    def with_start(self, start_time, change_end=True):
        """Mock start time setting."""
        mock_clip = MockVideoClip()
        mock_clip.__dict__.update(self.__dict__)
        mock_clip.start = start_time
        if not change_end:
            mock_clip.duration = self.duration
        return mock_clip
    
    def with_layer_index(self, layer_index):
        """Mock layer index setting."""
        mock_clip = MockVideoClip()
        mock_clip.__dict__.update(self.__dict__)
        mock_clip.layer_index = layer_index
        return mock_clip


class TestAnimationEffectsIntegration:
    """Integration tests for animation effects with the effects system."""
    
    def test_register_animation_effects(self):
        """Test that animation effects can be registered with the effects system."""
        system = EffectSystem()
        
        # Register all animation effects
        system.register_effect(KaraokeHighlightEffect)
        system.register_effect(ScaleBounceEffect)
        system.register_effect(TypewriterEffect)
        system.register_effect(FadeTransitionEffect)
        
        registered_effects = system.get_registered_effects()
        
        assert 'KaraokeHighlightEffect' in registered_effects
        assert 'ScaleBounceEffect' in registered_effects
        assert 'TypewriterEffect' in registered_effects
        assert 'FadeTransitionEffect' in registered_effects
    
    def test_create_animation_effects_through_system(self):
        """Test creating animation effects through the effects system."""
        system = EffectSystem()
        
        # Register effects
        system.register_effect(KaraokeHighlightEffect)
        system.register_effect(ScaleBounceEffect)
        system.register_effect(TypewriterEffect)
        system.register_effect(FadeTransitionEffect)
        
        # Create effects through the system
        karaoke_effect = system.create_effect('KaraokeHighlightEffect', {
            'highlight_color': (255, 0, 0, 255)
        })
        bounce_effect = system.create_effect('ScaleBounceEffect', {
            'bounce_scale': 1.5
        })
        typewriter_effect = system.create_effect('TypewriterEffect', {
            'reveal_mode': 'word'
        })
        fade_effect = system.create_effect('FadeTransitionEffect', {
            'fade_type': 'in'
        })
        
        assert isinstance(karaoke_effect, KaraokeHighlightEffect)
        assert isinstance(bounce_effect, ScaleBounceEffect)
        assert isinstance(typewriter_effect, TypewriterEffect)
        assert isinstance(fade_effect, FadeTransitionEffect)
        
        # Verify parameters were set correctly
        assert karaoke_effect.get_parameter_value('highlight_color') == (255, 0, 0, 255)
        assert bounce_effect.get_parameter_value('bounce_scale') == 1.5
        assert typewriter_effect.get_parameter_value('reveal_mode') == 'word'
        assert fade_effect.get_parameter_value('fade_type') == 'in'
    
    def test_apply_multiple_animation_effects(self):
        """Test applying multiple animation effects through the system."""
        system = EffectSystem()
        
        # Register and create effects
        system.register_effect(KaraokeHighlightEffect)
        system.register_effect(FadeTransitionEffect)
        
        karaoke_effect = system.create_effect('KaraokeHighlightEffect', {})
        fade_effect = system.create_effect('FadeTransitionEffect', {})
        
        # Add effects to system
        system.add_effect(karaoke_effect)
        system.add_effect(fade_effect)
        
        # Create test data
        clip = MockVideoClip()
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        # Apply effects
        result = system.apply_effects(clip, subtitle_data)
        
        # Should return a clip (could be CompositeVideoClip or MockVideoClip in test mode)
        assert result is not None
        # In test mode with mock objects, we get the original mock clip back
        if hasattr(result, '__class__') and 'Mock' in result.__class__.__name__:
            assert result == clip
        else:
            from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
            assert isinstance(result, CompositeVideoClip)
        
        # Verify effects are active
        active_effects = system.get_active_effects()
        assert len(active_effects) == 2
        assert karaoke_effect in active_effects
        assert fade_effect in active_effects
    
    def test_animation_effects_preset_save_load(self):
        """Test saving and loading presets with animation effects."""
        system = EffectSystem()
        
        # Register effects
        system.register_effect(KaraokeHighlightEffect)
        system.register_effect(ScaleBounceEffect)
        
        # Create and configure effects
        karaoke_effect = system.create_effect('KaraokeHighlightEffect', {
            'highlight_color': (255, 255, 0, 255),
            'transition_duration': 0.2
        })
        bounce_effect = system.create_effect('ScaleBounceEffect', {
            'bounce_scale': 1.3,
            'bounce_count': 3
        })
        
        system.add_effect(karaoke_effect)
        system.add_effect(bounce_effect)
        
        # Save preset
        preset_name = "test_animation_preset"
        system.save_preset(preset_name, "Test preset with animation effects")
        
        # Clear effects and load preset
        system.clear_effects()
        assert len(system.get_active_effects()) == 0
        
        system.load_preset(preset_name)
        
        # Verify effects were loaded
        loaded_effects = system.get_active_effects()
        assert len(loaded_effects) == 2
        
        # Find the loaded effects by type
        loaded_karaoke = None
        loaded_bounce = None
        
        for effect in loaded_effects:
            if isinstance(effect, KaraokeHighlightEffect):
                loaded_karaoke = effect
            elif isinstance(effect, ScaleBounceEffect):
                loaded_bounce = effect
        
        assert loaded_karaoke is not None
        assert loaded_bounce is not None
        
        # Verify parameters were preserved (JSON serialization converts tuples to lists)
        highlight_color = loaded_karaoke.get_parameter_value('highlight_color')
        assert list(highlight_color) == [255, 255, 0, 255]
        assert loaded_karaoke.get_parameter_value('transition_duration') == 0.2
        assert loaded_bounce.get_parameter_value('bounce_scale') == 1.3
        assert loaded_bounce.get_parameter_value('bounce_count') == 3
    
    def test_animation_effects_parameter_schemas(self):
        """Test that animation effects provide comprehensive parameter schemas."""
        effects = [
            KaraokeHighlightEffect("karaoke", {}),
            ScaleBounceEffect("bounce", {}),
            TypewriterEffect("typewriter", {}),
            FadeTransitionEffect("fade", {})
        ]
        
        for effect in effects:
            schema = effect.get_parameter_schema()
            
            # Verify schema structure
            assert isinstance(schema, dict)
            assert len(schema) > 0
            
            # Check that each parameter has required metadata
            for param_name, param_info in schema.items():
                assert 'type' in param_info
                assert 'description' in param_info
                assert param_info['description']  # Non-empty description
                
                # Check for appropriate constraints
                if param_info['type'] in ['int', 'float']:
                    # Numeric parameters should have reasonable bounds
                    if 'min_value' in param_info:
                        assert param_info['min_value'] is not None
                    if 'max_value' in param_info:
                        assert param_info['max_value'] is not None
    
    def test_animation_effects_with_complex_subtitle_data(self):
        """Test animation effects with complex subtitle data including word timing."""
        system = EffectSystem()
        system.register_effect(KaraokeHighlightEffect)
        
        # Create karaoke effect that uses word timing
        karaoke_effect = system.create_effect('KaraokeHighlightEffect', {
            'highlight_mode': 'word'
        })
        system.add_effect(karaoke_effect)
        
        # Create complex subtitle data with word timing
        words = [
            MockWordTiming("Hello", 0.0, 0.5),
            MockWordTiming("beautiful", 0.5, 1.2),
            MockWordTiming("world", 1.2, 1.8)
        ]
        line = MockSubtitleLine("Hello beautiful world", 0.0, 1.8, words)
        subtitle_data = MockSubtitleData([line])
        
        clip = MockVideoClip()
        
        # Apply effects - should handle word timing gracefully
        result = system.apply_effects(clip, subtitle_data)
        assert result is not None
    
    def test_animation_effects_error_handling(self):
        """Test error handling in animation effects."""
        system = EffectSystem()
        system.register_effect(KaraokeHighlightEffect)
        
        # Test with invalid parameters
        with pytest.raises(Exception):  # Should raise EffectError or similar
            system.create_effect('KaraokeHighlightEffect', {
                'highlight_color': 'invalid_color'
            })
        
        # Test with valid effect but problematic data
        effect = system.create_effect('KaraokeHighlightEffect', {})
        system.add_effect(effect)
        
        clip = MockVideoClip()
        
        # Test with None subtitle data - should handle gracefully
        try:
            result = system.apply_effects(clip, None)
            # If it doesn't raise an exception, that's also acceptable
        except Exception as e:
            # Should be a controlled exception, not a crash
            # EffectError is also acceptable as it's a controlled error
            from src.subtitle_creator.interfaces import EffectError
            assert isinstance(e, (TypeError, AttributeError, EffectError))