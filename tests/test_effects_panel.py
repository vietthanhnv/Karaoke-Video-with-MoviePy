"""
Tests for the EffectsPanel widget and related components.

This module tests the effects control panel functionality including parameter
controls, effect management, preset handling, and integration with the EffectSystem.
"""

import pytest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from subtitle_creator.gui.effects_panel import (
    EffectsPanel, ParameterControl, SliderControl, ColorControl, 
    ComboBoxControl, CheckBoxControl, EffectControlWidget, PresetManager
)
from subtitle_creator.effects.system import EffectSystem
from subtitle_creator.effects.base import BaseEffect, EffectParameter
from subtitle_creator.effects.text_styling import TypographyEffect
from subtitle_creator.effects.animation import KaraokeHighlightEffect
from subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming


class MockEffect(BaseEffect):
    """Mock effect for testing."""
    
    def _define_parameters(self):
        return {
            'test_int': EffectParameter(
                name='test_int',
                value=50,
                param_type='int',
                min_value=0,
                max_value=100,
                default_value=50,
                description='Test integer parameter'
            ),
            'test_float': EffectParameter(
                name='test_float',
                value=0.5,
                param_type='float',
                min_value=0.0,
                max_value=1.0,
                default_value=0.5,
                description='Test float parameter'
            ),
            'test_color': EffectParameter(
                name='test_color',
                value=(255, 255, 255, 255),
                param_type='color',
                default_value=(255, 255, 255, 255),
                description='Test color parameter'
            ),
            'test_bool': EffectParameter(
                name='test_bool',
                value=True,
                param_type='bool',
                default_value=True,
                description='Test boolean parameter'
            ),
            'test_string': EffectParameter(
                name='test_string',
                value='test',
                param_type='str',
                default_value='test',
                description='Test string parameter'
            )
        }
    
    def apply(self, clip, subtitle_data):
        return clip


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def sample_subtitle_data():
    """Create sample subtitle data for testing."""
    words = [
        WordTiming("Hello", 0.0, 0.5),
        WordTiming("world", 0.5, 1.0)
    ]
    
    lines = [
        SubtitleLine(
            start_time=0.0,
            end_time=1.0,
            text="Hello world",
            words=words
        )
    ]
    
    return SubtitleData(lines=lines)


