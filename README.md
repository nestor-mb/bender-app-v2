# Screenshot Generator Pro

A Streamlit application for capturing website screenshots in multiple resolutions.

## Features

- Single and multiple URL processing
- Support for multiple resolutions (Desktop, Tablet, Mobile)
- Custom resolution support
- Batch processing with queue management
- Download individual screenshots or ZIP archives
- Preview thumbnails
- Cookie consent popup handling

## Project Structure

```
bender-app-v2/
├── src/
│   ├── components/        # UI components
│   │   ├── url_input.py
│   │   ├── queue_manager.py
│   │   └── results_display.py
│   ├── utils/            # Utility functions
│   │   ├── screenshot.py
│   │   └── validation.py
│   ├── styles/           # CSS styles
│   │   └── main.css
│   └── config/           # Configuration
│       └── constants.py
├── app.py               # Main application
├── requirements.txt     # Python dependencies
└── packages.txt        # System dependencies
```

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies:
- For macOS:
```bash
brew install --cask google-chrome
```
- For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install chromium-browser
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Open your browser at `http://localhost:8501`

3. Enter one or more URLs and select desired resolutions

4. Generate and download screenshots

## Best Practices

This project follows Streamlit best practices:

- Modular code organization
- Cached functions for performance
- Proper state management
- Responsive UI components
- Error handling and user feedback
- Clean and maintainable code structure
- Consistent styling
- Clear documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
