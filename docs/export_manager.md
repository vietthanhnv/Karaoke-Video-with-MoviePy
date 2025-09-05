# Export Manager Documentation

The ExportManager is a core component of the Subtitle Creator with Effects application that handles high-quality video rendering with MoviePy integration. It provides comprehensive export functionality with quality presets, custom settings, format support, progress tracking, and error handling.

## Features

### Quality Presets

The ExportManager provides three built-in quality presets:

- **High Quality (1080p)**: 1920x1080, 30 FPS, 8000k bitrate - Best quality for final output and professional use
- **Medium Quality (720p)**: 1280x720, 30 FPS, 4000k bitrate - Good balance of quality and file size for web sharing
- **Low Quality (480p)**: 854x480, 24 FPS, 2000k bitrate - Smaller file size for quick sharing and previews

### Custom Export Settings

For advanced users, the ExportManager supports custom export configurations:

- **Resolution**: Any resolution up to 8K (7680x4320)
- **Frame Rate**: 1-120 FPS
- **Bitrate**: Custom video and audio bitrates
- **Codecs**: Format-specific codec selection

### Format Support

The ExportManager supports multiple output formats with appropriate codec options:

- **MP4**: libx264, libx265, mpeg4 (video) | aac, mp3, libmp3lame (audio)
- **AVI**: libx264, mpeg4, libxvid (video) | mp3, libmp3lame, pcm_s16le (audio)
- **MOV**: libx264, libx265, prores (video) | aac, pcm_s16le, alac (audio)

### Progress Tracking

Real-time export progress tracking includes:

- **Status Updates**: Preparing → Rendering → Finalizing → Completed
- **Progress Percentage**: 0-100% completion
- **ETA Calculation**: Estimated time remaining based on current progress
- **Frame Counting**: Current frame vs total frames
- **Operation Details**: Current operation being performed

### Error Handling

Comprehensive error handling covers:

- **Input Validation**: Validates all export settings before starting
- **File System Errors**: Handles missing directories, permissions, disk space
- **Rendering Errors**: Catches and reports MoviePy rendering failures
- **Recovery**: Allows new exports after failures

## Usage Examples

### Basic Export with Quality Preset

```python
from subtitle_creator import ExportManager

# Create export manager
export_manager = ExportManager()

# Define export settings
settings = {
    "format": "mp4",
    "quality": "high"
}

# Start export
export_manager.export_video(
    background=video_clip,
    subtitle_data=subtitles,
    effects=effect_list,
    output_path="output.mp4",
    export_settings=settings
)

# Wait for completion
success = export_manager.wait_for_export_completion(timeout=300)
```

### Custom Export Settings

```python
# Custom export configuration
custom_settings = {
    "format": "mp4",
    "quality": "custom",
    "resolution": [1280, 720],
    "fps": 25,
    "bitrate": "3500k",
    "audio_bitrate": "160k",
    "codec": "libx264",
    "audio_codec": "aac"
}

export_manager.export_video(
    background=video_clip,
    subtitle_data=subtitles,
    effects=effect_list,
    output_path="custom_output.mp4",
    export_settings=custom_settings
)
```

### Progress Tracking

```python
def progress_callback(progress):
    print(f"Status: {progress.status.value}")
    print(f"Progress: {progress.progress * 100:.1f}%")
    print(f"Operation: {progress.current_operation}")
    if progress.estimated_time_remaining > 0:
        print(f"ETA: {progress.estimated_time_remaining:.0f}s")

# Add progress callback
export_manager.add_progress_callback(progress_callback)

# Start export with progress tracking
export_manager.export_video(...)
```

### Export Cancellation

```python
# Start export
export_manager.export_video(...)

# Cancel if needed
if export_manager.is_export_in_progress():
    success = export_manager.cancel_export()
    if success:
        print("Export cancelled successfully")
```

### Settings Validation

