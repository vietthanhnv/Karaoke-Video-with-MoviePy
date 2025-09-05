# MainWindow Component

The MainWindow class provides the primary GUI container for the Subtitle Creator with Effects application. It implements a comprehensive desktop interface with menu system, toolbar, responsive layout, and window state management.

## Features

### Layout Structure

The MainWindow implements a three-panel responsive layout:

- **Left Panel (60%)**: Contains the preview area and timeline editor
  - Preview widget for video display and playback controls
  - Timeline widget for subtitle editing (collapsible)
- **Right Panel (40%)**: Contains effects and styling controls
  - Effects panel for applying visual effects
  - Style controls for text formatting
- **Splitter Controls**: Resizable panels with proper handle styling

### Menu System

Complete menu bar with five main menus:

#### File Menu

- New Project (Ctrl+N)
- Open Project (Ctrl+O)
- Save Project (Ctrl+S)
- Save Project As (Ctrl+Shift+S)
- Import submenu (Background Media, Subtitles, Audio)
- Export Video (Ctrl+E)
- Exit (Ctrl+Q)

#### Edit Menu

- Undo (Ctrl+Z)
- Redo (Ctrl+Y)
- Cut (Ctrl+X)
- Copy (Ctrl+C)
- Paste (Ctrl+V)
- Select All (Ctrl+A)

#### View Menu

- Zoom In (Ctrl++)
- Zoom Out (Ctrl+-)
- Fit to Window (Ctrl+0)
- Show/Hide Timeline (Ctrl+T)
- Show/Hide Effects Panel (Ctrl+F)

#### Effects Menu

- Apply Preset
- Save Current as Preset
- Reset All Effects

#### Help Menu

- User Guide (F1)
- Keyboard Shortcuts
- About

### Toolbar

Main toolbar with common actions:

- New, Open, Save
- Play/Pause, Stop
- Export

### Window State Management

- Automatic geometry and state persistence using QSettings
- Splitter state restoration
- Panel visibility preferences
- Window centering on first launch

## Usage

### Basic Usage

```python
from PyQt6.QtWidgets import QApplication
from subtitle_creator.gui.main_window import MainWindow

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
```

### Signal Connections

The MainWindow emits signals for communication with the application controller:

```python
# Connect to project management signals
window.project_new_requested.connect(controller.new_project)
window.project_open_requested.connect(controller.open_project)
window.project_save_requested.connect(controller.save_project)
window.project_export_requested.connect(controller.export_project)

# Connect to playback signals
window.playback_play_requested.connect(controller.play_preview)
window.playback_pause_requested.connect(controller.pause_preview)
window.playback_stop_requested.connect(controller.stop_preview)
```

### State Management

```python
# Update project state
window.set_project_loaded(True)
window.set_project_modified(True)

# Update playback state
window.set_playback_state(True)  # Playing

# Show status messages
window.show_status_message("Project saved successfully", 2000)
```

### Panel Access

```python
# Get panel widgets for embedding components
preview_widget = window.get_preview_widget()
timeline_widget = window.get_timeline_widget()
effects_widget = window.get_effects_widget()

# Add custom layouts to panels
layout = QVBoxLayout(preview_widget)
layout.addWidget(custom_preview_component)
```

## Signals

### Project Management

- `project_new_requested()`: New project requested
- `project_open_requested(str)`: Open project with file path
- `project_save_requested()`: Save current project
- `project_save_as_requested(str)`: Save project with new file path
- `project_export_requested()`: Export video requested

### Playback Control

- `playback_play_requested()`: Play preview requested
- `playback_pause_requested()`: Pause preview requested
- `playback_stop_requested()`: Stop preview requested

## Public Methods

### State Management

- `set_project_modified(bool)`: Update project modification state
- `set_project_loaded(bool)`: Update project loaded state
- `set_playback_state(bool)`: Update playback state
- `show_status_message(str, int)`: Show status bar message

### Widget Access

- `get_preview_widget()`: Get preview panel widget
- `get_timeline_widget()`: Get timeline panel widget
- `get_effects_widget()`: Get effects panel widget

## Styling

The MainWindow uses a dark theme with the following color scheme:

- Background panels: `#2b2b2b` (preview), `#3c3c3c` (timeline/effects)
- Borders: `#555`
- Splitter handles: `#555` with hover effects

## Keyboard Shortcuts

| Action          | Shortcut     | Description              |
| --------------- | ------------ | ------------------------ |
| New Project     | Ctrl+N       | Create new project       |
| Open Project    | Ctrl+O       | Open existing project    |
| Save Project    | Ctrl+S       | Save current project     |
| Save As         | Ctrl+Shift+S | Save with new name       |
| Export          | Ctrl+E       | Export video             |
| Play/Pause      | Space        | Toggle preview playback  |
| Stop            | Ctrl+.       | Stop preview playback    |
| Toggle Timeline | Ctrl+T       | Show/hide timeline panel |
| Toggle Effects  | Ctrl+F       | Show/hide effects panel  |
| Zoom In         | Ctrl++       | Zoom in timeline         |
| Zoom Out        | Ctrl+-       | Zoom out timeline        |
| Fit Window      | Ctrl+0       | Fit timeline to window   |

## Requirements Satisfied

This implementation satisfies the following requirements from the specification:

- **7.1**: Complete menu bar with File, Edit, View, Effects, and Help menus
- **7.2**: Toolbar with common actions (New, Open, Save, Export, Play/Pause)
- **7.1**: Responsive layout with left panel (60%) and right panel (40%)
- **7.1**: Bottom panel for timeline editor with proper splitter controls
- **7.2**: Window state management and user preferences persistence

## Testing

The MainWindow component includes comprehensive tests covering:

- Window initialization and configuration
- Menu and toolbar creation
- Layout structure and splitter configuration
- Signal emission and handling
- State management functionality
- Panel visibility controls
- File dialog integration

Run tests with:

```bash
python -m pytest tests/test_main_window.py -v
```

## Demo

A complete demo is available that shows all MainWindow features:

```bash
python examples/main_window_demo.py
```

The demo includes:

- Interactive menu and toolbar
- Panel resizing and visibility controls
- Signal handling demonstration
- Status bar messaging
- Keyboard shortcut testing
