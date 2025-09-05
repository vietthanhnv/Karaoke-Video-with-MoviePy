"""
Application controller for coordinating all components of the Subtitle Creator.

This module provides the AppController class that serves as the central coordinator
between the GUI components and backend services, managing project state, handling
user interactions, and propagating changes throughout the system.
"""

import json
import os
import copy
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox, QFileDialog

# Optional import for MoviePy - will be available when dependencies are installed
try:
    from moviepy import VideoClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    # Create placeholders for development/testing
    class VideoClip:
        def __init__(self):
            self.duration = 0
            self.size = (1920, 1080)
    
    class AudioFileClip:
        def __init__(self, path):
            self.duration = 0
            self.fps = 44100
            
        def subclip(self, start_time, end_time=None):
            """Mock subclip method for testing."""
            new_clip = AudioFileClip("")
            new_clip.duration = (end_time or self.duration) - start_time if self.duration else 10.0
            new_clip.fps = self.fps
            return new_clip
    
    MOVIEPY_AVAILABLE = False

from .media_manager import MediaManager
from .subtitle_engine import SubtitleEngine
from .effects.system import EffectSystem
from .preview_engine import PreviewEngine
from .export_manager import ExportManager
from .models import SubtitleData
from .interfaces import SubtitleCreatorError, MediaError, AudioError, EffectError, ExportError
from .config import get_config


@dataclass
class ProjectState:
    """Represents the complete state of a project."""
    background_media_path: Optional[str] = None
    audio_file_path: Optional[str] = None
    subtitle_file_path: Optional[str] = None
    project_file_path: Optional[str] = None
    is_modified: bool = False
    is_loaded: bool = False


