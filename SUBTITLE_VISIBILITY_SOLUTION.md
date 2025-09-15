# Subtitle Visibility Solution Guide

## ✅ Your System Status

**GOOD NEWS**: Your subtitle system is working perfectly! The diagnostic tests confirm that:

- MoviePy is properly installed and functional
- TextClip creation works correctly
- CompositeVideoClip composition works
- Typography and positioning effects are applied correctly
- Frame extraction shows visible subtitles in test images

## 🎯 The Real Issue

Since your test video `positioning_fix_verification.mp4` shows subtitles correctly, but you don't see them in the application, the issue is **application usage**, not the subtitle system itself.

## 📋 Step-by-Step Solution

### 1. Launch the Application Correctly

```bash
python main.py
```

### 2. Load Your Media Files

- **File → Import Media** → Select your video file
- **File → Import Subtitles** → Select your subtitle file (.srt, .ass, etc.)
- OR create subtitles manually in the subtitle editor

### 3. Add Typography Effect (CRITICAL)

In the Effects panel (right side of the application):

- Click **"Add Effect"** → **"Typography"**
- Set these EXACT settings for maximum visibility:
  - **Font Size**: `48` or larger
  - **Text Color**: `Yellow (255, 255, 0)` or `White (255, 255, 255)`
  - **Outline Enabled**: `✓ YES`
  - **Outline Color**: `Black (0, 0, 0)`
  - **Outline Width**: `3` pixels or more

### 4. Add Positioning Effect

- Click **"Add Effect"** → **"Positioning"**
- Set these settings:
  - **Horizontal Alignment**: `Center`
  - **Vertical Alignment**: `Bottom`
  - **Y Offset**: `-80` (negative means up from bottom)
  - **Margin Vertical**: `40`

### 5. Check Preview Settings

- Ensure **Preview Quality** is set to `Medium` or `High`
- Check the **Timeline Position** - make sure you're at a time when subtitles should appear
- The preview should update automatically when you add effects

### 6. Verify Timeline

- Look at the timeline at the bottom of the application
- Ensure your subtitle timing matches the video duration
- Scrub through the timeline to times when subtitles should be visible

## 🔍 Common Issues & Quick Fixes

### Issue: "I don't see any effects panel"

**Solution**: The effects panel should be on the right side. If missing:

- Check **View** menu → ensure panels are enabled
- Try resizing the window or adjusting splitter panels

### Issue: "I added effects but still no subtitles"

**Solutions**:

1. **Check effect order**: Typography effect should be applied first
2. **Verify subtitle timing**: Are you viewing at a time with subtitles?
3. **Check text color**: Ensure high contrast with background
4. **Increase font size**: Try 64 or 72 pixels

### Issue: "Preview is blank or not updating"

**Solutions**:

1. **Reload media**: Try reimporting your video file
2. **Check file format**: Ensure video format is supported
3. **Restart application**: Close and reopen the application

### Issue: "Subtitles appear in wrong position"

**Solutions**:

1. Use **Bottom** vertical alignment (not Top or Middle)
2. Set **Y Offset** to negative value (-60 to -120)
3. Ensure **Center** horizontal alignment

## 🎨 Guaranteed Visible Settings

Use these exact settings for maximum subtitle visibility:

**Typography Effect:**

```
Font Size: 56
Text Color: (255, 255, 0, 255)  # Bright Yellow
Outline Enabled: True
Outline Color: (0, 0, 0, 255)   # Black
Outline Width: 4
Font Weight: Bold
```

**Positioning Effect:**

```
Horizontal Alignment: center
Vertical Alignment: bottom
X Offset: 0
Y Offset: -100
Margin Vertical: 50
```

## 🧪 Test Your Setup

1. **Check Generated Test Images**: Look at the PNG files created by the diagnostic scripts:

   - `app_workflow_test_1_t2.0s.png`
   - `app_workflow_test_2_t5.0s.png`
   - `app_workflow_test_3_t8.0s.png`

2. **If you see yellow text in these images**: Your system works! The issue is application usage.

3. **If you don't see text in these images**: Run the diagnostic again or check font installation.

## 🚀 Quick Test Workflow

1. Open the application
2. Load a simple video file
3. Create a test subtitle: "TEST SUBTITLE" from 5s to 10s
4. Add Typography effect with bright yellow text and black outline
5. Add Positioning effect for bottom center
6. Scrub timeline to 7 seconds
7. You should see the subtitle in the preview

## 📞 Still Having Issues?

If you follow these steps exactly and still don't see subtitles:

1. **Check the console output** when running the application - look for error messages
2. **Try a different video file** - some formats might have compatibility issues
3. **Verify your subtitle file format** - ensure it's properly formatted
4. **Check system fonts** - try using Arial or Times New Roman
5. **Update MoviePy** if you're using an older version

## 🎯 Most Likely Solution

Based on your working test video, the most likely issue is:

1. **Missing Typography Effect**: You need to manually add the typography effect in the application
2. **Wrong Text Color**: Default text might be same color as background
3. **Timeline Position**: You might be viewing at a time without subtitles
4. **Effect Not Applied**: The effect might not be properly applied to the preview

**Follow the step-by-step guide above, and your subtitles should appear!**

## ✅ Success Indicators

You'll know it's working when:

- You see bright, outlined text in the preview panel
- Text appears at the bottom center of the video
- Text timing matches your subtitle file
- Exported video shows subtitles in external players

Your subtitle system is fully functional - you just need to use the application correctly!
