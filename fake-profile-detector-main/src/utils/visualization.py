import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def generate_report(analysis_result: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive report from analysis results.
    
    This function prepares the data for visualization in the web interface,
    including summary statistics, charts, and detailed findings.
    
    Args:
        analysis_result: Dictionary with analysis results from the detector
        profile_data: Original profile data
        
    Returns:
        Dictionary with report data formatted for the web interface
    """
    logger.info(f"Generating report for profile: {profile_data.get('username', 'Unknown')}")
    
    try:
        # Extract key metrics from analysis result
        is_fake = analysis_result.get('is_fake', False)
        probability = analysis_result.get('probability', 0.0)
        indicators = analysis_result.get('indicators', [])
        feature_importance = analysis_result.get('feature_importance', {})
        recommendations = analysis_result.get('recommendations', [])
        
        # Format the probability score
        formatted_probability = f"{probability * 100:.1f}%"
        
        # Categorize the risk level
        if probability >= 0.9:
            risk_level = "Very High"
            risk_class = "danger"
        elif probability >= 0.7:
            risk_level = "High"
            risk_class = "danger"
        elif probability >= 0.4:
            risk_level = "Medium"
            risk_class = "warning"
        elif probability >= 0.2:
            risk_level = "Low"
            risk_class = "info"
        else:
            risk_level = "Very Low"
            risk_class = "success"
        
        # Prepare profile summary
        profile_summary = prepare_profile_summary(profile_data)
        
        # Prepare indicator details
        indicator_details = prepare_indicator_details(indicators)
        
        # Prepare feature importance for visualization
        feature_viz_data = prepare_feature_visualization(feature_importance)
        
        # Prepare comparison metrics
        comparison_metrics = prepare_comparison_metrics(analysis_result, profile_data)
        
        # Prepare platform-specific insights
        platform_insights = prepare_platform_insights(analysis_result, profile_data)
        
        # Generate detailed explanation
        detailed_explanation = generate_detailed_explanation(
            is_fake, probability, indicators, profile_data
        )
        
        # Generate a timeline if post data is available
        timeline_data = generate_timeline_data(profile_data)
        
        # Final report
        report = {
            'username': profile_data.get('username', 'Unknown'),
            'platform': profile_data.get('platform', 'Unknown'),
            'data_source': profile_data.get('data_source', 'simulated'),
            'profile_url': profile_data.get('url', ''),
            'profile_pic_url': profile_data.get('profile_pic_url', ''),
            'is_fake': is_fake,
            'probability': probability,
            'formatted_probability': formatted_probability,
            'risk_level': risk_level,
            'risk_class': risk_class,
            'profile_summary': profile_summary,
            'indicators': indicators,
            'indicator_details': indicator_details,
            'feature_importance': feature_viz_data,
            'recommendations': recommendations,
            'detailed_explanation': detailed_explanation,
            'comparison_metrics': comparison_metrics,
            'platform_insights': platform_insights,
            'timeline_data': timeline_data,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Report generation complete for {profile_data.get('username', 'Unknown')}")
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        # Return a minimal report on error
        return {
            'username': profile_data.get('username', 'Unknown'),
            'platform': profile_data.get('platform', 'Unknown'),
            'profile_url': profile_data.get('url', ''),
            'is_fake': analysis_result.get('is_fake', False),
            'probability': analysis_result.get('probability', 0.0),
            'formatted_probability': f"{analysis_result.get('probability', 0.0) * 100:.1f}%",
            'risk_level': "Unknown",
            'risk_class': "secondary",
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def prepare_profile_summary(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare a summary of profile information for the report."""
    
    # Extract common profile fields
    summary = {
        'username': profile_data.get('username', 'Unknown'),
        'name': profile_data.get('name', '') or profile_data.get('display_name', '') or profile_data.get('full_name', ''),
        'bio': profile_data.get('bio', ''),
        'followers': profile_data.get('followers_count', 0),
        'following': profile_data.get('following_count', 0),
        'posts': profile_data.get('post_count', 0),
        'creation_date': profile_data.get('creation_date', 'Unknown'),
        'verified': profile_data.get('verified', False) or profile_data.get('is_verified', False),
        'location': profile_data.get('location', ''),
        'external_url': profile_data.get('external_url', ''),
        'is_private': profile_data.get('is_private', False),
        'data_source': profile_data.get('data_source', 'simulated')
    }
    
    # Calculate account age days
    account_age_days = profile_data.get('account_age_days')
    if not account_age_days and summary['creation_date'] and summary['creation_date'] != 'Unknown':
        try:
            c_date = datetime.strptime(summary['creation_date'].split('T')[0], "%Y-%m-%d")
            account_age_days = max(1, (datetime.now() - c_date).days)
        except Exception:
            account_age_days = 365
    elif not account_age_days:
        account_age_days = 365
    summary['account_age_days'] = account_age_days
    
    # Calculate followers to following ratio
    if summary['following'] > 0:
        summary['followers_following_ratio'] = summary['followers'] / summary['following']
    else:
        summary['followers_following_ratio'] = float('inf') if summary['followers'] > 0 else 0
    
    # Format the ratio for display
    if summary['followers_following_ratio'] == float('inf'):
        summary['formatted_ratio'] = "∞"
    else:
        summary['formatted_ratio'] = f"{summary['followers_following_ratio']:.2f}"
    
    # Get platform-specific info
    platform = profile_data.get('platform', '').lower()
    if platform == 'twitter' or platform == 'x':
        summary['platform_name'] = 'Twitter/X'
        # Twitter-specific fields
        summary['retweets'] = sum(1 for post in profile_data.get('posts', []) 
                              if isinstance(post, dict) and post.get('is_retweet', False))
    elif platform == 'instagram':
        summary['platform_name'] = 'Instagram'
        # Instagram-specific fields
        summary['is_business'] = profile_data.get('is_business_account', False)
        summary['has_highlights'] = profile_data.get('has_highlights', False)
    elif platform == 'facebook':
        summary['platform_name'] = 'Facebook'
        # Facebook-specific fields
        summary['friend_count'] = profile_data.get('friend_count', 0)
        summary['page_likes'] = profile_data.get('page_likes_count', 0)
        summary['education'] = profile_data.get('education', '')
        summary['work'] = profile_data.get('work', '')
        summary['relationship_status'] = profile_data.get('relationship_status', '')
    else:
        summary['platform_name'] = 'Unknown Platform'
    
    return summary

def prepare_indicator_details(indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare detailed information about the suspicious indicators."""
    
    details = []
    
    for indicator in indicators:
        name = indicator.get('name', 'Unknown')
        description = indicator.get('description', '')
        severity = indicator.get('severity', 'medium')
        
        # Get severity class for styling
        if severity == 'high':
            severity_class = 'danger'
        elif severity == 'medium':
            severity_class = 'warning'
        else:
            severity_class = 'info'
        
        # Add explanations based on indicator type
        explanation = ''
        if name == 'New Account':
            explanation = 'Fake accounts are often recently created to avoid detection or replace banned accounts.'
        elif name == 'Following/Follower Imbalance':
            explanation = 'Fake accounts often follow many users but have few followers.'
        elif name == 'Excessive Posting':
            explanation = 'Unusually high posting frequency often indicates automation or spam activity.'
        elif name == 'Suspicious Profile Picture':
            explanation = 'AI-generated or stock photos are commonly used for fake profiles.'
        elif name == 'Low Engagement':
            explanation = 'Authentic accounts typically receive engagement proportional to their follower count.'
        elif name == 'Repetitive Content':
            explanation = 'Bot accounts often post similar content repeatedly.'
        elif name == 'Suspicious Content':
            explanation = 'Promotional language, spam patterns, or misleading claims are common in fake accounts.'
        elif name == 'Isolated Network':
            explanation = 'Fake accounts often have few connections to authentic accounts.'
        else:
            explanation = 'This pattern is associated with inauthentic behavior.'
        
        details.append({
            'name': name,
            'description': description,
            'severity': severity,
            'severity_class': severity_class,
            'explanation': explanation
        })
    
    return details

def prepare_feature_visualization(feature_importance: Dict[str, float]) -> Dict[str, Any]:
    """Prepare feature importance data for visualization."""
    
    # Sort features by importance
    sorted_features = sorted(
        feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Prepare data for chart visualization
    labels = []
    values = []
    colors = []
    
    for feature, importance in sorted_features[:10]:  # Top 10 features
        # Format feature name for display
        display_name = feature.replace('_', ' ').title()
        
        labels.append(display_name)
        values.append(importance)
        
        # Assign colors based on importance
        if importance > 0.2:
            colors.append('#dc3545')  # High importance (red)
        elif importance > 0.1:
            colors.append('#ffc107')  # Medium importance (yellow)
        else:
            colors.append('#17a2b8')  # Low importance (blue)
    
    return {
        'labels': labels,
        'values': values,
        'values_list': values,
        'scores': values,
        'colors': colors
    }

def prepare_comparison_metrics(analysis_result: Dict[str, Any], 
                           profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare metrics for comparison with typical profiles."""
    
    # Extract relevant metrics
    metrics = {}
    
    platform = profile_data.get('platform', '').lower()
    
    # Common metrics across platforms
    metrics['followers_count'] = profile_data.get('followers_count', 0)
    
    if platform == 'twitter' or platform == 'x':
        # Define typical Twitter metrics for comparison
        typical_metrics = {
            'followers_count': 707,  # Median Twitter followers
            'following_count': 395,  # Median Twitter following
            'posts_per_day': 0.5,    # Median posts per day
            'engagement_rate': 0.045  # Median engagement rate
        }
    elif platform == 'instagram':
        # Define typical Instagram metrics for comparison
        typical_metrics = {
            'followers_count': 150,  # Median Instagram followers
            'following_count': 400,  # Median Instagram following
            'posts_per_day': 0.3,    # Median posts per day
            'engagement_rate': 0.028  # Median engagement rate
        }
    elif platform == 'facebook':
        # Define typical Facebook metrics for comparison
        typical_metrics = {
            'friend_count': 338,     # Median Facebook friends
            'posts_per_day': 0.2,    # Median posts per day
            'engagement_rate': 0.035  # Median engagement rate
        }
    else:
        # Default metrics if platform unknown
        typical_metrics = {
            'followers_count': 500,
            'following_count': 500,
            'posts_per_day': 0.5,
            'engagement_rate': 0.04
        }
    
    # Get actual metrics
    actual_metrics = {}
    
    # Add basic metrics
    if platform == 'facebook':
        actual_metrics['followers_count'] = profile_data.get('friend_count', 0)
    else:
        actual_metrics['followers_count'] = profile_data.get('followers_count', 0)
        actual_metrics['following_count'] = profile_data.get('following_count', 0)
    
    # Add activity metrics
    if 'activity_analysis_performed' in analysis_result and analysis_result['activity_analysis_performed']:
        actual_metrics['posts_per_day'] = analysis_result.get('posts_per_day', 0)
        actual_metrics['engagement_rate'] = analysis_result.get('engagement_rate', 0)
    
    # Compare with typical values
    comparisons = {}
    for key in actual_metrics:
        if key in typical_metrics:
            actual = actual_metrics[key]
            typical = typical_metrics[key]
            
            # Calculate difference as a percentage
            if typical > 0:
                diff_percent = ((actual - typical) / typical) * 100
            else:
                diff_percent = 0
            
            comparisons[key] = {
                'actual': actual,
                'typical': typical,
                'diff_percent': diff_percent,
                'is_suspicious': (key == 'followers_count' and diff_percent < -80) or 
                                (key == 'following_count' and diff_percent > 200) or
                                (key == 'posts_per_day' and (diff_percent > 1000 or diff_percent < -90)) or
                                (key == 'engagement_rate' and diff_percent < -70)
            }
    
    return comparisons

def prepare_platform_insights(analysis_result: Dict[str, Any], 
                          profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare platform-specific insights."""
    
    platform = profile_data.get('platform', '').lower()
    insights = {}
    
    if platform == 'twitter' or platform == 'x':
        # Twitter-specific insights
        insights['platform_name'] = 'Twitter/X'
        insights['created_after_elon_acquisition'] = False
        
        # Check if account was created after Elon Musk's Twitter acquisition
        creation_date_str = profile_data.get('creation_date')
        if creation_date_str:
            try:
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]:
                    try:
                        creation_date = datetime.strptime(creation_date_str, fmt)
                        acquisition_date = datetime.strptime("2022-10-27", "%Y-%m-%d")
                        insights['created_after_elon_acquisition'] = creation_date > acquisition_date
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
        
        # Check for suspicious Twitter patterns
        insights['high_retweet_ratio'] = False
        posts = profile_data.get('posts', [])
        retweet_count = sum(1 for post in posts if isinstance(post, dict) and post.get('is_retweet', False))
        if posts:
            retweet_ratio = retweet_count / len(posts)
            insights['high_retweet_ratio'] = retweet_ratio > 0.8
        
    elif platform == 'instagram':
        # Instagram-specific insights
        insights['platform_name'] = 'Instagram'
        
        # Business account analysis
        insights['is_business_account'] = profile_data.get('is_business_account', False)
        
        # Hashtag analysis
        posts = profile_data.get('posts', [])
        hashtag_count = 0
        for post in posts:
            if isinstance(post, dict) and 'caption' in post:
                hashtag_count += post['caption'].count('#')
        
        if posts:
            avg_hashtags = hashtag_count / len(posts)
            insights['excessive_hashtags'] = avg_hashtags > 15
            insights['avg_hashtags_per_post'] = avg_hashtags
        else:
            insights['excessive_hashtags'] = False
            insights['avg_hashtags_per_post'] = 0
        
    elif platform == 'facebook':
        # Facebook-specific insights
        insights['platform_name'] = 'Facebook'
        
        # Check profile completeness
        profile_fields = ['work', 'education', 'relationship_status', 'location']
        filled_fields = sum(1 for field in profile_fields if profile_data.get(field))
        profile_completeness = filled_fields / len(profile_fields)
        
        insights['profile_completeness'] = profile_completeness
        insights['low_profile_completeness'] = profile_completeness < 0.25
        
        # Friend to page likes ratio
        friend_count = profile_data.get('friend_count', 0)
        page_likes = profile_data.get('page_likes_count', 0)
        
        if friend_count > 0:
            page_friend_ratio = page_likes / friend_count
            insights['high_page_like_ratio'] = page_friend_ratio > 10
            insights['page_friend_ratio'] = page_friend_ratio
        else:
            insights['high_page_like_ratio'] = False
            insights['page_friend_ratio'] = 0
    
    return insights

def generate_detailed_explanation(is_fake: bool, probability: float, 
                              indicators: List[Dict[str, Any]], 
                              profile_data: Dict[str, Any]) -> str:
    """Generate a detailed textual explanation of the analysis results."""
    
    if probability >= 0.9:
        confidence = "very high confidence"
    elif probability >= 0.7:
        confidence = "high confidence"
    elif probability >= 0.4:
        confidence = "moderate confidence"
    else:
        confidence = "low confidence"
    
    platform = profile_data.get('platform', 'social media')
    username = profile_data.get('username', 'This account')
    
    if is_fake:
        explanation = f"The analysis of the {platform} account '{username}' indicates with {confidence} "
        explanation += f"({probability:.1%}) that it is likely a fake or bot account. "
        
        if indicators:
            explanation += "The following suspicious patterns were detected: "
            indicator_list = [f"{ind['name']} ({ind['description']})" for ind in indicators[:3]]
            explanation += ", ".join(indicator_list)
            
            if len(indicators) > 3:
                explanation += f", and {len(indicators) - 3} other suspicious indicators."
            else:
                explanation += "."
    else:
        explanation = f"The analysis of the {platform} account '{username}' indicates with {confidence} "
        explanation += f"({(1-probability):.1%}) that it is likely an authentic account. "
        
        if indicators:
            explanation += "However, the following potentially suspicious patterns were detected: "
            indicator_list = [f"{ind['name']} ({ind['description']})" for ind in indicators[:2]]
            explanation += ", ".join(indicator_list) + "."
            explanation += " These patterns are not sufficient to classify the account as fake, "
            explanation += "but may warrant further investigation."
        else:
            explanation += "No significant suspicious patterns were detected."
    
    return explanation

def generate_timeline_data(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate timeline data for visualizing activity patterns."""
    
    posts = profile_data.get('posts', [])
    timeline = {
        'dates': [],
        'post_counts': [],
        'engagement': []
    }
    
    if not posts:
        return timeline
    
    # Extract post dates and sort them
    post_dates = []
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
                
                # Use just the date part
                date_str = dt.strftime("%Y-%m-%d")
                post_dates.append((date_str, post))
            except Exception:
                continue
    
    # If less than 2 posts have dates, return empty timeline
    if len(post_dates) < 2:
        return timeline
    
    # Count posts and engagement by date
    from collections import defaultdict
    date_counts = defaultdict(int)
    date_engagement = defaultdict(int)
    
    for date_str, post in post_dates:
        date_counts[date_str] += 1
        
        # Sum engagement metrics
        likes = post.get('likes', 0)
        comments = post.get('comments', 0)
        shares = post.get('shares', 0) if 'shares' in post else post.get('retweets', 0)
        
        date_engagement[date_str] += likes + comments + shares
    
    # Sort by date
    sorted_dates = sorted(date_counts.keys())
    
    # Prepare data for chart
    timeline['dates'] = sorted_dates
    timeline['post_counts'] = [date_counts[date] for date in sorted_dates]
    timeline['engagement'] = [date_engagement[date] for date in sorted_dates]
    
    return timeline