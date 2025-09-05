"""
Effects package for Subtitle Creator with Effects.

This package provides the effect system and concrete effect implementations
for creating stylized subtitle videos with MoviePy.
"""

from .base import BaseEffect, EffectParameter
from .system import EffectSystem, EffectPreset, CompositionLayer
from .text_styling import TypographyEffect, PositioningEffect, BackgroundEffect, TransitionEffect
from .animation import KaraokeHighlightEffect, ScaleBounceEffect, TypewriterEffect, FadeTransitionEffect
from .particles import (
    ParticleEffect, HeartParticleEffect, StarParticleEffect,
    MusicNoteParticleEffect, SparkleParticleEffect, CustomImageParticleEffect,
    ParticleConfig
)

__all__ = [
    'BaseEffect',
    'EffectParameter', 
    'EffectSystem',
    'EffectPreset',
    'CompositionLayer',
    'TypographyEffect',
    'PositioningEffect', 
    'BackgroundEffect',
    'TransitionEffect',
    'KaraokeHighlightEffect',
    'ScaleBounceEffect',
    'TypewriterEffect',
    'FadeTransitionEffect',
    'ParticleEffect',
    'HeartParticleEffect',
    'StarParticleEffect',
    'MusicNoteParticleEffect',
    'SparkleParticleEffect',
    'CustomImageParticleEffect',
    'ParticleConfig'
]