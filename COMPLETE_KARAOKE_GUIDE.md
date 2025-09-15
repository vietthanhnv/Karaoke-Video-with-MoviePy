# 🎤 Complete Karaoke Video Creation Guide

## Quick Start (Easiest Method)

**Just run this command and follow the interactive menu:**

```bash
python launch_karaoke_creator.py
```

The launcher will:

- Check your system requirements
- Install missing dependencies automatically
- Guide you through creating your first karaoke video
- Show you examples and previews

---

## Method 1: Interactive Launcher 🚀 (RECOMMENDED)

### Step 1: Launch the Interactive Menu

```bash
python launch_karaoke_creator.py
```

### Step 2: Follow the Menu Options

The launcher provides these options:

1. **Create karaoke video (with GUI)** - Full visual editor
2. **Create karaoke video (automated script)** - Quick creation
3. **Create preview images only** - See how it looks first
4. **View existing examples** - Check what you've created
5. **Install/check dependencies** - Fix any issues
6. **Exit**

### Step 3: Choose Option 3 First (Recommended)

- Select "3. Create preview images only"
- This creates preview images showing how your karaoke video will look
- No dependencies required, works immediately

### Step 4: View Your Previews

- Open the `karaoke_preview/` folder
- Look at the generated PNG files
- Each shows subtitles at different time points

### Step 5: Create Full Video (Optional)

- Go back to the menu
- Select "2. Create karaoke video (automated script)"
- Add your audio file when prompted
- Wait for video generation

---

## Method 2: Direct Script Usage ⚡

### Quick Preview (No Dependencies)

```bash
python create_karaoke_video.py --preview-only
```

### Full Video with Audio

```bash
python create_karaoke_video.py --audio your-audio-file.mp3 --duration 60
```

### Command Options

- `--audio` or `-a`: Path to your audio file (MP3, WAV, etc.)
- `--duration` or `-d`: Video length in seconds (default: 60)
- `--output` or `-o`: Output video filename
- `--preview-only` or `-p`: Create preview images only

---

## Method 3: GUI Application 🎨

### Launch GUI

```bash
python src/subtitle_creator/main.py
```

### Using the GUI

1. **File → New Project** - Start a new karaoke project
2. **File → Import Media** - Add your audio file
3. **File → Import Subtitles** - Load `examples/Dancing in Your Eyes.json`
4. **Preview** - See how it looks in real-time
5. **Effects Panel** - Customize fonts, colors, animations
6. **File → Export Video** - Create your final video

---

## What You Get

### Preview Images

- Multiple PNG files showing subtitle overlay at different times
- Located in `karaoke_preview/` folder
- Shows exactly how subtitles will appear

### Video Output

- MP4 karaoke video with synchronized subtitles
- Animated background with professional styling
- Audio track (if provided)

### Subtitle Files

- `dancing_eyes.srt` - Standard subtitle format
- `dancing_eyes.vtt` - Web-compatible format
- Compatible with any video player

---

## Example Files Included

### Dancing in Your Eyes Data

- **File**: `examples/Dancing in Your Eyes.json`
- **Content**: Complete karaoke timing data
- **Segments**: 17 subtitle segments
- **Duration**: 202 seconds of lyrics
- **Quality**: Professional timing with confidence scores

### Sample Lyrics

```
21.3s - 29.4s: "Under the glow of the silver moon, I find my heart in a tender tune."
29.4s - 38.3s: "Every step brings me close to you, every moment feels so true."
39.1s - 43.1s: "Soft is the night as it holds our song."
43.7s - 51.5s: "In your embraces where I belong, every glance is a sweet surprise."
52.0s - 55.7s: "I keep dancing in your eyes."
```

---

## Troubleshooting

### "No module named..." Errors

```bash
# Install missing packages
pip install matplotlib numpy pillow moviepy PyQt6
```

### MoviePy Issues

- If MoviePy fails, use `--preview-only` to create images first
- Preview images work without MoviePy
- Install MoviePy later for video creation

### Audio Problems

- Supported formats: MP3, WAV, M4A
- Audio is optional - you can create video without it
- Add audio later using video editing software

### GUI Won't Start

- Make sure PyQt6 is installed: `pip install PyQt6`
- Use Method 1 (launcher) or Method 2 (script) instead

---

## Advanced Usage

### Custom Audio Files

1. Place your audio file anywhere on your system
2. Use the `--audio` parameter to specify the path
3. The script will automatically sync subtitles to your audio

### Different Durations

- Use `--duration` to control video length
- Subtitles will automatically fit within the specified time
- Longer durations show more of the song

### Multiple Songs

- Create different JSON files for different songs
- Use `--json` parameter to specify different subtitle data
- Each song gets its own karaoke video

---

## File Structure After Creation

```
your-project/
├── karaoke_preview/                    # Preview images
│   ├── karaoke_frame_01_t22.3s.png   # Subtitle at 22.3 seconds
│   ├── karaoke_frame_02_t40.1s.png   # Subtitle at 40.1 seconds
│   └── ...
├── dancing_eyes_karaoke.mp4           # Final karaoke video
├── dancing_eyes.srt                   # Standard subtitles
├── dancing_eyes.vtt                   # Web subtitles
└── examples/
    └── Dancing in Your Eyes.json      # Source timing data
```

---

## Next Steps

1. **Start with previews** - Run the launcher and choose option 3
2. **View your results** - Open the preview images to see how it looks
3. **Add your audio** - Use your own music file for the full experience
4. **Customize styling** - Try the GUI for advanced visual effects
5. **Create more videos** - Use the same process with different songs

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Use the launcher's dependency checker (option 5)
3. Start with preview-only mode to test without dependencies
4. The preview images will show you exactly how the final video will look

**Happy karaoke creating! 🎵**
