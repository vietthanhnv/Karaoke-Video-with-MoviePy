# Project Structure

## Directory Organization

```
karaoke-video-moviepy/
├── src/                    # Source code
│   ├── karaoke/           # Main application package
│   │   ├── __init__.py
│   │   ├── generator.py   # Core karaoke video generation
│   │   ├── audio.py       # Audio processing utilities
│   │   ├── text.py        # Text rendering and timing
│   │   ├── effects.py     # Visual effects and transitions
│   │   └── config.py      # Configuration management
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── file_handler.py
│       └── validators.py
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_generator.py
│   ├── test_audio.py
│   └── fixtures/          # Test data
├── assets/                # Static resources
│   ├── fonts/            # Font files
│   ├── templates/        # Video templates
│   └── themes/           # Visual themes
├── examples/             # Example scripts and demos
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
├── setup.py             # Package configuration
├── main.py              # Entry point
└── README.md            # Project documentation
```

## File Naming Conventions

- Use snake_case for Python files and directories
- Use descriptive names that indicate functionality
- Keep module names short but clear
- Test files should mirror source structure with `test_` prefix

## Code Organization Principles

- Separate concerns: audio processing, text rendering, video composition
- Keep configuration centralized in `config.py`
- Use factory patterns for creating different karaoke styles
- Implement plugin architecture for custom effects
- Maintain clear separation between core logic and UI/CLI interfaces

## Import Structure

- Relative imports within the karaoke package
- Absolute imports for external dependencies
- Group imports: standard library, third-party, local modules
