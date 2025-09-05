#!/usr/bin/env python3
"""
Animation Effects Demo

This script demonstrates the usage of the four concrete animation effects:
- KaraokeHighlightEffect: Word-by-word color highlighting
- ScaleBounceEffect: Bouncy scaling animations
- TypewriterEffect: Character/word reveal animations
- FadeTransitionEffect: Smooth fade in/out transitions

Run this script to see how the animation effects can be configured and used.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from subtitle_creator.effects.animation import (
    KaraokeHighlightEffect, ScaleBounceEffect, TypewriterEffect, FadeTransitionEffect
)
from subtitle_creator.effects.system import EffectSystem


def create_sample_subtitle_data():
    """Create sample subtitle data for demonstration."""
    from dataclasses import dataclass
    from typing import List, Optional
    
    @dataclass
    class WordTiming:
        word: str
        start_time: float
        end_time: float
    
    @dataclass
    class SubtitleLine:
        text: str
        start_time: float
        end_time: float
        words: Optional[List[WordTiming]] = None
        
        @property
        def duration(self) -> float:
            return self.end_time - self.start_time
    
    @dataclass
    class SubtitleData:
        lines: List[SubtitleLine]
    
    # Create sample data with word-level timing
    words1 = [
        WordTiming("Hello", 0.0, 0.5),
        WordTiming("beautiful", 0.5, 1.2),
        WordTiming("world", 1.2, 1.8)
    ]
    
    words2 = [
        WordTiming("How", 2.0, 2.3),
        WordTiming("are", 2.3, 2.6),
        WordTiming("you", 2.6, 3.0),
        WordTiming("today?", 3.0, 3.5)
    ]
    
    lines = [
        SubtitleLine("Hello beautiful world", 0.0, 1.8, words1),
        SubtitleLine("How are you today?", 2.0, 3.5, words2),
        SubtitleLine("This is a demo!", 4.0, 5.5)
    ]
    
    return SubtitleData(lines)


def demo_karaoke_highlight_effect():
    """Demonstrate the KaraokeHighlightEffect."""
    print("=== KaraokeHighlightEffect Demo ===")
    
    # Create effect with custom parameters
    effect = KaraokeHighlightEffect("karaoke_demo", {
        'default_color': (255, 255, 255, 255),  # White
        'highlight_color': (255, 255, 0, 255),  # Yellow
        'transition_duration': 0.15,
        'highlight_mode': 'word',
        'glow_enabled': True,
        'glow_intensity': 0.7
    })
    
    print(f"Effect name: {effect.name}")
    print(f"Default color: {effect.get_parameter_value('default_color')}")
    print(f"Highlight color: {effect.get_parameter_value('highlight_color')}")
    print(f"Transition duration: {effect.get_parameter_value('transition_duration')}s")
    print(f"Highlight mode: {effect.get_parameter_value('highlight_mode')}")
    print(f"Glow enabled: {effect.get_parameter_value('glow_enabled')}")
    
    # Show parameter schema
    schema = effect.get_parameter_schema()
    print(f"Available parameters: {list(schema.keys())}")
    print()


def demo_scale_bounce_effect():
    """Demonstrate the ScaleBounceEffect."""
    print("=== ScaleBounceEffect Demo ===")
    
    # Create effect with custom parameters
    effect = ScaleBounceEffect("bounce_demo", {
        'bounce_scale': 1.4,
        'bounce_duration': 0.8,
        'bounce_count': 3,
        'trigger_mode': 'entrance',
        'easing_function': 'bounce',
        'scale_origin': 'center'
    })
    
    print(f"Effect name: {effect.name}")
    print(f"Bounce scale: {effect.get_parameter_value('bounce_scale')}x")
    print(f"Bounce duration: {effect.get_parameter_value('bounce_duration')}s")
    print(f"Bounce count: {effect.get_parameter_value('bounce_count')}")
    print(f"Trigger mode: {effect.get_parameter_value('trigger_mode')}")
    print(f"Easing function: {effect.get_parameter_value('easing_function')}")
    
    # Test different easing functions
    easing_functions = ['bounce', 'cubic', 'sine', 'linear']
    print(f"Available easing functions: {easing_functions}")
    print()


def demo_typewriter_effect():
    """Demonstrate the TypewriterEffect."""
    print("=== TypewriterEffect Demo ===")
    
    # Create effect with custom parameters
    effect = TypewriterEffect("typewriter_demo", {
        'reveal_mode': 'character',
        'reveal_speed': 0.08,
        'cursor_enabled': True,
        'cursor_character': '|',
        'cursor_blink_rate': 0.6,
        'sound_enabled': False,
        'start_delay': 0.2
    })
    
    print(f"Effect name: {effect.name}")
    print(f"Reveal mode: {effect.get_parameter_value('reveal_mode')}")
    print(f"Reveal speed: {effect.get_parameter_value('reveal_speed')}s per character")
    print(f"Cursor enabled: {effect.get_parameter_value('cursor_enabled')}")
    print(f"Cursor character: '{effect.get_parameter_value('cursor_character')}'")
    print(f"Start delay: {effect.get_parameter_value('start_delay')}s")
    
    # Show different reveal modes
    reveal_modes = ['character', 'word', 'line']
    print(f"Available reveal modes: {reveal_modes}")
    print()


def demo_fade_transition_effect():
    """Demonstrate the FadeTransitionEffect."""
    print("=== FadeTransitionEffect Demo ===")
    
    # Create effect with custom parameters
    effect = FadeTransitionEffect("fade_demo", {
        'fade_type': 'both',
        'fade_in_duration': 0.7,
        'fade_out_duration': 0.5,
        'fade_curve': 'ease_in_out',
        'start_opacity': 0.0,
        'end_opacity': 0.0,
        'hold_opacity': 1.0
    })
    
    print(f"Effect name: {effect.name}")
    print(f"Fade type: {effect.get_parameter_value('fade_type')}")
    print(f"Fade in duration: {effect.get_parameter_value('fade_in_duration')}s")
    print(f"Fade out duration: {effect.get_parameter_value('fade_out_duration')}s")
    print(f"Fade curve: {effect.get_parameter_value('fade_curve')}")
    print(f"Hold opacity: {effect.get_parameter_value('hold_opacity')}")
    
    # Show different fade types and curves
    fade_types = ['in', 'out', 'both']
    fade_curves = ['linear', 'ease_in', 'ease_out', 'ease_in_out']
    print(f"Available fade types: {fade_types}")
    print(f"Available fade curves: {fade_curves}")
    print()


def demo_effects_system_integration():
    """Demonstrate using animation effects with the EffectSystem."""
    print("=== EffectSystem Integration Demo ===")
    
    # Create effects system
    system = EffectSystem()
    
    # Register all animation effects
    system.register_effect(KaraokeHighlightEffect)
    system.register_effect(ScaleBounceEffect)
    system.register_effect(TypewriterEffect)
    system.register_effect(FadeTransitionEffect)
    
    print(f"Registered effects: {list(system.get_registered_effects().keys())}")
    
    # Create effects through the system
    karaoke = system.create_effect('KaraokeHighlightEffect', {
        'highlight_color': (255, 100, 100, 255)  # Light red
    })
    
    fade = system.create_effect('FadeTransitionEffect', {
        'fade_type': 'in',
        'fade_in_duration': 1.0
    })
    
    # Add effects to system
    system.add_effect(karaoke)
    system.add_effect(fade)
    
    print(f"Active effects: {len(system.get_active_effects())}")
    
    # Save as preset
    preset_name = "demo_animation_preset"
    system.save_preset(preset_name, "Demo preset with karaoke and fade effects")
    print(f"Saved preset: {preset_name}")
    
    # List available presets
    presets = system.list_presets()
    print(f"Available presets: {presets}")
    
    # Get preset info
    if preset_name in presets:
        preset_info = system.get_preset_info(preset_name)
        print(f"Preset info: {preset_info}")
    
    print()


def demo_parameter_validation():
    """Demonstrate parameter validation in animation effects."""
    print("=== Parameter Validation Demo ===")
    
    try:
        # This should work fine
        effect1 = KaraokeHighlightEffect("valid", {
            'highlight_color': (255, 0, 0, 255),
            'transition_duration': 0.2
        })
        print("✓ Valid parameters accepted")
        
        # This should raise an error - invalid color
        try:
            effect2 = KaraokeHighlightEffect("invalid_color", {
                'highlight_color': (300, 0, 0, 255)  # Invalid: > 255
            })
        except Exception as e:
            print(f"✓ Invalid color rejected: {type(e).__name__}")
        
        # This should raise an error - invalid duration
        try:
            effect3 = ScaleBounceEffect("invalid_duration", {
                'bounce_duration': -0.5  # Invalid: negative
            })
        except Exception as e:
            print(f"✓ Invalid duration rejected: {type(e).__name__}")
        
        # This should raise an error - invalid reveal speed
        try:
            effect4 = TypewriterEffect("invalid_speed", {
                'reveal_speed': 0.005  # Invalid: too small
            })
        except Exception as e:
            print(f"✓ Invalid reveal speed rejected: {type(e).__name__}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print()


def main():
    """Run all animation effects demonstrations."""
    print("Animation Effects Demonstration")
    print("=" * 50)
    print()
    
    # Demo each effect individually
    demo_karaoke_highlight_effect()
    demo_scale_bounce_effect()
    demo_typewriter_effect()
    demo_fade_transition_effect()
    
    # Demo system integration
    demo_effects_system_integration()
    
    # Demo parameter validation
    demo_parameter_validation()
    
    print("Demo completed successfully!")
    print()
    print("Note: This demo shows the effect configuration and parameter handling.")
    print("In a real application with MoviePy installed, these effects would")
    print("generate actual video clips with the specified animations.")


if __name__ == "__main__":
    main()