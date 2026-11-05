# Fake Profile Detector for Social Media

An AI-powered tool to detect fake, bot, and fraudulent accounts on social media platforms (Twitter/X, Instagram, and Facebook).

Incorporates social network heuristics and machine learning methodologies inspired by benchmark research and [Vinod-Ghanchi/Social-Media-Fake-Account-Detection](https://github.com/Vinod-Ghanchi/Social-Media-Fake-Account-Detection).

---

## Features

- **Advanced ML Ensemble**: High-accuracy ensemble combining **Random Forest** and **Gradient Boosting / XGBoost** classifiers with probability calibration.
- **20+ Social Indicators**:
  - Follower & Following metrics, Followers-to-Following ratio, and **Reputation Ratio** ($Followers / (Followers + Friends)$)
  - Activity & posting frequency (posts/day, posting interval regularity, circadian entropy)
  - Content NLP analysis (sentiment, vocabulary diversity, spam/phishing pattern detection)
  - Visual heuristic scoring (AI-generated face artifacts, stock photo hash matching)
  - Network graph isolation and clustering analysis
  - Username entropy and character distribution analysis
- **Modern Web Interface**: Responsive Flask UI with Plotly interactive charts for feature importance and activity timelines.
- **Batch Processing**: Upload CSV/TXT files to evaluate up to hundreds of accounts simultaneously.
- **RESTful API**: JSON endpoints (`/api/analyze` and `/api/model-info`) for easy programmatic integration.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10 to 3.13+
- pip

### 2. Setup Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(A default secure secret key is already configured for local development)*

---

## Running the Application

### Option A: From Project Folder
```bash
python app.py
```

### Option B: From Root Workspace
```bash
python run.py
```

The web dashboard will be available at: **http://127.0.0.1:5000/**

---

## Retraining the Machine Learning Model

You can retrain the ensemble model anytime:
```bash
python -m src.models.train_model
```
This performs 5-fold stratified cross-validation, reports accuracy, precision, recall, F1, and ROC-AUC, and saves:
- `models/fake_profile_detector.pkl`: Model weights and estimators bundle.
- `models/model_metadata.json`: Evaluation statistics and feature importance rankings.

---

## Running Automated Tests

To run the automated test suite:
```bash
python -m unittest tests/test_detector.py
```

---

## REST API Usage

### Single Profile Analysis
```bash
curl -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "user123", "platform": "twitter"}'
```

### Model Information & Metrics
```bash
curl http://127.0.0.1:5000/api/model-info
```

---

## License
MIT License
