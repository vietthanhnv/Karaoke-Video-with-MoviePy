# Subtitle Creator with Effects

A desktop application for creating stylized subtitle videos by combining background media, timed subtitles, and visual effects.

## Features

- Import various background media formats (images and videos)
- Support for subtitle files in JSON and .ASS formats
- Real-time preview with MoviePy rendering
- Comprehensive text editing and timing controls
- Visual effects including text styling, animations, and particle effects
- Flexible export options with quality presets
- Intuitive PyQt6 desktop interface

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:

```bash
git clone https://github.com/subtitle-creator/subtitle-creator-with-effects.git
cd subtitle-creator-with-effects
```

2. Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install the package in development mode:

```bash
pip install -e .
```

## Usage

### Running the Application

```bash
python main.py
```

Or using the installed console script:

```bash
subtitle-creator
```

### Development

Run tests:

```bash
python -m pytest tests/
```

Format code:

```bash
black .
flake8 .
```

## Project Structure

```
subtitle-creator-with-effects/
├── src/subtitle_creator/    # Main application package
├── tests/                   # Test suite
├── assets/                  # Static resources
├── requirements.txt         # Python dependencies
├── setup.py                # Package configuration
├── main.py                 # Entry point
└── README.md               # This file
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
