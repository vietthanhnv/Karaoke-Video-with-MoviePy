# 🎤 Complete Step-by-Step Guide: Creating a Karaoke Video

This comprehensive guide will walk you through creating a karaoke video using the "Dancing in Your Eyes" example data. We've created multiple ways to do this - choose the method that works best for you!

## Prerequisites

Before starting, ensure you have:

- Python 3.8+ installed
- All required dependencies installed
- The application files in your project directory
- Your audio/video file and subtitle data ready

## Step 1: Install Dependencies

First, make sure all required packages are installed:

```bash
pip install PyQt6 moviepy pillow matplotlib numpy scipy
```

## Step 2: Launch the Application

### Option A: Using the GUI Application

```bash
python src/subtitle_creator/main.py
```

### Option B: Using the Simple Test (for quick testing)

```bash
python simple_dancing_eyes_test.py
```

## Step 3: Prepare Your Files

For this example, we'll use the "Dancing in Your Eyes" data that's already available:

### Files you need:

1. **Audio file**: Your karaoke track (MP3, WAV, etc.)
2. **Subtitle data**: `examples/Dancing in Your Eyes.json` (already provided)
3. **Background video** (optional): Can be generated automatically

### File locations:

```
your-project/
├── examples/
│   └── Dancing in Your Eyes.json    # Subtitle timing data
├── audio/
│   └── your-audio-file.mp3         # Your audio track
└── output/
    └── (generated videos will go here)
```

## Step 4: Using the GUI Application

### 4.1 Start the Application

```bash
python src/subtitle_creator/main.py
```

### 4.2 Create a New Project

1. Click **File** → **New Project**
2. Choose a name for your project (e.g., "Dancing in Your Eyes Karaoke")

### 4.3 Import Your Media

1. Click **File** → **Import Media**
2. Select your audio file (MP3, WAV, etc.)
3. The application will load the audio for preview

### 4.4 Import Subtitle Data

1. Click **File** → **Import Subtitles**
2. Navigate to `examples/Dancing in Your Eyes.json`
3. Select and import the file
4. You should see the subtitle segments loaded in the timeline

### 4.5 Preview Your Karaoke Video

1. Use the preview panel to see how subtitles will appear
2. Click the play button to preview with timing
3. Adjust subtitle positioning if needed

### 4.6 Customize Styling (Optional)

1. Use the Effects panel to customize:
   - Font size and color
   - Background effects
   - Animation styles
   - Positioning

### 4.7 Export Your Video

1. Click **File** → **Export Video**
2. Choose your output format (MP4 recommended)
3. Select output location
4. Click **Export** and wait for processing

## Step 5: Alternative - Quick Creation Script

If you prefer a script-based approach, I'll create a simple karaoke video generator:

```python
# Run this command to create a quick karaoke video
python create_karaoke_video.py
```

## Step 6: Verify Your Output

After export, you should have:

- A karaoke video file (MP4)
- Subtitle files (SRT, VTT) for compatibility
- Preview images showing key moments

## Troubleshooting

### Common Issues:

1. **"No module named PyQt6"**

   ```bash
   pip install PyQt6
   ```

2. **"MoviePy import error"**

   ```bash
   pip install moviepy
   ```

3. **Audio not playing**

   - Check audio file format (MP3, WAV supported)
   - Ensure file path is correct

4. **Subtitles not appearing**
   - Verify JSON file format
   - Check timing values in subtitle data

### Getting Help:

- Check the generated preview images to verify subtitle timing
- Use the timeline view to see all subtitle segments
- Test with the simple preview scripts first

## Example Output

Your final karaoke video will include:

- Background visuals (animated or static)
- Synchronized subtitle text
- Proper timing based on the JSON data
- Professional styling and effects

## Next Steps

Once you've created your first karaoke video:

1. Experiment with different visual effects
2. Try different fonts and colors
3. Add custom backgrounds
4. Create videos for other songs

The application supports various subtitle formats and can work with any properly timed subtitle data.
