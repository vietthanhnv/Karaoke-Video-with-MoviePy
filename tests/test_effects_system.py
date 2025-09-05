"""
Unit tests for the EffectSystem class.

Tests effect system functionality including effect registration, composition,
preset management, and clip manipulation.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.subtitle_creator.effects.system import (
    EffectSystem, EffectPreset, CompositionLayer
)
from src.subtitle_creator.effects.base import BaseEffect, EffectParameter
from src.subtitle_creator.interfaces import EffectError, SubtitleData, SubtitleLine, WordTiming


class MockEffect(BaseEffect):
    """Mock effect for testing."""
    
    def _define_parameters(self):
        return {
            'intensity': EffectParameter(
                name='intensity',
                value=1.0,
                param_type='float',
                min_value=0.0,
                max_value=2.0,
                default_value=1.0,
                description='Effect intensity'
            )
        }
    
    def apply(self, clip, subtitle_data):
        """Mock apply method that returns a modified mock clip."""
        mock_result = Mock()
        mock_result.duration = clip.duration
        mock_result.size = getattr(clip, 'size', (1920, 1080))
        mock_result.effect_applied = self.name
        return mock_result


class AnotherMockEffect(BaseEffect):
    """Another mock effect for testing multiple effects."""
    
    def _define_parameters(self):
        return {
            'strength': EffectParameter(
                name='strength',
                value=0.5,
                param_type='float',
                min_value=0.0,
                max_value=1.0,
                default_value=0.5,
                description='Effect strength'
            )
        }
    
    def apply(self, clip, subtitle_data):
        """Mock apply method."""
        mock_result = Mock()
        mock_result.duration = clip.duration
        mock_result.size = getattr(clip, 'size', (1920, 1080))
        mock_result.effect_applied = self.name
        return mock_result


class TestEffectSystem:
    """Test cases for EffectSystem class."""
    
    def test_effect_system_initialization(self):
        """Test EffectSystem initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = EffectSystem(Path(temp_dir))
            
            assert system.preset_directory == Path(temp_dir)
            assert len(system._registered_effects) == 0
            assert len(system._active_effects) == 0
    
    def test_register_effect(self):
        """Test effect registration."""
        system = EffectSystem()
        
        system.register_effect(MockEffect)
        
        assert 'MockEffect' in system._registered_effects
        assert system._registered_effects['MockEffect'] == MockEffect
    
    def test_register_invalid_effect(self):
        """Test registering invalid effect class."""
        system = EffectSystem()
        
        class InvalidEffect:
            pass
        
        with pytest.raises(EffectError):
            system.register_effect(InvalidEffect)
    
    def test_create_effect(self):
        """Test effect creation."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        
        effect = system.create_effect('MockEffect', {'intensity': 1.5})
        
        assert isinstance(effect, MockEffect)
        assert effect.get_parameter_value('intensity') == 1.5
    
    def test_create_unregistered_effect(self):
        """Test creating unregistered effect."""
        system = EffectSystem()
        
        with pytest.raises(EffectError):
            system.create_effect('UnknownEffect', {})
    
    def test_add_effect(self):
        """Test adding effect to active effects."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        
        effect = system.create_effect('MockEffect', {})
        system.add_effect(effect)
        
        assert len(system._active_effects) == 1
        assert effect in system._active_effects
    
    def test_remove_effect(self):
        """Test removing effect from active effects."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        
        effect = system.create_effect('MockEffect', {})
        system.add_effect(effect)
        system.remove_effect(effect)
        
        assert len(system._active_effects) == 0
        assert effect not in system._active_effects
    
    def test_clear_effects(self):
        """Test clearing all effects."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        
        effect1 = system.create_effect('MockEffect', {'intensity': 1.0})
        effect2 = system.create_effect('MockEffect', {'intensity': 2.0})
        
        system.add_effect(effect1)
        system.add_effect(effect2)
        
        assert len(system._active_effects) == 2
        
        system.clear_effects()
        
        assert len(system._active_effects) == 0
    
    def test_apply_effects_empty(self):
        """Test applying effects with no active effects."""
        system = EffectSystem()
        mock_clip = Mock()
        mock_clip.duration = 5.0
        
        subtitle_data = SubtitleData()
        
        result = system.apply_effects(mock_clip, subtitle_data)
        
        assert result == mock_clip
    
    def test_apply_effects_single(self):
        """Test applying single effect."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        
        effect = system.create_effect('MockEffect', {})
        system.add_effect(effect)
        
        mock_clip = Mock()
        mock_clip.duration = 5.0
        mock_clip.size = (1920, 1080)
        
        subtitle_data = SubtitleData()
        
        result = system.apply_effects(mock_clip, subtitle_data)
        
        # Should return the original clip in test environment (no MoviePy)
        assert result == mock_clip
    
    def test_apply_effects_multiple(self):
        """Test applying multiple effects."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        system.register_effect(AnotherMockEffect)
        
        effect1 = system.create_effect('MockEffect', {})
        effect2 = system.create_effect('AnotherMockEffect', {})
        
        system.add_effect(effect1)
        system.add_effect(effect2)
        
        mock_clip = Mock()
        mock_clip.duration = 5.0
        mock_clip.size = (1920, 1080)
        
        subtitle_data = SubtitleData()
        
        result = system.apply_effects(mock_clip, subtitle_data)
        
        # Should return the original clip in test environment
        assert result == mock_clip
    
    def test_save_preset(self):
        """Test saving effect preset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = EffectSystem(Path(temp_dir))
            system.register_effect(MockEffect)
            
            effect = system.create_effect('MockEffect', {'intensity': 1.5})
            system.add_effect(effect)
            
            system.save_preset('test_preset', 'Test description')
            
            preset_file = Path(temp_dir) / 'test_preset.json'
            assert preset_file.exists()
            
            with open(preset_file, 'r') as f:
                data = json.load(f)
            
            assert data['name'] == 'test_preset'
            assert data['description'] == 'Test description'
            assert len(data['effects']) == 1
    
    def test_save_preset_no_effects(self):
        """Test saving preset with no active effects."""
        system = EffectSystem()
        
        with pytest.raises(EffectError):
            system.save_preset('empty_preset')
    
    def test_load_preset(self):
        """Test loading effect preset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = EffectSystem(Path(temp_dir))
            system.register_effect(MockEffect)
            
            # Create and save a preset
            effect = system.create_effect('MockEffect', {'intensity': 1.5})
            system.add_effect(effect)
            system.save_preset('test_preset', 'Test description')
            
            # Clear effects and load preset
            system.clear_effects()
            assert len(system._active_effects) == 0
            
            system.load_preset('test_preset')
            
            assert len(system._active_effects) == 1
            loaded_effect = system._active_effects[0]
            assert loaded_effect.get_parameter_value('intensity') == 1.5
    
    def test_load_nonexistent_preset(self):
        """Test loading nonexistent preset."""
        system = EffectSystem()
        
        with pytest.raises(EffectError):
            system.load_preset('nonexistent_preset')
    
    def test_list_presets(self):
        """Test listing available presets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = EffectSystem(Path(temp_dir))
            system.register_effect(MockEffect)
            
            # Create some presets
            effect = system.create_effect('MockEffect', {})
            system.add_effect(effect)
            
            system.save_preset('preset1')
            system.save_preset('preset2')
            
            presets = system.list_presets()
            
            assert 'preset1' in presets
            assert 'preset2' in presets
            assert len(presets) == 2
    
    def test_get_preset_info(self):
        """Test getting preset information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = EffectSystem(Path(temp_dir))
            system.register_effect(MockEffect)
            
            effect = system.create_effect('MockEffect', {'intensity': 1.2})
            system.add_effect(effect)
            
            system.save_preset('info_test', 'Test preset info')
            
            info = system.get_preset_info('info_test')
            
            assert info['name'] == 'info_test'
            assert info['description'] == 'Test preset info'
            assert info['effect_count'] == 1
            assert 'MockEffect' in info['effects']
    
    def test_get_active_effects(self):
        """Test getting active effects list."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        
        effect1 = system.create_effect('MockEffect', {'intensity': 1.0})
        effect2 = system.create_effect('MockEffect', {'intensity': 2.0})
        
        system.add_effect(effect1)
        system.add_effect(effect2)
        
        active_effects = system.get_active_effects()
        
        assert len(active_effects) == 2
        assert effect1 in active_effects
        assert effect2 in active_effects
        
        # Should be a copy, not the original list
        active_effects.clear()
        assert len(system._active_effects) == 2
    
    def test_get_registered_effects(self):
        """Test getting registered effects dictionary."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        system.register_effect(AnotherMockEffect)
        
        registered = system.get_registered_effects()
        
        assert 'MockEffect' in registered
        assert 'AnotherMockEffect' in registered
        assert registered['MockEffect'] == MockEffect
        assert registered['AnotherMockEffect'] == AnotherMockEffect
        
        # Should be a copy, not the original dict
        registered.clear()
        assert len(system._registered_effects) == 2
    
    def test_validate_effect_stack(self):
        """Test effect stack validation."""
        system = EffectSystem()
        system.register_effect(MockEffect)
        
        effect1 = system.create_effect('MockEffect', {'intensity': 1.0})
        effect2 = system.create_effect('MockEffect', {'intensity': 2.0})
        
        system.add_effect(effect1)
        system.add_effect(effect2)
        
        is_valid, issues = system.validate_effect_stack()
        
        # Should detect multiple instances of same effect type
        assert not is_valid
        assert len(issues) > 0
        assert 'MockEffect' in issues[0]


