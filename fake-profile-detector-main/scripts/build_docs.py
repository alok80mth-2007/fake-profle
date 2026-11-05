#!/usr/bin/env python
"""
Script to build documentation for the Fake Profile Detector project.
This script uses mkdocs to generate a static website from the markdown files.
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Build the documentation using mkdocs."""
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent
    
    # Ensure we're in the project root directory
    os.chdir(project_root)
    
    print("Building documentation...")
    
    # Check if mkdocs is installed
    try:
        subprocess.run(["mkdocs", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: mkdocs is not installed or not in PATH.")
        print("Please install it with: pip install mkdocs mkdocs-material mkdocstrings")
        return 1
    
    # Build the documentation
    try:
        subprocess.run(["mkdocs", "build"], check=True)
        print("Documentation built successfully!")
        print(f"You can find the output in the {project_root / 'site'} directory.")
        
        # Optionally serve the documentation locally
        if len(sys.argv) > 1 and sys.argv[1] == "--serve":
            print("Starting local server...")
            subprocess.run(["mkdocs", "serve"], check=True)
            
    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())