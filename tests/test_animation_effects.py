"""
Tests for animation effects implementation.

This module tests the concrete animation effects including karaoke highlighting,
scale bounce, typewriter reveal, and fade transitions.
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Optional

from src.subtitle_creator.effects.animation import (
    KaraokeHighlightEffect, ScaleBounceEffect, TypewriterEffect, FadeTransitionEffect
)
from src.subtitle_creator.interfaces import EffectError


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


class MockVideoClip:
    """Mock VideoClip for testing."""
    def __init__(self):
        self.duration = 0
        self.size = (1920, 1080)
        self.start = 0
        self.pos = ('center', 'bottom')
    
    def set_duration(self, duration):
        self.duration = duration
        return self
    
    def set_start(self, start):
        self.start = start
        return self
    
    def set_position(self, position):
        self.pos = position
        return self
    
    def set_opacity(self, opacity):
        self.opacity = opacity
        return self
    
    def resize(self, factor):
        return self
    
    def subclip(self, start, end):
        return self
    
    def crossfadein(self, duration):
        return self
    
    def crossfadeout(self, duration):
        return self


class TestKaraokeHighlightEffect:
    """Test cases for KaraokeHighlightEffect."""
    
    def test_init_with_default_parameters(self):
        """Test initialization with default parameters."""
        effect = KaraokeHighlightEffect("karaoke", {})
        
        assert effect.name == "karaoke"
        assert effect.get_parameter_value('default_color') == (255, 255, 255, 255)
        assert effect.get_parameter_value('highlight_color') == (255, 255, 0, 255)
        assert effect.get_parameter_value('transition_duration') == 0.1
        assert effect.get_parameter_value('highlight_mode') == 'word'
        assert effect.get_parameter_value('glow_enabled') == False
        assert effect.get_parameter_value('glow_intensity') == 0.5
    
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        params = {
            'default_color': (200, 200, 200, 255),
            'highlight_color': (255, 0, 0, 255),
            'transition_duration': 0.2,
            'highlight_mode': 'character',
            'glow_enabled': True,
            'glow_intensity': 0.8
        }
        
        effect = KaraokeHighlightEffect("karaoke", params)
        
        assert effect.get_parameter_value('default_color') == (200, 200, 200, 255)
        assert effect.get_parameter_value('highlight_color') == (255, 0, 0, 255)
        assert effect.get_parameter_value('transition_duration') == 0.2
        assert effect.get_parameter_value('highlight_mode') == 'character'
        assert effect.get_parameter_value('glow_enabled') == True
        assert effect.get_parameter_value('glow_intensity') == 0.8
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Test invalid color
        with pytest.raises(EffectError):
            KaraokeHighlightEffect("karaoke", {'default_color': (256, 0, 0, 0)})
        
        # Test invalid transition duration
        with pytest.raises(EffectError):
            KaraokeHighlightEffect("karaoke", {'transition_duration': -0.1})
        
        # Test invalid glow intensity
        with pytest.raises(EffectError):
            KaraokeHighlightEffect("karaoke", {'glow_intensity': 1.5})
    
    def test_apply_with_empty_subtitle_data(self):
        """Test apply method with empty subtitle data."""
        effect = KaraokeHighlightEffect("karaoke", {})
        clip = MockVideoClip()
        subtitle_data = MockSubtitleData([])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_word_level_karaoke(self):
        """Test apply method with word-level karaoke data."""
        effect = KaraokeHighlightEffect("karaoke", {'highlight_mode': 'word'})
        clip = MockVideoClip()
        
        # Create subtitle data with word timing
        words = [
            MockWordTiming("Hello", 0.0, 0.5),
            MockWordTiming("world", 0.5, 1.0)
        ]
        line = MockSubtitleLine("Hello world", 0.0, 1.0, words)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        # Should return the original clip in test environment
        assert result == clip
    
    def test_apply_with_line_level_karaoke(self):
        """Test apply method with line-level karaoke (fallback)."""
        effect = KaraokeHighlightEffect("karaoke", {'highlight_mode': 'line'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 1.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_interpolate_color(self):
        """Test color interpolation method."""
        effect = KaraokeHighlightEffect("karaoke", {})
        
        color1 = (255, 0, 0, 255)  # Red
        color2 = (0, 255, 0, 255)  # Green
        
        # Test interpolation at different progress points
        result_0 = effect._interpolate_color(color1, color2, 0.0)
        assert result_0 == color1
        
        result_1 = effect._interpolate_color(color1, color2, 1.0)
        assert result_1 == color2
        
        result_half = effect._interpolate_color(color1, color2, 0.5)
        assert result_half == (127, 127, 0, 255)


class TestScaleBounceEffect:
    """Test cases for ScaleBounceEffect."""
    
    def test_init_with_default_parameters(self):
        """Test initialization with default parameters."""
        effect = ScaleBounceEffect("bounce", {})
        
        assert effect.name == "bounce"
        assert effect.get_parameter_value('bounce_scale') == 1.2
        assert effect.get_parameter_value('bounce_duration') == 0.5
        assert effect.get_parameter_value('bounce_count') == 2
        assert effect.get_parameter_value('trigger_mode') == 'entrance'
        assert effect.get_parameter_value('easing_function') == 'bounce'
        assert effect.get_parameter_value('scale_origin') == 'center'
    
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        params = {
            'bounce_scale': 1.5,
            'bounce_duration': 1.0,
            'bounce_count': 3,
            'trigger_mode': 'exit',
            'easing_function': 'cubic',
            'scale_origin': 'top'
        }
        
        effect = ScaleBounceEffect("bounce", params)
        
        assert effect.get_parameter_value('bounce_scale') == 1.5
        assert effect.get_parameter_value('bounce_duration') == 1.0
        assert effect.get_parameter_value('bounce_count') == 3
        assert effect.get_parameter_value('trigger_mode') == 'exit'
        assert effect.get_parameter_value('easing_function') == 'cubic'
        assert effect.get_parameter_value('scale_origin') == 'top'
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Test invalid bounce scale
        with pytest.raises(EffectError):
            ScaleBounceEffect("bounce", {'bounce_scale': 0.1})
        
        # Test invalid bounce duration
        with pytest.raises(EffectError):
            ScaleBounceEffect("bounce", {'bounce_duration': 0.05})
        
        # Test invalid bounce count
        with pytest.raises(EffectError):
            ScaleBounceEffect("bounce", {'bounce_count': 0})
    
    def test_apply_with_empty_subtitle_data(self):
        """Test apply method with empty subtitle data."""
        effect = ScaleBounceEffect("bounce", {})
        clip = MockVideoClip()
        subtitle_data = MockSubtitleData([])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_entrance_bounce(self):
        """Test apply method with entrance bounce."""
        effect = ScaleBounceEffect("bounce", {'trigger_mode': 'entrance'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_exit_bounce(self):
        """Test apply method with exit bounce."""
        effect = ScaleBounceEffect("bounce", {'trigger_mode': 'exit'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_continuous_bounce(self):
        """Test apply method with continuous bounce."""
        effect = ScaleBounceEffect("bounce", {'trigger_mode': 'continuous'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_get_easing_function(self):
        """Test easing function retrieval."""
        effect = ScaleBounceEffect("bounce", {})
        
        # Test different easing functions
        bounce_func = effect._get_easing_function('bounce')
        assert callable(bounce_func)
        
        cubic_func = effect._get_easing_function('cubic')
        assert callable(cubic_func)
        
        linear_func = effect._get_easing_function('linear')
        assert callable(linear_func)
        assert linear_func(0.5) == 0.5
        
        # Test unknown function defaults to bounce
        unknown_func = effect._get_easing_function('unknown')
        assert callable(unknown_func)


class TestTypewriterEffect:
    """Test cases for TypewriterEffect."""
    
    def test_init_with_default_parameters(self):
        """Test initialization with default parameters."""
        effect = TypewriterEffect("typewriter", {})
        
        assert effect.name == "typewriter"
        assert effect.get_parameter_value('reveal_mode') == 'character'
        assert effect.get_parameter_value('reveal_speed') == 0.05
        assert effect.get_parameter_value('cursor_enabled') == True
        assert effect.get_parameter_value('cursor_character') == '|'
        assert effect.get_parameter_value('cursor_blink_rate') == 0.5
        assert effect.get_parameter_value('sound_enabled') == False
        assert effect.get_parameter_value('start_delay') == 0.0
    
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        params = {
            'reveal_mode': 'word',
            'reveal_speed': 0.1,
            'cursor_enabled': False,
            'cursor_character': '_',
            'cursor_blink_rate': 1.0,
            'sound_enabled': True,
            'start_delay': 0.5
        }
        
        effect = TypewriterEffect("typewriter", params)
        
        assert effect.get_parameter_value('reveal_mode') == 'word'
        assert effect.get_parameter_value('reveal_speed') == 0.1
        assert effect.get_parameter_value('cursor_enabled') == False
        assert effect.get_parameter_value('cursor_character') == '_'
        assert effect.get_parameter_value('cursor_blink_rate') == 1.0
        assert effect.get_parameter_value('sound_enabled') == True
        assert effect.get_parameter_value('start_delay') == 0.5
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Test invalid reveal speed
        with pytest.raises(EffectError):
            TypewriterEffect("typewriter", {'reveal_speed': 0.005})
        
        # Test invalid cursor blink rate
        with pytest.raises(EffectError):
            TypewriterEffect("typewriter", {'cursor_blink_rate': 0.05})
        
        # Test invalid start delay
        with pytest.raises(EffectError):
            TypewriterEffect("typewriter", {'start_delay': -1.0})
    
    def test_apply_with_empty_subtitle_data(self):
        """Test apply method with empty subtitle data."""
        effect = TypewriterEffect("typewriter", {})
        clip = MockVideoClip()
        subtitle_data = MockSubtitleData([])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_character_mode(self):
        """Test apply method with character reveal mode."""
        effect = TypewriterEffect("typewriter", {'reveal_mode': 'character'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_word_mode(self):
        """Test apply method with word reveal mode."""
        effect = TypewriterEffect("typewriter", {'reveal_mode': 'word'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_line_mode(self):
        """Test apply method with line reveal mode."""
        effect = TypewriterEffect("typewriter", {'reveal_mode': 'line'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip


class TestFadeTransitionEffect:
    """Test cases for FadeTransitionEffect."""
    
    def test_init_with_default_parameters(self):
        """Test initialization with default parameters."""
        effect = FadeTransitionEffect("fade", {})
        
        assert effect.name == "fade"
        assert effect.get_parameter_value('fade_type') == 'both'
        assert effect.get_parameter_value('fade_in_duration') == 0.5
        assert effect.get_parameter_value('fade_out_duration') == 0.5
        assert effect.get_parameter_value('fade_curve') == 'linear'
        assert effect.get_parameter_value('start_opacity') == 0.0
        assert effect.get_parameter_value('end_opacity') == 0.0
        assert effect.get_parameter_value('hold_opacity') == 1.0
    
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        params = {
            'fade_type': 'in',
            'fade_in_duration': 1.0,
            'fade_out_duration': 1.5,
            'fade_curve': 'ease_in_out',
            'start_opacity': 0.2,
            'end_opacity': 0.1,
            'hold_opacity': 0.8
        }
        
        effect = FadeTransitionEffect("fade", params)
        
        assert effect.get_parameter_value('fade_type') == 'in'
        assert effect.get_parameter_value('fade_in_duration') == 1.0
        assert effect.get_parameter_value('fade_out_duration') == 1.5
        assert effect.get_parameter_value('fade_curve') == 'ease_in_out'
        assert effect.get_parameter_value('start_opacity') == 0.2
        assert effect.get_parameter_value('end_opacity') == 0.1
        assert effect.get_parameter_value('hold_opacity') == 0.8
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Test invalid fade duration
        with pytest.raises(EffectError):
            FadeTransitionEffect("fade", {'fade_in_duration': 0.05})
        
        # Test invalid opacity values
        with pytest.raises(EffectError):
            FadeTransitionEffect("fade", {'start_opacity': -0.1})
        
        with pytest.raises(EffectError):
            FadeTransitionEffect("fade", {'hold_opacity': 1.5})
    
    def test_apply_with_empty_subtitle_data(self):
        """Test apply method with empty subtitle data."""
        effect = FadeTransitionEffect("fade", {})
        clip = MockVideoClip()
        subtitle_data = MockSubtitleData([])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_fade_in(self):
        """Test apply method with fade in only."""
        effect = FadeTransitionEffect("fade", {'fade_type': 'in'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_fade_out(self):
        """Test apply method with fade out only."""
        effect = FadeTransitionEffect("fade", {'fade_type': 'out'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_apply_with_both_fades(self):
        """Test apply method with both fade in and out."""
        effect = FadeTransitionEffect("fade", {'fade_type': 'both'})
        clip = MockVideoClip()
        
        line = MockSubtitleLine("Hello world", 0.0, 2.0)
        subtitle_data = MockSubtitleData([line])
        
        result = effect.apply(clip, subtitle_data)
        assert result == clip
    
    def test_get_fade_curve_function(self):
        """Test fade curve function retrieval."""
        effect = FadeTransitionEffect("fade", {})
        
        # Test different curve functions
        linear_func = effect._get_fade_curve_function('linear')
        assert callable(linear_func)
        assert linear_func(0.5) == 0.5
        
        ease_in_func = effect._get_fade_curve_function('ease_in')
        assert callable(ease_in_func)
        
        ease_out_func = effect._get_fade_curve_function('ease_out')
        assert callable(ease_out_func)
        
        ease_in_out_func = effect._get_fade_curve_function('ease_in_out')
        assert callable(ease_in_out_func)
        
        # Test unknown function defaults to linear
        unknown_func = effect._get_fade_curve_function('unknown')
        assert callable(unknown_func)
        assert unknown_func(0.5) == 0.5


class TestAnimationEffectsIntegration:
    """Integration tests for animation effects."""
    
    def test_all_effects_can_be_instantiated(self):
        """Test that all animation effects can be instantiated."""
        effects = [
            KaraokeHighlightEffect("karaoke", {}),
            ScaleBounceEffect("bounce", {}),
            TypewriterEffect("typewriter", {}),
            FadeTransitionEffect("fade", {})
        ]
        
        for effect in effects:
            assert effect is not None
            assert hasattr(effect, 'apply')
            assert hasattr(effect, 'get_parameter_schema')
    
    def test_effects_parameter_schemas(self):
        """Test that all effects provide valid parameter schemas."""
        effects = [
            KaraokeHighlightEffect("karaoke", {}),
            ScaleBounceEffect("bounce", {}),
            TypewriterEffect("typewriter", {}),
            FadeTransitionEffect("fade", {})
        ]
        
        for effect in effects:
            schema = effect.get_parameter_schema()
            assert isinstance(schema, dict)
            assert len(schema) > 0
            
            # Check that each parameter has required fields
            for param_name, param_info in schema.items():
                assert 'type' in param_info
                assert 'description' in param_info
    
    def test_effects_with_complex_subtitle_data(self):
        """Test effects with complex subtitle data."""
        # Create complex subtitle data
        words1 = [
            MockWordTiming("Hello", 0.0, 0.5),
            MockWordTiming("beautiful", 0.5, 1.2),
            MockWordTiming("world", 1.2, 1.8)
        ]
        words2 = [
            MockWordTiming("How", 2.0, 2.3),
            MockWordTiming("are", 2.3, 2.6),
            MockWordTiming("you", 2.6, 3.0)
        ]
        
        lines = [
            MockSubtitleLine("Hello beautiful world", 0.0, 1.8, words1),
            MockSubtitleLine("How are you", 2.0, 3.0, words2)
        ]
        subtitle_data = MockSubtitleData(lines)
        
        effects = [
            KaraokeHighlightEffect("karaoke", {}),
            ScaleBounceEffect("bounce", {}),
            TypewriterEffect("typewriter", {}),
            FadeTransitionEffect("fade", {})
        ]
        
        clip = MockVideoClip()
        
        # Test that all effects can handle complex data
        for effect in effects:
            result = effect.apply(clip, subtitle_data)
            assert result is not None