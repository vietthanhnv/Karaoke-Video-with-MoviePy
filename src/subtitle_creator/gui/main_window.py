"""
Main window implementation for the Subtitle Creator with Effects application.

This module provides the MainWindow class which serves as the primary GUI container
for the application, implementing the layout structure, menu system, toolbar, and
window state management.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSettings, QSize, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QPixmap, QAction, QActionGroup

from .preview_panel import PreviewPanel


class MainWindow(QMainWindow):
    """
    Main application window with responsive layout and comprehensive menu system.
    
    Provides a three-panel layout:
    - Left panel (60%): Preview and timeline controls
    - Right panel (40%): Effects and styling controls  
    - Bottom panel: Timeline editor (collapsible)
    
    Features:
    - Complete menu bar with File, Edit, View, Effects, Help menus
    - Toolbar with common actions
    - Window state persistence
    - Responsive layout with splitter controls
    """
    
    # Signals for communication with application controller
    project_new_requested = pyqtSignal()
    project_open_requested = pyqtSignal(str)  # file_path
    project_save_requested = pyqtSignal()
    project_save_as_requested = pyqtSignal(str)  # file_path
    project_export_requested = pyqtSignal()
    
    # Import signals
    import_media_requested = pyqtSignal(str)  # file_path
    import_subtitles_requested = pyqtSignal(str)  # file_path
    import_audio_requested = pyqtSignal(str)  # file_path
    
    playback_play_requested = pyqtSignal()
    playback_pause_requested = pyqtSignal()
    playback_stop_requested = pyqtSignal()
    audio_preview_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the main window with layout and components."""
        super().__init__(parent)
        
        # Window configuration
        self.setWindowTitle("Subtitle Creator with Effects")
        self.setMinimumSize(1200, 800)
        
        # Settings for persistence
        self.settings = QSettings("SubtitleCreator", "MainWindow")
        
        # Initialize UI components
        self._setup_actions()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_layout()
        self._setup_status_bar()
        
        # Restore window state
        self._restore_window_state()
        
        # Connect internal signals
        self._connect_signals()
    
    def _setup_actions(self) -> None:
        """Create all actions for menus and toolbar."""
        # File menu actions
        self.action_new = QAction("&New Project", self)
        self.action_new.setShortcut(QKeySequence.StandardKey.New)
        self.action_new.setStatusTip("Create a new subtitle project")
        
        self.action_open = QAction("&Open Project...", self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.setStatusTip("Open an existing subtitle project")
        
        self.action_save = QAction("&Save Project", self)
        self.action_save.setShortcut(QKeySequence.StandardKey.Save)
        self.action_save.setStatusTip("Save the current project")
        self.action_save.setEnabled(False)
        
        self.action_save_as = QAction("Save Project &As...", self)
        self.action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.action_save_as.setStatusTip("Save the project with a new name")
        self.action_save_as.setEnabled(False)
        
        self.action_import_media = QAction("Import &Background Media...", self)
        self.action_import_media.setStatusTip("Import background image or video")
        
        self.action_import_subtitles = QAction("Import &Subtitles...", self)
        self.action_import_subtitles.setStatusTip("Import subtitle file (JSON or ASS)")
        
        self.action_import_audio = QAction("Import &Audio...", self)
        self.action_import_audio.setStatusTip("Import audio file")
        
        self.action_export = QAction("&Export Video...", self)
        self.action_export.setShortcut(QKeySequence("Ctrl+E"))
        self.action_export.setStatusTip("Export the final video")
        self.action_export.setEnabled(False)
        
        self.action_exit = QAction("E&xit", self)
        self.action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_exit.setStatusTip("Exit the application")
        
        # Edit menu actions
        self.action_undo = QAction("&Undo", self)
        self.action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.action_undo.setStatusTip("Undo the last action")
        self.action_undo.setEnabled(False)
        
        self.action_redo = QAction("&Redo", self)
        self.action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.action_redo.setStatusTip("Redo the last undone action")
        self.action_redo.setEnabled(False)
        
        self.action_cut = QAction("Cu&t", self)
        self.action_cut.setShortcut(QKeySequence.StandardKey.Cut)
        self.action_cut.setStatusTip("Cut selected text")
        self.action_cut.setEnabled(False)
        
        self.action_copy = QAction("&Copy", self)
        self.action_copy.setShortcut(QKeySequence.StandardKey.Copy)
        self.action_copy.setStatusTip("Copy selected text")
        self.action_copy.setEnabled(False)
        
        self.action_paste = QAction("&Paste", self)
        self.action_paste.setShortcut(QKeySequence.StandardKey.Paste)
        self.action_paste.setStatusTip("Paste text from clipboard")
        self.action_paste.setEnabled(False)
        
        self.action_select_all = QAction("Select &All", self)
        self.action_select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.action_select_all.setStatusTip("Select all subtitle lines")
        self.action_select_all.setEnabled(False)
        
        # View menu actions
        self.action_zoom_in = QAction("Zoom &In", self)
        self.action_zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.action_zoom_in.setStatusTip("Zoom in on the timeline")
        
        self.action_zoom_out = QAction("Zoom &Out", self)
        self.action_zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.action_zoom_out.setStatusTip("Zoom out on the timeline")
        
        self.action_zoom_fit = QAction("&Fit to Window", self)
        self.action_zoom_fit.setShortcut(QKeySequence("Ctrl+0"))
        self.action_zoom_fit.setStatusTip("Fit timeline to window width")
        
        self.action_toggle_timeline = QAction("Show/Hide &Timeline", self)
        self.action_toggle_timeline.setShortcut(QKeySequence("Ctrl+T"))
        self.action_toggle_timeline.setStatusTip("Toggle timeline panel visibility")
        self.action_toggle_timeline.setCheckable(True)
        self.action_toggle_timeline.setChecked(True)
        
        self.action_toggle_effects = QAction("Show/Hide &Effects Panel", self)
        self.action_toggle_effects.setShortcut(QKeySequence("Ctrl+F"))
        self.action_toggle_effects.setStatusTip("Toggle effects panel visibility")
        self.action_toggle_effects.setCheckable(True)
        self.action_toggle_effects.setChecked(True)
        
        # Playback actions
        self.action_play = QAction("&Play", self)
        self.action_play.setShortcut(QKeySequence("Space"))
        self.action_play.setStatusTip("Play/pause preview")
        self.action_play.setCheckable(True)
        
        self.action_stop = QAction("&Stop", self)
        self.action_stop.setShortcut(QKeySequence("Ctrl+."))
        self.action_stop.setStatusTip("Stop playback")
        
        # Audio preview action
        self.action_preview_audio = QAction("Preview &Audio", self)
        self.action_preview_audio.setShortcut(QKeySequence("Ctrl+A"))
        self.action_preview_audio.setStatusTip("Preview audio (first 10 seconds)")
        self.action_preview_audio.setEnabled(False)  # Enabled when audio is loaded
        
        # Effects menu actions
        self.action_apply_preset = QAction("Apply &Preset...", self)
        self.action_apply_preset.setStatusTip("Apply a saved effect preset")
        
        self.action_save_preset = QAction("&Save Current as Preset...", self)
        self.action_save_preset.setStatusTip("Save current effects as a preset")
        self.action_save_preset.setEnabled(False)
        
        self.action_reset_effects = QAction("&Reset All Effects", self)
        self.action_reset_effects.setStatusTip("Remove all applied effects")
        self.action_reset_effects.setEnabled(False)
        
        # Help menu actions
        self.action_user_guide = QAction("&User Guide", self)
        self.action_user_guide.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.action_user_guide.setStatusTip("Open the user guide")
        
        self.action_keyboard_shortcuts = QAction("&Keyboard Shortcuts", self)
        self.action_keyboard_shortcuts.setStatusTip("Show keyboard shortcuts")
        
        self.action_about = QAction("&About", self)
        self.action_about.setStatusTip("About Subtitle Creator with Effects")
    
    def _setup_menu_bar(self) -> None:
        """Create the menu bar with all menus and actions."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.action_new)
        file_menu.addAction(self.action_open)
        file_menu.addSeparator()
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        file_menu.addSeparator()
        
        import_menu = file_menu.addMenu("&Import")
        import_menu.addAction(self.action_import_media)
        import_menu.addAction(self.action_import_subtitles)
        import_menu.addAction(self.action_import_audio)
        
        file_menu.addSeparator()
        file_menu.addAction(self.action_export)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.action_undo)
        edit_menu.addAction(self.action_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_cut)
        edit_menu.addAction(self.action_copy)
        edit_menu.addAction(self.action_paste)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_select_all)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.action_zoom_in)
        view_menu.addAction(self.action_zoom_out)
        view_menu.addAction(self.action_zoom_fit)
        view_menu.addSeparator()
        view_menu.addAction(self.action_toggle_timeline)
        view_menu.addAction(self.action_toggle_effects)
        
        # Effects menu
        effects_menu = menubar.addMenu("&Effects")
        effects_menu.addAction(self.action_apply_preset)
        effects_menu.addAction(self.action_save_preset)
        effects_menu.addSeparator()
        effects_menu.addAction(self.action_reset_effects)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.action_user_guide)
        help_menu.addAction(self.action_keyboard_shortcuts)
        help_menu.addSeparator()
        help_menu.addAction(self.action_about)
    
    def _setup_toolbar(self) -> None:
        """Create the main toolbar with common actions."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setObjectName("MainToolbar")  # For state persistence
        
        # File operations
        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_open)
        toolbar.addAction(self.action_save)
        toolbar.addSeparator()
        
        # Playback controls
        toolbar.addAction(self.action_play)
        toolbar.addAction(self.action_stop)
        toolbar.addAction(self.action_preview_audio)
        toolbar.addSeparator()
        
        # Export
        toolbar.addAction(self.action_export)
        
        # Make toolbar movable and allow context menu
        toolbar.setMovable(True)
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
    
    def _setup_layout(self) -> None:
        """Create the main layout with three-panel design."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Create main horizontal splitter (left/right panels)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setObjectName("MainSplitter")
        
        # Create vertical splitter for left panel (preview/timeline)
        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        self.left_splitter.setObjectName("LeftSplitter")
        
        # Left panel - Preview area
        self.preview_panel = PreviewPanel()
        self.preview_panel.setMinimumSize(400, 300)
        
        # Bottom panel - Subtitle timeline editor
        from .subtitle_editor import SubtitleEditor
        self.subtitle_editor = SubtitleEditor()
        self.subtitle_editor.setMinimumHeight(150)
        self.subtitle_editor.setMaximumHeight(400)
        
        # Add widgets to left splitter
        self.left_splitter.addWidget(self.preview_panel)
        self.left_splitter.addWidget(self.subtitle_editor)
        
        # Set initial sizes for left splitter (preview larger than timeline)
        self.left_splitter.setSizes([400, 200])
        self.left_splitter.setStretchFactor(0, 1)  # Preview stretches
        self.left_splitter.setStretchFactor(1, 0)  # Timeline fixed height
        
        # Right panel - Effects control panel
        from .effects_panel import EffectsPanel
        self.effects_panel = EffectsPanel()
        self.effects_panel.setMinimumSize(300, 400)
        self.effects_panel.effects_changed.connect(self._on_effects_changed)
        
        # Add panels to main splitter
        self.main_splitter.addWidget(self.left_splitter)
        self.main_splitter.addWidget(self.effects_panel)
        
        # Set initial sizes (60% left, 40% right)
        self.main_splitter.setSizes([720, 480])  # Based on 1200px width
        self.main_splitter.setStretchFactor(0, 3)  # Left panel gets more space
        self.main_splitter.setStretchFactor(1, 2)  # Right panel gets less space
        
        # Add main splitter to layout
        main_layout.addWidget(self.main_splitter)
        
        # Configure splitter appearance
        self.main_splitter.setHandleWidth(6)
        self.left_splitter.setHandleWidth(6)
        
        # Set splitter styles
        splitter_style = """
            QSplitter::handle {
                background-color: #555;
                border: 1px solid #777;
            }
            QSplitter::handle:hover {
                background-color: #666;
            }
            QSplitter::handle:pressed {
                background-color: #444;
            }
        """
        self.main_splitter.setStyleSheet(splitter_style)
        self.left_splitter.setStyleSheet(splitter_style)
    
    def _setup_status_bar(self) -> None:
        """Create the status bar for displaying application status."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Show ready message
        self.status_bar.showMessage("Ready", 2000)
    
    def _connect_signals(self) -> None:
        """Connect internal signals to slots."""
        # File menu connections
        self.action_new.triggered.connect(self.project_new_requested.emit)
        self.action_open.triggered.connect(self._handle_open_project)
        self.action_save.triggered.connect(self.project_save_requested.emit)
        self.action_save_as.triggered.connect(self._handle_save_as_project)
        self.action_export.triggered.connect(self.project_export_requested.emit)
        self.action_exit.triggered.connect(self.close)
        
        # Import menu connections
        self.action_import_media.triggered.connect(self._handle_import_media)
        self.action_import_subtitles.triggered.connect(self._handle_import_subtitles)
        self.action_import_audio.triggered.connect(self._handle_import_audio)
        
        # Playback connections
        self.action_play.triggered.connect(self._handle_play_pause)
        self.action_stop.triggered.connect(self._handle_stop)
        self.action_preview_audio.triggered.connect(self._handle_preview_audio)
        
        # Connect preview panel signals
        self.preview_panel.play_requested.connect(self.playback_play_requested.emit)
        self.preview_panel.pause_requested.connect(self.playback_pause_requested.emit)
        self.preview_panel.stop_requested.connect(self.playback_stop_requested.emit)
        
        # View menu connections
        self.action_toggle_timeline.triggered.connect(self._toggle_timeline_panel)
        self.action_toggle_effects.triggered.connect(self._toggle_effects_panel)
        
        # Help menu connections
        self.action_about.triggered.connect(self._show_about_dialog)
    
    def _handle_open_project(self) -> None:
        """Handle open project action with file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "Project Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.project_open_requested.emit(file_path)
    
    def _handle_save_as_project(self) -> None:
        """Handle save as project action with file dialog."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            "",
            "Project Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.project_save_as_requested.emit(file_path)
    
    def _handle_import_media(self) -> None:
        """Handle import background media action with file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Background Media",
            "",
            "Media Files (*.mp4 *.avi *.mov *.mkv *.jpg *.jpeg *.png *.bmp);;Video Files (*.mp4 *.avi *.mov *.mkv);;Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )
        
        if file_path:
            self.import_media_requested.emit(file_path)
    
    def _handle_import_subtitles(self) -> None:
        """Handle import subtitles action with file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Subtitles",
            "",
            "Subtitle Files (*.json *.ass *.srt);;JSON Files (*.json);;ASS Files (*.ass);;SRT Files (*.srt);;All Files (*)"
        )
        
        if file_path:
            self.import_subtitles_requested.emit(file_path)
    
    def _handle_import_audio(self) -> None:
        """Handle import audio action with file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Audio",
            "",
            "Audio Files (*.mp3 *.wav *.aac *.flac *.ogg);;MP3 Files (*.mp3);;WAV Files (*.wav);;All Files (*)"
        )
        
        if file_path:
            self.import_audio_requested.emit(file_path)
    
    def _handle_play_pause(self) -> None:
        """Handle play/pause toggle."""
        if self.action_play.isChecked():
            self.action_play.setText("&Pause")
            self.preview_panel._handle_play()
        else:
            self.action_play.setText("&Play")
            self.preview_panel._handle_pause()
    
    def _handle_stop(self) -> None:
        """Handle stop playback."""
        self.action_play.setChecked(False)
        self.action_play.setText("&Play")
        self.preview_panel._handle_stop()
    
    def _handle_preview_audio(self) -> None:
        """Handle audio preview request."""
        self.audio_preview_requested.emit()
    
    def _toggle_timeline_panel(self) -> None:
        """Toggle timeline panel visibility."""
        visible = self.action_toggle_timeline.isChecked()
        self.subtitle_editor.setVisible(visible)
    
    def _toggle_effects_panel(self) -> None:
        """Toggle effects panel visibility."""
        visible = self.action_toggle_effects.isChecked()
        self.effects_panel.setVisible(visible)
    
    def _show_about_dialog(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Subtitle Creator with Effects",
            "<h3>Subtitle Creator with Effects</h3>"
            "<p>A desktop application for creating stylized subtitle videos "
            "with visual effects and synchronized text overlays.</p>"
            "<p>Built with Python, PyQt6, and MoviePy.</p>"
        )
    
    def _restore_window_state(self) -> None:
        """Restore window geometry and state from settings."""
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Default size and center on screen
            self.resize(1200, 800)
            self._center_on_screen()
        
        # Restore window state (toolbars, docks, etc.)
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
        
        # Restore splitter states
        main_splitter_state = self.settings.value("mainSplitterState")
        if main_splitter_state:
            self.main_splitter.restoreState(main_splitter_state)
        
        left_splitter_state = self.settings.value("leftSplitterState")
        if left_splitter_state:
            self.left_splitter.restoreState(left_splitter_state)
        
        # Restore panel visibility
        timeline_visible = self.settings.value("timelineVisible", True, type=bool)
        self.action_toggle_timeline.setChecked(timeline_visible)
        self.subtitle_editor.setVisible(timeline_visible)
        
        effects_visible = self.settings.value("effectsVisible", True, type=bool)
        self.action_toggle_effects.setChecked(effects_visible)
        self.effects_panel.setVisible(effects_visible)
    
    def _center_on_screen(self) -> None:
        """Center the window on the screen."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def closeEvent(self, event) -> None:
        """Handle window close event and save state."""
        # Save window geometry and state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Save splitter states
        self.settings.setValue("mainSplitterState", self.main_splitter.saveState())
        self.settings.setValue("leftSplitterState", self.left_splitter.saveState())
        
        # Save panel visibility
        self.settings.setValue("timelineVisible", self.action_toggle_timeline.isChecked())
        self.settings.setValue("effectsVisible", self.action_toggle_effects.isChecked())
        
        # Accept the close event
        event.accept()
    
    # Public methods for external control
    
    def set_project_modified(self, modified: bool) -> None:
        """Update UI to reflect project modification state."""
        self.action_save.setEnabled(modified)
        
        # Update window title
        title = "Subtitle Creator with Effects"
        if modified:
            title += " *"
        self.setWindowTitle(title)
    
    def set_project_loaded(self, loaded: bool) -> None:
        """Update UI to reflect project loaded state."""
        self.action_save_as.setEnabled(loaded)
        self.action_export.setEnabled(loaded)
        self.action_save_preset.setEnabled(loaded)
        self.action_reset_effects.setEnabled(loaded)
        self.action_select_all.setEnabled(loaded)
    
    def set_playback_state(self, playing: bool) -> None:
        """Update playback controls based on current state."""
        self.action_play.setChecked(playing)
        if playing:
            self.action_play.setText("&Pause")
        else:
            self.action_play.setText("&Play")
    
    def set_audio_loaded(self, loaded: bool) -> None:
        """Update UI to reflect audio loaded state."""
        self.action_preview_audio.setEnabled(loaded)
        if loaded:
            self.action_preview_audio.setStatusTip("Preview audio (first 10 seconds)")
        else:
            self.action_preview_audio.setStatusTip("No audio loaded")
    
    def show_status_message(self, message: str, timeout: int = 0) -> None:
        """Show a message in the status bar."""
        self.status_bar.showMessage(message, timeout)
    
    def get_preview_panel(self) -> PreviewPanel:
        """Get the preview panel for external control."""
        return self.preview_panel
    
    def get_subtitle_editor(self) -> 'SubtitleEditor':
        """Get the subtitle editor for external control."""
        return self.subtitle_editor
    
    def get_effects_panel(self) -> 'EffectsPanel':
        """Get the effects panel for external control."""
        return self.effects_panel
    
    def update_subtitle_data(self, subtitle_data) -> None:
        """Update the subtitle editor with new subtitle data."""
        if hasattr(self, 'subtitle_editor') and self.subtitle_editor:
            self.subtitle_editor.set_subtitle_data(subtitle_data)
    
    def _on_effects_changed(self) -> None:
        """Handle effects changes from the effects panel."""
        # This would trigger preview updates in a real application
        active_effects = self.effects_panel.get_active_effects()
        effect_count = len(active_effects)
        
        if effect_count > 0:
            effect_names = [effect.name for effect in active_effects]
            self.show_status_message(f"Effects active: {', '.join(effect_names)}", 3000)
        else:
            self.show_status_message("No effects active", 2000)