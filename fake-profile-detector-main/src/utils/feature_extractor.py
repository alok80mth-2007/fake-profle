import math
import collections
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class FeatureExtractor:
    """
    Extracts features from profile data for use in machine learning models.
    
    This class standardizes the extraction of features across different
    social media platforms to ensure consistent input to the ML model.
    """
    
    def __init__(self):
        """Initialize the FeatureExtractor."""
        logger.info("Initializing FeatureExtractor")
        logger.info("FeatureExtractor initialized successfully")
    
    def extract_features(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from profile data for model input.
        
        Args:
            profile_data: Dictionary containing profile information
            
        Returns:
            Dictionary with extracted features
        """
        logger.info(f"Extracting features for profile: {profile_data.get('username', 'Unknown')}")
        
        features = {}
        
        # Extract basic account metrics
        account_metrics = self._extract_account_metrics(profile_data)
        features.update(account_metrics)
        
        # Extract activity-related features
        features.update(self._extract_activity_features(profile_data, account_metrics))
        
        # Extract content-related features
        features.update(self._extract_content_features(profile_data))
        
        # Extract profile-related features
        features.update(self._extract_profile_features(profile_data))
        
        # Platform-specific features
        platform = profile_data.get('platform', '').lower()
        if platform == 'twitter' or platform == 'x':
            features.update(self._extract_twitter_features(profile_data))
        elif platform == 'instagram':
            features.update(self._extract_instagram_features(profile_data))
        elif platform == 'facebook':
            features.update(self._extract_facebook_features(profile_data))
        
        logger.info(f"Feature extraction complete for {profile_data.get('username', 'Unknown')}")
        
        return features
    
    def _extract_account_metrics(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic account metrics."""
        features = {}
        
        # Account age
        creation_date_str = profile_data.get('creation_date')
        if creation_date_str:
            try:
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]:
                    try:
                        creation_date = datetime.strptime(creation_date_str, fmt)
                        break
                    except ValueError:
                        continue
                        
                if 'creation_date' in locals():
                    # Calculate account age in days
                    features['account_age_days'] = (datetime.now() - creation_date).days
            except Exception as e:
                logger.warning(f"Error parsing creation date: {str(e)}")
                features['account_age_days'] = 365  # Default to 1 year if parse fails
        else:
            features['account_age_days'] = 365  # Default value
        
        # Follower and following counts
        followers_count = 0
        following_count = 0
        
        # Different platforms use different field names
        if 'followers_count' in profile_data:
            followers_count = profile_data['followers_count']
        elif 'friend_count' in profile_data:  # Facebook
            followers_count = profile_data['friend_count']
            
        if 'following_count' in profile_data:
            following_count = profile_data['following_count']
            
        features['followers_count'] = followers_count
        features['following_count'] = following_count
        
        # Calculate follower to following ratio
        if following_count > 0:
            features['followers_to_following_ratio'] = followers_count / following_count
        else:
            features['followers_to_following_ratio'] = 1.0 if followers_count == 0 else 100.0
            
        # Reputation ratio (Vinod-Ghanchi feature: followers / (followers + friends))
        total_connections = followers_count + following_count
        if total_connections > 0:
            features['reputation_ratio'] = followers_count / total_connections
        else:
            features['reputation_ratio'] = 0.5
        
        # Post count
        if 'post_count' in profile_data:
            features['post_count'] = profile_data['post_count']
        else:
            # Try to infer from posts list
            posts = profile_data.get('posts', [])
            features['post_count'] = len(posts)
        
        return features
    
    def _extract_activity_features(self, profile_data: Dict[str, Any], account_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract activity-related features."""
        features = {}
        
        # Posts per day
        metrics = account_metrics or {}
        account_age_days = metrics.get('account_age_days', profile_data.get('account_age_days', 365))
        post_count = metrics.get('post_count', profile_data.get('post_count', len(profile_data.get('posts', []))))
        
        if account_age_days > 0:
            features['posts_per_day'] = post_count / account_age_days
        else:
            features['posts_per_day'] = 0.0
        
        # Extract post timestamps if available
        posts = profile_data.get('posts', [])
        post_timestamps = []
        
        for post in posts:
            if isinstance(post, dict) and 'timestamp' in post:
                try:
                    # Handle different timestamp formats
                    if isinstance(post['timestamp'], (int, float)):
                        # Unix timestamp
                        dt = datetime.fromtimestamp(post['timestamp'])
                    else:
                        # ISO format or other string formats
                        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                            try:
                                dt = datetime.strptime(post['timestamp'], fmt)
                                break
                            except (ValueError, TypeError):
                                continue
                        else:
                            # If no format matched, try ISO format with parsing
                            try:
                                dt = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                            except (ValueError, AttributeError):
                                continue
                    
                    post_timestamps.append(dt)
                except Exception as e:
                    logger.debug(f"Error parsing post timestamp: {str(e)}")
        
        # Add posting time features if timestamps are available
        if post_timestamps:
            # Hours between posts (median)
            if len(post_timestamps) > 1:
                sorted_timestamps = sorted(post_timestamps)
                hours_between_posts = []
                
                for i in range(1, len(sorted_timestamps)):
                    diff_hours = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds() / 3600
                    hours_between_posts.append(diff_hours)
                
                # Sort and get median
                hours_between_posts.sort()
                median_idx = len(hours_between_posts) // 2
                features['median_hours_between_posts'] = hours_between_posts[median_idx]
            else:
                features['median_hours_between_posts'] = 24  # Default to daily
            
            # Calculate hour of day distribution (to detect automation)
            hours_of_day = [ts.hour for ts in post_timestamps]
            hour_counts = [0] * 24
            
            for hour in hours_of_day:
                hour_counts[hour] += 1
            
            # Calculate entropy of hour distribution (higher is more random/natural)
            total_posts = len(hours_of_day)
            hour_probs = [count / total_posts for count in hour_counts if count > 0]
            
            if hour_probs:
                entropy = -sum(p * math.log2(p) for p in hour_probs if p > 0)
                features['posting_time_entropy'] = float(entropy)
            else:
                features['posting_time_entropy'] = 0.0
                
            # Calculate time consistency (percentage in 8-hour window)
            max_window_posts = 0
            for start_hour in range(24):
                window_posts = sum(hour_counts[(start_hour + i) % 24] for i in range(8))
                max_window_posts = max(max_window_posts, window_posts)
            
            features['time_consistency'] = max_window_posts / total_posts if total_posts > 0 else 0
        else:
            # Default values if no timestamps
            features['median_hours_between_posts'] = 24
            features['posting_time_entropy'] = 0
            features['time_consistency'] = 0.5
        
        # Calculate engagement rate
        total_engagement = 0
        total_posts = len(posts)
        
        for post in posts:
            if isinstance(post, dict):
                # Sum likes, comments, shares/retweets
                likes = post.get('likes', 0)
                comments = post.get('comments', 0)
                shares = post.get('shares', 0) if 'shares' in post else post.get('retweets', 0)
                
                total_engagement += likes + comments + shares
        
        if total_posts > 0 and features.get('followers_count', 0) > 0:
            # Average engagement per post divided by follower count
            features['engagement_rate'] = (total_engagement / total_posts) / features['followers_count']
        else:
            features['engagement_rate'] = 0
        
        return features
    
    def _extract_content_features(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content-related features."""
        features = {}
        
        posts = profile_data.get('posts', [])
        post_texts = []
        
        # Extract text from posts
        for post in posts:
            if isinstance(post, dict):
                text = post.get('text', '') or post.get('caption', '')
                if text:
                    post_texts.append(text)
            elif isinstance(post, str):
                post_texts.append(post)
        
        # Bio length
        bio = profile_data.get('bio', '')
        features['bio_length'] = len(bio) if bio else 0
        
        # External URL
        features['has_external_url'] = 1 if profile_data.get('external_url') or profile_data.get('has_external_url') else 0
        
        # Text features if we have posts
        if post_texts:
            # Average post length
            features['avg_post_length'] = sum(len(text) for text in post_texts) / len(post_texts)
            
            # Hashtag usage
            hashtag_count = sum(text.count('#') for text in post_texts)
            features['hashtags_per_post'] = hashtag_count / len(post_texts)
            
            # URL usage
            url_indicators = ['http://', 'https://', 'www.', '.com', '.net', '.org']
            url_count = sum(any(url in text.lower() for url in url_indicators) for text in post_texts)
            features['urls_per_post'] = url_count / len(post_texts)
            
            # Mention usage
            mention_count = sum(text.count('@') for text in post_texts)
            features['mentions_per_post'] = mention_count / len(post_texts)
            
            # Emoji usage
            emoji_indicators = [':)', ':(', ':D', ';)', '❤️', '👍', '😊', '🙌', '🎉']
            emoji_count = sum(sum(text.count(emoji) for emoji in emoji_indicators) for text in post_texts)
            features['emojis_per_post'] = emoji_count / len(post_texts)
        else:
            # Default values if no post texts
            features['avg_post_length'] = 0
            features['hashtags_per_post'] = 0
            features['urls_per_post'] = 0
            features['mentions_per_post'] = 0
            features['emojis_per_post'] = 0
        
        return features
    
    def _extract_profile_features(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract profile-related features."""
        features = {}
        
        # Verified status
        features['is_verified'] = 1 if profile_data.get('verified') or profile_data.get('is_verified') else 0
        
        # Profile privacy
        features['is_private'] = 1 if profile_data.get('is_private') else 0
        
        # Username characteristics
        username = profile_data.get('username', '')
        if username:
            # Length
            features['username_length'] = len(username)
            
            # Digit ratio
            digit_count = sum(c.isdigit() for c in username)
            features['username_digit_ratio'] = digit_count / len(username) if len(username) > 0 else 0
            
            # Underscore count
            features['username_underscore_count'] = username.count('_')
            
            # Consecutive digits
            max_consecutive_digits = 0
            current_consecutive = 0
            
            for char in username:
                if char.isdigit():
                    current_consecutive += 1
                    max_consecutive_digits = max(max_consecutive_digits, current_consecutive)
                else:
                    current_consecutive = 0
            
            features['username_max_consecutive_digits'] = max_consecutive_digits
            
            # Username entropy (Shannon entropy of character distribution)
            char_counts = collections.Counter(username)
            features['username_entropy'] = float(-sum((cnt / len(username)) * math.log2(cnt / len(username)) for cnt in char_counts.values()))
        else:
            features['username_length'] = 0
            features['username_digit_ratio'] = 0
            features['username_underscore_count'] = 0
            features['username_max_consecutive_digits'] = 0
            features['username_entropy'] = 0.0
        
        # Profile completeness
        profile_fields = ['bio', 'location', 'profile_pic_url', 'name', 'display_name']
        filled_fields = sum(1 for field in profile_fields if profile_data.get(field))
        features['profile_completeness'] = filled_fields / len(profile_fields)
        
        return features
    
    def _extract_twitter_features(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Twitter/X-specific features."""
        features = {}
        
        # Retweet ratio
        posts = profile_data.get('posts', [])
        retweet_count = sum(1 for post in posts if isinstance(post, dict) and post.get('is_retweet', False))
        features['retweet_ratio'] = retweet_count / len(posts) if posts else 0
        
        # Default profile image
        profile_pic_url = profile_data.get('profile_pic_url', '')
        features['has_default_profile_image'] = 1 if 'default_profile' in profile_pic_url else 0
        
        # Tweet source consistency
        sources = [post.get('source') for post in posts if isinstance(post, dict) and 'source' in post]
        unique_sources = set(sources)
        features['source_count'] = len(unique_sources)
        
        # Twitter Blue / verification
        features['is_twitter_blue'] = 1 if profile_data.get('is_blue') else 0
        
        return features
    
    def _extract_instagram_features(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Instagram-specific features."""
        features = {}
        
        # Business account
        features['is_business_account'] = 1 if profile_data.get('is_business_account') else 0
        
        # Highlights
        features['has_highlights'] = 1 if profile_data.get('has_highlights') else 0
        
        # Hashtag usage (already covered in content features)
        
        # IGTV content
        features['has_igtv'] = 1 if profile_data.get('has_igtv') else 0
        
        # Post count to follower ratio
        post_count = profile_data.get('post_count', 0)
        followers_count = profile_data.get('followers_count', 0)
        if followers_count > 0:
            features['post_to_follower_ratio'] = post_count / followers_count
        else:
            features['post_to_follower_ratio'] = 0
        
        return features
    
    def _extract_facebook_features(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Facebook-specific features."""
        features = {}
        
        # Friend count already covered in account metrics
        
        # Page likes
        features['page_likes_count'] = profile_data.get('page_likes_count', 0)
        
        # Profile details completeness
        profile_detail_fields = ['work', 'education', 'relationship_status', 'location']
        filled_detail_fields = sum(1 for field in profile_detail_fields if profile_data.get(field))
        features['profile_details_completeness'] = filled_detail_fields / len(profile_detail_fields)
        
        # Has profile details
        features['has_profile_details'] = 1 if profile_data.get('has_profile_details') else 0
        
        return features