class TestCompositionLayer:
    """Test cases for CompositionLayer dataclass."""
    
    def test_composition_layer_creation(self):
        """Test creating composition layer."""
        mock_clip = Mock()
        mock_effect = Mock()
        
        layer = CompositionLayer(
            clip=mock_clip,
            effect=mock_effect,
            layer_order=1,
            blend_mode='multiply',
            opacity=0.8
        )
        
        assert layer.clip == mock_clip
        assert layer.effect == mock_effect
        assert layer.layer_order == 1
        assert layer.blend_mode == 'multiply'
        assert layer.opacity == 0.8


class TestEffectPreset:
    """Test cases for EffectPreset dataclass."""
    
    def test_effect_preset_creation(self):
        """Test creating effect preset."""
        effects_data = [
            {'name': 'Effect1', 'class': 'MockEffect', 'parameters': {'intensity': 1.0}},
            {'name': 'Effect2', 'class': 'AnotherMockEffect', 'parameters': {'strength': 0.5}}
        ]
        
        preset = EffectPreset(
            name='test_preset',
            description='Test preset',
            effects=effects_data,
            created_at='2023-01-01',
            version='1.0'
        )
        
        assert preset.name == 'test_preset'
        assert preset.description == 'Test preset'
        assert len(preset.effects) == 2
        assert preset.created_at == '2023-01-01'
        assert preset.version == '1.0'