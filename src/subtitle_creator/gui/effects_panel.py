"""
Effects control panel implementation for the Subtitle Creator with Effects application.

This module provides the EffectsPanel class which implements a tabbed interface
for categorized effect controls, parameter management, preset handling, and
real-time effect application with the EffectSystem.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QScrollArea,
    QGroupBox, QLabel, QSlider, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QColorDialog, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QMessageBox, QFileDialog, QSplitter,
    QFrame, QGridLayout, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont

from ..effects.system import EffectSystem
from ..effects.base import BaseEffect, EffectParameter
from ..effects.text_styling import TypographyEffect, PositioningEffect, BackgroundEffect, TransitionEffect
from ..effects.animation import KaraokeHighlightEffect, ScaleBounceEffect, TypewriterEffect, FadeTransitionEffect
from ..effects.particles import HeartParticleEffect, StarParticleEffect, MusicNoteParticleEffect, SparkleParticleEffect


class ParameterControl(QWidget):
    """Base class for effect parameter controls."""
    
    value_changed = pyqtSignal(str, object)  # parameter_name, new_value
    
    def __init__(self, parameter: EffectParameter, parent=None):
        super().__init__(parent)
        self.parameter = parameter
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI for this parameter control."""
        raise NotImplementedError("Subclasses must implement _setup_ui")
    
    def get_value(self) -> Any:
        """Get the current parameter value."""
        raise NotImplementedError("Subclasses must implement get_value")
    
    def set_value(self, value: Any) -> None:
        """Set the parameter value."""
        raise NotImplementedError("Subclasses must implement set_value")


class SliderControl(ParameterControl):
    """Slider control for numeric parameters."""
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label with current value
        self.label = QLabel(f"{self.parameter.name}: {self.parameter.value}")
        layout.addWidget(self.label)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        
        if self.parameter.param_type == 'int':
            min_val = self.parameter.min_value or 0
            max_val = self.parameter.max_value or 100
            self.slider.setRange(min_val, max_val)
            self.slider.setValue(int(self.parameter.value))
        elif self.parameter.param_type == 'float':
            min_val = self.parameter.min_value or 0.0
            max_val = self.parameter.max_value or 1.0
            # Scale float to int range for slider
            self.slider.setRange(0, 1000)
            scaled_value = int((self.parameter.value - min_val) / (max_val - min_val) * 1000)
            self.slider.setValue(scaled_value)
        
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)
    
    def _on_slider_changed(self, value):
        if self.parameter.param_type == 'int':
            actual_value = value
        else:  # float
            min_val = self.parameter.min_value or 0.0
            max_val = self.parameter.max_value or 1.0
            actual_value = min_val + (value / 1000.0) * (max_val - min_val)
        
        self.label.setText(f"{self.parameter.name}: {actual_value:.2f}")
        self.value_changed.emit(self.parameter.name, actual_value)
    
    def get_value(self) -> Union[int, float]:
        if self.parameter.param_type == 'int':
            return self.slider.value()
        else:
            min_val = self.parameter.min_value or 0.0
            max_val = self.parameter.max_value or 1.0
            return min_val + (self.slider.value() / 1000.0) * (max_val - min_val)
    
    def set_value(self, value: Union[int, float]) -> None:
        if self.parameter.param_type == 'int':
            self.slider.setValue(int(value))
        else:
            min_val = self.parameter.min_value or 0.0
            max_val = self.parameter.max_value or 1.0
            scaled_value = int((value - min_val) / (max_val - min_val) * 1000)
            self.slider.setValue(scaled_value)


