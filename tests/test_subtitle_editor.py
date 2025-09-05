"""
Tests for the subtitle timeline editor widget.

This module tests the SubtitleEditor widget functionality including
timeline visualization, text editing, selection management, and timing controls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QMouseEvent

from src.subtitle_creator.gui.subtitle_editor import (
    SubtitleEditor, SubtitleLineWidget, TimelineVisualizationWidget, TimelineSelection
)
from src.subtitle_creator.models import SubtitleData, SubtitleLine, WordTiming


@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_subtitle_data():
    """Create sample subtitle data for testing."""
    data = SubtitleData()
    
    # Add some test lines
    data.add_line(0.0, 2.0, "First subtitle line")
    data.add_line(3.0, 5.0, "Second subtitle line")
    data.add_line(6.0, 8.0, "Third subtitle line")
    
    return data


@pytest.fixture
def subtitle_editor(app, sample_subtitle_data):
    """Create SubtitleEditor widget for testing."""
    editor = SubtitleEditor()
    editor.set_subtitle_data(sample_subtitle_data)
    return editor


class TestTimelineSelection:
    """Test the TimelineSelection class."""
    
    def test_empty_selection(self):
        """Test empty selection behavior."""
        selection = TimelineSelection(set())
        assert selection.is_empty()
        assert not selection.contains_line(0)
    
    def test_single_selection(self):
        """Test single line selection."""
        selection = TimelineSelection({1})
        assert not selection.is_empty()
        assert selection.contains_line(1)
        assert not selection.contains_line(0)
    
    def test_multiple_selection(self):
        """Test multiple line selection."""
        selection = TimelineSelection({0, 2, 4})
        assert not selection.is_empty()
        assert selection.contains_line(0)
        assert selection.contains_line(2)
        assert selection.contains_line(4)
        assert not selection.contains_line(1)
    
    def test_get_time_range(self, sample_subtitle_data):
        """Test getting time range from selection."""
        selection = TimelineSelection({0, 2})  # First and third lines
        start_time, end_time = selection.get_time_range(sample_subtitle_data)
        
        assert start_time == 0.0  # Start of first line
        assert end_time == 8.0    # End of third line
    
    def test_get_time_range_empty(self, sample_subtitle_data):
        """Test getting time range from empty selection."""
        selection = TimelineSelection(set())
        start_time, end_time = selection.get_time_range(sample_subtitle_data)
        
        assert start_time == 0.0
        assert end_time == 0.0


class TestTimelineVisualizationWidget:
    """Test the TimelineVisualizationWidget class."""
    
    def test_initialization(self, app):
        """Test widget initialization."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = TimelineVisualizationWidget(line, scale=50.0)
        
        assert widget.subtitle_line == line
        assert widget.scale == 50.0
        assert widget.min_duration == 0.1
    
    def test_set_scale(self, app):
        """Test setting timeline scale."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = TimelineVisualizationWidget(line, scale=50.0)
        
        widget.set_scale(100.0)
        assert widget.scale == 100.0
    
    def test_update_timing(self, app):
        """Test updating timing values."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = TimelineVisualizationWidget(line, scale=50.0)
        
        widget.update_timing(2.0, 4.0)
        assert widget.subtitle_line.start_time == 2.0
        assert widget.subtitle_line.end_time == 4.0
    
    def test_bar_rect_calculation(self, app):
        """Test timing bar rectangle calculation."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = TimelineVisualizationWidget(line, scale=50.0)
        widget.resize(300, 40)
        
        bar_rect = widget._get_bar_rect()
        
        # Start position should be 1.0 * 50 = 50 pixels
        assert bar_rect.left() == 50
        
        # Width should be (3.0 - 1.0) * 50 = 100 pixels
        assert bar_rect.width() == 100
    
    def test_handle_rect_calculation(self, app):
        """Test handle rectangle calculation."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = TimelineVisualizationWidget(line, scale=50.0)
        widget.resize(300, 40)
        
        start_handle = widget._get_start_handle_rect()
        end_handle = widget._get_end_handle_rect()
        
        # Start handle should be at the left edge of the bar (approximately)
        assert abs(start_handle.center().x() - 50) <= 3
        
        # End handle should be at the right edge of the bar (approximately)
        assert abs(end_handle.center().x() - 150) <= 3
    
    def test_hover_area_detection(self, app):
        """Test hover area detection."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = TimelineVisualizationWidget(line, scale=50.0)
        widget.resize(300, 40)
        
        # Test start handle area
        start_pos = QPoint(50, 20)
        assert widget._get_hover_area(start_pos) == 'start'
        
        # Test end handle area
        end_pos = QPoint(150, 20)
        assert widget._get_hover_area(end_pos) == 'end'
        
        # Test body area
        body_pos = QPoint(100, 20)
        assert widget._get_hover_area(body_pos) == 'body'
        
        # Test outside area
        outside_pos = QPoint(200, 20)
        assert widget._get_hover_area(outside_pos) is None


class TestSubtitleLineWidget:
    """Test the SubtitleLineWidget class."""
    
    def test_initialization(self, app):
        """Test widget initialization."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = SubtitleLineWidget(0, line, timeline_scale=50.0)
        
        assert widget.line_index == 0
        assert widget.subtitle_line == line
        assert widget.timeline_scale == 50.0
        assert not widget.is_selected
    
    def test_text_editing(self, app):
        """Test text editing functionality."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = SubtitleLineWidget(0, line, timeline_scale=50.0)
        
        # Mock signal emission
        with patch.object(widget, 'line_text_changed') as mock_signal:
            widget.text_editor.setText("New text")
            widget._on_text_changed()
            
            mock_signal.emit.assert_called_once_with(0, "New text")
    
    def test_timing_adjustment(self, app):
        """Test timing adjustment through spinboxes."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = SubtitleLineWidget(0, line, timeline_scale=50.0)
        
        # Mock signal emission
        with patch.object(widget, 'line_timing_changed') as mock_signal:
            # Set values directly without triggering valueChanged signals
            widget.start_time_spinbox.blockSignals(True)
            widget.end_time_spinbox.blockSignals(True)
            widget.start_time_spinbox.setValue(2.0)
            widget.end_time_spinbox.setValue(4.0)
            widget.start_time_spinbox.blockSignals(False)
            widget.end_time_spinbox.blockSignals(False)
            
            widget._on_timing_changed()
            
            mock_signal.emit.assert_called_with(0, 2.0, 4.0)
    
    def test_timing_validation(self, app):
        """Test timing validation (end time must be after start time)."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = SubtitleLineWidget(0, line, timeline_scale=50.0)
        
        # Set invalid timing (end before start)
        widget.start_time_spinbox.setValue(5.0)
        widget.end_time_spinbox.setValue(3.0)
        widget._on_timing_changed()
        
        # End time should be adjusted to maintain minimum duration
        assert widget.end_time_spinbox.value() >= widget.start_time_spinbox.value() + widget.min_duration
    
    def test_selection_state(self, app):
        """Test selection state management."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = SubtitleLineWidget(0, line, timeline_scale=50.0)
        
        # Initially not selected
        assert not widget.is_selected
        
        # Set selected
        widget.set_selected(True)
        assert widget.is_selected
        
        # Set not selected
        widget.set_selected(False)
        assert not widget.is_selected
    
    def test_timeline_scale_update(self, app):
        """Test timeline scale update."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = SubtitleLineWidget(0, line, timeline_scale=50.0)
        
        widget.set_timeline_scale(100.0)
        assert widget.timeline_scale == 100.0
        assert widget.timeline_widget.scale == 100.0
    
    def test_line_data_update(self, app):
        """Test updating line data."""
        line = SubtitleLine(1.0, 3.0, "Test line", [], {})
        widget = SubtitleLineWidget(0, line, timeline_scale=50.0)
        
        # Update with new line data
        new_line = SubtitleLine(2.0, 4.0, "New text", [], {})
        
        # Block signals to avoid triggering validation during update
        widget.start_time_spinbox.blockSignals(True)
        widget.end_time_spinbox.blockSignals(True)
        widget.text_editor.blockSignals(True)
        
        widget.update_line_data(new_line)
        
        widget.start_time_spinbox.blockSignals(False)
        widget.end_time_spinbox.blockSignals(False)
        widget.text_editor.blockSignals(False)
        
        assert widget.subtitle_line == new_line
        assert widget.text_editor.text() == "New text"
        assert widget.start_time_spinbox.value() == 2.0
        assert widget.end_time_spinbox.value() == 4.0


class TestSubtitleEditor:
    """Test the SubtitleEditor class."""
    
    def test_initialization(self, app):
        """Test editor initialization."""
        editor = SubtitleEditor()
        
        assert editor.subtitle_data is None
        assert len(editor.line_widgets) == 0
        assert editor.selection.is_empty()
        assert editor.timeline_scale == 50.0
    
    def test_set_subtitle_data(self, subtitle_editor, sample_subtitle_data):
        """Test setting subtitle data."""
        assert subtitle_editor.subtitle_data == sample_subtitle_data
        assert len(subtitle_editor.line_widgets) == 3
    
    def test_line_widget_creation(self, subtitle_editor):
        """Test that line widgets are created correctly."""
        assert len(subtitle_editor.line_widgets) == 3
        
        for i, widget in enumerate(subtitle_editor.line_widgets):
            assert widget.line_index == i
            assert isinstance(widget, SubtitleLineWidget)
    
    def test_line_selection(self, subtitle_editor):
        """Test line selection functionality."""
        # Test single selection
        subtitle_editor._on_line_selected(1, False)
        assert subtitle_editor.selection.contains_line(1)
        assert len(subtitle_editor.selection.line_indices) == 1
        
        # Test multi-selection
        subtitle_editor._on_line_selected(2, True)
        assert subtitle_editor.selection.contains_line(1)
        assert subtitle_editor.selection.contains_line(2)
        assert len(subtitle_editor.selection.line_indices) == 2
        
        # Test toggle selection
        subtitle_editor._on_line_selected(1, True)
        assert not subtitle_editor.selection.contains_line(1)
        assert subtitle_editor.selection.contains_line(2)
        assert len(subtitle_editor.selection.line_indices) == 1
    
    def test_select_all_lines(self, subtitle_editor):
        """Test select all functionality."""
        subtitle_editor._select_all_lines()
        
        assert len(subtitle_editor.selection.line_indices) == 3
        assert subtitle_editor.selection.contains_line(0)
        assert subtitle_editor.selection.contains_line(1)
        assert subtitle_editor.selection.contains_line(2)
    
    def test_clear_selection(self, subtitle_editor):
        """Test clearing selection."""
        # First select some lines
        subtitle_editor._on_line_selected(0, False)
        subtitle_editor._on_line_selected(1, True)
        assert len(subtitle_editor.selection.line_indices) == 2
        
        # Clear selection
        subtitle_editor.clear_selection()
        assert subtitle_editor.selection.is_empty()
    
    def test_add_new_line(self, subtitle_editor):
        """Test adding new subtitle line."""
        initial_count = len(subtitle_editor.subtitle_data.lines)
        
        subtitle_editor._add_new_line()
        
        assert len(subtitle_editor.subtitle_data.lines) == initial_count + 1
        assert len(subtitle_editor.line_widgets) == initial_count + 1
        
        # New line should be selected
        new_index = initial_count
        assert subtitle_editor.selection.contains_line(new_index)
    
    def test_delete_selected_lines(self, subtitle_editor):
        """Test deleting selected lines."""
        initial_count = len(subtitle_editor.subtitle_data.lines)
        
        # Select first line
        subtitle_editor._on_line_selected(0, False)
        
        # Mock the confirmation dialog to return Yes
        with patch('PyQt6.QtWidgets.QMessageBox.question', 
                  return_value=QMessageBox.StandardButton.Yes):
            subtitle_editor._delete_selected_lines()
        
        assert len(subtitle_editor.subtitle_data.lines) == initial_count - 1
        assert len(subtitle_editor.line_widgets) == initial_count - 1
        assert subtitle_editor.selection.is_empty()
    
    def test_delete_selected_lines_cancelled(self, subtitle_editor):
        """Test cancelling line deletion."""
        initial_count = len(subtitle_editor.subtitle_data.lines)
        
        # Select first line
        subtitle_editor._on_line_selected(0, False)
        
        # Mock the confirmation dialog to return No
        with patch('PyQt6.QtWidgets.QMessageBox.question', 
                  return_value=QMessageBox.StandardButton.No):
            subtitle_editor._delete_selected_lines()
        
        # Nothing should be deleted
        assert len(subtitle_editor.subtitle_data.lines) == initial_count
        assert len(subtitle_editor.line_widgets) == initial_count
    
    def test_duplicate_line(self, subtitle_editor):
        """Test duplicating a line."""
        initial_count = len(subtitle_editor.subtitle_data.lines)
        original_line = subtitle_editor.subtitle_data.lines[1]
        original_text = original_line.text
        original_end_time = original_line.end_time
        
        # Mock the _rebuild_line_widgets method to avoid GUI updates during test
        with patch.object(subtitle_editor, '_rebuild_line_widgets'):
            subtitle_editor._duplicate_line(1)
        
        assert len(subtitle_editor.subtitle_data.lines) == initial_count + 1
        
        # Find the duplicated line (should have same text but later timing)
        duplicated_line = None
        for line in subtitle_editor.subtitle_data.lines:
            if (line.text == original_text and 
                line.start_time > original_end_time):
                duplicated_line = line
                break
        
        assert duplicated_line is not None, "Duplicated line not found"
        assert duplicated_line.text == original_text
        assert duplicated_line.start_time > original_end_time
    
    def test_text_change_handling(self, subtitle_editor):
        """Test handling text changes."""
        with patch.object(subtitle_editor, 'subtitle_data_changed') as mock_signal:
            with patch.object(subtitle_editor, 'preview_update_requested') as mock_preview:
                subtitle_editor._on_line_text_changed(0, "New text")
                
                assert subtitle_editor.subtitle_data.lines[0].text == "New text"
                mock_signal.emit.assert_called_once()
                mock_preview.emit.assert_called_once()
    
    def test_timing_change_handling(self, subtitle_editor):
        """Test handling timing changes."""
        with patch.object(subtitle_editor, 'subtitle_data_changed') as mock_signal:
            with patch.object(subtitle_editor, 'preview_update_requested') as mock_preview:
                subtitle_editor._on_line_timing_changed(0, 1.5, 3.5)
                
                # Line should be updated
                line = subtitle_editor.subtitle_data.lines[0]
                assert line.start_time == 1.5
                assert line.end_time == 3.5
                
                mock_signal.emit.assert_called_once()
                mock_preview.emit.assert_called_once()
    
    def test_zoom_functionality(self, subtitle_editor):
        """Test zoom in/out functionality."""
        initial_scale = subtitle_editor.timeline_scale
        
        # Zoom in
        subtitle_editor._zoom_in()
        zoomed_in_scale = subtitle_editor.timeline_scale
        assert zoomed_in_scale > initial_scale
        
        # Zoom out
        subtitle_editor._zoom_out()
        assert subtitle_editor.timeline_scale < zoomed_in_scale
    
    def test_zoom_limits(self, subtitle_editor):
        """Test zoom limits."""
        # Zoom to maximum
        subtitle_editor.timeline_scale = subtitle_editor.max_scale
        subtitle_editor._zoom_in()
        assert subtitle_editor.timeline_scale == subtitle_editor.max_scale
        
        # Zoom to minimum
        subtitle_editor.timeline_scale = subtitle_editor.min_scale
        subtitle_editor._zoom_out()
        assert subtitle_editor.timeline_scale == subtitle_editor.min_scale
    
    def test_zoom_fit(self, subtitle_editor):
        """Test zoom to fit functionality."""
        subtitle_editor._zoom_fit()
        
        # Scale should be adjusted to fit content
        assert subtitle_editor.min_scale <= subtitle_editor.timeline_scale <= subtitle_editor.max_scale
    
    def test_scroll_to_line(self, subtitle_editor):
        """Test scrolling to a specific line."""
        # Mock the scroll area
        with patch.object(subtitle_editor.scroll_area, 'ensureWidgetVisible') as mock_scroll:
            subtitle_editor.scroll_to_line(1)
            
            mock_scroll.assert_called_once_with(subtitle_editor.line_widgets[1])
    
    def test_scroll_to_time(self, subtitle_editor):
        """Test scrolling to a specific time."""
        with patch.object(subtitle_editor, 'scroll_to_line') as mock_scroll:
            # Time 1.5 should be in the first line (0.0-2.0)
            subtitle_editor.scroll_to_time(1.5)
            
            mock_scroll.assert_called_once_with(0)
    
    def test_get_selected_lines(self, subtitle_editor):
        """Test getting selected lines."""
        # Select first and third lines
        subtitle_editor._on_line_selected(0, False)
        subtitle_editor._on_line_selected(2, True)
        
        selected_lines = subtitle_editor.get_selected_lines()
        
        assert len(selected_lines) == 2
        assert selected_lines[0] == subtitle_editor.subtitle_data.lines[0]
        assert selected_lines[1] == subtitle_editor.subtitle_data.lines[2]
    
    def test_select_line_method(self, subtitle_editor):
        """Test the select_line method."""
        subtitle_editor.select_line(1)
        
        assert subtitle_editor.selection.contains_line(1)
        assert len(subtitle_editor.selection.line_indices) == 1
    
    def test_status_updates(self, subtitle_editor):
        """Test status bar updates."""
        # Status should show line count and duration
        status_text = subtitle_editor.status_label.text()
        assert "3 lines" in status_text
        assert "total duration" in status_text
    
    def test_selection_label_updates(self, subtitle_editor):
        """Test selection label updates."""
        # No selection
        assert subtitle_editor.selection_label.text() == ""
        
        # Single selection
        subtitle_editor._on_line_selected(0, False)
        assert "Line 1 selected" in subtitle_editor.selection_label.text()
        
        # Multiple selection
        subtitle_editor._on_line_selected(1, True)
        assert "2 lines selected" in subtitle_editor.selection_label.text()
    
    def test_toolbar_button_states(self, subtitle_editor):
        """Test toolbar button enable/disable states."""
        # Initially no selection
        assert not subtitle_editor.delete_line_button.isEnabled()
        assert not subtitle_editor.batch_edit_button.isEnabled()
        
        # Single selection
        subtitle_editor._on_line_selected(0, False)
        assert subtitle_editor.delete_line_button.isEnabled()
        assert not subtitle_editor.batch_edit_button.isEnabled()
        
        # Multiple selection
        subtitle_editor._on_line_selected(1, True)
        assert subtitle_editor.delete_line_button.isEnabled()
        assert subtitle_editor.batch_edit_button.isEnabled()
    
    def test_empty_subtitle_data(self, app):
        """Test editor with empty subtitle data."""
        editor = SubtitleEditor()
        empty_data = SubtitleData()
        
        editor.set_subtitle_data(empty_data)
        
        assert len(editor.line_widgets) == 0
        assert "No subtitles loaded" in editor.status_label.text()
    
    def test_keyboard_shortcuts(self, subtitle_editor):
        """Test keyboard shortcuts exist and methods work."""
        # Test that shortcuts exist
        assert subtitle_editor.delete_shortcut is not None
        assert subtitle_editor.select_all_shortcut is not None
        assert subtitle_editor.zoom_in_shortcut is not None
        assert subtitle_editor.zoom_out_shortcut is not None
        assert subtitle_editor.zoom_fit_shortcut is not None
        
        # Test the actual methods that shortcuts call
        # Select a line first
        subtitle_editor._on_line_selected(0, False)
        
        # Test delete method works
        initial_count = len(subtitle_editor.subtitle_data.lines)
        with patch('PyQt6.QtWidgets.QMessageBox.question', 
                  return_value=QMessageBox.StandardButton.Yes):
            subtitle_editor._delete_selected_lines()
        assert len(subtitle_editor.subtitle_data.lines) == initial_count - 1
        
        # Test select all method works
        subtitle_editor._select_all_lines()
        assert len(subtitle_editor.selection.line_indices) == len(subtitle_editor.subtitle_data.lines)
        
        # Test zoom methods work
        initial_scale = subtitle_editor.timeline_scale
        subtitle_editor._zoom_in()
        assert subtitle_editor.timeline_scale > initial_scale
        
        subtitle_editor._zoom_out()
        assert subtitle_editor.timeline_scale < initial_scale * 1.5  # Should be less than zoomed in value


if __name__ == '__main__':
    pytest.main([__file__])