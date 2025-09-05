"""
Subtitle timeline editor widget for comprehensive subtitle editing.

This module provides the SubtitleEditor widget that offers timeline-based subtitle
editing with timing visualization, direct text editing, batch selection capabilities,
and timing adjustment controls with numerical input and drag functionality.
"""

import math
from typing import Optional, List, Dict, Any, Set, Tuple, Callable
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QPushButton, QFrame, QSizePolicy, QSpacerItem,
    QAbstractItemView, QRubberBand, QMenu, QMessageBox, QToolTip, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QSize, QRect, QPoint, QMimeData, QItemSelectionModel,
    QAbstractItemModel, QModelIndex, QVariant, QRectF, QPointF
)
from PyQt6.QtGui import (
    QPainter, QPixmap, QImage, QPalette, QKeySequence, QShortcut,
    QFont, QFontMetrics, QPen, QBrush, QColor, QLinearGradient,
    QMouseEvent, QPaintEvent, QResizeEvent, QContextMenuEvent, QDragEnterEvent,
    QDropEvent, QDragMoveEvent, QWheelEvent
)

from ..models import SubtitleData, SubtitleLine, WordTiming, ValidationError
from ..interfaces import SubtitleCreatorError


@dataclass
class TimelineSelection:
    """Represents a selection of subtitle lines in the timeline."""
    line_indices: Set[int]
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def is_empty(self) -> bool:
        """Check if selection is empty."""
        return len(self.line_indices) == 0
    
    def contains_line(self, index: int) -> bool:
        """Check if selection contains a specific line."""
        return index in self.line_indices
    
    def get_time_range(self, subtitle_data: SubtitleData) -> Tuple[float, float]:
        """Get the time range covered by selected lines."""
        if self.is_empty() or not subtitle_data.lines:
            return 0.0, 0.0
        
        selected_lines = [subtitle_data.lines[i] for i in self.line_indices 
                         if i < len(subtitle_data.lines)]
        
        if not selected_lines:
            return 0.0, 0.0
        
        start_time = min(line.start_time for line in selected_lines)
        end_time = max(line.end_time for line in selected_lines)
        
        return start_time, end_time