class AppController(QObject):
    """
    Central application controller coordinating all components.
    
    Manages project state, coordinates between GUI and backend services,
    handles user interactions, and provides reactive updates throughout
    the system using Qt signals and slots.
    """
    
    # Signals for reactive updates
    project_loaded = pyqtSignal(bool)  # project_loaded
    project_modified = pyqtSignal(bool)  # is_modified
    preview_updated = pyqtSignal()
    effects_changed = pyqtSignal(list)  # active_effects
    subtitle_data_changed = pyqtSignal()
    playback_state_changed = pyqtSignal(bool)  # is_playing
    export_progress_changed = pyqtSignal(float)  # progress_percentage
    status_message = pyqtSignal(str, int)  # message, timeout
    error_occurred = pyqtSignal(str, str)  # title, message
    
    def __init__(self, main_window=None, test_mode: bool = False):
        """
        Initialize the application controller.
        
        Args:
            main_window: Reference to the main window for GUI interactions
            test_mode: If True, initialize in test mode (skip dependency validation)
        """
        super().__init__()
        
        self.main_window = main_window
        self.config = get_config()
        self.test_mode = test_mode
        
        # Initialize backend components
        self.media_manager = MediaManager(test_mode=test_mode)
        self.subtitle_engine = SubtitleEngine()
        self.effect_system = EffectSystem()
        self.preview_engine = PreviewEngine()
        self.export_manager = ExportManager()
        
        # Project state
        self.project_state = ProjectState()
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._max_undo_levels = 50
        
        # Current loaded media objects
        self._background_clip: Optional[VideoClip] = None
        self._audio_clip: Optional[AudioFileClip] = None
        
        # Preview update timer for performance optimization
        self._preview_update_timer = QTimer()
        self._preview_update_timer.setSingleShot(True)
        self._preview_update_timer.timeout.connect(self._update_preview_delayed)
        self._preview_update_delay = 100  # ms
        
        # Background processing for smooth UI responsiveness
        self._background_update_timer = QTimer()
        self._background_update_timer.setSingleShot(True)
        self._background_update_timer.timeout.connect(self._background_preview_update)
        self._background_update_delay = 50  # ms for immediate UI feedback
        
        # Performance optimization flags
        self._is_preview_updating = False
        self._pending_preview_update = False
        self._last_update_time = 0.0
        
        # Connect internal signals
        self._connect_internal_signals()
        
        # Connect to GUI if provided
        if self.main_window:
            self._connect_gui_signals()
    
    def _connect_internal_signals(self) -> None:
        """Connect internal component signals."""
        # Connect export manager progress
        self.export_manager.add_progress_callback(self._on_export_progress)
        
        # Connect preview engine callbacks
        self.preview_engine.add_time_callback(self._on_preview_time_changed)
    
    def _connect_gui_signals(self) -> None:
        """Connect GUI signals to controller methods."""
        if not self.main_window:
            return
        
        # Project management signals
        self.main_window.project_new_requested.connect(self.create_new_project)
        self.main_window.project_open_requested.connect(self.load_project)
        self.main_window.project_save_requested.connect(self.save_project)
        self.main_window.project_save_as_requested.connect(self.save_project_as)
        self.main_window.project_export_requested.connect(self.export_video)
        
        # Import signals
        self.main_window.import_media_requested.connect(self.load_background_media)
        self.main_window.import_subtitles_requested.connect(self.load_subtitle_file)
        self.main_window.import_audio_requested.connect(self.load_audio_file)
        
        # Playback control signals
        self.main_window.playback_play_requested.connect(self.start_playback)
        self.main_window.playback_pause_requested.connect(self.pause_playback)
        self.main_window.playback_stop_requested.connect(self.stop_playback)
        
        # Connect controller signals to GUI updates
        self.project_loaded.connect(self.main_window.set_project_loaded)
        self.project_modified.connect(self.main_window.set_project_modified)
        self.playback_state_changed.connect(self.main_window.set_playback_state)
        self.status_message.connect(self.main_window.show_status_message)
        self.error_occurred.connect(self._show_error_dialog)
        self.subtitle_data_changed.connect(self._update_subtitle_editor)
        
        # Connect GUI component signals
        self._connect_gui_component_signals()
    
    def _connect_gui_component_signals(self) -> None:
        """Connect signals from GUI components."""
        if not self.main_window:
            return
        
        # Effects panel changes
        effects_panel = self.main_window.get_effects_panel()
        if effects_panel:
            effects_panel.effects_changed.connect(self._on_effects_changed)
        
        # Subtitle editor changes
        subtitle_editor = self.main_window.get_subtitle_editor()
        if subtitle_editor:
            subtitle_editor.subtitle_data_changed.connect(self._on_subtitle_data_changed)
            subtitle_editor.preview_update_requested.connect(self._on_preview_update_requested)
            subtitle_editor.line_selected.connect(self._on_subtitle_line_selected)
            subtitle_editor.selection_changed.connect(self._on_subtitle_selection_changed)
        
        # Preview panel interactions
        preview_panel = self.main_window.get_preview_panel()
        if preview_panel:
            # Connect the preview engine to the preview panel - this is crucial for timeline functionality
            preview_panel.set_preview_engine(self.preview_engine)
            
            # Connect preview panel signals
            preview_panel.seek_requested.connect(self.seek_to_time)
            preview_panel.play_requested.connect(self._on_preview_play_requested)
            preview_panel.pause_requested.connect(self._on_preview_pause_requested)
            preview_panel.stop_requested.connect(self._on_preview_stop_requested)
    
    # Project Management Methods
    
    def create_new_project(self) -> None:
        """Create a new empty project."""
        try:
            # Check for unsaved changes
            if self.project_state.is_modified:
                if not self._confirm_discard_changes():
                    return
            
            # Reset all components (this already calls subtitle_engine.create_new())
            self._reset_project_state()
            
            # Add some default test subtitles for preview
            if self.test_mode:
                from .models import SubtitleLine
                test_lines = [
                    SubtitleLine(
                        start_time=0.0,
                        end_time=3.0,
                        text="Welcome to Subtitle Creator",
                        style={'font_size': 24, 'color': '#FFFFFF'}
                    ),
                    SubtitleLine(
                        start_time=3.5,
                        end_time=6.0,
                        text="Create amazing subtitle videos!",
                        style={'font_size': 24, 'color': '#FFFFFF'}
                    )
                ]
                for line in test_lines:
                    self.subtitle_engine.add_line(line)
                print(f"DEBUG: Added test subtitles, has_data: {self.subtitle_engine.has_data}")
            
            # Update state
            self.project_state = ProjectState(is_loaded=True)
            
            # Emit signals
            self.project_loaded.emit(True)
            self.project_modified.emit(False)
            self.status_message.emit("New project created", 2000)
            
        except Exception as e:
            self.error_occurred.emit("New Project Error", f"Failed to create new project: {str(e)}")
    
    def load_project(self, file_path: str) -> None:
        """
        Load a project from file.
        
        Args:
            file_path: Path to the project file
        """
        try:
            # Check for unsaved changes
            if self.project_state.is_modified:
                if not self._confirm_discard_changes():
                    return
            
            # Validate file exists
            if not os.path.exists(file_path):
                self.error_occurred.emit("File Not Found", f"Project file not found: {file_path}")
                return
            
            # Load project configuration
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Reset current state
            self._reset_project_state()
            
            # Load project components
            self._load_project_components(project_data, file_path)
            
            # Update project state
            self.project_state.project_file_path = file_path
            self.project_state.is_loaded = True
            self.project_state.is_modified = False
            
            # Emit signals
            self.project_loaded.emit(True)
            self.project_modified.emit(False)
            self.status_message.emit(f"Project loaded: {Path(file_path).name}", 3000)
            
            # Update preview
            self._schedule_preview_update()
            
        except Exception as e:
            self.error_occurred.emit("Load Project Error", f"Failed to load project: {str(e)}")
    
    def _load_project_components(self, project_data: Dict[str, Any], project_file_path: str) -> None:
        """
        Load individual project components from project data.
        
        Args:
            project_data: Project configuration data
            project_file_path: Path to the project file (for relative path resolution)
        """
        project_dir = Path(project_file_path).parent
        
        # Load background media
        if 'background_media' in project_data and project_data['background_media']:
            background_path = self._resolve_project_path(project_data['background_media'], project_dir)
            self.load_background_media(background_path)
        
        # Load audio file
        if 'audio_file' in project_data and project_data['audio_file']:
            audio_path = self._resolve_project_path(project_data['audio_file'], project_dir)
            self.load_audio_file(audio_path)
        
        # Load subtitle data
        if 'subtitle_data' in project_data:
            # Create SubtitleData from dictionary (simplified for now)
            subtitle_data = SubtitleData(
                lines=project_data['subtitle_data'].get('lines', []),
                global_style=project_data['subtitle_data'].get('global_style', {}),
                metadata=project_data['subtitle_data'].get('metadata', {})
            )
            self.subtitle_engine.load_from_data(subtitle_data)
        
        # Load effects
        if 'effects' in project_data:
            self._load_effects_from_data(project_data['effects'])
    
    def _resolve_project_path(self, path: str, project_dir: Path) -> str:
        """
        Resolve a path relative to the project directory.
        
        Args:
            path: File path (absolute or relative)
            project_dir: Project directory for relative path resolution
            
        Returns:
            Absolute path to the file
        """
        if os.path.isabs(path):
            return path
        else:
            return str(project_dir / path)
    
    def _load_effects_from_data(self, effects_data: List[Dict[str, Any]]) -> None:
        """
        Load effects from project data.
        
        Args:
            effects_data: List of effect configurations
        """
        try:
            self.effect_system.clear_effects()
            
            for effect_data in effects_data:
                effect_name = effect_data.get('name', 'Unknown')
                effect_class = effect_data.get('class')
                effect_params = effect_data.get('parameters', {})
                
                if effect_class:
                    try:
                        effect = self.effect_system.create_effect(effect_class, effect_params)
                        self.effect_system.add_effect(effect)
                    except EffectError as e:
                        print(f"Warning: Failed to load effect '{effect_name}': {e}")
            
            # Emit effects changed signal
            self.effects_changed.emit(self.effect_system.get_active_effects())
            
        except Exception as e:
            print(f"Warning: Failed to load effects: {e}")
    
    def save_project(self) -> None:
        """Save the current project."""
        if not self.project_state.project_file_path:
            self.save_project_as()
        else:
            self._save_project_to_file(self.project_state.project_file_path)
    
    def save_project_as(self, file_path: Optional[str] = None) -> None:
        """
        Save the project with a new name.
        
        Args:
            file_path: Optional file path. If None, shows file dialog.
        """
        if not file_path and self.main_window:
            file_path, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Save Project As",
                "",
                "Project Files (*.json);;All Files (*)"
            )
        
        if file_path:
            self._save_project_to_file(file_path)
    
    def _save_project_to_file(self, file_path: str) -> None:
        """
        Save project data to a file.
        
        Args:
            file_path: Path to save the project file
        """
        try:
            # Create project data
            project_data = self._create_project_data(file_path)
            
            # Ensure directory exists
            os.makedirs(Path(file_path).parent, exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # Update project state
            self.project_state.project_file_path = file_path
            self.project_state.is_modified = False
            
            # Emit signals
            self.project_modified.emit(False)
            self.status_message.emit(f"Project saved: {Path(file_path).name}", 3000)
            
        except Exception as e:
            self.error_occurred.emit("Save Project Error", f"Failed to save project: {str(e)}")
    
    def _create_project_data(self, project_file_path: str) -> Dict[str, Any]:
        """
        Create project data dictionary for saving.
        
        Args:
            project_file_path: Path where the project will be saved
            
        Returns:
            Project data dictionary
        """
        project_dir = Path(project_file_path).parent
        
        # Create relative paths for portability
        background_path = None
        if self.project_state.background_media_path:
            background_path = self._make_relative_path(
                self.project_state.background_media_path, project_dir
            )
        
        audio_path = None
        if self.project_state.audio_file_path:
            audio_path = self._make_relative_path(
                self.project_state.audio_file_path, project_dir
            )
        
        # Get subtitle data
        subtitle_data = None
        if self.subtitle_engine.has_data:
            # Convert SubtitleData to dictionary (simplified for now)
            data = self.subtitle_engine.subtitle_data
            subtitle_data = {
                'lines': [line.__dict__ for line in data.lines] if hasattr(data, 'lines') else [],
                'global_style': data.global_style if hasattr(data, 'global_style') else {},
                'metadata': data.metadata if hasattr(data, 'metadata') else {}
            }
        
        # Get effects data
        effects_data = []
        for effect in self.effect_system.get_active_effects():
            if hasattr(effect, 'to_dict'):
                effects_data.append(effect.to_dict())
            else:
                effects_data.append({
                    'name': effect.name,
                    'class': effect.__class__.__name__,
                    'parameters': effect.parameters
                })
        
        return {
            'version': '1.0',
            'background_media': background_path,
            'audio_file': audio_path,
            'subtitle_data': subtitle_data,
            'effects': effects_data,
            'created_at': str(Path.cwd()),  # Placeholder for timestamp
            'application': 'Subtitle Creator with Effects'
        }
    
    def _make_relative_path(self, file_path: str, project_dir: Path) -> str:
        """
        Make a file path relative to the project directory if possible.
        
        Args:
            file_path: Absolute file path
            project_dir: Project directory
            
        Returns:
            Relative path if possible, otherwise absolute path
        """
        try:
            return str(Path(file_path).relative_to(project_dir))
        except ValueError:
            # Path is not relative to project directory, return absolute
            return file_path
    
    # Media Loading Methods
    
    def load_background_media(self, file_path: str) -> None:
        """
        Load background media (image or video).
        
        Args:
            file_path: Path to the media file
        """
        try:
            # Validate file
            if not os.path.exists(file_path):
                self.error_occurred.emit("File Not Found", f"Media file not found: {file_path}")
                return
            
            # Load media through media manager
            self._background_clip = self.media_manager.load_background_media(file_path)
            
            # Update project state
            self.project_state.background_media_path = file_path
            self._mark_project_modified()
            
            # Update preview
            self._schedule_preview_update()
            
            self.status_message.emit(f"Background media loaded: {Path(file_path).name}", 3000)
            
        except MediaError as e:
            self.error_occurred.emit("Media Load Error", str(e))
        except Exception as e:
            self.error_occurred.emit("Media Load Error", f"Failed to load media: {str(e)}")
    
    def load_audio_file(self, file_path: str) -> None:
        """
        Load audio file for synchronization.
        
        Args:
            file_path: Path to the audio file
        """
        print(f"DEBUG: load_audio_file called with: {file_path}")
        try:
            # Validate file
            if not os.path.exists(file_path):
                self.error_occurred.emit("File Not Found", f"Audio file not found: {file_path}")
                return
            
            # Load audio through media manager
            print("DEBUG: About to call media_manager.load_audio")
            self._audio_clip = self.media_manager.load_audio(file_path)
            print(f"DEBUG: Audio clip loaded successfully: {self._audio_clip is not None}")
            if self._audio_clip:
                print(f"DEBUG: Audio clip duration: {getattr(self._audio_clip, 'duration', 'None')}")
            
            # Update project state
            self.project_state.audio_file_path = file_path
            self._mark_project_modified()
            
            # Update preview to include audio
            self._schedule_preview_update()
            
            self.status_message.emit(f"Audio loaded: {Path(file_path).name}", 3000)
            
        except AudioError as e:
            print(f"DEBUG: AudioError caught: {e}")
            self.error_occurred.emit("Audio Load Error", str(e))
        except Exception as e:
            print(f"DEBUG: Exception caught: {e}")
            self.error_occurred.emit("Audio Load Error", f"Failed to load audio: {str(e)}")
    
    def load_subtitle_file(self, file_path: str) -> None:
        """
        Load subtitle file.
        
        Args:
            file_path: Path to the subtitle file
        """
        try:
            # Load subtitles through subtitle engine
            self.subtitle_engine.load_from_file(file_path)
            
            # Update project state
            self.project_state.subtitle_file_path = file_path
            self._mark_project_modified()
            
            # Emit subtitle data changed signal
            self.subtitle_data_changed.emit()
            
            # Update preview
            self._schedule_preview_update()
            
            self.status_message.emit(f"Subtitles loaded: {Path(file_path).name}", 3000)
            
        except Exception as e:
            self.error_occurred.emit("Subtitle Load Error", f"Failed to load subtitles: {str(e)}")
    
    # Effect Management Methods
    
    def apply_effect(self, effect_name: str, parameters: Dict[str, Any]) -> None:
        """
        Apply an effect with the given parameters.
        
        Args:
            effect_name: Name of the effect class
            parameters: Effect parameters
        """
        try:
            # Save state for undo
            self._save_state_for_undo()
            
            # Create and add effect
            effect = self.effect_system.create_effect(effect_name, parameters)
            self.effect_system.add_effect(effect)
            
            # Mark project as modified
            self._mark_project_modified()
            
            # Emit effects changed signal
            self.effects_changed.emit(self.effect_system.get_active_effects())
            
            # Update preview
            self._schedule_preview_update()
            
            self.status_message.emit(f"Effect applied: {effect.name}", 2000)
            
        except EffectError as e:
            self.error_occurred.emit("Effect Error", str(e))
        except Exception as e:
            self.error_occurred.emit("Effect Error", f"Failed to apply effect: {str(e)}")
    
    def remove_effect(self, effect) -> None:
        """
        Remove an effect.
        
        Args:
            effect: Effect instance to remove
        """
        try:
            # Save state for undo
            self._save_state_for_undo()
            
            # Remove effect
            self.effect_system.remove_effect(effect)
            
            # Mark project as modified
            self._mark_project_modified()
            
            # Emit effects changed signal
            self.effects_changed.emit(self.effect_system.get_active_effects())
            
            # Update preview
            self._schedule_preview_update()
            
            self.status_message.emit(f"Effect removed: {effect.name}", 2000)
            
        except Exception as e:
            self.error_occurred.emit("Effect Error", f"Failed to remove effect: {str(e)}")
    
    def clear_all_effects(self) -> None:
        """Clear all applied effects."""
        try:
            # Save state for undo
            self._save_state_for_undo()
            
            # Clear effects
            self.effect_system.clear_effects()
            
            # Mark project as modified
            self._mark_project_modified()
            
            # Emit effects changed signal
            self.effects_changed.emit([])
            
            # Update preview
            self._schedule_preview_update()
            
            self.status_message.emit("All effects cleared", 2000)
            
        except Exception as e:
            self.error_occurred.emit("Effect Error", f"Failed to clear effects: {str(e)}")
    
    # Preview and Playback Methods
    
    def start_playback(self) -> None:
        """Start preview playback."""
        try:
            if self._can_preview():
                current_time = self.preview_engine.get_current_time()
                self.preview_engine.start_playback(current_time)
                self.playback_state_changed.emit(True)
                self.status_message.emit("Playback started", 1000)
            else:
                self.status_message.emit("No media loaded for playback", 2000)
                
        except Exception as e:
            self.error_occurred.emit("Playback Error", f"Failed to start playback: {str(e)}")
    
    def pause_playback(self) -> None:
        """Pause preview playback."""
        try:
            self.preview_engine.pause_playback()
            self.playback_state_changed.emit(False)
            self.status_message.emit("Playback paused", 1000)
            
        except Exception as e:
            self.error_occurred.emit("Playback Error", f"Failed to pause playback: {str(e)}")
    
    def stop_playback(self) -> None:
        """Stop preview playback."""
        try:
            self.preview_engine.stop_playback()
            self.playback_state_changed.emit(False)
            self.status_message.emit("Playback stopped", 1000)
            
        except Exception as e:
            self.error_occurred.emit("Playback Error", f"Failed to stop playback: {str(e)}")
    
    def seek_to_time(self, time: float) -> None:
        """
        Seek to a specific time in the preview.
        
        Args:
            time: Time in seconds to seek to
        """
        try:
            if self._can_preview():
                self.preview_engine.seek_to_time(time)
                
        except Exception as e:
            self.error_occurred.emit("Seek Error", f"Failed to seek to time: {str(e)}")
    
    def _can_preview(self) -> bool:
        """Check if preview is possible with current project state."""
        return (self._background_clip is not None and 
                self.subtitle_engine.has_data)
    
    def _schedule_preview_update(self) -> None:
        """Schedule a preview update with debouncing and performance optimization."""
        import time
        current_time = time.time()
        
        # If we're already updating, mark that another update is pending
        if self._is_preview_updating:
            self._pending_preview_update = True
            return
        
        # Throttle updates to avoid overwhelming the system
        time_since_last_update = current_time - self._last_update_time
        if time_since_last_update < 0.05:  # Minimum 50ms between updates
            self._background_update_timer.start(self._background_update_delay)
        else:
            self._preview_update_timer.start(self._preview_update_delay)
    
    def _background_preview_update(self) -> None:
        """Handle background preview updates for immediate UI feedback."""
        # Provide immediate UI feedback without full preview generation
        try:
            if self._can_preview():
                # Update preview engine with current time for seeking
                current_time = self.preview_engine.get_current_time()
                
                # Update GUI components immediately
                if self.main_window:
                    preview_panel = self.main_window.get_preview_panel()
                    if preview_panel:
                        # This provides immediate visual feedback
                        frame = self.preview_engine.seek_to_time(current_time)
                
                # Schedule full update after brief delay
                self._preview_update_timer.start(self._preview_update_delay)
                
        except Exception as e:
            print(f"Warning: Background preview update failed: {e}")
    
    def _update_preview_delayed(self) -> None:
        """Update preview after delay with performance optimization and audio sync."""
        import time
        
        print("DEBUG: _update_preview_delayed called")
        
        if self._is_preview_updating:
            self._pending_preview_update = True
            return
        
        try:
            self._is_preview_updating = True
            self._last_update_time = time.time()
            
            print(f"DEBUG: _can_preview check - background_clip: {self._background_clip is not None}, subtitle_data: {self.subtitle_engine.has_data}")
            
            if self._can_preview():
                print("DEBUG: Can preview, generating preview...")
                print(f"DEBUG: Background clip type: {type(self._background_clip)}")
                print(f"DEBUG: Background clip duration: {getattr(self._background_clip, 'duration', 'None')}")
                print(f"DEBUG: Audio clip: {self._audio_clip is not None}")
                if self._audio_clip:
                    print(f"DEBUG: Audio clip type: {type(self._audio_clip)}")
                    print(f"DEBUG: Audio clip duration: {getattr(self._audio_clip, 'duration', 'None')}")
                
                # Get current settings
                subtitle_data = self.subtitle_engine.subtitle_data
                effects = self.effect_system.get_active_effects()
                
                # Performance optimization: filter complex effects if needed
                optimized_effects = self._optimize_effects_for_preview(effects)
                
                print("DEBUG: About to generate preview with audio sync...")
                # Generate preview with audio synchronization
                preview_clip = self._generate_preview_with_audio_sync(
                    self._background_clip, subtitle_data, optimized_effects
                )
                print(f"DEBUG: Preview clip generated: {preview_clip is not None}")
                
                # Update preview engine
                if preview_clip:
                    # Set the preview engine's current clip
                    self.preview_engine._current_clip = preview_clip
                    
                    # Update duration in GUI
                    if self.main_window:
                        preview_panel = self.main_window.get_preview_panel()
                        if preview_panel:
                            # Safely get duration with fallback
                            try:
                                duration = getattr(preview_clip, 'duration', 10.0)
                                if duration is None:
                                    duration = 10.0  # Default duration for images
                                preview_panel.set_duration(duration)
                            except (AttributeError, TypeError):
                                # Fallback to default duration
                                preview_panel.set_duration(10.0)
                
                # Emit preview updated signal
                self.preview_updated.emit()
                
                # Handle pending updates
                if self._pending_preview_update:
                    self._pending_preview_update = False
                    # Schedule another update after a brief delay
                    QTimer.singleShot(50, self._update_preview_delayed)
                
        except Exception as e:
            self.error_occurred.emit("Preview Error", f"Preview update failed: {str(e)}")
        finally:
            self._is_preview_updating = False
    
    def _optimize_effects_for_preview(self, effects: List) -> List:
        """Optimize effects for preview performance."""
        if not effects:
            return effects
        
        # Performance optimization: limit complex effects during preview
        optimized_effects = []
        particle_effect_count = 0
        max_particle_effects = 2  # Limit particle effects for performance
        
        for effect in effects:
            effect_type = type(effect).__name__
            
            # Limit particle effects
            if 'Particle' in effect_type:
                if particle_effect_count < max_particle_effects:
                    # Reduce particle count for preview
                    if hasattr(effect, 'parameters') and 'particle_count' in effect.parameters:
                        preview_effect = copy.deepcopy(effect)
                        preview_effect.parameters['particle_count'] = min(
                            effect.parameters['particle_count'], 20
                        )
                        optimized_effects.append(preview_effect)
                    else:
                        optimized_effects.append(effect)
                    particle_effect_count += 1
                # Skip additional particle effects
            else:
                optimized_effects.append(effect)
        
        return optimized_effects
    
    def _generate_preview_with_audio_sync(self, background_clip, subtitle_data, effects):
        """Generate preview with proper audio synchronization."""
        print("DEBUG: _generate_preview_with_audio_sync called")
        try:
            # Generate basic preview
            print("DEBUG: Generating basic preview...")
            preview_clip = self.preview_engine.generate_preview(
                background_clip, subtitle_data, effects
            )
            print(f"DEBUG: Basic preview generated: {preview_clip is not None}")
            if preview_clip:
                print(f"DEBUG: Preview clip duration: {getattr(preview_clip, 'duration', 'None')}")
            
            # Add audio synchronization if audio is available
            if self._audio_clip and preview_clip:
                print("DEBUG: Adding audio synchronization...")
                # Safely get durations
                try:
                    preview_duration = getattr(preview_clip, 'duration', None)
                    audio_duration = getattr(self._audio_clip, 'duration', None)
                    
                    if preview_duration and audio_duration:
                        if preview_duration > audio_duration:
                            # Loop audio if video is longer
                            if MOVIEPY_AVAILABLE:
                                try:
                                    from moviepy import afx
                                    looped_audio = self._audio_clip.with_effects([afx.AudioLoop(duration=preview_duration)])
                                    preview_clip = preview_clip.with_audio(looped_audio)
                                except (ImportError, AttributeError):
                                    # Fallback: just set the audio as-is
                                    preview_clip = preview_clip.with_audio(self._audio_clip)
                        else:
                            # Trim audio to match video duration
                            trimmed_audio = self._audio_clip.subclipped(0, preview_duration)
                            preview_clip = preview_clip.with_audio(trimmed_audio)
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Could not sync audio with video: {e}")
                    # Just set audio without duration matching
                    try:
                        preview_clip = preview_clip.with_audio(self._audio_clip)
                    except Exception:
                        pass  # Continue without audio if setting fails
            
            return preview_clip
            
        except Exception as e:
            print(f"Warning: Audio sync failed, using video-only preview: {e}")
            # Return preview without audio if sync fails
            return self.preview_engine.generate_preview(background_clip, subtitle_data, effects)
    
    # Export Methods
    
    def export_video(self, output_path: Optional[str] = None, 
                    export_settings: Optional[Dict[str, Any]] = None) -> None:
        """
        Export the final video.
        
        Args:
            output_path: Optional output path. If None, shows file dialog.
            export_settings: Optional export settings. If None, uses defaults.
        """
        try:
            # Check if export is possible
            if not self._can_preview():
                self.error_occurred.emit("Export Error", "No media or subtitles loaded for export")
                return
            
            # Get output path if not provided
            if not output_path and self.main_window:
                output_path, _ = QFileDialog.getSaveFileName(
                    self.main_window,
                    "Export Video",
                    "",
                    "MP4 Files (*.mp4);;AVI Files (*.avi);;MOV Files (*.mov);;All Files (*)"
                )
            
            if not output_path:
                return
            
            # Use default export settings if not provided
            if not export_settings:
                export_settings = {
                    'format': 'mp4',
                    'quality': 'high'
                }
            
            # Start export
            subtitle_data = self.subtitle_engine.subtitle_data
            effects = self.effect_system.get_active_effects()
            
            self.export_manager.export_video(
                self._background_clip, subtitle_data, effects, 
                output_path, export_settings
            )
            
            self.status_message.emit("Export started...", 0)
            
        except ExportError as e:
            self.error_occurred.emit("Export Error", str(e))
        except Exception as e:
            self.error_occurred.emit("Export Error", f"Failed to start export: {str(e)}")
    
    # State Management Methods
    
    def _save_state_for_undo(self) -> None:
        """Save current state for undo functionality."""
        try:
            state = self._capture_current_state()
            self._undo_stack.append(state)
            
            # Limit undo stack size
            if len(self._undo_stack) > self._max_undo_levels:
                self._undo_stack.pop(0)
            
            # Clear redo stack when new action is performed
            self._redo_stack.clear()
            
        except Exception as e:
            print(f"Warning: Failed to save state for undo: {e}")
    
    def _capture_current_state(self) -> Dict[str, Any]:
        """Capture the current application state."""
        state = {
            'subtitle_data': None,
            'effects': [],
            'project_state': copy.deepcopy(self.project_state)
        }
        
        # Capture subtitle data
        if self.subtitle_engine.has_data:
            state['subtitle_data'] = copy.deepcopy(self.subtitle_engine.subtitle_data)
        
        # Capture effects
        for effect in self.effect_system.get_active_effects():
            if hasattr(effect, 'to_dict'):
                state['effects'].append(effect.to_dict())
            else:
                state['effects'].append({
                    'name': effect.name,
                    'class': effect.__class__.__name__,
                    'parameters': copy.deepcopy(effect.parameters)
                })
        
        return state
    
    def undo(self) -> bool:
        """
        Undo the last operation.
        
        Returns:
            True if undo was successful, False if no undo available
        """
        if not self._undo_stack:
            return False
        
        try:
            # Save current state to redo stack
            current_state = self._capture_current_state()
            self._redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = self._undo_stack.pop()
            self._restore_state(previous_state)
            
            self.status_message.emit("Undo completed", 1000)
            return True
            
        except Exception as e:
            self.error_occurred.emit("Undo Error", f"Failed to undo: {str(e)}")
            return False
    
    def redo(self) -> bool:
        """
        Redo the last undone operation.
        
        Returns:
            True if redo was successful, False if no redo available
        """
        if not self._redo_stack:
            return False
        
        try:
            # Save current state to undo stack
            current_state = self._capture_current_state()
            self._undo_stack.append(current_state)
            
            # Restore next state
            next_state = self._redo_stack.pop()
            self._restore_state(next_state)
            
            self.status_message.emit("Redo completed", 1000)
            return True
            
        except Exception as e:
            self.error_occurred.emit("Redo Error", f"Failed to redo: {str(e)}")
            return False
    
    def _restore_state(self, state: Dict[str, Any]) -> None:
        """
        Restore application state from a saved state.
        
        Args:
            state: Saved state dictionary
        """
        # Restore subtitle data
        if state['subtitle_data']:
            self.subtitle_engine.load_from_data(state['subtitle_data'])
            self.subtitle_data_changed.emit()
        
        # Restore effects
        self.effect_system.clear_effects()
        for effect_data in state['effects']:
            try:
                effect_class = effect_data.get('class')
                if effect_class:
                    effect = self.effect_system.create_effect(
                        effect_class, effect_data['parameters']
                    )
                    self.effect_system.add_effect(effect)
            except Exception as e:
                print(f"Warning: Failed to restore effect: {e}")
        
        # Restore project state
        self.project_state = state['project_state']
        
        # Emit update signals
        self.effects_changed.emit(self.effect_system.get_active_effects())
        self.project_modified.emit(self.project_state.is_modified)
        
        # Update preview
        self._schedule_preview_update()
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0
    
    # Event Handlers
    
    def _on_effects_changed(self) -> None:
        """Handle effects changes from GUI."""
        self._mark_project_modified()
        self._schedule_preview_update()
    
    def _on_subtitle_changed(self) -> None:
        """Handle subtitle content changes from GUI."""
        self._mark_project_modified()
        self._schedule_preview_update()
    
    def _on_timing_changed(self) -> None:
        """Handle subtitle timing changes from GUI."""
        self._mark_project_modified()
        self._schedule_preview_update()
    
    def _on_export_progress(self, progress) -> None:
        """Handle export progress updates."""
        if hasattr(progress, 'progress'):
            self.export_progress_changed.emit(progress.progress)
        
        if hasattr(progress, 'status'):
            status_messages = {
                'preparing': 'Preparing export...',
                'rendering': 'Rendering video...',
                'finalizing': 'Finalizing export...',
                'completed': 'Export completed successfully',
                'failed': f'Export failed: {getattr(progress, "error_message", "Unknown error")}',
                'cancelled': 'Export cancelled'
            }
            
            message = status_messages.get(progress.status.value, f'Export status: {progress.status.value}')
            timeout = 0 if progress.status.value in ['rendering', 'preparing'] else 3000
            self.status_message.emit(message, timeout)
    
    def _on_subtitle_data_changed(self, subtitle_data: SubtitleData) -> None:
        """Handle subtitle data changes from editor."""
        try:
            # Update subtitle engine with new data
            self.subtitle_engine.load_from_data(subtitle_data)
            self._mark_project_modified()
            
            # Emit subtitle data changed signal
            self.subtitle_data_changed.emit()
            
            # Schedule preview update with debouncing
            self._schedule_preview_update()
            
        except Exception as e:
            self.error_occurred.emit("Subtitle Update Error", f"Failed to update subtitles: {str(e)}")
    
    def _on_preview_update_requested(self) -> None:
        """Handle explicit preview update requests from GUI."""
        self._schedule_preview_update()
    
    def _on_subtitle_line_selected(self, line_index: int) -> None:
        """Handle subtitle line selection changes."""
        # Seek preview to the selected line's start time
        if self.subtitle_engine.has_data and line_index < len(self.subtitle_engine.subtitle_data.lines):
            line = self.subtitle_engine.subtitle_data.lines[line_index]
            self.seek_to_time(line.start_time)
    
    def _on_subtitle_selection_changed(self, selection) -> None:
        """Handle subtitle selection changes."""
        # Could be used for batch operations or preview focusing
        # For now, just log the selection change
        if hasattr(selection, 'line_indices') and selection.line_indices:
            first_line_index = min(selection.line_indices)
            self._on_subtitle_line_selected(first_line_index)
    
    def _update_subtitle_editor(self) -> None:
        """Update the subtitle editor with current subtitle data."""
        if self.main_window and self.subtitle_engine.has_data:
            subtitle_editor = self.main_window.get_subtitle_editor()
            if subtitle_editor:
                subtitle_editor.set_subtitle_data(self.subtitle_engine.subtitle_data)
    
    def _on_preview_play_requested(self) -> None:
        """Handle play request from preview panel."""
        self.start_playback()
    
    def _on_preview_pause_requested(self) -> None:
        """Handle pause request from preview panel."""
        self.pause_playback()
    
    def _on_preview_stop_requested(self) -> None:
        """Handle stop request from preview panel."""
        self.stop_playback()
    
    def _on_preview_time_changed(self, time: float) -> None:
        """Handle preview time changes."""
        # The preview panel handles its own time updates through callbacks
        # This method can be used for other app-level time-based updates
        pass
    
    # Utility Methods
    
    def _mark_project_modified(self) -> None:
        """Mark the project as modified."""
        if not self.project_state.is_modified:
            self.project_state.is_modified = True
            self.project_modified.emit(True)
    
    def _reset_project_state(self) -> None:
        """Reset all project state and components."""
        # Clear media objects
        self._background_clip = None
        self._audio_clip = None
        
        # Clear components
        self.subtitle_engine.create_new()
        print(f"DEBUG: After create_new, subtitle_engine.has_data: {self.subtitle_engine.has_data}")
        self.effect_system.clear_effects()
        self.preview_engine.clear_cache()
        
        # Clear undo/redo stacks
        self._undo_stack.clear()
        self._redo_stack.clear()
        
        # Reset project state
        self.project_state = ProjectState()
    
    def _confirm_discard_changes(self) -> bool:
        """
        Show confirmation dialog for discarding unsaved changes.
        
        Returns:
            True if user confirms, False otherwise
        """
        if not self.main_window:
            return True
        
        reply = QMessageBox.question(
            self.main_window,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to discard them?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        return reply == QMessageBox.StandardButton.Yes
    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """
        Show error dialog to user.
        
        Args:
            title: Dialog title
            message: Error message
        """
        try:
            if self.main_window:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self.main_window, title, message)
        except Exception as e:
            # Fallback for testing or when GUI is not available
            print(f"Error Dialog - {title}: {message}")
            print(f"Dialog error: {e}")
    
    # Public API Methods
    
    def get_project_state(self) -> ProjectState:
        """Get current project state."""
        return self.project_state
    
    def get_subtitle_data(self) -> Optional[SubtitleData]:
        """Get current subtitle data."""
        return self.subtitle_engine.subtitle_data if self.subtitle_engine.has_data else None
    
    def get_active_effects(self) -> List:
        """Get list of active effects."""
        return self.effect_system.get_active_effects()
    
    def get_preview_duration(self) -> float:
        """Get total duration of the preview."""
        return self.preview_engine.get_duration()
    
    def get_current_time(self) -> float:
        """Get current playback time."""
        return self.preview_engine.get_current_time()
    
    def is_playing(self) -> bool:
        """Check if preview is currently playing."""
        return self.preview_engine.is_playing()