```python
# Validate settings before export
settings = {"format": "mp4", "quality": "high"}
errors = export_manager.validate_export_settings(settings)

if errors:
    print(f"Invalid settings: {errors}")
else:
    print("Settings are valid")
```

### File Size Estimation

```python
# Estimate output file size
duration = 60.0  # seconds
settings = {"format": "mp4", "quality": "medium"}

estimated_size = export_manager.estimate_file_size(duration, settings)
print(f"Estimated file size: {estimated_size / 1024 / 1024:.1f} MB")
```

## API Reference

### ExportManager Class

#### Methods

- `export_video(background, subtitle_data, effects, output_path, export_settings)` - Start video export
- `get_export_progress()` - Get current progress (0.0-1.0)
- `get_detailed_progress()` - Get detailed progress information
- `cancel_export()` - Cancel current export
- `is_export_in_progress()` - Check if export is running
- `wait_for_export_completion(timeout)` - Wait for export to finish
- `get_quality_presets()` - Get available quality presets
- `get_supported_formats()` - Get supported output formats
- `get_supported_codecs(format)` - Get codecs for specific format
- `validate_export_settings(settings)` - Validate export configuration
- `estimate_file_size(duration, settings)` - Estimate output file size
- `add_progress_callback(callback)` - Add progress update callback
- `remove_progress_callback(callback)` - Remove progress callback

#### Properties

- `QUALITY_PRESETS` - Dictionary of built-in quality presets
- `FORMAT_CODECS` - Supported codecs for each format

### ExportProgress Class

#### Properties

- `status` - Current export status (ExportStatus enum)
- `progress` - Progress percentage (0.0-1.0)
- `current_frame` - Current frame being processed
- `total_frames` - Total frames to process
- `elapsed_time` - Time elapsed since export started
- `estimated_time_remaining` - Estimated time to completion
- `current_operation` - Description of current operation
- `error_message` - Error message if export failed

### ExportStatus Enum

- `IDLE` - No export in progress
- `PREPARING` - Preparing video composition
- `RENDERING` - Rendering video frames
- `FINALIZING` - Finalizing output file
- `COMPLETED` - Export completed successfully
- `FAILED` - Export failed with error
- `CANCELLED` - Export cancelled by user

## Integration with Other Components

The ExportManager integrates seamlessly with other application components:

- **MediaManager**: Accepts VideoClip objects from media loading
- **SubtitleEngine**: Uses SubtitleData for timing and content
- **EffectSystem**: Applies Effect objects during rendering
- **PreviewEngine**: Uses same MoviePy pipeline for consistency

## Performance Considerations

- **Memory Usage**: Large videos may require significant RAM during rendering
- **CPU Usage**: Multi-threaded rendering utilizes available CPU cores
- **Disk Space**: Ensure sufficient space for output files
- **Codec Selection**: Different codecs have varying performance characteristics

## Error Recovery

The ExportManager provides robust error recovery:

1. **Validation Errors**: Caught before export starts
2. **Rendering Errors**: Reported with detailed error messages
3. **File System Errors**: Handled with appropriate user feedback
4. **Cancellation**: Clean cancellation without corrupted files
5. **Recovery**: New exports can be started after failures

## Best Practices

1. **Validate Settings**: Always validate export settings before starting
2. **Monitor Progress**: Use progress callbacks for user feedback
3. **Handle Errors**: Implement proper error handling in your application
4. **Resource Management**: Clean up resources after export completion
5. **Testing**: Test exports with various settings and content types

## Troubleshooting

### Common Issues

1. **Export Fails to Start**: Check input validation and file permissions
2. **Slow Export**: Consider lower quality settings or simpler effects
3. **Large File Sizes**: Adjust bitrate settings or use compression
4. **Codec Errors**: Ensure MoviePy dependencies are properly installed
5. **Memory Issues**: Close other applications or use lower resolution

### Debug Information

Enable debug logging to get detailed information about export operations:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

The ExportManager provides comprehensive logging for troubleshooting export issues.
