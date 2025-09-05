#!/usr/bin/env python3
"""
Demo script for the SubtitleEditor widget.

This script demonstrates the comprehensive subtitle timeline editor functionality
including timing visualization, text editing, selection management, and all
interactive features.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QFileDialog, QMessageBox, QSplitter,
    QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

from subtitle_creator.gui.subtitle_editor import SubtitleEditor, TimelineSelection
from subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming


class SubtitleEditorDemo(QMainWindow):
    """
    Demo application for the SubtitleEditor widget.
    
    Features:
    - Load/save subtitle files
    - Full subtitle editing capabilities
    - Selection management demonstration
    - Timeline visualization
    - Live preview of changes
    """
    
    def __init__(self):
        """Initialize the demo application."""
        super().__init__()
        
        self.setWindowTitle("Subtitle Editor Demo - Subtitle Creator with Effects")
        self.setGeometry(100, 100, 1400, 800)
        
        # Create sample data
        self.create_sample_data()
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Load sample data
        self.subtitle_editor.set_subtitle_data(self.sample_data)
    
    def create_sample_data(self):
        """Create sample subtitle data for demonstration."""
        self.sample_data = SubtitleData()
        
        # Add sample subtitle lines with various timings
        sample_lines = [
            (0.0, 2.5, "Welcome to the Subtitle Editor demo!"),
            (3.0, 5.5, "This editor provides comprehensive subtitle editing capabilities."),
            (6.0, 8.0, "You can edit text directly in each line."),
            (8.5, 11.0, "Drag the timing bars to adjust start and end times."),
            (11.5, 14.0, "Use Ctrl+Click to select multiple lines."),
            (14.5, 17.0, "Right-click for context menu options."),
            (17.5, 20.0, "The timeline visualization shows timing relationships."),
            (20.5, 23.0, "Zoom in and out to see different levels of detail."),
            (23.5, 26.0, "Add new lines with the toolbar button."),
            (26.5, 29.0, "Delete selected lines with the Delete key."),
            (29.5, 32.0, "All changes are reflected in real-time."),
            (32.5, 35.0, "This is the final demonstration line.")
        ]
        
        for start_time, end_time, text in sample_lines:
            try:
                self.sample_data.add_line(start_time, end_time, text)
            except Exception as e:
                print(f"Warning: Could not add line '{text}': {e}")
        
        # Add some word-level timing to demonstrate karaoke features
        if self.sample_data.lines:
            first_line = self.sample_data.lines[0]
            words = first_line.text.split()
            word_duration = (first_line.end_time - first_line.start_time) / len(words)
            
            first_line.words = []
            for i, word in enumerate(words):
                word_start = first_line.start_time + i * word_duration
                word_end = word_start + word_duration
                first_line.words.append(WordTiming(word, word_start, word_end))
    
    def setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Subtitle Editor
        editor_panel = self.create_editor_panel()
        splitter.addWidget(editor_panel)
        
        # Right panel - Information and controls
        info_panel = self.create_info_panel()
        splitter.addWidget(info_panel)
        
        # Set splitter proportions (70% editor, 30% info)
        splitter.setSizes([1000, 400])
        
        main_layout.addWidget(splitter)
    
    def create_editor_panel(self):
        """Create the main editor panel."""
        panel = QGroupBox("Subtitle Timeline Editor")
        layout = QVBoxLayout(panel)
        
        # Subtitle editor widget
        self.subtitle_editor = SubtitleEditor()
        layout.addWidget(self.subtitle_editor)
        
        return panel
    
    def create_info_panel(self):
        """Create the information and controls panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        # File operations
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout(file_group)
        
        self.load_button = QPushButton("Load Subtitle File")
        self.load_button.setToolTip("Load subtitle file (JSON or ASS format)")
        file_layout.addWidget(self.load_button)
        
        self.save_button = QPushButton("Save Subtitle File")
        self.save_button.setToolTip("Save current subtitles to file")
        file_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("Reset to Sample Data")
        self.reset_button.setToolTip("Reset to original sample data")
        file_layout.addWidget(self.reset_button)
        
        layout.addWidget(file_group)
        
        # Selection information
        selection_group = QGroupBox("Selection Information")
        selection_layout = QVBoxLayout(selection_group)
        
        self.selection_info = QLabel("No selection")
        self.selection_info.setWordWrap(True)
        self.selection_info.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)
        selection_layout.addWidget(self.selection_info)
        
        layout.addWidget(selection_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_info = QLabel()
        self.stats_info.setWordWrap(True)
        self.stats_info.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)
        stats_layout.addWidget(self.stats_info)
        
        layout.addWidget(stats_group)
        
        # Live preview of changes
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions = QLabel("""
<b>How to use the Subtitle Editor:</b><br><br>

<b>Text Editing:</b><br>
• Click in any text field to edit subtitle content<br>
• Changes are applied automatically<br><br>

<b>Timing Adjustment:</b><br>
• Use the spinboxes for precise timing<br>
• Drag the timeline bars to adjust visually<br>
• Drag handles to adjust start/end times<br>
• Drag the bar body to move entire timing<br><br>

<b>Selection:</b><br>
• Click a line to select it<br>
• Ctrl+Click to add/remove from selection<br>
• Use Ctrl+A to select all lines<br><br>

<b>Context Menu:</b><br>
• Right-click for duplicate/delete options<br><br>

<b>Keyboard Shortcuts:</b><br>
• Delete: Remove selected lines<br>
• Ctrl+A: Select all<br>
• Ctrl++: Zoom in<br>
• Ctrl+-: Zoom out<br>
• Ctrl+0: Zoom to fit
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11px;")
        instructions_layout.addWidget(instructions)
        
        layout.addWidget(instructions_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
    
    def connect_signals(self):
        """Connect widget signals."""
        # File operations
        self.load_button.clicked.connect(self.load_subtitle_file)
        self.save_button.clicked.connect(self.save_subtitle_file)
        self.reset_button.clicked.connect(self.reset_to_sample_data)
        
        # Subtitle editor signals
        self.subtitle_editor.subtitle_data_changed.connect(self.on_subtitle_data_changed)
        self.subtitle_editor.selection_changed.connect(self.on_selection_changed)
        self.subtitle_editor.line_selected.connect(self.on_line_selected)
        self.subtitle_editor.preview_update_requested.connect(self.on_preview_update_requested)
    
    @pyqtSlot()
    def load_subtitle_file(self):
        """Load a subtitle file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Subtitle File",
            "",
            "Subtitle Files (*.json *.ass);;JSON Files (*.json);;ASS Files (*.ass);;All Files (*)"
        )
        
        if file_path:
            try:
                # For demo purposes, we'll just show a message
                # In a real application, you would use the subtitle parsers
                QMessageBox.information(
                    self,
                    "Load File",
                    f"In a real application, this would load:\n{file_path}\n\n"
                    "For this demo, use 'Reset to Sample Data' to reload the sample."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Load Error",
                    f"Failed to load subtitle file:\n{str(e)}"
                )
    
    @pyqtSlot()
    def save_subtitle_file(self):
        """Save the current subtitle data."""
        if not self.subtitle_editor.subtitle_data:
            QMessageBox.warning(self, "Save Error", "No subtitle data to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Subtitle File",
            "",
            "JSON Files (*.json);;ASS Files (*.ass);;All Files (*)"
        )
        
        if file_path:
            try:
                # For demo purposes, we'll just show the data
                # In a real application, you would use the subtitle parsers
                data = self.subtitle_editor.subtitle_data
                stats = data.get_statistics()
                
                QMessageBox.information(
                    self,
                    "Save File",
                    f"In a real application, this would save to:\n{file_path}\n\n"
                    f"Data to save:\n"
                    f"• {stats['total_lines']} subtitle lines\n"
                    f"• {stats['total_duration']:.1f}s total duration\n"
                    f"• {stats['total_words']} total words"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save subtitle file:\n{str(e)}"
                )
    
    @pyqtSlot()
    def reset_to_sample_data(self):
        """Reset to the original sample data."""
        self.create_sample_data()
        self.subtitle_editor.set_subtitle_data(self.sample_data)
        self.update_statistics()
    
    @pyqtSlot(SubtitleData)
    def on_subtitle_data_changed(self, subtitle_data):
        """Handle subtitle data changes."""
        self.update_statistics()
        self.update_preview()
    
    @pyqtSlot(TimelineSelection)
    def on_selection_changed(self, selection):
        """Handle selection changes."""
        self.update_selection_info(selection)
    
    @pyqtSlot(int)
    def on_line_selected(self, line_index):
        """Handle single line selection."""
        if (self.subtitle_editor.subtitle_data and 
            0 <= line_index < len(self.subtitle_editor.subtitle_data.lines)):
            
            line = self.subtitle_editor.subtitle_data.lines[line_index]
            self.preview_text.append(f"Selected line {line_index + 1}: {line.text}")
    
    @pyqtSlot()
    def on_preview_update_requested(self):
        """Handle preview update requests."""
        self.update_preview()
    
    def update_selection_info(self, selection):
        """Update the selection information display."""
        if selection.is_empty():
            self.selection_info.setText("No selection")
            return
        
        if not self.subtitle_editor.subtitle_data:
            return
        
        selected_lines = [
            self.subtitle_editor.subtitle_data.lines[i] 
            for i in selection.line_indices
            if i < len(self.subtitle_editor.subtitle_data.lines)
        ]
        
        if not selected_lines:
            self.selection_info.setText("Invalid selection")
            return
        
        # Calculate selection statistics
        total_duration = sum(line.end_time - line.start_time for line in selected_lines)
        total_words = sum(len(line.text.split()) for line in selected_lines)
        start_time, end_time = selection.get_time_range(self.subtitle_editor.subtitle_data)
        
        info_text = f"""Selected Lines: {len(selected_lines)}
Time Range: {start_time:.1f}s - {end_time:.1f}s
Total Duration: {total_duration:.1f}s
Total Words: {total_words}

Line Details:"""
        
        for i, line_index in enumerate(sorted(selection.line_indices)):
            if line_index < len(self.subtitle_editor.subtitle_data.lines):
                line = self.subtitle_editor.subtitle_data.lines[line_index]
                info_text += f"\n{line_index + 1}: {line.start_time:.1f}s-{line.end_time:.1f}s"
                if len(line.text) > 30:
                    info_text += f" '{line.text[:30]}...'"
                else:
                    info_text += f" '{line.text}'"
        
        self.selection_info.setText(info_text)
    
    def update_statistics(self):
        """Update the statistics display."""
        if not self.subtitle_editor.subtitle_data:
            self.stats_info.setText("No data loaded")
            return
        
        stats = self.subtitle_editor.subtitle_data.get_statistics()
        
        stats_text = f"""Total Lines: {stats['total_lines']}
Total Duration: {stats['total_duration']:.1f}s
Total Words: {stats['total_words']}
Average Line Duration: {stats['average_line_duration']:.1f}s
Average Words/Line: {stats['average_words_per_line']:.1f}
Earliest Start: {stats.get('earliest_start', 0):.1f}s
Latest End: {stats.get('latest_end', 0):.1f}s"""
        
        self.stats_info.setText(stats_text)
    
    def update_preview(self):
        """Update the live preview display."""
        if not self.subtitle_editor.subtitle_data:
            self.preview_text.clear()
            return
        
        # Show recent changes in the preview
        self.preview_text.append("--- Subtitle data updated ---")
        
        # Limit preview text length
        if self.preview_text.document().blockCount() > 50:
            cursor = self.preview_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 10)
            cursor.removeSelectedText()


def main():
    """Run the subtitle editor demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Subtitle Editor Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Subtitle Creator")
    
    # Create and show the demo window
    demo = SubtitleEditorDemo()
    demo.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()