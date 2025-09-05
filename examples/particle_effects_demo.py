#!/usr/bin/env python3
"""
Particle Effects Demo

This script demonstrates the particle effects system for the Subtitle Creator
with Effects application. It shows how to create and configure different types
of particle effects including hearts, stars, music notes, and sparkles.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from subtitle_creator.effects.particles import (
    HeartParticleEffect, StarParticleEffect, MusicNoteParticleEffect,
    SparkleParticleEffect, CustomImageParticleEffect
)
from subtitle_creator.effects.system import EffectSystem
from subtitle_creator.models import SubtitleLine, SubtitleData, WordTiming


def create_sample_subtitle_data():
    """Create sample subtitle data for demonstration."""
    return SubtitleData(
        lines=[
            SubtitleLine(
                start_time=0.0,
                end_time=4.0,
                text="Love is in the air tonight",
                words=[
                    WordTiming("Love", 0.0, 0.8),
                    WordTiming("is", 0.8, 1.0),
                    WordTiming("in", 1.0, 1.3),
                    WordTiming("the", 1.3, 1.5),
                    WordTiming("air", 1.5, 2.2),
                    WordTiming("tonight", 2.5, 4.0)
                ]
            ),
            SubtitleLine(
                start_time=4.5,
                end_time=7.0,
                text="Stars are shining bright",
                words=[
                    WordTiming("Stars", 4.5, 5.0),
                    WordTiming("are", 5.0, 5.2),
                    WordTiming("shining", 5.2, 6.0),
                    WordTiming("bright", 6.0, 7.0)
                ]
            ),
            SubtitleLine(
                start_time=7.5,
                end_time=10.0,
                text="Music fills the soul",
                words=[
                    WordTiming("Music", 7.5, 8.2),
                    WordTiming("fills", 8.2, 8.7),
                    WordTiming("the", 8.7, 8.9),
                    WordTiming("soul", 8.9, 10.0)
                ]
            )
        ],
        global_style={}
    )


def demo_heart_particles():
    """Demonstrate heart particle effects."""
    print("=== Heart Particle Effect Demo ===")
    
    # Create heart effect with romantic settings
    heart_effect = HeartParticleEffect("romantic_hearts", {
        'particle_count': 15,
        'emission_rate': 3.0,
        'particle_lifetime': 2.5,
        'heart_color': (255, 105, 180, 255),  # Hot pink
        'heart_size': 28,
        'pulse_enabled': True,
        'pulse_rate': 1.2,
        'float_pattern': 'rising',
        'gravity': -50.0,  # Slight upward float
        'wind_force': 20.0  # Gentle drift
    })
    
    print(f"Effect Name: {heart_effect.name}")
    print(f"Heart Color: {heart_effect.get_parameter_value('heart_color')}")
    print(f"Particle Count: {heart_effect.get_parameter_value('particle_count')}")
    print(f"Pulse Enabled: {heart_effect.get_parameter_value('pulse_enabled')}")
    print(f"Float Pattern: {heart_effect.get_parameter_value('float_pattern')}")
    
    # Test parameter schema
    schema = heart_effect.get_parameter_schema()
    print(f"Available Parameters: {list(schema.keys())}")
    
    print("✓ Heart particle effect created successfully\n")


def demo_star_particles():
    """Demonstrate star particle effects."""
    print("=== Star Particle Effect Demo ===")
    
    # Create star effect with magical settings
    star_effect = StarParticleEffect("magical_stars", {
        'particle_count': 25,
        'emission_rate': 8.0,
        'particle_lifetime': 3.0,
        'star_color': (255, 215, 0, 255),  # Gold
        'star_points': 5,
        'twinkle_enabled': True,
        'twinkle_rate': 3.0,
        'trail_enabled': True,
        'velocity_range': (80, 120),
        'size_range': (0.8, 1.5)
    })
    
    print(f"Effect Name: {star_effect.name}")
    print(f"Star Color: {star_effect.get_parameter_value('star_color')}")
    print(f"Star Points: {star_effect.get_parameter_value('star_points')}")
    print(f"Twinkle Rate: {star_effect.get_parameter_value('twinkle_rate')}")
    print(f"Trail Enabled: {star_effect.get_parameter_value('trail_enabled')}")
    
    print("✓ Star particle effect created successfully\n")


def demo_music_note_particles():
    """Demonstrate music note particle effects."""
    print("=== Music Note Particle Effect Demo ===")
    
    # Create music note effect with rhythm sync
    note_effect = MusicNoteParticleEffect("rhythm_notes", {
        'particle_count': 20,
        'emission_rate': 4.0,
        'particle_lifetime': 2.0,
        'note_color': (138, 43, 226, 255),  # Blue violet
        'note_type': 'eighth',
        'rhythm_sync': True,
        'beat_duration': 0.5,  # 120 BPM
        'bounce_on_beat': True,
        'staff_lines': False,
        'gravity': 30.0  # Gentle fall
    })
    
    print(f"Effect Name: {note_effect.name}")
    print(f"Note Color: {note_effect.get_parameter_value('note_color')}")
    print(f"Note Type: {note_effect.get_parameter_value('note_type')}")
    print(f"Rhythm Sync: {note_effect.get_parameter_value('rhythm_sync')}")
    print(f"Beat Duration: {note_effect.get_parameter_value('beat_duration')}")
    print(f"Bounce on Beat: {note_effect.get_parameter_value('bounce_on_beat')}")
    
    print("✓ Music note particle effect created successfully\n")


def demo_sparkle_particles():
    """Demonstrate sparkle particle effects."""
    print("=== Sparkle Particle Effect Demo ===")
    
    # Create sparkle effect with burst mode
    sparkle_effect = SparkleParticleEffect("celebration_sparkles", {
        'particle_count': 40,
        'emission_rate': 20.0,
        'particle_lifetime': 1.5,
        'sparkle_size_variation': 1.2,
        'flash_duration': 0.08,
        'burst_mode': True,
        'burst_interval': 0.8,
        'radial_spread': True,
        'velocity_range': (100, 200),
        'fade_in_duration': 0.1,
        'fade_out_duration': 0.4
    })
    
    print(f"Effect Name: {sparkle_effect.name}")
    print(f"Burst Mode: {sparkle_effect.get_parameter_value('burst_mode')}")
    print(f"Burst Interval: {sparkle_effect.get_parameter_value('burst_interval')}")
    print(f"Flash Duration: {sparkle_effect.get_parameter_value('flash_duration')}")
    print(f"Radial Spread: {sparkle_effect.get_parameter_value('radial_spread')}")
    
    print("✓ Sparkle particle effect created successfully\n")


def demo_custom_image_particles():
    """Demonstrate custom image particle effects."""
    print("=== Custom Image Particle Effect Demo ===")
    
    # Create custom image effect
    custom_effect = CustomImageParticleEffect("custom_particles", {
        'particle_count': 12,
        'emission_rate': 6.0,
        'particle_lifetime': 3.0,
        'image_path': 'assets/particles/heart.svg',
        'image_scale': 1.5,
        'color_tint': (255, 255, 255, 255),  # No tint
        'preserve_aspect': True,
        'random_flip': True,
        'blend_mode': 'normal',
        'velocity_range': (60, 100),
        'gravity': -20.0  # Float upward
    })
    
    print(f"Effect Name: {custom_effect.name}")
    print(f"Image Path: {custom_effect.get_parameter_value('image_path')}")
    print(f"Image Scale: {custom_effect.get_parameter_value('image_scale')}")
    print(f"Preserve Aspect: {custom_effect.get_parameter_value('preserve_aspect')}")
    print(f"Random Flip: {custom_effect.get_parameter_value('random_flip')}")
    
    # Test image validation
    valid_formats = custom_effect.get_supported_formats()
    print(f"Supported Formats: {valid_formats}")
    
    # Test path validation
    is_valid = custom_effect.validate_image_path('assets/particles/heart.svg')
    print(f"Image Path Valid: {is_valid}")
    
    print("✓ Custom image particle effect created successfully\n")


def demo_effect_system_integration():
    """Demonstrate particle effects integration with the effect system."""
    print("=== Effect System Integration Demo ===")
    
    # Create effect system
    system = EffectSystem()
    
    # Register particle effects
    system.register_effect(HeartParticleEffect)
    system.register_effect(StarParticleEffect)
    system.register_effect(SparkleParticleEffect)
    
    print("Registered Effects:")
    for effect_name in system.get_registered_effects().keys():
        print(f"  - {effect_name}")
    
    # Create and add effects
    hearts = system.create_effect("HeartParticleEffect", {
        'particle_count': 10,
        'heart_color': (255, 20, 147, 255)
    })
    
    stars = system.create_effect("StarParticleEffect", {
        'particle_count': 15,
        'twinkle_enabled': True
    })
    
    sparkles = system.create_effect("SparkleParticleEffect", {
        'particle_count': 20,
        'burst_mode': True
    })
    
    system.add_effect(hearts)
    system.add_effect(stars)
    system.add_effect(sparkles)
    
    print(f"\nActive Effects: {len(system.get_active_effects())}")
    
    # Test effect validation
    is_valid, issues = system.validate_effect_stack()
    print(f"Effect Stack Valid: {is_valid}")
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Save as preset
    try:
        system.save_preset("celebration_combo", "Hearts, stars, and sparkles for celebrations")
        print("✓ Preset saved successfully")
    except Exception as e:
        print(f"Preset save failed: {e}")
    
    # List presets
    presets = system.list_presets()
    print(f"Available Presets: {presets}")
    
    print("✓ Effect system integration completed successfully\n")


def demo_particle_physics():
    """Demonstrate particle physics simulation."""
    print("=== Particle Physics Demo ===")
    
    # Create effect with complex physics
    physics_effect = HeartParticleEffect("physics_hearts", {
        'particle_count': 8,
        'emission_rate': 2.0,
        'particle_lifetime': 4.0,
        'gravity': 80.0,  # Moderate gravity
        'wind_force': -30.0,  # Left wind
        'velocity_range': (120, 180),
        'emission_area': (150, 100)
    })
    
    print("Physics Parameters:")
    print(f"  Gravity: {physics_effect.get_parameter_value('gravity')} px/s²")
    print(f"  Wind Force: {physics_effect.get_parameter_value('wind_force')} px/s²")
    print(f"  Velocity Range: {physics_effect.get_parameter_value('velocity_range')} px/s")
    print(f"  Emission Area: {physics_effect.get_parameter_value('emission_area')} px")
    
    # Generate sample particle configuration
    config = physics_effect._generate_particle_config()
    print(f"\nSample Particle:")
    print(f"  Position: ({config.position[0]:.1f}, {config.position[1]:.1f})")
    print(f"  Velocity: ({config.velocity[0]:.1f}, {config.velocity[1]:.1f})")
    print(f"  Size: {config.size:.2f}")
    print(f"  Rotation: {config.rotation:.1f}°")
    print(f"  Lifetime: {config.lifetime:.1f}s")
    
    print("✓ Particle physics demonstration completed\n")


def main():
    """Run all particle effect demonstrations."""
    print("Particle Effects System Demo")
    print("=" * 50)
    print()
    
    try:
        # Run individual effect demos
        demo_heart_particles()
        demo_star_particles()
        demo_music_note_particles()
        demo_sparkle_particles()
        demo_custom_image_particles()
        
        # Run integration demos
        demo_effect_system_integration()
        demo_particle_physics()
        
        # Test with sample subtitle data
        print("=== Subtitle Integration Test ===")
        subtitle_data = create_sample_subtitle_data()
        
        heart_effect = HeartParticleEffect("test_hearts", {
            'particle_count': 5,
            'emission_rate': 2.0
        })
        
        # Mock clip for testing
        class MockClip:
            def __init__(self):
                self.duration = 10.0
                self.size = (1920, 1080)
        
        mock_clip = MockClip()
        
        # Apply effect (will return original clip when MoviePy not available)
        result = heart_effect.apply(mock_clip, subtitle_data)
        print(f"Effect applied to {len(subtitle_data.lines)} subtitle lines")
        print("✓ Subtitle integration test completed")
        
        print("\n" + "=" * 50)
        print("All particle effect demonstrations completed successfully!")
        print("The particle effects system is ready for use.")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())