#!/usr/bin/env python3
"""
Demo script for the EffectsPanel widget.

This script demonstrates the effects control panel functionality including:
- Tabbed interface for different effect categories
- Parameter controls for various effect types
- Preset management system
- Real-time effect preview capabilities
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from subtitle_creator.gui.effects_panel import EffectsPanel
from subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming


class EffectsPanelDemo(QMainWindow):
    """Demo window for the EffectsPanel widget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Effects Panel Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QHBoxLayout(central_widget)
        
        # Create effects panel
        self.effects_panel = EffectsPanel()
        self.effects_panel.effects_changed.connect(self._on_effects_changed)
        layout.addWidget(self.effects_panel)
        
        # Create info panel
        info_widget = QWidget()
        info_widget.setMaximumWidth(300)
        info_layout = QVBoxLayout(info_widget)
        
        # Title
        title_label = QLabel("Effects Panel Demo")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        info_layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel("""
        <b>Instructions:</b><br><br>
        
        1. <b>Text Styling Tab:</b><br>
           - Add typography effects for font control<br>
           - Add positioning effects for text placement<br>
           - Add background effects for text backgrounds<br><br>
        
        2. <b>Animation Tab:</b><br>
           - Add karaoke highlighting effects<br>
           - Add scale bounce animations<br>
           - Add typewriter reveal effects<br><br>
        
        3. <b>Particles Tab:</b><br>
           - Add heart, star, or music note particles<br>
           - Add sparkle effects<br><br>
        
        4. <b>Active Effects Tab:</b><br>
           - View and modify active effects<br>
           - Adjust parameters with sliders and controls<br>
           - Remove individual effects<br><br>
        
        5. <b>Presets Tab:</b><br>
           - Save current effect combinations<br>
           - Load saved presets<br>
           - Manage preset library<br><br>
        
        <b>Features:</b><br>
        • Real-time parameter updates<br>
        • Color picker for color parameters<br>
        • Slider controls for numeric values<br>
        • Dropdown menus for choices<br>
        • Effect preview buttons<br>
        • Preset save/load system
        """)
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignTop)
        instructions.setStyleSheet("font-size: 11px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        info_layout.addWidget(instructions)
        
        # Status label
        self.status_label = QLabel("Ready - No effects active")
        self.status_label.setStyleSheet("font-weight: bold; color: #666; margin-top: 10px;")
        info_layout.addWidget(self.status_label)
        
        # Effect count label
        self.effect_count_label = QLabel("Active Effects: 0")
        self.effect_count_label.setStyleSheet("color: #888;")
        info_layout.addWidget(self.effect_count_label)
        
        info_layout.addStretch()
        layout.addWidget(info_widget)
        
        # Create sample subtitle data for testing
        self.sample_subtitle_data = self._create_sample_subtitle_data()
        
        # Apply dark theme
        self._apply_dark_theme()
    
    def _create_sample_subtitle_data(self) -> SubtitleData:
        """Create sample subtitle data for effect testing."""
        # Create sample word timings
        words1 = [
            WordTiming("Hello", 0.0, 0.5),
            WordTiming("world", 0.5, 1.0),
            WordTiming("from", 1.0, 1.3),
            WordTiming("effects", 1.3, 2.0)
        ]
        
        words2 = [
            WordTiming("This", 2.5, 2.8),
            WordTiming("is", 2.8, 3.0),
            WordTiming("a", 3.0, 3.1),
            WordTiming("demo", 3.1, 3.5)
        ]
        
        # Create subtitle lines
        lines = [
            SubtitleLine(
                start_time=0.0,
                end_time=2.0,
                text="Hello world from effects",
                words=words1
            ),
            SubtitleLine(
                start_time=2.5,
                end_time=3.5,
                text="This is a demo",
                words=words2
            )
        ]
        
        return SubtitleData(lines=lines)
    
    def _on_effects_changed(self):
        """Handle effects changes."""
        active_effects = self.effects_panel.get_active_effects()
        effect_count = len(active_effects)
        
        # Update status
        if effect_count == 0:
            self.status_label.setText("Ready - No effects active")
            self.status_label.setStyleSheet("font-weight: bold; color: #666; margin-top: 10px;")
        else:
            effect_names = [effect.name for effect in active_effects]
            self.status_label.setText(f"Effects active: {', '.join(effect_names)}")
            self.status_label.setStyleSheet("font-weight: bold; color: #0a84ff; margin-top: 10px;")
        
        # Update effect count
        self.effect_count_label.setText(f"Active Effects: {effect_count}")
        
        # Simulate effect application (in real app, this would update preview)
        print(f"Effects changed - {effect_count} active effects:")
        for effect in active_effects:
            print(f"  - {effect.name}: {effect.parameters}")
    
    def _apply_dark_theme(self):
        """Apply a dark theme to the demo window."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #555;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0a84ff;
            }
            QTabBar::tab:hover {
                background-color: #666;
            }
            QPushButton {
                background-color: #0a84ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 8px;
                background: #3c3c3c;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0a84ff;
                border: 1px solid #0056b3;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #0056b3;
            }
            QComboBox {
                border: 1px solid #555;
                border-radius: 3px;
                padding: 4px 8px;
                background-color: #3c3c3c;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QListWidget {
                border: 1px solid #555;
                background-color: #3c3c3c;
                alternate-background-color: #444;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #555;
            }
            QListWidget::item:selected {
                background-color: #0a84ff;
            }
            QTextEdit {
                border: 1px solid #555;
                background-color: #3c3c3c;
            }
            QScrollArea {
                border: 1px solid #555;
                background-color: #3c3c3c;
            }
            QScrollBar:vertical {
                background-color: #3c3c3c;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #666;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
        """)


def main():
    """Run the effects panel demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Effects Panel Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show demo window
    demo = EffectsPanelDemo()
    demo.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()