"""
Simple test to verify effects system functionality.
"""

import pytest
from src.subtitle_creator.effects.system import EffectSystem


def test_effect_system_creation():
    """Test that EffectSystem can be created."""
    system = EffectSystem()
    assert system is not None
    assert len(system._registered_effects) == 0
    assert len(system._active_effects) == 0


def test_effect_system_with_text_styling_effects():
    """Test that text styling effects can be registered."""
    from src.subtitle_creator.effects.text_styling import TypographyEffect
    
    system = EffectSystem()
    system.register_effect(TypographyEffect)
    
    assert 'TypographyEffect' in system._registered_effects
    
    # Create an effect instance
    effect = system.create_effect('TypographyEffect', {'font_size': 60})
    assert effect.get_parameter_value('font_size') == 60
    
    # Add to active effects
    system.add_effect(effect)
    assert len(system._active_effects) == 1