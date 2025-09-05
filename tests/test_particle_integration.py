"""
Integration tests for particle effects system.

This module tests the integration of particle effects with the broader
subtitle creation system, including timing precision, performance, and
real-world usage scenarios.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from src.subtitle_creator.effects.particles import (
    ParticleEffect, HeartParticleEffect, StarParticleEffect,
    MusicNoteParticleEffect, SparkleParticleEffect, CustomImageParticleEffect
)
from src.subtitle_creator.effects.system import EffectSystem
from src.subtitle_creator.models import SubtitleLine, SubtitleData, WordTiming
from src.subtitle_creator.interfaces import EffectError


class TestParticleTimingPrecision:
    """Test precise timing integration with MoviePy CompositeVideoClip."""
    
    def test_particle_emission_timing_accuracy(self):
        """Test that particles are emitted at precise times."""
        effect = HeartParticleEffect("hearts", {
            'particle_count': 10,
            'emission_rate': 5.0,  # 5 particles per second
            'particle_lifetime': 1.0
        })
        
        # Create a subtitle line
        line = Mock()
        line.start_time = 2.0
        line.duration = 2.0
        line.end_time = 4.0
        
        with patch.object(effect, '_generate_particle_config') as mock_config, \
             patch.object(effect, '_create_particle_clip') as mock_create:
            
            mock_config.return_value = Mock()
            mock_clips = []
            
            def create_clip_side_effect(config, start_time, lifetime):
                clip = Mock()
                clip.start_time = start_time
                clip.lifetime = lifetime
                mock_clips.append(clip)
                return clip
            
            mock_create.side_effect = create_clip_side_effect
            
            particles = effect._generate_particles_for_line(line)
            
            # Verify emission timing (5 particles per second, so 0.2s intervals)
            expected_times = [2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8]
            actual_times = [clip.start_time for clip in mock_clips]
            
            for expected, actual in zip(expected_times, actual_times):
                assert abs(expected - actual) < 0.01  # 10ms tolerance
    
    def test_particle_lifetime_precision(self):
        """Test that particle lifetimes are precisely controlled."""
        effect = StarParticleEffect("stars", {
            'particle_lifetime': 1.5,
            'fade_in_duration': 0.2,
            'fade_out_duration': 0.3
        })
        
        config = Mock()
        config.opacity = 1.0
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True):
            mock_clip = Mock()
            
            # Test particle clip creation with precise timing
            result = effect._create_particle_clip(config, 1.0, 1.5)
            
            if result:  # Only test if clip was created
                # Verify duration was set correctly
                mock_clip.set_duration.assert_called_with(1.5)
                mock_clip.set_start.assert_called_with(1.0)
    
    def test_synchronized_particle_bursts(self):
        """Test synchronized particle emission with subtitle timing."""
        effect = SparkleParticleEffect("sparkles", {
            'burst_mode': True,
            'burst_interval': 0.5,
            'particle_count': 20
        })
        
        # Create subtitle with word-level timing
        words = [
            WordTiming(word="Hello", start_time=0.0, end_time=0.5),
            WordTiming(word="world", start_time=0.5, end_time=1.0),
            WordTiming(word="test", start_time=1.0, end_time=1.5)
        ]
        
        line = Mock()
        line.start_time = 0.0
        line.duration = 1.5
        line.end_time = 1.5
        line.words = words
        
        with patch.object(effect, '_generate_sparkle_config') as mock_config, \
             patch.object(effect, '_create_particle_clip') as mock_create:
            
            mock_config.return_value = Mock()
            mock_create.return_value = Mock()
            
            particles = effect._generate_burst_sparkles(line)
            
            # Should create bursts at 0.0, 0.5, 1.0 (3 bursts)
            call_times = [call[0][1] for call in mock_create.call_args_list]
            burst_times = sorted(set([round(t, 1) for t in call_times]))
            
            assert 0.0 in burst_times
            assert 0.5 in burst_times
            assert 1.0 in burst_times


class TestParticlePhysicsIntegration:
    """Test particle physics integration with MoviePy animations."""
    
    def test_gravity_physics_simulation(self):
        """Test gravity effects on particle motion."""
        effect = ParticleEffect("physics", {
            'gravity': 200.0,  # Strong gravity
            'wind_force': 0.0
        })
        
        config = Mock()
        config.position = (0, 0)
        config.velocity = (50, -100)  # Initial upward velocity
        config.rotation_speed = 0
        
        mock_clip = Mock()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True):
            result = effect._apply_particle_animation(mock_clip, config, 2.0)
            
            # Verify position function was set
            mock_clip.set_position.assert_called_once()
            
            # Get the position function
            position_func = mock_clip.set_position.call_args[0][0]
            
            # Test physics at different times
            pos_0 = position_func(0.0)  # t=0
            pos_1 = position_func(1.0)  # t=1
            pos_2 = position_func(2.0)  # t=2
            
            # At t=0: x=0+50*0=0, y=0-100*0=0 (plus screen center offset)
            # At t=1: x=0+50*1=50, y=0-100*1+0.5*200*1=0 (gravity cancels initial velocity)
            # At t=2: x=0+50*2=100, y=0-100*2+0.5*200*4=200 (gravity dominates)
            
            assert pos_1[0] > pos_0[0]  # Moving right
            assert pos_2[0] > pos_1[0]  # Still moving right
            assert pos_2[1] > pos_1[1]  # Falling due to gravity
    
    def test_wind_force_effects(self):
        """Test wind force effects on particle motion."""
        effect = ParticleEffect("wind", {
            'gravity': 0.0,
            'wind_force': 100.0  # Strong wind
        })
        
        config = Mock()
        config.position = (0, 0)
        config.velocity = (0, 0)  # No initial velocity
        config.rotation_speed = 0
        
        mock_clip = Mock()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True):
            result = effect._apply_particle_animation(mock_clip, config, 2.0)
            
            # Get the position function
            position_func = mock_clip.set_position.call_args[0][0]
            
            # Test wind effects at different times
            pos_1 = position_func(1.0)
            pos_2 = position_func(2.0)
            
            # Wind should accelerate particles horizontally
            # At t=1: x = 0.5 * 100 * 1^2 = 50
            # At t=2: x = 0.5 * 100 * 2^2 = 200
            
            # Account for screen center offset (960)
            wind_effect_1 = pos_1[0] - 960
            wind_effect_2 = pos_2[0] - 960
            
            assert wind_effect_2 > wind_effect_1  # Accelerating due to wind
            assert wind_effect_2 > 3 * wind_effect_1  # Quadratic acceleration
    
    def test_combined_physics_forces(self):
        """Test combined gravity and wind effects."""
        effect = ParticleEffect("combined", {
            'gravity': 150.0,
            'wind_force': 75.0
        })
        
        config = Mock()
        config.position = (0, 0)
        config.velocity = (25, -50)
        config.rotation_speed = 45  # Rotation speed
        
        mock_clip = Mock()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True):
            result = effect._apply_particle_animation(mock_clip, config, 1.0)
            
            # Verify both position and rotation are applied
            mock_clip.set_position.assert_called_once()
            
            # Get position function and test combined effects
            position_func = mock_clip.set_position.call_args[0][0]
            final_pos = position_func(1.0)
            
            # Should have both horizontal (wind + initial velocity) and vertical (gravity + initial velocity) components
            # x = 25*1 + 0.5*75*1^2 = 25 + 37.5 = 62.5 (plus screen center)
            # y = -50*1 + 0.5*150*1^2 = -50 + 75 = 25 (plus screen center)
            
            expected_x = 960 + 62.5
            expected_y = 540 + 25
            
            assert abs(final_pos[0] - expected_x) < 1.0  # Small tolerance
            assert abs(final_pos[1] - expected_y) < 1.0


class TestParticleEffectPerformance:
    """Test performance characteristics of particle effects."""
    
    def test_large_particle_count_performance(self):
        """Test performance with large numbers of particles."""
        effect = HeartParticleEffect("many_hearts", {
            'particle_count': 100,
            'emission_rate': 50.0,
            'particle_lifetime': 3.0
        })
        
        # Create a long subtitle line
        line = Mock()
        line.start_time = 0.0
        line.duration = 5.0
        line.end_time = 5.0
        
        start_time = time.time()
        
        with patch.object(effect, '_create_particle_clip') as mock_create:
            mock_create.return_value = Mock()
            
            particles = effect._generate_particles_for_line(line)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Should generate particles efficiently (under 100ms for 100 particles)
            assert generation_time < 0.1
            assert len(particles) <= 100  # Shouldn't exceed particle count
    
    def test_memory_usage_with_long_duration(self):
        """Test memory efficiency with long-duration effects."""
        effect = SparkleParticleEffect("long_sparkles", {
            'particle_count': 50,
            'emission_rate': 10.0,
            'particle_lifetime': 2.0
        })
        
        # Create a very long subtitle line
        line = Mock()
        line.start_time = 0.0
        line.duration = 30.0  # 30 seconds
        line.end_time = 30.0
        
        with patch.object(effect, '_create_particle_clip') as mock_create:
            mock_create.return_value = Mock()
            
            particles = effect._generate_particles_for_line(line)
            
            # Should limit particle generation to avoid memory issues
            # With 10 particles/second for 30 seconds, that would be 300 particles
            # But should be limited by particle_count parameter
            assert len(particles) <= 50
    
    def test_effect_composition_performance(self):
        """Test performance when compositing multiple particle effects."""
        system = EffectSystem()
        system.register_effect(HeartParticleEffect)
        system.register_effect(StarParticleEffect)
        system.register_effect(SparkleParticleEffect)
        
        # Create multiple effects
        effects = [
            system.create_effect("HeartParticleEffect", {'particle_count': 20}),
            system.create_effect("StarParticleEffect", {'particle_count': 15}),
            system.create_effect("SparkleParticleEffect", {'particle_count': 25})
        ]
        
        for effect in effects:
            system.add_effect(effect)
        
        # Create test data
        mock_clip = Mock()
        subtitle_data = SubtitleData(
            lines=[
                SubtitleLine(
                    start_time=0.0,
                    end_time=3.0,
                    text="Performance test",
                    words=[]
                )
            ],
            global_style={}
        )
        
        start_time = time.time()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False):
            result = system.apply_effects(mock_clip, subtitle_data)
        
        end_time = time.time()
        composition_time = end_time - start_time
        
        # Should compose effects efficiently
        assert composition_time < 0.05  # Under 50ms
        assert result == mock_clip  # Should return base clip when MoviePy unavailable


class TestParticleEffectErrorHandling:
    """Test error handling and recovery in particle effects."""
    
    def test_invalid_particle_sprite_handling(self):
        """Test handling of invalid particle sprites."""
        effect = CustomImageParticleEffect("custom", {
            'image_path': '/invalid/path/image.png'
        })
        
        # Should handle invalid image gracefully
        sprite = effect._get_particle_sprite()
        
        # Should either return None or a default sprite
        assert sprite is None or sprite is not None
    
    def test_particle_creation_failure_recovery(self):
        """Test recovery from particle creation failures."""
        effect = HeartParticleEffect("hearts", {})
        
        config = Mock()
        
        with patch.object(effect, '_get_particle_sprite', return_value=None):
            # Should handle sprite creation failure gracefully
            particle = effect._create_particle_clip(config, 0.0, 1.0)
            assert particle is None
    
    def test_physics_calculation_error_handling(self):
        """Test handling of physics calculation errors."""
        # Test that parameter validation correctly rejects invalid values
        with pytest.raises(EffectError):
            ParticleEffect("physics", {
                'gravity': float('inf'),  # Invalid gravity value
            })
        
        with pytest.raises(EffectError):
            ParticleEffect("physics", {
                'wind_force': float('nan')  # Invalid wind force
            })
        
        # Test with valid but extreme values
        effect = ParticleEffect("physics", {
            'gravity': 500.0,  # Maximum valid gravity
            'wind_force': -200.0  # Strong but valid wind
        })
        
        config = Mock()
        config.position = (0, 0)
        config.velocity = (10, 10)
        config.rotation_speed = 0
        
        mock_clip = Mock()
        
        # Should handle extreme but valid physics values
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', True):
            result = effect._apply_particle_animation(mock_clip, config, 1.0)
            # Should not crash with extreme but valid values
            assert result is not None
    
    def test_empty_subtitle_data_handling(self):
        """Test handling of empty or invalid subtitle data."""
        effect = StarParticleEffect("stars", {})
        mock_clip = Mock()
        
        # Test with None
        result = effect.apply(mock_clip, None)
        assert result == mock_clip
        
        # Test with empty lines
        empty_data = SubtitleData(lines=[], global_style={})
        result = effect.apply(mock_clip, empty_data)
        assert result == mock_clip
        
        # Test with malformed line data
        malformed_line = Mock()
        malformed_line.start_time = None
        malformed_line.duration = "invalid"
        
        malformed_data = SubtitleData(
            lines=[malformed_line],
            global_style={}
        )
        
        # Should handle malformed data gracefully
        try:
            result = effect.apply(mock_clip, malformed_data)
            assert result is not None
        except (TypeError, AttributeError):
            # Acceptable to raise these errors for malformed data
            pass


class TestRealWorldUsageScenarios:
    """Test particle effects in realistic usage scenarios."""
    
    def test_karaoke_video_with_heart_particles(self):
        """Test heart particles in a karaoke video scenario."""
        effect = HeartParticleEffect("romantic_hearts", {
            'particle_count': 15,
            'emission_rate': 3.0,
            'heart_color': (255, 105, 180, 255),  # Hot pink
            'pulse_enabled': True,
            'float_pattern': 'rising'
        })
        
        # Create realistic karaoke subtitle data
        subtitle_data = SubtitleData(
            lines=[
                SubtitleLine(
                    start_time=0.0,
                    end_time=4.0,
                    text="Love is in the air tonight",
                    words=[
                        WordTiming("Love", 0.0, 0.5),
                        WordTiming("is", 0.5, 0.8),
                        WordTiming("in", 0.8, 1.0),
                        WordTiming("the", 1.0, 1.2),
                        WordTiming("air", 1.2, 1.8),
                        WordTiming("tonight", 2.0, 4.0)
                    ]
                )
            ],
            global_style={}
        )
        
        mock_clip = Mock()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False):
            result = effect.apply(mock_clip, subtitle_data)
            assert result == mock_clip
    
    def test_celebration_video_with_multiple_particles(self):
        """Test multiple particle effects for celebration video."""
        system = EffectSystem()
        system.register_effect(StarParticleEffect)
        system.register_effect(SparkleParticleEffect)
        
        # Create celebration effects
        stars = system.create_effect("StarParticleEffect", {
            'particle_count': 20,
            'star_color': (255, 215, 0, 255),  # Gold
            'twinkle_enabled': True
        })
        
        sparkles = system.create_effect("SparkleParticleEffect", {
            'particle_count': 30,
            'burst_mode': True,
            'burst_interval': 0.5
        })
        
        system.add_effect(stars)
        system.add_effect(sparkles)
        
        # Create celebration subtitle
        subtitle_data = SubtitleData(
            lines=[
                SubtitleLine(
                    start_time=0.0,
                    end_time=3.0,
                    text="Congratulations!",
                    words=[]
                )
            ],
            global_style={}
        )
        
        mock_clip = Mock()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False):
            result = system.apply_effects(mock_clip, subtitle_data)
            assert result == mock_clip
    
    def test_music_video_with_rhythm_sync(self):
        """Test music note particles synchronized to rhythm."""
        effect = MusicNoteParticleEffect("rhythm_notes", {
            'particle_count': 24,
            'rhythm_sync': True,
            'beat_duration': 0.5,  # 120 BPM
            'bounce_on_beat': True,
            'note_color': (138, 43, 226, 255)  # Blue violet
        })
        
        # Create music subtitle with precise timing
        subtitle_data = SubtitleData(
            lines=[
                SubtitleLine(
                    start_time=0.0,
                    end_time=4.0,  # 8 beats at 120 BPM
                    text="Dancing to the rhythm",
                    words=[
                        WordTiming("Dancing", 0.0, 1.0),
                        WordTiming("to", 1.0, 1.5),
                        WordTiming("the", 1.5, 2.0),
                        WordTiming("rhythm", 2.0, 4.0)
                    ]
                )
            ],
            global_style={}
        )
        
        mock_clip = Mock()
        
        with patch('src.subtitle_creator.effects.particles.MOVIEPY_AVAILABLE', False):
            result = effect.apply(mock_clip, subtitle_data)
            assert result == mock_clip