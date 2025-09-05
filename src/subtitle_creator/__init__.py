"""
Subtitle Creator with Effects - A desktop application for creating stylized subtitle videos.

This package provides tools for combining background media, timed subtitles, and visual effects
to create professional-quality subtitle videos with synchronized text overlays.
"""

__version__ = "0.1.0"
__author__ = "Subtitle Creator Team"

# Import main classes for easy access
from .export_manager import ExportManager
from .preview_engine import PreviewEngine
from .media_manager import MediaManager
from .subtitle_engine import SubtitleEngine
from .effects.system import EffectSystem

__all__ = [
    'ExportManager',
    'PreviewEngine', 
    'MediaManager',
    'SubtitleEngine',
    'EffectSystem'
]