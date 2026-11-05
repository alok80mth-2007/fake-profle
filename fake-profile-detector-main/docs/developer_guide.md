# Developer Guide

This guide is intended for developers who want to extend or modify the Fake Profile Detector.

## Project Structure

```
fake-profile-detector/
├── app.py                # Main Flask application
├── detector.py           # Core detection engine
├── models/               # ML models
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
├── utils/                # Utility functions
│   ├── data_processing.py
│   ├── feature_extraction.py
│   ├── visualization.py
│   └── api_connectors.py
├── tests/                # Unit and integration tests
└── docs/                 # Documentation
```

## Architecture

The application follows a modular architecture:

1. **Web Layer** (`app.py`, `templates/`) - Flask-based web interface
2. **Core Engine** (`detector.py`) - Detection logic and algorithms
3. **Data Processing** (`utils/data_processing.py`) - Data handling
4. **API Connectors** (`utils/api_connectors.py`) - Social media API integration
5. **ML Models** (`models/`) - Trained machine learning models

## Development Setup

1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Unix) or `venv\\Scripts\\activate` (Windows)
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest tests/`
5. Start development server: `python app.py --debug`

## Adding New Features

### Adding a New Social Media Platform

1. Create a new connector in `utils/api_connectors.py`
2. Implement platform-specific feature extraction in `utils/feature_extraction.py`
3. Update the UI to include the new platform
4. Add platform-specific tests

### Creating Custom Detection Rules

1. Define new rules in `detector.py`
2. Add appropriate feature extraction in `utils/feature_extraction.py`
3. Update model training to incorporate new features

### Extending the API

1. Define new routes in `app.py`
2. Document API changes in `docs/api_docs.md`
3. Add tests for new endpoints

## Testing

We use pytest for testing:

- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- API tests: `pytest tests/api/`

Run with coverage: `pytest --cov=.`

## Code Style

We follow PEP 8 guidelines. Run linters before submitting code:

```bash
flake8 .
black .
isort .
```

## Building Documentation

Documentation is written in Markdown. To generate HTML:

```bash
pip install mkdocs
mkdocs build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.

## Plugin System

The application supports plugins for custom feature extraction and detection rules:

1. Create a Python package with the prefix `fpd_plugin_`
2. Implement the required interfaces from `utils/plugin_base.py`
3. Install your plugin alongside the application

Example plugin structure:
```
fpd_plugin_example/
├── __init__.py
├── features.py
└── rules.py
```

## Troubleshooting Development Issues

- **Flask debugger not working**: Ensure `--debug` flag is set
- **Model loading errors**: Check model version compatibility
- **API rate limiting**: Use mock data during development