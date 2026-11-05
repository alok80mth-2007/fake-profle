import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

class ActivityAnalyzer:
    """
    Analyzes activity patterns from social media profiles to detect anomalies
    associated with fake accounts.
    
    This includes:
    - Posting frequency and timing
    - Engagement rates
    - Activity regularity
    - Time zone patterns
    - Posting bursts
    """
    
    def __init__(self):
        """Initialize the ActivityAnalyzer with necessary resources."""
        logger.info("Initializing ActivityAnalyzer")
        logger.info("ActivityAnalyzer initialized successfully")
    
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the activity patterns from a profile to identify anomalies.
        
        Args:
            profile_data: Dictionary containing profile information including posts,
                          creation date, and activity metrics
            
        Returns:
            Dictionary with activity analysis results
        """
        logger.info(f"Analyzing activity for profile: {profile_data.get('username', 'Unknown')}")
        
        # Extract relevant data
        posts = profile_data.get('posts', [])
        creation_date_str = profile_data.get('creation_date')
        
        # Default values if data is missing
        if not posts:
            logger.warning("No posts found for activity analysis")
            return {
                'activity_analysis_performed': False,
                'posts_per_day': 0,
                'engagement_rate': 0,
                'posting_regularity': 0.5,  # Neutral score
                'activity_score': 0.5,      # Neutral score
                'time_zone_consistency': 0.5  # Neutral score
            }
        
        # Process creation date
        creation_date = None
        account_age_days = 365  # Default to 1 year if unknown
        
        if creation_date_str:
            try:
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]:
                    try:
                        creation_date = datetime.strptime(creation_date_str, fmt)
                        break
                    except ValueError:
                        continue
                        
                if creation_date:
                    # Calculate account age in days
                    account_age_days = (datetime.now() - creation_date).days
            except Exception as e:
                logger.warning(f"Error parsing creation date: {str(e)}")
        
        # Calculate posting frequency
        posts_per_day = self._calculate_posting_frequency(posts, account_age_days)
        
        # Extract post timestamps if available
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
        
        # Only analyze posting patterns if we have timestamps
        if post_timestamps:
            posting_regularity = self._analyze_posting_regularity(post_timestamps)
            time_zone_consistency = self._analyze_time_zone_consistency(post_timestamps)
            posting_bursts = self._detect_posting_bursts(post_timestamps)
        else:
            posting_regularity = 0.5  # Neutral score
            time_zone_consistency = 0.5  # Neutral score
            posting_bursts = 0
        
        # Calculate engagement rate
        engagement_rate = self._calculate_engagement_rate(posts)
        
        # Calculate overall activity score
        activity_score = self._calculate_activity_score(
            account_age_days,
            posts_per_day,
            posting_regularity,
            engagement_rate,
            time_zone_consistency,
            posting_bursts
        )
        
        logger.info(f"Activity analysis complete for {profile_data.get('username', 'Unknown')}")
        
        return {
            'activity_analysis_performed': True,
            'account_age_days': account_age_days,
            'posts_per_day': posts_per_day,
            'posting_regularity': posting_regularity,
            'time_zone_consistency': time_zone_consistency,
            'engagement_rate': engagement_rate,
            'posting_bursts': posting_bursts,
            'activity_score': activity_score
        }
    
    def _calculate_posting_frequency(self, posts: List[Any], account_age_days: int) -> float:
        """
        Calculate the average number of posts per day.
        
        Args:
            posts: List of posts
            account_age_days: Age of the account in days
            
        Returns:
            Average posts per day
        """
        if account_age_days <= 0:
            account_age_days = 1  # Avoid division by zero
            
        return len(posts) / account_age_days
    
    def _calculate_engagement_rate(self, posts: List[Any]) -> float:
        """
        Calculate the average engagement rate across posts.
        
        Engagement rate = (likes + comments + shares) / followers
        
        Returns:
            Average engagement rate (0.0 to 1.0)
        """
        total_engagement = 0
        total_posts = len(posts)
        
        if total_posts == 0:
            return 0.0
            
        for post in posts:
            if isinstance(post, dict):
                # Extract engagement metrics
                likes = post.get('likes', 0)
                comments = post.get('comments', 0)
                shares = post.get('shares', 0)
                
                # Sum the engagement
                total_engagement += likes + comments + shares
        
        # Calculate average engagement per post
        avg_engagement_per_post = total_engagement / total_posts
        
        # Normalize to a 0-1 scale using a sigmoid function
        # This assumes a "normal" engagement is around 10 interactions per post
        normalized_engagement = 1 / (1 + np.exp(-0.1 * (avg_engagement_per_post - 10)))
        
        return normalized_engagement
    
    def _analyze_posting_regularity(self, timestamps: List[datetime]) -> float:
        """
        Analyze how regular the posting pattern is.
        
        Returns a score from 0.0 (completely irregular) to 1.0 (perfectly regular).
        High regularity could be suspicious (automated posting).
        """
        if len(timestamps) < 2:
            return 0.5  # Not enough data
            
        # Sort timestamps
        sorted_timestamps = sorted(timestamps)
        
        # Calculate time differences between consecutive posts
        time_diffs = []
        for i in range(1, len(sorted_timestamps)):
            diff = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds()
            time_diffs.append(diff)
        
        # Calculate coefficient of variation (standard deviation / mean)
        # Lower values indicate more regularity
        mean_diff = np.mean(time_diffs)
        if mean_diff == 0:
            return 1.0  # Perfectly regular (suspicious)
            
        std_diff = np.std(time_diffs)
        cv = std_diff / mean_diff
        
        # Convert to regularity score (0-1)
        # Lower CV = higher regularity
        # CV of 0 = perfect regularity (score 1.0)
        # CV of 2+ = very irregular (score 0.0)
        regularity = max(0.0, min(1.0, 1.0 - (cv / 2.0)))
        
        return regularity
    
    def _analyze_time_zone_consistency(self, timestamps: List[datetime]) -> float:
        """
        Analyze if posting times are consistent with a single time zone.
        
        Returns a score from 0.0 (inconsistent) to 1.0 (very consistent).
        High consistency is normal, low consistency may indicate multiple users
        or automated posting from different locations.
        """
        if len(timestamps) < 5:
            return 0.5  # Not enough data
            
        # Extract hour of day for each post
        hours = [dt.hour for dt in timestamps]
        
        # Count frequency of each hour
        hour_counts = Counter(hours)
        
        # Calculate what percentage of posts occur in the most common 8-hour window
        # (representing a typical waking period in one time zone)
        total_posts = len(hours)
        
        # Find the 8-hour window with most posts
        max_window_posts = 0
        for start_hour in range(24):
            # Count posts in 8-hour window
            window_posts = sum(hour_counts[h % 24] for h in range(start_hour, start_hour + 8))
            max_window_posts = max(max_window_posts, window_posts)
        
        # Calculate consistency score as percentage of posts in the 8-hour window
        consistency = max_window_posts / total_posts
        
        return consistency
    
    def _detect_posting_bursts(self, timestamps: List[datetime]) -> int:
        """
        Detect unusual bursts of posting activity.
        
        A burst is defined as multiple posts within a short time frame,
        which is often associated with automated or coordinated posting.
        
        Returns:
            Number of posting bursts detected
        """
        if len(timestamps) < 3:
            return 0  # Not enough data
            
        # Sort timestamps
        sorted_timestamps = sorted(timestamps)
        
        # Define what constitutes a "burst"
        # Here: 3+ posts within a 10-minute window
        burst_window = timedelta(minutes=10)
        min_posts_for_burst = 3
        
        bursts = 0
        i = 0
        while i < len(sorted_timestamps):
            # Check if there's a burst starting at this timestamp
            window_end = sorted_timestamps[i] + burst_window
            
            # Count posts within the window
            window_posts = 0
            j = i
            while j < len(sorted_timestamps) and sorted_timestamps[j] <= window_end:
                window_posts += 1
                j += 1
            
            # Check if this qualifies as a burst
            if window_posts >= min_posts_for_burst:
                bursts += 1
                i = j  # Skip to end of this burst
            else:
                i += 1  # Move to next post
        
        return bursts
    
    def _calculate_activity_score(self, account_age_days: int, posts_per_day: float,
                              posting_regularity: float, engagement_rate: float,
                              time_zone_consistency: float, posting_bursts: int) -> float:
        """
        Calculate overall suspicious activity score based on various factors.
        
        Returns a score from 0.0 (not suspicious) to 1.0 (highly suspicious).
        """
        # Define suspicious patterns for each metric
        
        # Very new account is suspicious
        age_factor = max(0, min(1, 1 - (account_age_days / 180)))  # Max suspicion if < 6 months
        
        # Extremely high or low posting frequency is suspicious
        if posts_per_day > 15:  # Very high posting frequency
            frequency_factor = min(1, (posts_per_day - 15) / 10)  # Scales up to 1.0 at 25+ posts/day
        elif posts_per_day < 0.05:  # Very low posting frequency (less than 1 post / 20 days)
            frequency_factor = min(1, (0.05 - posts_per_day) / 0.05)  # Scales up to 1.0 at 0 posts/day
        else:
            frequency_factor = 0  # Normal posting frequency
        
        # Extremely regular posting pattern is suspicious (suggests automation)
        regularity_factor = posting_regularity if posting_regularity > 0.8 else 0
        
        # Very low engagement rate is suspicious
        engagement_factor = max(0, min(1, 1 - (engagement_rate * 10)))  # Max suspicion at 0 engagement
        
        # Inconsistent time zones can be suspicious
        time_zone_factor = max(0, min(1, 1 - time_zone_consistency))
        
        # Posting bursts are suspicious
        burst_factor = min(1, posting_bursts / 5)  # Scales up to 1.0 at 5+ bursts
        
        # Combine factors with different weights
        weights = {
            'age': 0.15,             # Account age is somewhat important
            'frequency': 0.2,        # Posting frequency is important
            'regularity': 0.15,      # Posting regularity is somewhat important
            'engagement': 0.25,      # Engagement rate is very important
            'time_zone': 0.1,        # Time zone consistency is less important
            'bursts': 0.15           # Posting bursts are somewhat important
        }
        
        suspicious_score = (
            weights['age'] * age_factor +
            weights['frequency'] * frequency_factor +
            weights['regularity'] * regularity_factor +
            weights['engagement'] * engagement_factor +
            weights['time_zone'] * time_zone_factor +
            weights['bursts'] * burst_factor
        )
        
        return suspicious_score