class SubtitleLineWidget(QFrame):
    """
    Custom widget representing a single subtitle line in the timeline.
    
    Features:
    - Visual timing bar with draggable handles
    - Direct text editing
    - Timing adjustment controls
    - Selection highlighting
    - Context menu support
    """
    
    # Signals
    line_selected = pyqtSignal(int, bool)  # index, add_to_selection
    line_text_changed = pyqtSignal(int, str)  # index, new_text
    line_timing_changed = pyqtSignal(int, float, float)  # index, start_time, end_time
    line_context_menu = pyqtSignal(int, QPoint)  # index, global_position
    
    def __init__(self, line_index: int, subtitle_line: SubtitleLine, 
                 timeline_scale: float = 1.0, parent: Optional[QWidget] = None):
        """
        Initialize the subtitle line widget.
        
        Args:
            line_index: Index of this line in the subtitle data
            subtitle_line: The subtitle line data
            timeline_scale: Pixels per second for timeline visualization
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.line_index = line_index
        self.subtitle_line = subtitle_line
        self.timeline_scale = timeline_scale
        
        # Widget state
        self.is_selected = False
        self.is_editing_text = False
        self.is_dragging_start = False
        self.is_dragging_end = False
        self.is_dragging_body = False
        self.drag_start_pos = QPoint()
        self.original_timing = (0.0, 0.0)
        
        # Visual properties
        self.min_duration = 0.1  # Minimum duration in seconds
        self.handle_width = 8
        self.line_height = 60
        
        # Setup UI
        self._setup_ui()
        self._setup_style()
        self._connect_signals()
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Set fixed height
        self.setFixedHeight(self.line_height)
    
    def _setup_ui(self) -> None:
        """Setup the user interface layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # Line number label
        self.line_number_label = QLabel(f"{self.line_index + 1:02d}")
        self.line_number_label.setFixedWidth(30)
        self.line_number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.line_number_label)
        
        # Text editing area
        text_container = QFrame()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(4, 2, 4, 2)
        text_layout.setSpacing(2)
        
        # Text editor
        self.text_editor = QLineEdit(self.subtitle_line.text)
        self.text_editor.setPlaceholderText("Enter subtitle text...")
        text_layout.addWidget(self.text_editor)
        
        # Timing controls
        timing_layout = QHBoxLayout()
        timing_layout.setSpacing(4)
        
        # Start time
        timing_layout.addWidget(QLabel("Start:"))
        self.start_time_spinbox = QDoubleSpinBox()
        self.start_time_spinbox.setRange(0.0, 9999.99)
        self.start_time_spinbox.setDecimals(2)
        self.start_time_spinbox.setSuffix("s")
        self.start_time_spinbox.setValue(self.subtitle_line.start_time)
        self.start_time_spinbox.setFixedWidth(80)
        timing_layout.addWidget(self.start_time_spinbox)
        
        # End time
        timing_layout.addWidget(QLabel("End:"))
        self.end_time_spinbox = QDoubleSpinBox()
        self.end_time_spinbox.setRange(0.0, 9999.99)
        self.end_time_spinbox.setDecimals(2)
        self.end_time_spinbox.setSuffix("s")
        self.end_time_spinbox.setValue(self.subtitle_line.end_time)
        self.end_time_spinbox.setFixedWidth(80)
        timing_layout.addWidget(self.end_time_spinbox)
        
        # Duration display
        duration = self.subtitle_line.end_time - self.subtitle_line.start_time
        self.duration_label = QLabel(f"({duration:.2f}s)")
        self.duration_label.setStyleSheet("color: #888; font-size: 11px;")
        timing_layout.addWidget(self.duration_label)
        
        timing_layout.addStretch()
        text_layout.addLayout(timing_layout)
        
        layout.addWidget(text_container, 1)  # Text area takes remaining space
        
        # Timeline visualization area
        self.timeline_widget = TimelineVisualizationWidget(
            self.subtitle_line, self.timeline_scale
        )
        self.timeline_widget.setFixedWidth(200)  # Fixed width for timeline
        layout.addWidget(self.timeline_widget)
    
    def _setup_style(self) -> None:
        """Setup widget styling."""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self._update_selection_style()
        
        # Style components
        self.line_number_label.setStyleSheet("""
            QLabel {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ccc;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        self.text_editor.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 3px;
                color: #fff;
                padding: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        
        spinbox_style = """
            QDoubleSpinBox {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ccc;
                padding: 2px;
                font-size: 11px;
            }
            QDoubleSpinBox:focus {
                border-color: #4a90e2;
            }
        """
        
        self.start_time_spinbox.setStyleSheet(spinbox_style)
        self.end_time_spinbox.setStyleSheet(spinbox_style)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.text_editor.textChanged.connect(self._on_text_changed)
        self.start_time_spinbox.valueChanged.connect(self._on_timing_changed)
        self.end_time_spinbox.valueChanged.connect(self._on_timing_changed)
        
        # Connect timeline widget signals
        self.timeline_widget.timing_changed.connect(self._on_timeline_timing_changed)
    
    def _update_selection_style(self) -> None:
        """Update widget style based on selection state."""
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #3a4a5a;
                    border: 2px solid #4a90e2;
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2a2a2a;
                    border: 1px solid #555;
                    border-radius: 4px;
                }
                QFrame:hover {
                    border-color: #666;
                }
            """)
    
    def _on_text_changed(self) -> None:
        """Handle text change in editor."""
        new_text = self.text_editor.text()
        if new_text != self.subtitle_line.text:
            self.subtitle_line.text = new_text
            self.line_text_changed.emit(self.line_index, new_text)
    
    def _on_timing_changed(self) -> None:
        """Handle timing change in spinboxes."""
        start_time = self.start_time_spinbox.value()
        end_time = self.end_time_spinbox.value()
        
        # Validate timing
        if end_time <= start_time:
            end_time = start_time + self.min_duration
            self.end_time_spinbox.setValue(end_time)
        
        # Update duration display
        duration = end_time - start_time
        self.duration_label.setText(f"({duration:.2f}s)")
        
        # Update subtitle line data
        self.subtitle_line.start_time = start_time
        self.subtitle_line.end_time = end_time
        
        # Update timeline visualization
        self.timeline_widget.update_timing(start_time, end_time)
        
        # Emit signal
        self.line_timing_changed.emit(self.line_index, start_time, end_time)
    
    def _on_timeline_timing_changed(self, start_time: float, end_time: float) -> None:
        """Handle timing change from timeline visualization."""
        # Update spinboxes
        self.start_time_spinbox.setValue(start_time)
        self.end_time_spinbox.setValue(end_time)
        
        # This will trigger _on_timing_changed which handles the rest
    
    def set_selected(self, selected: bool) -> None:
        """Set the selection state of this widget."""
        if self.is_selected != selected:
            self.is_selected = selected
            self._update_selection_style()
    
    def set_timeline_scale(self, scale: float) -> None:
        """Update the timeline scale."""
        self.timeline_scale = scale
        self.timeline_widget.set_scale(scale)
    
    def update_line_data(self, subtitle_line: SubtitleLine) -> None:
        """Update the widget with new subtitle line data."""
        self.subtitle_line = subtitle_line
        
        # Update UI elements
        self.text_editor.setText(subtitle_line.text)
        self.start_time_spinbox.setValue(subtitle_line.start_time)
        self.end_time_spinbox.setValue(subtitle_line.end_time)
        
        duration = subtitle_line.end_time - subtitle_line.start_time
        self.duration_label.setText(f"({duration:.2f}s)")
        
        # Update timeline visualization
        self.timeline_widget.update_timing(subtitle_line.start_time, subtitle_line.end_time)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for selection."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if Ctrl is pressed for multi-selection
            add_to_selection = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            self.line_selected.emit(self.line_index, add_to_selection)
        
        super().mousePressEvent(event)
    
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Handle context menu request."""
        self.line_context_menu.emit(self.line_index, event.globalPos())


class TimelineVisualizationWidget(QWidget):
    """
    Widget for visualizing and editing subtitle timing on a timeline.
    
    Features:
    - Visual timing bar with duration representation
    - Draggable start/end handles
    - Draggable body for moving entire timing
    - Hover effects and visual feedback
    """
    
    # Signals
    timing_changed = pyqtSignal(float, float)  # start_time, end_time
    
    def __init__(self, subtitle_line: SubtitleLine, scale: float = 1.0, 
                 parent: Optional[QWidget] = None):
        """
        Initialize the timeline visualization widget.
        
        Args:
            subtitle_line: The subtitle line to visualize
            scale: Pixels per second for timeline scale
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.subtitle_line = subtitle_line
        self.scale = scale
        
        # Dragging state
        self.is_dragging_start = False
        self.is_dragging_end = False
        self.is_dragging_body = False
        self.drag_start_pos = QPoint()
        self.original_start_time = 0.0
        self.original_end_time = 0.0
        
        # Visual properties
        self.handle_width = 6
        self.bar_height = 20
        self.min_duration = 0.1
        
        # Colors
        self.bar_color = QColor(74, 144, 226)
        self.bar_hover_color = QColor(90, 160, 242)
        self.handle_color = QColor(255, 255, 255)
        self.handle_hover_color = QColor(255, 255, 150)
        
        # Mouse tracking
        self.setMouseTracking(True)
        self.hover_area = None  # 'start', 'end', 'body', or None
        
        # Set minimum size
        self.setMinimumSize(100, 40)
    
    def set_scale(self, scale: float) -> None:
        """Update the timeline scale."""
        self.scale = scale
        self.update()
    
    def update_timing(self, start_time: float, end_time: float) -> None:
        """Update the timing values."""
        self.subtitle_line.start_time = start_time
        self.subtitle_line.end_time = end_time
        self.update()
    
    def _get_bar_rect(self) -> QRect:
        """Get the rectangle for the timing bar."""
        widget_rect = self.rect()
        
        # Calculate bar position and size
        start_x = int(self.subtitle_line.start_time * self.scale)
        duration = self.subtitle_line.end_time - self.subtitle_line.start_time
        width = max(int(duration * self.scale), 10)  # Minimum width for visibility
        
        # Center vertically
        y = (widget_rect.height() - self.bar_height) // 2
        
        return QRect(start_x, y, width, self.bar_height)
    
    def _get_start_handle_rect(self) -> QRect:
        """Get the rectangle for the start handle."""
        bar_rect = self._get_bar_rect()
        return QRect(
            bar_rect.left() - self.handle_width // 2,
            bar_rect.top(),
            self.handle_width,
            bar_rect.height()
        )
    
    def _get_end_handle_rect(self) -> QRect:
        """Get the rectangle for the end handle."""
        bar_rect = self._get_bar_rect()
        return QRect(
            bar_rect.right() - self.handle_width // 2,
            bar_rect.top(),
            self.handle_width,
            bar_rect.height()
        )
    
    def _get_hover_area(self, pos: QPoint) -> Optional[str]:
        """Determine which area the mouse is hovering over."""
        start_handle = self._get_start_handle_rect()
        end_handle = self._get_end_handle_rect()
        bar_rect = self._get_bar_rect()
        
        if start_handle.contains(pos):
            return 'start'
        elif end_handle.contains(pos):
            return 'end'
        elif bar_rect.contains(pos):
            return 'body'
        else:
            return None
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the timeline visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get rectangles
        bar_rect = self._get_bar_rect()
        start_handle = self._get_start_handle_rect()
        end_handle = self._get_end_handle_rect()
        
        # Draw timing bar
        bar_color = self.bar_hover_color if self.hover_area == 'body' else self.bar_color
        painter.fillRect(bar_rect, bar_color)
        
        # Draw border
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.drawRect(bar_rect)
        
        # Draw handles
        start_color = self.handle_hover_color if self.hover_area == 'start' else self.handle_color
        end_color = self.handle_hover_color if self.hover_area == 'end' else self.handle_color
        
        painter.fillRect(start_handle, start_color)
        painter.fillRect(end_handle, end_color)
        
        # Draw handle borders
        painter.setPen(QPen(QColor(0, 0, 0, 150), 1))
        painter.drawRect(start_handle)
        painter.drawRect(end_handle)
        
        # Draw timing text
        duration = self.subtitle_line.end_time - self.subtitle_line.start_time
        timing_text = f"{self.subtitle_line.start_time:.1f}s - {self.subtitle_line.end_time:.1f}s ({duration:.1f}s)"
        
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 8))
        
        text_rect = QRect(bar_rect.left(), bar_rect.bottom() + 2, 
                         self.width() - bar_rect.left(), 15)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, timing_text)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            hover_area = self._get_hover_area(event.pos())
            
            if hover_area == 'start':
                self.is_dragging_start = True
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif hover_area == 'end':
                self.is_dragging_end = True
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif hover_area == 'body':
                self.is_dragging_body = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
            if hover_area:
                self.drag_start_pos = event.pos()
                self.original_start_time = self.subtitle_line.start_time
                self.original_end_time = self.subtitle_line.end_time
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for dragging and hover effects."""
        try:
            if self.is_dragging_start or self.is_dragging_end or self.is_dragging_body:
                # Calculate time delta from drag
                delta_x = event.pos().x() - self.drag_start_pos.x()
                delta_time = delta_x / self.scale if self.scale > 0 else 0
                
                if self.is_dragging_start:
                    # Drag start handle
                    new_start = max(0, self.original_start_time + delta_time)
                    new_end = self.original_end_time
                    
                    # Ensure minimum duration
                    if new_end - new_start < self.min_duration:
                        new_start = new_end - self.min_duration
                    
                    self.timing_changed.emit(new_start, new_end)
                    
                elif self.is_dragging_end:
                    # Drag end handle
                    new_start = self.original_start_time
                    new_end = max(self.original_start_time + self.min_duration, 
                                 self.original_end_time + delta_time)
                    
                    self.timing_changed.emit(new_start, new_end)
                    
                elif self.is_dragging_body:
                    # Drag entire timing
                    new_start = max(0, self.original_start_time + delta_time)
                    duration = self.original_end_time - self.original_start_time
                    new_end = new_start + duration
                    
                    self.timing_changed.emit(new_start, new_end)
            
            else:
                # Update hover effects
                new_hover_area = self._get_hover_area(event.pos())
                if new_hover_area != self.hover_area:
                    self.hover_area = new_hover_area
                    
                    # Update cursor
                    if self.hover_area in ['start', 'end']:
                        self.setCursor(Qt.CursorShape.SizeHorCursor)
                    elif self.hover_area == 'body':
                        self.setCursor(Qt.CursorShape.OpenHandCursor)
                    else:
                        self.setCursor(Qt.CursorShape.ArrowCursor)
                    
                    self.update()
            
            super().mouseMoveEvent(event)
        except RuntimeError:
            # Widget has been deleted, ignore the event
            pass
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release to end dragging."""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.is_dragging_start = False
                self.is_dragging_end = False
                self.is_dragging_body = False
                
                # Reset cursor based on current hover area
                hover_area = self._get_hover_area(event.pos())
                if hover_area in ['start', 'end']:
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                elif hover_area == 'body':
                    self.setCursor(Qt.CursorShape.OpenHandCursor)
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            
            super().mouseReleaseEvent(event)
        except RuntimeError:
            # Widget has been deleted, ignore the event
            pass
    
    def leaveEvent(self, event) -> None:
        """Handle mouse leave to clear hover effects."""
        try:
            self.hover_area = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()
            super().leaveEvent(event)
        except RuntimeError:
            # Widget has been deleted, ignore the event
            pass