class ColorControl(ParameterControl):
    """Color picker control for color parameters."""
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(f"{self.parameter.name}:")
        layout.addWidget(self.label)
        
        # Color button
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 30)
        self.color_button.clicked.connect(self._open_color_dialog)
        
        # Set initial color
        if isinstance(self.parameter.value, (tuple, list)) and len(self.parameter.value) >= 3:
            r, g, b = self.parameter.value[:3]
            self.current_color = QColor(r, g, b)
        else:
            self.current_color = QColor(255, 255, 255)
        
        self._update_button_color()
        layout.addWidget(self.color_button)
        
        layout.addStretch()
    
    def _update_button_color(self):
        """Update the button's background color."""
        self.color_button.setStyleSheet(
            f"QPushButton {{ background-color: {self.current_color.name()}; "
            f"border: 2px solid #555; border-radius: 4px; }}"
        )
    
    def _open_color_dialog(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.current_color, self, f"Choose {self.parameter.name}")
        if color.isValid():
            self.current_color = color
            self._update_button_color()
            # Convert to RGBA tuple
            rgba = (color.red(), color.green(), color.blue(), 255)
            self.value_changed.emit(self.parameter.name, rgba)
    
    def get_value(self) -> tuple:
        return (self.current_color.red(), self.current_color.green(), 
                self.current_color.blue(), 255)
    
    def set_value(self, value: tuple) -> None:
        if isinstance(value, (tuple, list)) and len(value) >= 3:
            r, g, b = value[:3]
            self.current_color = QColor(r, g, b)
            self._update_button_color()


class ComboBoxControl(ParameterControl):
    """Combo box control for string choice parameters."""
    
    def __init__(self, parameter: EffectParameter, choices: List[str], parent=None):
        self.choices = choices
        super().__init__(parameter, parent)
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(f"{self.parameter.name}:")
        layout.addWidget(self.label)
        
        # Combo box
        self.combo_box = QComboBox()
        self.combo_box.addItems(self.choices)
        
        # Set current value
        if self.parameter.value in self.choices:
            self.combo_box.setCurrentText(self.parameter.value)
        
        self.combo_box.currentTextChanged.connect(
            lambda text: self.value_changed.emit(self.parameter.name, text)
        )
        layout.addWidget(self.combo_box)
    
    def get_value(self) -> str:
        return self.combo_box.currentText()
    
    def set_value(self, value: str) -> None:
        if value in self.choices:
            self.combo_box.setCurrentText(value)


class CheckBoxControl(ParameterControl):
    """Checkbox control for boolean parameters."""
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Checkbox with label
        self.checkbox = QCheckBox(self.parameter.name)
        self.checkbox.setChecked(bool(self.parameter.value))
        self.checkbox.toggled.connect(
            lambda checked: self.value_changed.emit(self.parameter.name, checked)
        )
        layout.addWidget(self.checkbox)
        
        layout.addStretch()
    
    def get_value(self) -> bool:
        return self.checkbox.isChecked()
    
    def set_value(self, value: bool) -> None:
        self.checkbox.setChecked(bool(value))


class EffectControlWidget(QWidget):
    """Widget for controlling a single effect with all its parameters."""
    
    effect_changed = pyqtSignal(object)  # effect instance
    effect_removed = pyqtSignal(object)  # effect instance
    
    def __init__(self, effect: BaseEffect, parent=None):
        super().__init__(parent)
        self.effect = effect
        self.parameter_controls: Dict[str, ParameterControl] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with effect name and remove button
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.effect.name)
        self.name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header_layout.addWidget(self.name_label)
        
        header_layout.addStretch()
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setMaximumWidth(80)
        self.remove_button.clicked.connect(lambda: self.effect_removed.emit(self.effect))
        header_layout.addWidget(self.remove_button)
        
        layout.addLayout(header_layout)
        
        # Parameters
        self._create_parameter_controls()
        
        # Preview button
        self.preview_button = QPushButton("Preview Effect")
        self.preview_button.clicked.connect(self._preview_effect)
        layout.addWidget(self.preview_button)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
    
    def _create_parameter_controls(self):
        """Create controls for all effect parameters."""
        if hasattr(self.effect, '_parameter_definitions'):
            for param_name, param_def in self.effect._parameter_definitions.items():
                control = self._create_parameter_control(param_def)
                if control:
                    control.value_changed.connect(self._on_parameter_changed)
                    self.parameter_controls[param_name] = control
                    self.layout().addWidget(control)
    
    def _create_parameter_control(self, parameter: EffectParameter) -> Optional[ParameterControl]:
        """Create appropriate control widget for a parameter."""
        if parameter.param_type in ['int', 'float']:
            return SliderControl(parameter)
        elif parameter.param_type == 'color':
            return ColorControl(parameter)
        elif parameter.param_type == 'bool':
            return CheckBoxControl(parameter)
        elif parameter.param_type == 'str':
            # Check for common string choices
            if parameter.name == 'font_weight':
                return ComboBoxControl(parameter, ['normal', 'bold'])
            elif parameter.name == 'highlight_mode':
                return ComboBoxControl(parameter, ['word', 'line', 'character'])
            elif parameter.name == 'position':
                return ComboBoxControl(parameter, ['center', 'left', 'right', 'top', 'bottom'])
            else:
                # Generic string parameter - could add text input if needed
                return None
        
        return None
    
    def _on_parameter_changed(self, param_name: str, value: Any):
        """Handle parameter value changes."""
        try:
            self.effect.set_parameter_value(param_name, value)
            self.effect_changed.emit(self.effect)
        except Exception as e:
            QMessageBox.warning(self, "Parameter Error", f"Failed to set parameter: {str(e)}")
    
    def _preview_effect(self):
        """Trigger effect preview."""
        self.effect_changed.emit(self.effect)