@pytest.fixture
def temp_preset_dir():
    """Create temporary directory for presets."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestParameterControls:
    """Test parameter control widgets."""
    
    def test_slider_control_int(self, app):
        """Test SliderControl with integer parameter."""
        param = EffectParameter(
            name='test_param',
            value=50,
            param_type='int',
            min_value=0,
            max_value=100,
            default_value=50,
            description='Test parameter'
        )
        
        control = SliderControl(param)
        
        # Test initial value
        assert control.get_value() == 50
        
        # Test value change
        control.slider.setValue(75)
        assert control.get_value() == 75
        
        # Test set_value
        control.set_value(25)
        assert control.slider.value() == 25
    
    def test_slider_control_float(self, app):
        """Test SliderControl with float parameter."""
        param = EffectParameter(
            name='test_param',
            value=0.5,
            param_type='float',
            min_value=0.0,
            max_value=1.0,
            default_value=0.5,
            description='Test parameter'
        )
        
        control = SliderControl(param)
        
        # Test initial value (approximately)
        assert abs(control.get_value() - 0.5) < 0.01
        
        # Test value change
        control.slider.setValue(750)  # 75% of range
        assert abs(control.get_value() - 0.75) < 0.01
    
    def test_color_control(self, app):
        """Test ColorControl widget."""
        param = EffectParameter(
            name='test_color',
            value=(255, 0, 0, 255),
            param_type='color',
            default_value=(255, 255, 255, 255),
            description='Test color'
        )
        
        control = ColorControl(param)
        
        # Test initial value
        r, g, b, a = control.get_value()
        assert r == 255 and g == 0 and b == 0 and a == 255
        
        # Test set_value
        control.set_value((0, 255, 0, 255))
        r, g, b, a = control.get_value()
        assert r == 0 and g == 255 and b == 0 and a == 255
    
    def test_combo_box_control(self, app):
        """Test ComboBoxControl widget."""
        param = EffectParameter(
            name='test_choice',
            value='option1',
            param_type='str',
            default_value='option1',
            description='Test choice'
        )
        
        choices = ['option1', 'option2', 'option3']
        control = ComboBoxControl(param, choices)
        
        # Test initial value
        assert control.get_value() == 'option1'
        
        # Test value change
        control.combo_box.setCurrentText('option2')
        assert control.get_value() == 'option2'
        
        # Test set_value
        control.set_value('option3')
        assert control.combo_box.currentText() == 'option3'
    
    def test_checkbox_control(self, app):
        """Test CheckBoxControl widget."""
        param = EffectParameter(
            name='test_bool',
            value=True,
            param_type='bool',
            default_value=False,
            description='Test boolean'
        )
        
        control = CheckBoxControl(param)
        
        # Test initial value
        assert control.get_value() is True
        
        # Test value change
        control.checkbox.setChecked(False)
        assert control.get_value() is False
        
        # Test set_value
        control.set_value(True)
        assert control.checkbox.isChecked() is True


class TestEffectControlWidget:
    """Test EffectControlWidget."""
    
    def test_effect_control_creation(self, app):
        """Test creating an effect control widget."""
        effect = MockEffect("TestEffect", {})
        control = EffectControlWidget(effect)
        
        # Check that parameter controls were created
        assert len(control.parameter_controls) > 0
        
        # Check for specific parameter controls
        assert 'test_int' in control.parameter_controls
        assert 'test_float' in control.parameter_controls
        assert 'test_color' in control.parameter_controls
        assert 'test_bool' in control.parameter_controls
    
    def test_parameter_change_handling(self, app):
        """Test parameter change handling."""
        effect = MockEffect("TestEffect", {})
        control = EffectControlWidget(effect)
        
        # Mock the effect_changed signal
        signal_emitted = False
        def on_effect_changed(eff):
            nonlocal signal_emitted
            signal_emitted = True
        
        control.effect_changed.connect(on_effect_changed)
        
        # Trigger parameter change
        control._on_parameter_changed('test_int', 75)
        
        # Check that effect was updated and signal emitted
        assert effect.get_parameter_value('test_int') == 75
        assert signal_emitted
    
    def test_effect_removal(self, app):
        """Test effect removal signal."""
        effect = MockEffect("TestEffect", {})
        control = EffectControlWidget(effect)
        
        # Mock the effect_removed signal
        removed_effect = None
        def on_effect_removed(eff):
            nonlocal removed_effect
            removed_effect = eff
        
        control.effect_removed.connect(on_effect_removed)
        
        # Trigger removal
        control.remove_button.click()
        
        # Check that signal was emitted with correct effect
        assert removed_effect == effect


class TestPresetManager:
    """Test PresetManager widget."""
    
    def test_preset_manager_creation(self, app, temp_preset_dir):
        """Test creating a preset manager."""
        effect_system = EffectSystem(temp_preset_dir)
        manager = PresetManager(effect_system)
        
        # Check initial state
        assert manager.preset_list.count() == 0
        assert manager.info_text.toPlainText() == ""
    
    def test_preset_save_and_load(self, app, temp_preset_dir):
        """Test saving and loading presets."""
        effect_system = EffectSystem(temp_preset_dir)
        manager = PresetManager(effect_system)
        
        # Add an effect to the system
        effect = MockEffect("TestEffect", {})
        effect_system.add_effect(effect)
        
        # Save preset
        with patch('PyQt6.QtWidgets.QInputDialog.getText') as mock_input:
            mock_input.return_value = ("test_preset", True)
            manager._save_current_preset()
        
        # Check that preset file was created
        preset_file = temp_preset_dir / "test_preset.json"
        assert preset_file.exists()
        
        # Refresh list and check
        manager._refresh_preset_list()
        assert manager.preset_list.count() == 1
        assert manager.preset_list.item(0).text() == "test_preset"
    
    def test_preset_info_display(self, app, temp_preset_dir):
        """Test preset info display."""
        effect_system = EffectSystem(temp_preset_dir)
        manager = PresetManager(effect_system)
        
        # Create a test preset file
        preset_data = {
            "name": "test_preset",
            "description": "Test description",
            "effects": [{"name": "TestEffect", "class": "MockEffect", "parameters": {}}],
            "created_at": "2023-01-01",
            "version": "1.0"
        }
        
        preset_file = temp_preset_dir / "test_preset.json"
        with open(preset_file, 'w') as f:
            json.dump(preset_data, f)
        
        # Refresh list and select item
        manager._refresh_preset_list()
        manager.preset_list.setCurrentRow(0)
        
        # Check info display
        info_text = manager.info_text.toPlainText()
        assert "test_preset" in info_text
        assert "Test description" in info_text
        assert "TestEffect" in info_text


class TestEffectsPanel:
    """Test main EffectsPanel widget."""
    
    def test_effects_panel_creation(self, app):
        """Test creating an effects panel."""
        panel = EffectsPanel()
        
        # Check that tabs were created
        assert panel.tab_widget.count() == 5  # Text, Animation, Particles, Active, Presets
        
        # Check tab names
        tab_names = [panel.tab_widget.tabText(i) for i in range(panel.tab_widget.count())]
        expected_names = ["Text Styling", "Animation", "Particles", "Active Effects", "Presets"]
        assert tab_names == expected_names
        
        # Check that effect system was initialized
        assert panel.effect_system is not None
        assert len(panel.effect_system.get_registered_effects()) > 0
    
    def test_add_effect(self, app):
        """Test adding an effect."""
        panel = EffectsPanel()
        
        # Mock the effect class
        with patch.object(panel.effect_system, 'register_effect'):
            panel.effect_system.register_effect(MockEffect)
        
        # Add effect
        panel._add_effect(MockEffect)
        
        # Check that effect was added
        active_effects = panel.get_active_effects()
        assert len(active_effects) == 1
        assert active_effects[0].__class__.__name__ == "MockEffect"
        
        # Check that control widget was created
        assert len(panel.active_effects) == 1
    
    def test_remove_effect(self, app):
        """Test removing an effect."""
        panel = EffectsPanel()
        
        # Add an effect first
        effect = MockEffect("TestEffect", {})
        panel.effect_system.add_effect(effect)
        
        # Create control widget
        control_widget = EffectControlWidget(effect)
        panel.active_effects.append(control_widget)
        
        # Remove effect
        panel._remove_effect(effect)
        
        # Check that effect was removed
        assert len(panel.get_active_effects()) == 0
        assert len(panel.active_effects) == 0
    
    def test_clear_all_effects(self, app):
        """Test clearing all effects."""
        panel = EffectsPanel()
        
        # Add multiple effects
        for i in range(3):
            effect = MockEffect(f"TestEffect{i}", {})
            panel.effect_system.add_effect(effect)
            control_widget = EffectControlWidget(effect)
            panel.active_effects.append(control_widget)
        
        # Mock the confirmation dialog
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.Yes
            panel._clear_all_effects()
        
        # Check that all effects were cleared
        assert len(panel.get_active_effects()) == 0
        assert len(panel.active_effects) == 0
    
    def test_effects_changed_signal(self, app):
        """Test effects changed signal emission."""
        panel = EffectsPanel()
        
        # Connect signal
        signal_emitted = False
        def on_effects_changed():
            nonlocal signal_emitted
            signal_emitted = True
        
        panel.effects_changed.connect(on_effects_changed)
        
        # Add effect (should trigger signal)
        effect = MockEffect("TestEffect", {})
        panel.effect_system.add_effect(effect)
        panel._schedule_effects_changed()
        
        # Process events to trigger timer
        QTest.qWait(150)  # Wait for timer delay
        
        assert signal_emitted
    
    def test_preset_application(self, app, temp_preset_dir):
        """Test applying a preset."""
        panel = EffectsPanel()
        panel.effect_system.preset_directory = temp_preset_dir
        
        # Register the mock effect first
        panel.effect_system.register_effect(MockEffect)
        
        # Create a test preset
        effect = MockEffect("TestEffect", {})
        panel.effect_system.add_effect(effect)
        panel.effect_system.save_preset("test_preset", "Test preset")
        
        # Check the preset file was created
        preset_file = temp_preset_dir / "test_preset.json"
        assert preset_file.exists()
        
        # Clear effects
        panel.effect_system.clear_effects()
        assert len(panel.get_active_effects()) == 0
        
        # Simulate the full preset application workflow:
        # 1. Load preset into effect system
        panel.effect_system.load_preset("test_preset")
        
        # 2. Call the UI update method (which is what the signal does)
        panel._on_preset_applied("test_preset")
        
        # Check that effects were loaded and UI updated
        active_effects = panel.get_active_effects()
        assert len(active_effects) == 1
        assert len(panel.active_effects) == 1
    
    def test_effect_system_integration(self, app, sample_subtitle_data):
        """Test integration with effect system."""
        panel = EffectsPanel()
        
        # Add some effects
        effect1 = MockEffect("Effect1", {})
        effect2 = MockEffect("Effect2", {})
        
        panel.effect_system.add_effect(effect1)
        panel.effect_system.add_effect(effect2)
        
        # Test applying effects to clip (mock clip)
        mock_clip = Mock()
        mock_clip.duration = 5.0
        mock_clip.fps = 24
        mock_clip.layer_index = 0
        mock_clip.audio = None
        mock_clip.start = 0
        mock_clip.size = (1920, 1080)
        mock_clip.end = 5.0
        mock_clip.mask = None  # No mask to avoid CompositeVideoClip mask issues
        
        result_clip = panel.apply_effects_to_clip(mock_clip, sample_subtitle_data)
        
        # Should return a clip (in this case, the mock clip since MockEffect doesn't modify it)
        assert result_clip is not None


class TestEffectsPanelIntegration:
    """Integration tests for effects panel with real effect classes."""
    
    def test_typography_effect_integration(self, app):
        """Test integration with TypographyEffect."""
        panel = EffectsPanel()
        
        # Add typography effect
        panel._add_effect(TypographyEffect)
        
        # Check that effect was added with proper parameters
        active_effects = panel.get_active_effects()
        assert len(active_effects) == 1
        
        effect = active_effects[0]
        assert effect.__class__.__name__ == "TypographyEffect"
        
        # Check that control widget has expected parameters
        control_widget = panel.active_effects[0]
        assert 'font_size' in control_widget.parameter_controls
        assert 'text_color' in control_widget.parameter_controls
    
    def test_karaoke_effect_integration(self, app):
        """Test integration with KaraokeHighlightEffect."""
        panel = EffectsPanel()
        
        # Add karaoke effect
        panel._add_effect(KaraokeHighlightEffect)
        
        # Check that effect was added
        active_effects = panel.get_active_effects()
        assert len(active_effects) == 1
        
        effect = active_effects[0]
        assert effect.__class__.__name__ == "KaraokeHighlightEffect"
        
        # Check that control widget has expected parameters
        control_widget = panel.active_effects[0]
        assert 'default_color' in control_widget.parameter_controls
        assert 'highlight_color' in control_widget.parameter_controls
    
    def test_multiple_effects_interaction(self, app, sample_subtitle_data):
        """Test multiple effects working together."""
        panel = EffectsPanel()
        
        # Add multiple effects
        panel._add_effect(TypographyEffect)
        panel._add_effect(KaraokeHighlightEffect)
        
        # Check that both effects are active
        active_effects = panel.get_active_effects()
        assert len(active_effects) == 2
        
        # Test that effects can be applied together
        mock_clip = Mock()
        mock_clip.duration = 5.0
        
        result_clip = panel.apply_effects_to_clip(mock_clip, sample_subtitle_data)
        assert result_clip is not None
    
    def test_effect_parameter_persistence(self, app):
        """Test that effect parameters persist correctly."""
        panel = EffectsPanel()
        
        # Add effect
        panel._add_effect(TypographyEffect)
        
        # Get the control widget and modify a parameter
        control_widget = panel.active_effects[0]
        if 'font_size' in control_widget.parameter_controls:
            font_size_control = control_widget.parameter_controls['font_size']
            font_size_control.set_value(72)
        
        # Check that the effect parameter was updated
        effect = panel.get_active_effects()[0]
        assert effect.get_parameter_value('font_size') == 72


if __name__ == "__main__":
    pytest.main([__file__])