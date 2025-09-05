# Technology Stack

## Core Technologies

- **Python 3.8+**: Primary programming language
- **MoviePy**: Video editing and composition library
- **NumPy**: Numerical operations for audio/video processing
- **Pillow (PIL)**: Image processing for text rendering and effects

## Audio Processing

- **pydub**: Audio manipulation and format conversion
- **librosa**: Advanced audio analysis and feature extraction
- **scipy**: Signal processing utilities

## Text and Typography

- **fonttools**: Font handling and text rendering
- **matplotlib**: Text positioning and styling utilities

## Common Commands

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install moviepy pydub librosa pillow numpy scipy
```

### Development

```bash
# Run main application
python main.py

# Process single video
python karaoke_generator.py --audio input.mp3 --lyrics lyrics.txt --output output.mp4

# Run tests
python -m pytest tests/

# Format code
black .
flake8 .
```

### Build and Distribution

```bash
# Create executable
pyinstaller --onefile main.py

# Package for distribution
python setup.py sdist bdist_wheel
```