class SubtitleEditor(QWidget):
    """
    Comprehensive subtitle timeline editor widget.
    
    Features:
    - QScrollArea with custom subtitle line widgets
    - Timing visualization with draggable duration bars
    - Direct text editing with live preview updates
    - Batch selection capabilities using QItemSelectionModel
    - Timing adjustment controls with numerical input and drag functionality
    - Context menu support
    - Keyboard shortcuts
    - Zoom and pan functionality
    """
    
    # Signals for communication with application
    subtitle_data_changed = pyqtSignal(SubtitleData)
    line_selected = pyqtSignal(int)  # line_index
    selection_changed = pyqtSignal(TimelineSelection)
    preview_update_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the subtitle editor."""
        super().__init__(parent)
        
        # Data
        self.subtitle_data: Optional[SubtitleData] = None
        self.line_widgets: List[SubtitleLineWidget] = []
        
        # Selection management
        self.selection = TimelineSelection(set())
        
        # Timeline properties
        self.timeline_scale = 50.0  # Pixels per second
        self.min_scale = 10.0
        self.max_scale = 200.0
        
        # UI state
        self.is_batch_editing = False
        
        # Setup UI
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # Main scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container widget for subtitle lines
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(8, 8, 8, 8)
        self.container_layout.setSpacing(2)
        
        # Add stretch to push lines to top
        self.container_layout.addStretch()
        
        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)
        
        # Status bar
        status_bar = self._create_status_bar()
        layout.addWidget(status_bar)
        
        # Style the scroll area
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
        """)
    
    def _create_toolbar(self) -> QFrame:
        """Create the toolbar with editing controls."""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Add line button
        self.add_line_button = QPushButton("Add Line")
        self.add_line_button.setToolTip("Add new subtitle line")
        
        # Delete line button
        self.delete_line_button = QPushButton("Delete Selected")
        self.delete_line_button.setToolTip("Delete selected subtitle lines")
        self.delete_line_button.setEnabled(False)
        
        # Batch edit button
        self.batch_edit_button = QPushButton("Batch Edit")
        self.batch_edit_button.setToolTip("Edit multiple lines simultaneously")
        self.batch_edit_button.setEnabled(False)
        self.batch_edit_button.setCheckable(True)
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setFixedSize(24, 24)
        self.zoom_out_button.setToolTip("Zoom out timeline")
        
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setFixedSize(24, 24)
        self.zoom_in_button.setToolTip("Zoom in timeline")
        
        self.zoom_fit_button = QPushButton("Fit")
        self.zoom_fit_button.setToolTip("Fit all subtitles in view")
        
        # Scale display
        self.scale_label = QLabel(f"{self.timeline_scale:.0f}px/s")
        self.scale_label.setMinimumWidth(60)
        
        # Add widgets to layout
        layout.addWidget(self.add_line_button)
        layout.addWidget(self.delete_line_button)
        layout.addWidget(self.batch_edit_button)
        layout.addWidget(QFrame())  # Separator
        layout.addWidget(zoom_label)
        layout.addWidget(self.zoom_out_button)
        layout.addWidget(self.zoom_in_button)
        layout.addWidget(self.zoom_fit_button)
        layout.addWidget(self.scale_label)
        layout.addStretch()
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ccc;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666;
                border-color: #444;
            }
            QPushButton:checked {
                background-color: #4a90e2;
                border-color: #357abd;
            }
        """
        
        for button in [self.add_line_button, self.delete_line_button, 
                      self.batch_edit_button, self.zoom_out_button, 
                      self.zoom_in_button, self.zoom_fit_button]:
            button.setStyleSheet(button_style)
        
        return toolbar
    
    def _create_status_bar(self) -> QFrame:
        """Create the status bar with selection info."""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(8, 2, 8, 2)
        
        self.status_label = QLabel("No subtitles loaded")
        self.status_label.setStyleSheet("color: #ccc; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.selection_label)
        
        return status_bar
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Delete selected lines
        self.delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        self.delete_shortcut.activated.connect(self._delete_selected_lines)
        
        # Select all
        self.select_all_shortcut = QShortcut(QKeySequence.StandardKey.SelectAll, self)
        self.select_all_shortcut.activated.connect(self._select_all_lines)
        
        # Zoom shortcuts
        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.zoom_in_shortcut.activated.connect(self._zoom_in)
        
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_shortcut.activated.connect(self._zoom_out)
        
        self.zoom_fit_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        self.zoom_fit_shortcut.activated.connect(self._zoom_fit)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Toolbar buttons
        self.add_line_button.clicked.connect(self._add_new_line)
        self.delete_line_button.clicked.connect(self._delete_selected_lines)
        self.batch_edit_button.toggled.connect(self._toggle_batch_edit)
        
        # Zoom controls
        self.zoom_in_button.clicked.connect(self._zoom_in)
        self.zoom_out_button.clicked.connect(self._zoom_out)
        self.zoom_fit_button.clicked.connect(self._zoom_fit)
    
    def set_subtitle_data(self, subtitle_data: SubtitleData) -> None:
        """
        Set the subtitle data to edit.
        
        Args:
            subtitle_data: The subtitle data to load
        """
        self.subtitle_data = subtitle_data
        self._rebuild_line_widgets()
        self._update_status()
    
    def _rebuild_line_widgets(self) -> None:
        """Rebuild all line widgets from current subtitle data."""
        # Clear existing widgets
        for widget in self.line_widgets:
            widget.setParent(None)
        self.line_widgets.clear()
        
        if not self.subtitle_data or not self.subtitle_data.lines:
            return
        
        # Create new widgets
        for i, line in enumerate(self.subtitle_data.lines):
            widget = SubtitleLineWidget(i, line, self.timeline_scale)
            
            # Connect signals
            widget.line_selected.connect(self._on_line_selected)
            widget.line_text_changed.connect(self._on_line_text_changed)
            widget.line_timing_changed.connect(self._on_line_timing_changed)
            widget.line_context_menu.connect(self._on_line_context_menu)
            
            # Insert before stretch
            self.container_layout.insertWidget(i, widget)
            self.line_widgets.append(widget)
        
        # Clear selection
        self.selection = TimelineSelection(set())
        self._update_selection_ui()
    
    def _on_line_selected(self, line_index: int, add_to_selection: bool) -> None:
        """Handle line selection."""
        if add_to_selection:
            # Toggle selection
            if line_index in self.selection.line_indices:
                self.selection.line_indices.remove(line_index)
            else:
                self.selection.line_indices.add(line_index)
        else:
            # Single selection
            self.selection.line_indices = {line_index}
        
        self._update_selection_ui()
        self.selection_changed.emit(self.selection)
        
        if len(self.selection.line_indices) == 1:
            self.line_selected.emit(line_index)
    
    def _on_line_text_changed(self, line_index: int, new_text: str) -> None:
        """Handle text change in a line."""
        if (self.subtitle_data and 
            0 <= line_index < len(self.subtitle_data.lines)):
            
            self.subtitle_data.lines[line_index].text = new_text
            self.subtitle_data_changed.emit(self.subtitle_data)
            self.preview_update_requested.emit()
    
    def _on_line_timing_changed(self, line_index: int, start_time: float, end_time: float) -> None:
        """Handle timing change in a line."""
        if (self.subtitle_data and 
            0 <= line_index < len(self.subtitle_data.lines)):
            
            line = self.subtitle_data.lines[line_index]
            line.start_time = start_time
            line.end_time = end_time
            
            # Re-sort lines by start time
            self.subtitle_data.lines.sort(key=lambda x: x.start_time)
            
            # Rebuild widgets to reflect new order
            self._rebuild_line_widgets()
            
            self.subtitle_data_changed.emit(self.subtitle_data)
            self.preview_update_requested.emit()
    
    def _on_line_context_menu(self, line_index: int, global_pos: QPoint) -> None:
        """Handle context menu request for a line."""
        menu = QMenu(self)
        
        # Add actions
        duplicate_action = menu.addAction("Duplicate Line")
        duplicate_action.triggered.connect(lambda: self._duplicate_line(line_index))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete Line")
        delete_action.triggered.connect(lambda: self._delete_line(line_index))
        
        if len(self.selection.line_indices) > 1:
            menu.addSeparator()
            delete_selected_action = menu.addAction(f"Delete {len(self.selection.line_indices)} Selected Lines")
            delete_selected_action.triggered.connect(self._delete_selected_lines)
        
        menu.exec(global_pos)
    
    def _update_selection_ui(self) -> None:
        """Update UI to reflect current selection."""
        # Update line widget selection states
        for i, widget in enumerate(self.line_widgets):
            widget.set_selected(i in self.selection.line_indices)
        
        # Update toolbar buttons
        has_selection = not self.selection.is_empty()
        self.delete_line_button.setEnabled(has_selection)
        self.batch_edit_button.setEnabled(len(self.selection.line_indices) > 1)
        
        # Update selection label
        if self.selection.is_empty():
            self.selection_label.setText("")
        elif len(self.selection.line_indices) == 1:
            index = next(iter(self.selection.line_indices))
            self.selection_label.setText(f"Line {index + 1} selected")
        else:
            self.selection_label.setText(f"{len(self.selection.line_indices)} lines selected")
    
    def _update_status(self) -> None:
        """Update status bar information."""
        if not self.subtitle_data or not self.subtitle_data.lines:
            self.status_label.setText("No subtitles loaded")
        else:
            count = len(self.subtitle_data.lines)
            duration = self.subtitle_data.total_duration
            self.status_label.setText(f"{count} lines, {duration:.1f}s total duration")
    
    def _add_new_line(self) -> None:
        """Add a new subtitle line."""
        if not self.subtitle_data:
            self.subtitle_data = SubtitleData()
        
        # Determine start time for new line
        if self.subtitle_data.lines:
            # Add after the last line
            last_line = self.subtitle_data.lines[-1]
            start_time = last_line.end_time + 0.5
        else:
            start_time = 0.0
        
        end_time = start_time + 2.0  # Default 2-second duration
        
        try:
            self.subtitle_data.add_line(start_time, end_time, "New subtitle line")
            self._rebuild_line_widgets()
            self._update_status()
            
            # Select the new line
            new_index = len(self.subtitle_data.lines) - 1
            self.selection.line_indices = {new_index}
            self._update_selection_ui()
            
            # Scroll to new line
            if self.line_widgets:
                new_widget = self.line_widgets[-1]
                self.scroll_area.ensureWidgetVisible(new_widget)
            
            self.subtitle_data_changed.emit(self.subtitle_data)
            
        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
    
    def _delete_selected_lines(self) -> None:
        """Delete selected subtitle lines."""
        if self.selection.is_empty() or not self.subtitle_data:
            return
        
        # Confirm deletion
        count = len(self.selection.line_indices)
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete {count} selected subtitle line{'s' if count > 1 else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Delete lines (in reverse order to maintain indices)
        indices = sorted(self.selection.line_indices, reverse=True)
        for index in indices:
            if 0 <= index < len(self.subtitle_data.lines):
                del self.subtitle_data.lines[index]
        
        # Clear selection and rebuild
        self.selection = TimelineSelection(set())
        self._rebuild_line_widgets()
        self._update_status()
        
        self.subtitle_data_changed.emit(self.subtitle_data)
    
    def _delete_line(self, line_index: int) -> None:
        """Delete a specific line."""
        self.selection.line_indices = {line_index}
        self._delete_selected_lines()
    
    def _duplicate_line(self, line_index: int) -> None:
        """Duplicate a specific line."""
        if (not self.subtitle_data or 
            line_index < 0 or line_index >= len(self.subtitle_data.lines)):
            return
        
        original_line = self.subtitle_data.lines[line_index]
        
        # Create duplicate with offset timing
        start_time = original_line.end_time + 0.5
        end_time = start_time + (original_line.end_time - original_line.start_time)
        
        try:
            self.subtitle_data.add_line(
                start_time, end_time, original_line.text,
                original_line.words.copy(), original_line.style_overrides.copy()
            )
            
            self._rebuild_line_widgets()
            self._update_status()
            self.subtitle_data_changed.emit(self.subtitle_data)
            
        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
    
    def _select_all_lines(self) -> None:
        """Select all subtitle lines."""
        if not self.subtitle_data:
            return
        
        self.selection.line_indices = set(range(len(self.subtitle_data.lines)))
        self._update_selection_ui()
        self.selection_changed.emit(self.selection)
    
    def _toggle_batch_edit(self, enabled: bool) -> None:
        """Toggle batch editing mode."""
        self.is_batch_editing = enabled
        # TODO: Implement batch editing UI
    
    def _zoom_in(self) -> None:
        """Zoom in on the timeline."""
        new_scale = min(self.timeline_scale * 1.5, self.max_scale)
        self._set_timeline_scale(new_scale)
    
    def _zoom_out(self) -> None:
        """Zoom out on the timeline."""
        new_scale = max(self.timeline_scale / 1.5, self.min_scale)
        self._set_timeline_scale(new_scale)
    
    def _zoom_fit(self) -> None:
        """Fit all subtitles in the timeline view."""
        if not self.subtitle_data or not self.subtitle_data.lines:
            return
        
        # Calculate scale to fit all subtitles
        total_duration = self.subtitle_data.total_duration
        if total_duration > 0:
            available_width = self.scroll_area.viewport().width() - 50  # Account for margins
            new_scale = available_width / total_duration
            new_scale = max(self.min_scale, min(new_scale, self.max_scale))
            self._set_timeline_scale(new_scale)
    
    def _set_timeline_scale(self, scale: float) -> None:
        """Set the timeline scale and update all widgets."""
        self.timeline_scale = scale
        self.scale_label.setText(f"{scale:.0f}px/s")
        
        # Update all line widgets
        for widget in self.line_widgets:
            widget.set_timeline_scale(scale)
    
    def get_selected_lines(self) -> List[SubtitleLine]:
        """Get the currently selected subtitle lines."""
        if not self.subtitle_data:
            return []
        
        return [self.subtitle_data.lines[i] for i in self.selection.line_indices
                if i < len(self.subtitle_data.lines)]
    
    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.selection = TimelineSelection(set())
        self._update_selection_ui()
        self.selection_changed.emit(self.selection)
    
    def select_line(self, line_index: int) -> None:
        """Select a specific line."""
        if (self.subtitle_data and 
            0 <= line_index < len(self.subtitle_data.lines)):
            
            self.selection.line_indices = {line_index}
            self._update_selection_ui()
            self.selection_changed.emit(self.selection)
    
    def scroll_to_line(self, line_index: int) -> None:
        """Scroll to make a specific line visible."""
        if 0 <= line_index < len(self.line_widgets):
            widget = self.line_widgets[line_index]
            self.scroll_area.ensureWidgetVisible(widget)
    
    def scroll_to_time(self, time: float) -> None:
        """Scroll to show a specific time in the timeline."""
        if not self.subtitle_data:
            return
        
        # Find the line that contains this time
        for i, line in enumerate(self.subtitle_data.lines):
            if line.start_time <= time <= line.end_time:
                self.scroll_to_line(i)
                break