class PresetManager(QWidget):
    """Widget for managing effect presets."""
    
    preset_applied = pyqtSignal(str)  # preset_name
    
    def __init__(self, effect_system: EffectSystem, parent=None):
        super().__init__(parent)
        self.effect_system = effect_system
        self._setup_ui()
        self._refresh_preset_list()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Effect Presets")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Preset list
        self.preset_list = QListWidget()
        self.preset_list.itemDoubleClicked.connect(self._apply_selected_preset)
        layout.addWidget(self.preset_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_selected_preset)
        button_layout.addWidget(self.apply_button)
        
        self.save_button = QPushButton("Save Current")
        self.save_button.clicked.connect(self._save_current_preset)
        button_layout.addWidget(self.save_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_selected_preset)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # Preset info
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        # Connect selection change
        self.preset_list.currentItemChanged.connect(self._on_preset_selection_changed)
    
    def _refresh_preset_list(self):
        """Refresh the list of available presets."""
        self.preset_list.clear()
        try:
            presets = self.effect_system.list_presets()
            for preset_name in presets:
                self.preset_list.addItem(preset_name)
        except Exception as e:
            print(f"Error loading presets: {e}")
    
    def _apply_selected_preset(self):
        """Apply the selected preset."""
        current_item = self.preset_list.currentItem()
        if current_item:
            preset_name = current_item.text()
            try:
                self.effect_system.load_preset(preset_name)
                self.preset_applied.emit(preset_name)
                QMessageBox.information(self, "Preset Applied", f"Applied preset: {preset_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to apply preset: {str(e)}")
    
    def _save_current_preset(self):
        """Save current effects as a new preset."""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            try:
                self.effect_system.save_preset(name, f"Saved preset: {name}")
                self._refresh_preset_list()
                QMessageBox.information(self, "Preset Saved", f"Saved preset: {name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save preset: {str(e)}")
    
    def _delete_selected_preset(self):
        """Delete the selected preset."""
        current_item = self.preset_list.currentItem()
        if current_item:
            preset_name = current_item.text()
            reply = QMessageBox.question(
                self, "Delete Preset", 
                f"Are you sure you want to delete preset '{preset_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    preset_file = self.effect_system.preset_directory / f"{preset_name}.json"
                    if preset_file.exists():
                        preset_file.unlink()
                    self._refresh_preset_list()
                    QMessageBox.information(self, "Preset Deleted", f"Deleted preset: {preset_name}")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete preset: {str(e)}")
    
    def _on_preset_selection_changed(self, current, previous):
        """Handle preset selection changes."""
        if current:
            preset_name = current.text()
            try:
                info = self.effect_system.get_preset_info(preset_name)
                info_text = f"Name: {info['name']}\n"
                info_text += f"Description: {info['description']}\n"
                info_text += f"Effects: {', '.join(info['effects'])}\n"
                info_text += f"Effect Count: {info['effect_count']}"
                self.info_text.setText(info_text)
            except Exception as e:
                self.info_text.setText(f"Error loading preset info: {str(e)}")
        else:
            self.info_text.clear()


class EffectsPanel(QWidget):
    """
    Main effects control panel with tabbed interface for categorized effects.
    
    Provides:
    - Tabbed interface for different effect categories
    - Parameter controls for each effect type
    - Real-time effect preview
    - Preset management system
    - Integration with EffectSystem
    """
    
    effects_changed = pyqtSignal()  # Emitted when effects are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize effect system
        self.effect_system = EffectSystem()
        self._register_effects()
        
        # Active effect controls
        self.active_effects: List[EffectControlWidget] = []
        
        # Setup UI
        self._setup_ui()
        
        # Timer for debounced updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._emit_effects_changed)
    
    def _register_effects(self):
        """Register all available effect classes."""
        effect_classes = [
            TypographyEffect,
            PositioningEffect,
            BackgroundEffect,
            TransitionEffect,
            KaraokeHighlightEffect,
            ScaleBounceEffect,
            TypewriterEffect,
            FadeTransitionEffect,
            HeartParticleEffect,
            StarParticleEffect,
            MusicNoteParticleEffect,
            SparkleParticleEffect
        ]
        
        for effect_class in effect_classes:
            try:
                self.effect_system.register_effect(effect_class)
            except Exception as e:
                print(f"Failed to register effect {effect_class.__name__}: {e}")
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_text_styling_tab()
        self._create_animation_tab()
        self._create_particle_tab()
        self._create_active_effects_tab()
        self._create_presets_tab()
    
    def _create_text_styling_tab(self):
        """Create text styling effects tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area for effects
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Add effect buttons
        text_effects = [
            ("Typography", TypographyEffect, "Control font, size, weight, and color"),
            ("Positioning", PositioningEffect, "Control text position and alignment"),
            ("Background", BackgroundEffect, "Add backgrounds and outlines"),
            ("Transition", TransitionEffect, "Smooth parameter transitions")
        ]
        
        for name, effect_class, description in text_effects:
            self._create_effect_button(scroll_layout, name, effect_class, description)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(tab, "Text Styling")
    
    def _create_animation_tab(self):
        """Create animation effects tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        animation_effects = [
            ("Karaoke Highlight", KaraokeHighlightEffect, "Word-by-word highlighting"),
            ("Scale Bounce", ScaleBounceEffect, "Bouncing scale animation"),
            ("Typewriter", TypewriterEffect, "Progressive text reveal"),
            ("Fade Transition", FadeTransitionEffect, "Smooth fade in/out")
        ]
        
        for name, effect_class, description in animation_effects:
            self._create_effect_button(scroll_layout, name, effect_class, description)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(tab, "Animation")
    
    def _create_particle_tab(self):
        """Create particle effects tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        particle_effects = [
            ("Hearts", HeartParticleEffect, "Floating heart particles"),
            ("Stars", StarParticleEffect, "Twinkling star particles"),
            ("Music Notes", MusicNoteParticleEffect, "Musical note particles"),
            ("Sparkles", SparkleParticleEffect, "Sparkling light effects")
        ]
        
        for name, effect_class, description in particle_effects:
            self._create_effect_button(scroll_layout, name, effect_class, description)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(tab, "Particles")
    
    def _create_active_effects_tab(self):
        """Create active effects management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title_label = QLabel("Active Effects")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Scroll area for active effects
        self.active_effects_scroll = QScrollArea()
        self.active_effects_widget = QWidget()
        self.active_effects_layout = QVBoxLayout(self.active_effects_widget)
        self.active_effects_layout.addStretch()
        
        self.active_effects_scroll.setWidget(self.active_effects_widget)
        self.active_effects_scroll.setWidgetResizable(True)
        layout.addWidget(self.active_effects_scroll)
        
        # Clear all button
        self.clear_all_button = QPushButton("Clear All Effects")
        self.clear_all_button.clicked.connect(self._clear_all_effects)
        layout.addWidget(self.clear_all_button)
        
        self.tab_widget.addTab(tab, "Active Effects")
    
    def _create_presets_tab(self):
        """Create presets management tab."""
        self.preset_manager = PresetManager(self.effect_system)
        self.preset_manager.preset_applied.connect(self._on_preset_applied)
        self.tab_widget.addTab(self.preset_manager, "Presets")
    
    def _create_effect_button(self, layout: QVBoxLayout, name: str, effect_class: type, description: str):
        """Create a button to add an effect."""
        group_box = QGroupBox(name)
        group_layout = QVBoxLayout(group_box)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888; font-size: 10px;")
        group_layout.addWidget(desc_label)
        
        # Add button
        add_button = QPushButton(f"Add {name}")
        add_button.clicked.connect(lambda: self._add_effect(effect_class))
        group_layout.addWidget(add_button)
        
        layout.addWidget(group_box)
    
    def _add_effect(self, effect_class: type):
        """Add a new effect instance."""
        try:
            # Create effect with default parameters
            effect = effect_class(effect_class.__name__, {})
            
            # Add to effect system
            self.effect_system.add_effect(effect)
            
            # Create control widget
            control_widget = EffectControlWidget(effect)
            control_widget.effect_changed.connect(self._on_effect_changed)
            control_widget.effect_removed.connect(self._remove_effect)
            
            # Add to active effects
            self.active_effects.append(control_widget)
            
            # Insert before stretch
            self.active_effects_layout.insertWidget(
                self.active_effects_layout.count() - 1, 
                control_widget
            )
            
            # Switch to active effects tab
            self.tab_widget.setCurrentIndex(3)  # Active Effects tab
            
            # Emit change signal
            self._schedule_effects_changed()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add effect: {str(e)}")
    
    def _remove_effect(self, effect: BaseEffect):
        """Remove an effect."""
        try:
            # Remove from effect system
            self.effect_system.remove_effect(effect)
            
            # Find and remove control widget
            for i, control_widget in enumerate(self.active_effects):
                if control_widget.effect == effect:
                    self.active_effects_layout.removeWidget(control_widget)
                    control_widget.deleteLater()
                    self.active_effects.pop(i)
                    break
            
            # Emit change signal
            self._schedule_effects_changed()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to remove effect: {str(e)}")
    
    def _clear_all_effects(self):
        """Clear all active effects."""
        reply = QMessageBox.question(
            self, "Clear All Effects", 
            "Are you sure you want to remove all effects?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear effect system
            self.effect_system.clear_effects()
            
            # Remove all control widgets
            for control_widget in self.active_effects:
                self.active_effects_layout.removeWidget(control_widget)
                control_widget.deleteLater()
            
            self.active_effects.clear()
            
            # Emit change signal
            self._schedule_effects_changed()
    
    def _on_effect_changed(self, effect: BaseEffect):
        """Handle effect parameter changes."""
        self._schedule_effects_changed()
    
    def _on_preset_applied(self, preset_name: str):
        """Handle preset application."""
        # Clear current active effects UI
        for control_widget in self.active_effects:
            self.active_effects_layout.removeWidget(control_widget)
            control_widget.deleteLater()
        self.active_effects.clear()
        
        # Create control widgets for loaded effects
        for effect in self.effect_system.get_active_effects():
            control_widget = EffectControlWidget(effect)
            control_widget.effect_changed.connect(self._on_effect_changed)
            control_widget.effect_removed.connect(self._remove_effect)
            
            self.active_effects.append(control_widget)
            self.active_effects_layout.insertWidget(
                self.active_effects_layout.count() - 1, 
                control_widget
            )
        
        # Switch to active effects tab
        self.tab_widget.setCurrentIndex(3)
        
        # Emit change signal
        self._schedule_effects_changed()
    
    def _schedule_effects_changed(self):
        """Schedule effects changed signal with debouncing."""
        self.update_timer.start(100)  # 100ms delay
    
    def _emit_effects_changed(self):
        """Emit the effects changed signal."""
        self.effects_changed.emit()
    
    # Public interface methods
    
    def get_effect_system(self) -> EffectSystem:
        """Get the effect system instance."""
        return self.effect_system
    
    def get_active_effects(self) -> List[BaseEffect]:
        """Get list of active effects."""
        return self.effect_system.get_active_effects()
    
    def apply_effects_to_clip(self, clip, subtitle_data):
        """Apply all active effects to a clip."""
        return self.effect_system.apply_effects(clip, subtitle_data)