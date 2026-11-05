"""
Comprehensive unit and integration tests for Fake Profile Detector using Python unittest.
"""

import os
import tempfile
import unittest
import numpy as np

from src.detector import FakeProfileDetector
from src.utils.feature_extractor import FeatureExtractor
from src.utils.data_processor import process_profile_url
from src.models.model_loader import load_model, get_model_metadata
from src.models.train_model import FEATURE_NAMES, generate_benchmark_dataset
from app import app


class TestFeatureExtractor(unittest.TestCase):
    def setUp(self):
        self.fe = FeatureExtractor()

    def test_extract_features_normal(self):
        data = {
            'username': 'normal_user_1',
            'platform': 'twitter',
            'creation_date': '2023-01-01',
            'followers_count': 1200,
            'following_count': 450,
            'posts': [
                {'text': 'Hello world', 'timestamp': '2023-06-01T12:00:00', 'likes': 25, 'comments': 5},
                {'text': 'Nice day', 'timestamp': '2023-06-02T15:30:00', 'likes': 10, 'comments': 2},
            ],
            'bio': 'Software engineer and tech enthusiast',
            'location': 'New York',
            'profile_pic_url': 'https://example.com/photo.jpg',
            'verified': False,
        }
        features = self.fe.extract_features(data)
        
        self.assertIn('reputation_ratio', features)
        self.assertIn('followers_to_following_ratio', features)
        self.assertIn('posting_time_entropy', features)
        self.assertIn('username_entropy', features)
        self.assertIn('posts_per_day', features)
        self.assertAlmostEqual(features['followers_to_following_ratio'], 1200 / 450, places=2)
        self.assertAlmostEqual(features['reputation_ratio'], 1200 / 1650, places=2)

    def test_extract_features_empty_profile(self):
        data = {'username': '', 'platform': 'instagram'}
        features = self.fe.extract_features(data)
        self.assertEqual(features['followers_count'], 0)
        self.assertEqual(features['following_count'], 0)
        self.assertEqual(features['reputation_ratio'], 0.5)
        self.assertEqual(features['posts_per_day'], 0.0)

    def test_extract_features_all_platforms(self):
        for plat in ['twitter', 'instagram', 'facebook']:
            data = process_profile_url('demo_test_user', plat)
            features = self.fe.extract_features(data)
            self.assertIsInstance(features, dict)
            self.assertGreaterEqual(len(features), 15)


class TestModelAndDetector(unittest.TestCase):
    def setUp(self):
        self.detector = FakeProfileDetector()

    def test_model_predict_proba(self):
        self.assertIsNotNone(self.detector.model)
        metadata = get_model_metadata()
        self.assertIn('metrics', metadata)
        self.assertGreaterEqual(metadata['metrics']['accuracy'], 0.85)

    def test_analyze_profile_structure(self):
        profile_data = process_profile_url('bot_user_9994', 'twitter')
        result = self.detector.analyze_profile(profile_data)
        
        self.assertIn('is_fake', result)
        self.assertIn('probability', result)
        self.assertTrue(0.0 <= result['probability'] <= 1.0)
        self.assertIn('indicators', result)
        self.assertIsInstance(result['indicators'], list)
        self.assertIn('feature_importance', result)
        self.assertIsInstance(result['feature_importance'], dict)
        self.assertIn('recommendations', result)
        self.assertGreater(len(result['recommendations']), 0)

    def test_batch_analyze(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("user_alpha\nuser_beta\n@user_gamma\n")
            temp_path = f.name
        
        try:
            results = self.detector.batch_analyze(temp_path, 'twitter')
            self.assertEqual(len(results), 3)
            for r in results:
                self.assertIn('is_fake', r)
                self.assertIn('probability', r)
                self.assertIn('profile_data', r)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestFlaskWebApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Detect Fake Social Media Profiles", resp.data)

    def test_about_page(self):
        resp = self.client.get('/about')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"About Fake Profile Detector", resp.data)
        self.assertIn(b"Model Architecture", resp.data)

    def test_batch_page(self):
        resp = self.client.get('/batch')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Batch Profile Analysis", resp.data)

    def test_analyze_flow_and_results(self):
        post_resp = self.client.post('/analyze', data={
            'profile_url': 'verified_user_1',
            'platform': 'twitter'
        }, follow_redirects=True)
        self.assertEqual(post_resp.status_code, 200)
        self.assertIn(b"Analysis Results", post_resp.data)

    def test_api_model_info(self):
        resp = self.client.get('/api/model-info')
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('metrics', json_data['model_metadata'])

    def test_api_analyze(self):
        resp = self.client.post('/api/analyze', json={
            'profile_url': 'api_test_account',
            'platform': 'instagram'
        })
        self.assertEqual(resp.status_code, 200)
        json_data = resp.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertIn('is_fake', json_data)
        self.assertIn('probability', json_data)

    def test_404_error_page(self):
        resp = self.client.get('/non-existent-page-xyz')
        self.assertEqual(resp.status_code, 404)
        self.assertIn(b"404 - Page Not Found", resp.data)


if __name__ == '__main__':
    unittest.main()
