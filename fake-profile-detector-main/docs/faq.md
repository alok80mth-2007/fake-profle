# Frequently Asked Questions (FAQ)

## General Questions

### What is the Fake Profile Detector?
The Fake Profile Detector is an AI-powered tool that helps identify potentially fake or bot-operated social media profiles.

### Which social media platforms are supported?
Currently, we support Twitter, Instagram, Facebook, and LinkedIn. More platforms will be added in future updates.

### How accurate is the detection?
Our system achieves approximately 85-90% accuracy on validated test datasets. However, accuracy may vary depending on the characteristics of specific profiles.

## Technical Questions

### Do I need an API key for social media platforms?
Yes, for some platforms you'll need to provide API keys in your `.env` file. The application will guide you through this process during setup.

### Can I run this offline?
The core detection functionality works offline, but some features like profile data fetching require internet access.

### What are the system requirements?
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space

## Using the Application

### What does the authenticity score mean?
The authenticity score (0-100%) represents the likelihood that a profile is genuine:
- 0-30%: Highly likely to be fake
- 31-70%: Uncertain, requires manual review
- 71-100%: Likely authentic

### How do I analyze multiple profiles at once?
Use the Batch Analysis feature to upload a CSV file containing multiple profile URLs.

### Can I export the results?
Yes, you can export results in CSV, JSON, or PDF formats from the results page.

## Privacy and Security

### Does the application store user data?
By default, the application stores analysis results locally. You can configure data retention policies in the settings.

### Is my API key secure?
API keys are stored in your local `.env` file and are never transmitted to external servers.

## Troubleshooting

### The application won't start
Ensure you've installed all dependencies with `pip install -r requirements.txt` and configured your `.env` file correctly.

### Analysis is taking too long
For batch analysis of many profiles, processing time can be significant. Try reducing batch size or upgrading your hardware.

### I'm getting an "API rate limit exceeded" error
Social media platforms limit API requests. Try using a different API key or waiting before making more requests.

## Development and Contributions

### How can I contribute to the project?
Check out our [contribution guidelines](../CONTRIBUTING.md) for information on how to contribute.

### Can I build custom plugins?
Yes, the application supports a plugin system. See the developer documentation for details.

### Is there a commercial license available?
For commercial use, please contact us about licensing options.