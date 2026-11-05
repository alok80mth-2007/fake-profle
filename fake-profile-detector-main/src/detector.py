import os
import math
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union
import joblib
import csv
from datetime import datetime

from src.features.content_analyzer import ContentAnalyzer
from src.features.activity_analyzer import ActivityAnalyzer
from src.features.image_analyzer import ImageAnalyzer
from src.features.network_analyzer import NetworkAnalyzer
from src.models.model_loader import load_model
from src.models.train_model import FEATURE_NAMES
from src.utils.feature_extractor import FeatureExtractor

# Configure logging
logger = logging.getLogger(__name__)


class FakeProfileDetector:
    """
    Main class for detecting fake profiles on social media platforms.
    
    This class orchestrates the entire detection process by:
    1. Extracting 20+ behavioral, network, content, and metadata features
    2. Analyzing specialized aspects (content, activity, network, images)
    3. Running the ML ensemble model (Gradient Boosting + Random Forest)
    4. Generating detailed reports with calibrated confidence scores and indicators
    """
    
    def __init__(self, model_path: str = 'models/fake_profile_detector.pkl'):
        """
        Initialize the detector with pre-trained models and analyzers.
        
        Args:
            model_path: Path to the pre-trained ML model
        """
        logger.info("Initializing FakeProfileDetector")
        
        # Load the ML model or fallback to automatic training
        self.model = None
        try:
            self.model = load_model(model_path)
            logger.info(f"Loaded model from {model_path}")
        except Exception as e:
            logger.warning(f"Could not load model at {model_path}: {e}, will use heuristic detection")
            
        # Initialize the analyzers
        self.content_analyzer = ContentAnalyzer()
        self.activity_analyzer = ActivityAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.network_analyzer = NetworkAnalyzer()
        
        # Initialize the feature extractor
        self.feature_extractor = FeatureExtractor()
        
        logger.info("FakeProfileDetector initialized successfully")
    
    def _get_expected_feature_names(self) -> List[str]:
        """Retrieve the exact feature names expected by the model."""
        if hasattr(self.model, 'feature_names') and self.model.feature_names:
            return list(self.model.feature_names)
        if hasattr(self.model, 'feature_names_in_') and len(self.model.feature_names_in_) > 0:
            return list(self.model.feature_names_in_)
        return FEATURE_NAMES

    def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single profile and determine if it's fake.
        
        Args:
            profile_data: Dictionary containing profile information
            
        Returns:
            Dictionary with analysis results including:
            - is_fake: Boolean indicating if profile is likely fake
            - probability: Confidence score (0-1)
            - indicators: List of suspicious indicators found
            - feature_importance: Which features contributed most to the decision
            - recommendations: Suggested actions
        """
        username = profile_data.get('username', 'Unknown')
        logger.info(f"Analyzing profile: {username}")
        
        try:
            # Extract features from the profile data
            features = self.feature_extractor.extract_features(profile_data)
            
            # Run specialized analyzers
            content_analysis = self.content_analyzer.analyze(profile_data)
            activity_analysis = self.activity_analyzer.analyze(profile_data)
            image_analysis = self.image_analyzer.analyze(profile_data)
            network_analysis = self.network_analyzer.analyze(profile_data)
            
            # Combine all analyses
            combined_features = {
                **features,
                **content_analysis,
                **activity_analysis,
                **image_analysis,
                **network_analysis
            }
            
            # Prepare features for the model
            feature_vector = self._prepare_feature_vector(combined_features)
            
            # Make prediction using the model or fallback to heuristic
            if self.model:
                try:
                    expected_features = self._get_expected_feature_names()
                    feature_df = pd.DataFrame([feature_vector], columns=expected_features)
                    prob_array = self.model.predict_proba(feature_df)[0]
                    # Index 1 is probability of fake (class 1)
                    probability = float(prob_array[1]) if len(prob_array) > 1 else float(prob_array[0])
                except Exception as pred_err:
                    logger.warning(f"Model prediction failed ({pred_err}), using heuristic fallback")
                    probability, is_fake, feature_importance = self._heuristic_detection(combined_features)
                else:
                    probability = max(0.01, min(0.99, probability))
                    is_fake = probability >= 0.65
                    feature_importance = self._get_feature_importance(feature_vector)
            else:
                probability, is_fake, feature_importance = self._heuristic_detection(combined_features)
            
            # Generate list of suspicious indicators
            indicators = self._identify_suspicious_indicators(combined_features, feature_importance)
            
            # Generate recommendations based on the analysis
            recommendations = self._generate_recommendations(is_fake, probability, indicators)
            
            # Prepare the final result
            result = {
                'is_fake': is_fake,
                'probability': round(probability, 4),
                'indicators': indicators,
                'feature_importance': feature_importance,
                'recommendations': recommendations,
                'profile_data': profile_data,
                'combined_features': combined_features,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Analysis complete for {username}. Result: {'Fake' if is_fake else 'Real'} (Probability: {probability:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing profile: {str(e)}", exc_info=True)
            raise
    
    def batch_analyze(self, file_path: str, platform: str) -> List[Dict[str, Any]]:
        """
        Process a batch of profiles from a CSV or TXT file.
        
        Args:
            file_path: Path to file containing profile URLs or usernames
            platform: Social media platform name
            
        Returns:
            List of analysis results for each profile
        """
        logger.info(f"Starting batch analysis from {file_path} for platform {platform}")
        
        results = []
        profiles_processed = 0
        
        try:
            # Read the input file
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    profiles = [row[0].strip() for row in reader if row and row[0].strip()]
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    profiles = [line.strip() for line in f if line.strip()]
            
            # Process each profile
            from src.utils.data_processor import process_profile_url
            for profile in profiles:
                try:
                    profile_data = process_profile_url(profile, platform)
                    result = self.analyze_profile(profile_data)
                    results.append(result)
                    profiles_processed += 1
                except Exception as e:
                    logger.error(f"Error processing profile {profile}: {str(e)}")
                    results.append({
                        'error': str(e),
                        'profile': profile,
                        'platform': platform,
                        'profile_data': {
                            'username': profile,
                            'platform': platform,
                            'url': profile
                        },
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Save batch results to a CSV file
            output_file = os.path.join('results', f'batch_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            os.makedirs('results', exist_ok=True)
            self._save_batch_results(results, output_file)
            
            logger.info(f"Batch analysis completed. Processed {profiles_processed}/{len(profiles)} profiles")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}", exc_info=True)
            raise
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Convert the feature dictionary to a vector matching model expectations."""
        expected_features = self._get_expected_feature_names()
        feature_list = []
        for feat in expected_features:
            val = features.get(feat, 0.0)
            if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
                val = 0.0
            feature_list.append(float(val))
        return np.array(feature_list, dtype=float)
    
    def _get_feature_importance(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """Calculate the importance of each feature in the prediction."""
        if not self.model:
            return {}
            
        expected_features = self._get_expected_feature_names()
        
        if hasattr(self.model, 'get_feature_importances'):
            return self.model.get_feature_importances()
            
        try:
            importances = getattr(self.model, 'feature_importances_', None)
            if importances is not None and len(importances) == len(expected_features):
                return {name: float(imp) for name, imp in zip(expected_features, importances)}
        except Exception:
            pass
            
        return {name: 1.0 / len(expected_features) for name in expected_features}
    
    def _heuristic_detection(self, features: Dict[str, Any]) -> Tuple[float, bool, Dict[str, float]]:
        """
        Fallback detection method using rule-based heuristics.
        """
        red_flags = {
            'new_account': features.get('account_age_days', 365) < 30,
            'high_following_ratio': features.get('followers_to_following_ratio', 1.0) < 0.1,
            'low_reputation': features.get('reputation_ratio', 0.5) < 0.1,
            'excessive_posting': features.get('posts_per_day', 2.0) > 20,
            'suspicious_profile_pic': features.get('profile_pic_score', 0.0) > 0.7,
            'low_engagement': features.get('engagement_rate', 0.05) < 0.01,
            'suspicious_content': features.get('suspicious_content_score', 0.0) > 0.7,
            'isolated_network': features.get('network_isolation_score', 0.0) > 0.7,
            'duplicate_content': features.get('content_diversity', 1.0) < 0.3,
            'incomplete_profile': features.get('profile_completeness', 1.0) < 0.35,
            'high_username_entropy': features.get('username_entropy', 2.0) > 3.2,
        }
        
        red_flag_count = sum(1 for flag in red_flags.values() if flag)
        probability = min(0.15 + (red_flag_count / len(red_flags)) * 0.85, 0.99)
        is_fake = probability >= 0.65
        
        importance = {flag_name: (0.1 if is_triggered else 0.01) for flag_name, is_triggered in red_flags.items()}
        return probability, is_fake, importance
    
    def _identify_suspicious_indicators(self, features: Dict[str, Any], 
                                       importance: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate list of suspicious indicators based on features and their values.
        """
        indicators = []
        
        # Account age
        age = features.get('account_age_days', 365)
        if age < 30:
            indicators.append({
                'name': 'New Account',
                'description': f'Account was created recently ({int(age)} days ago)',
                'severity': 'high' if age < 7 else 'medium'
            })
            
        # Following to follower ratio
        ratio = features.get('followers_to_following_ratio', 1.0)
        followers = features.get('followers_count', 0)
        following = features.get('following_count', 0)
        if ratio < 0.1 and following > 100:
            indicators.append({
                'name': 'Following/Follower Imbalance',
                'description': f'Account follows {following:,} users but has only {followers:,} followers (ratio: {ratio:.3f})',
                'severity': 'high'
            })
            
        # Reputation Ratio (Vinod-Ghanchi metric)
        rep = features.get('reputation_ratio', 0.5)
        if rep < 0.05 and following > 150:
            indicators.append({
                'name': 'Critically Low Social Reputation',
                'description': f'Reputation score is only {rep:.1%}, characteristic of mass-following bot accounts',
                'severity': 'high'
            })
            
        # Posting frequency
        ppd = features.get('posts_per_day', 0.0)
        if ppd > 20:
            indicators.append({
                'name': 'Excessive Posting Frequency',
                'description': f'Account posts {ppd:.1f} times per day, indicating automated scripts',
                'severity': 'medium'
            })
            
        # Profile picture
        pic_score = features.get('profile_pic_score', 0.0)
        if pic_score > 0.65:
            indicators.append({
                'name': 'Suspicious Profile Picture',
                'description': 'Profile image exhibits artifacts characteristic of AI face generators or stock libraries',
                'severity': 'high'
            })
            
        # Engagement rate
        eng_rate = features.get('engagement_rate', 0.05)
        if eng_rate < 0.005 and followers > 200:
            indicators.append({
                'name': 'Extremely Low Engagement',
                'description': f'Engagement rate is {eng_rate:.3%}, far below natural audience interaction norms',
                'severity': 'medium'
            })
            
        # Content diversity
        diversity = features.get('content_diversity', 1.0)
        if diversity < 0.35:
            indicators.append({
                'name': 'Repetitive Post Content',
                'description': f'Post vocabulary diversity is unusually low ({diversity:.2f}), common in spam campaigns',
                'severity': 'medium'
            })
            
        # Suspicious content
        spam_score = features.get('suspicious_content_score', 0.0)
        if spam_score > 0.65:
            indicators.append({
                'name': 'Spam / Phishing Keyword Patterns',
                'description': 'Post texts match recurring promotional spam and external link bait patterns',
                'severity': 'high'
            })
            
        # Network isolation
        iso_score = features.get('network_isolation_score', 0.0)
        if iso_score > 0.70:
            indicators.append({
                'name': 'Isolated Social Network',
                'description': 'Account lacks organic bidirectional ties with legitimate verified accounts',
                'severity': 'high'
            })

        # Username pattern (Vinod-Ghanchi heuristic)
        entropy = features.get('username_entropy', 2.0)
        digit_ratio = features.get('username_digit_ratio', 0.0)
        if entropy > 3.3 or digit_ratio > 0.4:
            indicators.append({
                'name': 'Algorithmic Username Pattern',
                'description': f'Username displays high character randomness ({entropy:.2f}) and number density ({digit_ratio:.0%})',
                'severity': 'medium'
            })
            
        # Profile completeness
        completeness = features.get('profile_completeness', 1.0)
        if completeness < 0.35:
            indicators.append({
                'name': 'Minimal Profile Information',
                'description': f'Profile completion is only {completeness:.0%}; bio, location, and metadata are absent',
                'severity': 'low'
            })
            
        return indicators
    
    def _generate_recommendations(self, is_fake: bool, probability: float, 
                                  indicators: List[Dict[str, Any]]) -> List[str]:
        """Generate tailored recommendations based on analysis findings."""
        recommendations = []
        
        if is_fake and probability >= 0.85:
            recommendations.append("This profile is highly likely to be a fake or bot account. Consider reporting and blocking.")
        elif is_fake:
            recommendations.append("This profile exhibits multiple automated/fake patterns. Exercise caution before engaging or accepting requests.")
        elif probability >= 0.40:
            recommendations.append("This profile displays mixed signals. Verify its identity through mutual contacts before transacting or sharing data.")
        else:
            recommendations.append("This profile appears authentic based on social network, activity, and content indicators.")
            
        # Specific recommendations
        ind_names = [i['name'] for i in indicators]
        if 'Suspicious Profile Picture' in ind_names:
            recommendations.append("Conduct a reverse image search on the profile picture to verify if it was taken from stock databases or social web.")
        if 'Spam / Phishing Keyword Patterns' in ind_names:
            recommendations.append("Do not click any external links or URLs provided in the bio or recent posts.")
        if 'Following/Follower Imbalance' in ind_names or 'Critically Low Social Reputation' in ind_names:
            recommendations.append("Check who this account follows; mass-following bots frequently target popular pages to gather reciprocal follows.")
            
        return recommendations
    
    def _save_batch_results(self, results: List[Dict[str, Any]], output_file: str) -> None:
        """Save batch analysis results to a CSV file."""
        try:
            df = pd.DataFrame([{
                'username': r.get('profile_data', {}).get('username', 'Unknown'),
                'platform': r.get('profile_data', {}).get('platform', 'Unknown'),
                'is_fake': r.get('is_fake', None),
                'probability': r.get('probability', None),
                'indicators_count': len(r.get('indicators', [])),
                'top_indicator': r.get('indicators', [{}])[0].get('name', 'None') if r.get('indicators') else 'None',
                'url': r.get('profile_data', {}).get('url', ''),
                'error': r.get('error', '')
            } for r in results])
            
            df.to_csv(output_file, index=False)
            logger.info(f"Batch results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving batch results: {str(e)}", exc_info=True)
