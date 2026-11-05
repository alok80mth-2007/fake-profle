# Installation Guide

This guide will help you install and set up the Fake Profile Detector on your system.

## Prerequisites

Before installing, make sure you have the following prerequisites:

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Clone or Download the Repository

```bash
git clone https://github.com/Latex999/fake-profile-detector.git
cd fake-profile-detector
```

Alternatively, you can download the repository as a ZIP file from GitHub and extract it.

### 2. Create a Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred text editor and fill in the necessary API keys and configurations.

### 5. Run the Application

```bash
python app.py
```

The application should now be running at `http://localhost:5000`.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: If you encounter errors about missing packages, try reinstalling the requirements:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **Port Already in Use**: If the default port (5000) is already in use, you can specify a different port:
   ```bash
   python app.py --port 5001
   ```

3. **Environment Variables**: Ensure all required environment variables are set in your `.env` file.

For more detailed information, see the [User Guide](user_guide.md) and [API Documentation](api_docs.md).

## Next Steps

After installation, you might want to:
- Check out the [User Guide](user_guide.md) to learn how to use the application
- Read the [API Documentation](api_docs.md) if you want to integrate with the application
- Visit the [Model Training Guide](model_training.md) if you want to train custom detection models