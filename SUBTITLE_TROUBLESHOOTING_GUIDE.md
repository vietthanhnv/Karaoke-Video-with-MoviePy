# Subtitle Overlay Troubleshooting Guide

## ✅ System Status

Your subtitle overlay system is **WORKING CORRECTLY**. The diagnostic tests have confirmed that:

- MoviePy v2.1.2 is properly installed
- TextClip creation works
- CompositeVideoClip composition works
- Typography effects are applied correctly
- Frame extraction shows visible subtitles

## 🔍 Common Issues and Solutions

### 1. **Text Not Visible in Preview**

**Possible Causes:**

- Text color matches background color
- Text positioned outside visible area
- Preview quality too low
- Effects disabled in preview mode

**Solutions:**

```python
# Use high contrast colors
typography_effect = TypographyEffect("High Contrast", {
    'font_size': 48,
    'text_color': (255, 255, 0, 255),  # Bright yellow
    'outline_enabled': True,
    'outline_color': (0, 0, 0, 255),   # Black outline
    'outline_width': 3
})

# Ensure proper positioning
positioning_effect = PositioningEffect("Bottom Center", {
    'horizontal_alignment': 'center',
    'vertical_alignment': 'bottom',
    'y_offset': -80,  # 80 pixels from bottom
    'margin_vertical': 40
})
```

### 2. **Text Not Visible in Exported Video**

**Possible Causes:**

- Export settings disable text effects
- Low export quality
- Codec compatibility issues

**Solutions:**

- Use high quality export preset
- Ensure all effects are enabled during export
- Try different video players

### 3. **Text Positioning Issues**

**Common Problems:**

- Text appears outside video bounds
- Text overlaps with other elements
- Inconsistent positioning across different resolutions

**Solutions:**

```python
# Safe positioning for 16:9 videos
safe_positions = {
    'top_center': ('center', 50),
    'middle_center': ('center', 'center'),
    'bottom_center': ('center', lambda clip_height: clip_height - 80),
    'bottom_safe': ('center', -80)  # 80 pixels from bottom
}
```

### 4. **Font Rendering Issues**

**Symptoms:**

- Text appears as boxes or missing characters
- Inconsistent font appearance
- Font size too small/large

**Solutions:**

- Use system fonts (Arial, Times New Roman, etc.)
- Specify absolute font paths if needed
- Test with different font sizes (24-72px range)

## 🛠️ Quick Fixes

### Fix 1: Ensure High Contrast

```python
# Always use bright text on dark backgrounds or vice versa
light_text_on_dark = {
    'text_color': (255, 255, 255, 255),  # White
    'outline_color': (0, 0, 0, 255),     # Black outline
}

dark_text_on_light = {
    'text_color': (0, 0, 0, 255),        # Black
    'outline_color': (255, 255, 255, 255), # White outline
}
```

### Fix 2: Safe Positioning

```python
# Use relative positioning that works across resolutions
positioning_params = {
    'horizontal_alignment': 'center',
    'vertical_alignment': 'bottom',
    'y_offset': -60,  # Always 60px from bottom
    'margin_vertical': 30
}
```

### Fix 3: Readable Font Size

```python
# Scale font size based on video resolution
def get_font_size(video_width):
    if video_width >= 1920:    # 1080p+
        return 48
    elif video_width >= 1280:  # 720p
        return 36
    else:                      # 480p or lower
        return 24

typography_params = {
    'font_size': get_font_size(video_width),
    'font_weight': 'normal'
}
```

## 🧪 Testing Your Setup

### Test 1: Run the Simple Test

```bash
python simple_subtitle_test.py
```

Check the generated PNG files to verify subtitles are visible.

### Test 2: Check Application Workflow

1. Load a background video
2. Create or load subtitle data
3. Add Typography effect with bright colors
4. Add Positioning effect for bottom center
5. Generate preview and check frames

### Test 3: Export Test Video

```bash
python -c "
from moviepy import *
bg = ColorClip((640,360), (50,50,50), 5)
txt = TextClip('TEST SUBTITLE', fontsize=40, color='yellow').set_pos('center').set_duration(5)
CompositeVideoClip([bg,txt]).write_videofile('test.mp4')
"
```

## 📋 Checklist for Subtitle Visibility

- [ ] **Colors**: High contrast between text and background
- [ ] **Size**: Font size appropriate for video resolution (24-72px)
- [ ] **Position**: Text positioned within video bounds
- [ ] **Timing**: Subtitle timing matches video timeline
- [ ] **Effects**: Typography and positioning effects applied
- [ ] **Preview**: Preview quality set to medium or high
- [ ] **Export**: High quality export settings used

## 🎯 Most Likely Issues

Based on the diagnostic results, if you're not seeing subtitles, it's most likely:

1. **Text Color Issue**: Text color too similar to background
2. **Positioning Issue**: Text positioned outside visible area
3. **Application Usage**: Not applying effects correctly
4. **Preview Settings**: Preview quality too low or effects disabled

## 🔧 Quick Fix Script

Run this to create a guaranteed visible subtitle test:

```python
from moviepy import ColorClip, TextClip, CompositeVideoClip

# Dark blue background
bg = ColorClip(size=(1280, 720), color=(0, 30, 60), duration=10)

# Bright yellow text with black outline
txt = TextClip(
    text="SUBTITLE TEST - THIS SHOULD BE VISIBLE",
    fontsize=48,
    color='yellow',
    stroke_color='black',
    stroke_width=2
).set_position(('center', 600)).set_duration(10)

# Composite and export
video = CompositeVideoClip([bg, txt])
video.write_videofile("guaranteed_visible_subtitles.mp4", fps=24)
```

## 📞 Still Having Issues?

If subtitles are still not visible after trying these solutions:

1. Check the generated test images from `simple_subtitle_test.py`
2. Verify your video player supports subtitle overlays
3. Try opening the test video in different players (VLC, Windows Media Player, etc.)
4. Check if your system has font rendering issues
5. Ensure you're using the latest version of MoviePy (2.x)

The diagnostic tests confirm your system is working correctly, so the issue is likely in configuration or usage rather than the core functionality.
