# Model Training Guide

This guide explains how to train custom fake profile detection models.

## Prerequisites

- Python machine learning knowledge
- Labeled dataset of real and fake profiles
- Completed the [installation](installation.md)

## Preparing Training Data

Your dataset should be in CSV format with the following columns:
- `profile_id`: Unique identifier for the profile
- `platform`: Social media platform
- `is_fake`: Boolean (true/false) or numeric (1/0) indicating if the profile is fake
- Feature columns: Various profile attributes

Example:
```csv
profile_id,platform,account_age_days,followers_count,following_count,post_count,is_fake
user123,twitter,45,102,350,15,1
user456,twitter,732,1503,405,321,0
```

## Training Process

1. Navigate to "Settings > Custom Model Training"
2. Upload your training dataset
3. Configure training parameters:
   - Features to use
   - Model type (Random Forest, SVM, Neural Network)
   - Train/test split ratio
   - Hyperparameters
4. Click "Start Training"
5. Monitor the training progress

## Evaluating Models

After training, you'll see:
- Accuracy, precision, recall metrics
- Feature importance chart
- Confusion matrix
- ROC curve

Compare these metrics to decide if the model is suitable for your needs.

## Activating Your Model

1. Review the evaluation metrics
2. If satisfied, click "Activate Model"
3. The system will now use your custom model for all analyses

## Advanced: Custom Feature Engineering

For advanced users who want to define custom features:

1. Create a Python script with your feature extractors
2. Upload it in "Settings > Custom Features"
3. Map your custom features to the training data columns

## Model Management

You can:
- Save multiple models for different purposes
- Export models for external use
- Schedule periodic retraining with new data

## Troubleshooting

Common issues:
- Class imbalance: Ensure balanced fake/real samples
- Overfitting: Try reducing model complexity
- Poor performance: Consider adding more features

For technical support, refer to the [API Documentation](api_docs.md) or create an issue on GitHub.