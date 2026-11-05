#!/usr/bin/env python
"""
Fake Profile Detector - Root Runner.
Allows starting the web application directly from the repository root.
"""

import os
import sys

# Add inner project directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, 'fake-profile-detector-main')

if os.path.isdir(PROJECT_DIR):
    os.chdir(PROJECT_DIR)
    sys.path.insert(0, PROJECT_DIR)

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Fake Profile Detector on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
