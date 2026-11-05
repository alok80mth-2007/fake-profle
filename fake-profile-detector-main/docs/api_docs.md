# API Documentation

This document describes the REST API endpoints available in the Fake Profile Detector.

## Authentication

All API requests require authentication using an API key:

```
Authorization: Bearer YOUR_API_KEY
```

You can generate an API key in the application's settings.

## Endpoints

### 1. Analyze Single Profile

**Endpoint:** `/api/v1/analyze`

**Method:** POST

**Request Body:**
```json
{
  "profile_url": "https://platform.com/username",
  "platform": "twitter" // Optional, can be auto-detected
}
```

**Response:**
```json
{
  "profile_id": "username",
  "authenticity_score": 85,
  "confidence": "high",
  "indicators": [
    {
      "name": "account_age",
      "value": "2 years",
      "impact": "positive"
    },
    {
      "name": "post_frequency",
      "value": "normal",
      "impact": "positive"
    }
  ],
  "recommendation": "Profile appears authentic"
}
```

### 2. Batch Analysis

**Endpoint:** `/api/v1/analyze/batch`

**Method:** POST

**Request Body:**
```json
{
  "profiles": [
    "https://platform.com/username1",
    "https://platform.com/username2"
  ]
}
```

**Response:**
```json
{
  "batch_id": "batch_12345",
  "status": "processing",
  "results_url": "/api/v1/results/batch_12345"
}
```

### 3. Get Batch Results

**Endpoint:** `/api/v1/results/{batch_id}`

**Method:** GET

**Response:**
```json
{
  "batch_id": "batch_12345",
  "status": "completed",
  "profiles_analyzed": 2,
  "results": [
    {
      "profile_id": "username1",
      "authenticity_score": 85,
      "confidence": "high"
    },
    {
      "profile_id": "username2",
      "authenticity_score": 30,
      "confidence": "medium"
    }
  ]
}
```

## Rate Limits

- Free tier: 50 requests per day
- Pro tier: 1000 requests per day
- Enterprise tier: Custom limits

## Error Codes

- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

For more details on implementation, see the [Developer Guide](developer_guide.md).