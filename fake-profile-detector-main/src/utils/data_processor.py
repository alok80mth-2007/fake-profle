import os
import re
import logging
import json
import html
import requests
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse
import time
from datetime import datetime, timedelta
import random

# Configure logging
logger = logging.getLogger(__name__)

def process_profile_url(profile_input: str, platform: str, custom_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process a profile URL or username and extract profile data.
    
    Args:
        profile_input: URL or username of the profile
        platform: Social media platform (twitter, instagram, facebook)
        custom_overrides: Optional dict of manual metric overrides (followers, following, posts, etc.)
        
    Returns:
        Dictionary with profile data
    """
    logger.info(f"Processing profile: {profile_input} on platform: {platform}")
    
    # Normalize platform name
    platform = platform.lower().strip()
    
    # Extract username from URL if needed
    username = extract_username_from_input(profile_input, platform)
    
    if not username:
        raise ValueError(f"Could not extract a valid username from '{profile_input}'")
    
    # Get profile data based on platform
    if platform == 'twitter' or platform == 'x':
        profile_data = get_twitter_profile_data(username)
    elif platform == 'instagram':
        profile_data = get_instagram_profile_data(username)
    elif platform == 'facebook':
        profile_data = get_facebook_profile_data(username)
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    
    # Add original input and platform to profile data
    profile_data['original_input'] = profile_input
    profile_data['platform'] = platform
    profile_data['username'] = username
    
    # Apply manual overrides if provided
    if custom_overrides:
        has_manual = False
        for k, v in custom_overrides.items():
            if v is not None and v != '':
                profile_data[k] = v
                has_manual = True
        if has_manual:
            profile_data['data_source'] = 'manual'
    
    # Add URL if not already present
    if 'url' not in profile_data:
        profile_data['url'] = generate_profile_url(username, platform)
    
    logger.info(f"Successfully processed profile for {username} on {platform} (data source: {profile_data.get('data_source', 'simulated')})")
    
    return profile_data

def extract_username_from_input(profile_input: str, platform: str) -> Optional[str]:
    """
    Extract username from a profile URL or direct username input.
    
    Args:
        profile_input: URL or username string
        platform: Social media platform
        
    Returns:
        Extracted username or None if extraction failed
    """
    # Check if it's already a username (no slashes or dots)
    if re.match(r'^[A-Za-z0-9_]+$', profile_input):
        return profile_input
    
    # Parse URL to extract username
    try:
        parsed_url = urlparse(profile_input)
        
        # Add https:// if missing to help with parsing
        if not parsed_url.scheme:
            parsed_url = urlparse(f"https://{profile_input}")
        
        # Extract username based on platform URL patterns
        path = parsed_url.path.strip('/')
        
        if platform == 'twitter' or platform == 'x':
            # Twitter URL patterns:
            # twitter.com/username
            # x.com/username
            netloc = parsed_url.netloc.lower()
            if netloc in ['twitter.com', 'www.twitter.com', 'x.com', 'www.x.com']:
                # Split path by / and take the first segment as username
                username = path.split('/')[0] if path else None
                return username
        
        elif platform == 'instagram':
            # Instagram URL patterns:
            # instagram.com/username
            # instagram.com/username/
            netloc = parsed_url.netloc.lower()
            if netloc in ['instagram.com', 'www.instagram.com']:
                # Split path by / and take the first segment as username
                username = path.split('/')[0] if path else None
                return username
        
        elif platform == 'facebook':
            # Facebook URL patterns:
            # facebook.com/username
            # facebook.com/profile.php?id=123456789
            netloc = parsed_url.netloc.lower()
            if netloc in ['facebook.com', 'www.facebook.com']:
                if path.startswith('profile.php'):
                    # Extract user ID from URL query
                    if parsed_url.query:
                        query_params = dict(param.split('=') for param in parsed_url.query.split('&'))
                        return query_params.get('id')
                else:
                    # Split path by / and take the first segment as username
                    username = path.split('/')[0] if path else None
                    return username
    
    except Exception as e:
        logger.error(f"Error extracting username from URL: {str(e)}", exc_info=True)
    
    # If we can't parse it as a URL, try to extract username heuristically
    # Look for patterns like @username
    if profile_input.startswith('@'):
        return profile_input[1:]
    
    # As a last resort, just return the input as-is if it seems like a username
    if re.match(r'^[A-Za-z0-9_.]+$', profile_input):
        return profile_input
    
    # Failed to extract username
    return None

def generate_profile_url(username: str, platform: str) -> str:
    """Generate a profile URL based on username and platform."""
    if platform == 'twitter' or platform == 'x':
        return f"https://twitter.com/{username}"
    elif platform == 'instagram':
        return f"https://instagram.com/{username}"
    elif platform == 'facebook':
        if username.isdigit():  # Facebook ID
            return f"https://facebook.com/profile.php?id={username}"
        else:
            return f"https://facebook.com/{username}"
    else:
        return ""

# The following functions simulate API calls for different platforms
# In a real implementation, these would make actual API calls to the platforms

def get_twitter_profile_data(username: str) -> Dict[str, Any]:
    """
    Simulate fetching Twitter profile data.
    
    In a real implementation, this would use the Twitter API.
    """
    # Seed random generator with username for consistency
    seed = int(hash(username) % 10000000)
    random.seed(seed)
    
    # Generate creation date (between 2006 and now)
    oldest_date = datetime(2006, 3, 21)  # Twitter launch date
    days_since_launch = (datetime.now() - oldest_date).days
    account_age_days = random.randint(1, days_since_launch)
    creation_date = datetime.now() - timedelta(days=account_age_days)
    
    # Generate follower and following counts
    # More suspicious accounts tend to have weird follower/following ratios
    is_suspicious = random.random() < 0.3  # 30% chance account is suspicious
    
    if is_suspicious:
        # Suspicious accounts often follow many but have few followers
        followers_count = random.randint(1, 100)
        following_count = random.randint(500, 5000)
    else:
        # Normal accounts have more balanced ratios
        followers_base = random.randint(10, 1000)
        following_base = random.randint(50, 500)
        followers_count = followers_base
        following_count = following_base
    
    # Generate post count and post history
    if is_suspicious:
        # Suspicious accounts often have few posts or too many
        if random.random() < 0.5:
            post_count = random.randint(0, 10)
        else:
            post_count = random.randint(1000, 10000)
    else:
        post_count = random.randint(10, 500)
    
    # Generate post history (up to 20 recent posts)
    posts = []
    for i in range(min(20, post_count)):
        post_date = creation_date + timedelta(days=random.randint(1, account_age_days))
        
        # Generate engagement metrics
        if is_suspicious:
            likes = random.randint(0, 5)
            retweets = random.randint(0, 2)
            comments = random.randint(0, 3)
        else:
            likes = random.randint(1, 50)
            retweets = random.randint(0, 15)
            comments = random.randint(0, 20)
        
        # Generate post text
        if is_suspicious:
            # Suspicious accounts often post promotional content
            promo_phrases = [
                "Check out this amazing offer!",
                "Make money fast with this simple trick!",
                "You won't believe what happens next!",
                "Follow me for more content!",
                "DM me for exclusive deals!",
                "Click the link in my bio!",
                "Free gift for my followers!",
                "Limited time offer!",
                "Don't miss out on this opportunity!",
                "100% guaranteed results!"
            ]
            text = random.choice(promo_phrases)
        else:
            # Regular accounts post more diverse content
            normal_phrases = [
                f"Just had a great time at {random.choice(['the park', 'the beach', 'the movies', 'dinner'])}!",
                f"Really enjoying this {random.choice(['book', 'show', 'movie', 'game'])} right now.",
                f"Can't believe what happened with {random.choice(['the news', 'my friend', 'that team', 'the weather'])} today.",
                f"Happy {random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}!",
                f"Thinking about {random.choice(['the future', 'my plans', 'my work', 'my family'])}.",
                f"Just {random.choice(['cooked', 'baked', 'made', 'created'])} something amazing!",
                f"What a beautiful {random.choice(['day', 'sunset', 'view', 'moment'])}!",
                f"So excited about {random.choice(['my trip', 'the weekend', 'this project', 'these plans'])}!",
                f"Feeling {random.choice(['happy', 'sad', 'excited', 'grateful', 'inspired'])} today.",
                f"Anyone else watching {random.choice(['the game', 'this show', 'this movie', 'the news'])}?"
            ]
            text = random.choice(normal_phrases)
        
        posts.append({
            'text': text,
            'timestamp': post_date.isoformat(),
            'likes': likes,
            'retweets': retweets,
            'comments': comments
        })
    
    # Generate profile picture URL
    if is_suspicious and random.random() < 0.7:
        # Suspicious accounts often use stock photos or no photo
        profile_pic_types = [
            "default_profile_400x400.png",
            "stock_business_person.jpg",
            "ai_generated_face.png",
            "blank_avatar.png"
        ]
        profile_pic_url = f"https://example.com/images/{random.choice(profile_pic_types)}"
    else:
        profile_pic_url = f"https://pbs.twimg.com/profile_images/{random.randint(1000000, 9999999)}/{username}_{random.randint(100, 999)}.jpg"
    
    # Generate a bio
    if is_suspicious:
        # Suspicious accounts often have promotional or minimal bios
        suspicious_bios = [
            "DM for business inquiries!",
            "Entrepreneur | Investor | Making money online",
            "Follow for follow back!",
            "Check link in bio for amazing deals!",
            "Official account - Verified business partner",
            "",  # Empty bio
            "Making dreams come true since " + creation_date.strftime("%Y"),
            "Crypto expert | Financial advisor | Not financial advice",
            "Join my network and start earning today!",
            "♦️ Exclusive content ♦️ Link in bio ♦️"
        ]
        bio = random.choice(suspicious_bios)
    else:
        # Regular accounts have more personalized bios
        normal_bios = [
            f"{random.choice(['Writer', 'Designer', 'Developer', 'Artist', 'Teacher'])} | {random.choice(['Coffee lover', 'Dog person', 'Music enthusiast', 'Foodie', 'Traveler'])}",
            f"Living in {random.choice(['NYC', 'LA', 'London', 'Tokyo', 'Paris', 'Berlin', 'Sydney'])}",
            f"{random.choice(['Mom', 'Dad', 'Parent'])} of {random.randint(1, 4)} | {random.choice(['Reader', 'Runner', 'Gamer', 'Cook', 'Photographer'])}",
            f"Working at {random.choice(['Google', 'Amazon', 'Self-employed', 'Freelancer', 'StartupName'])}",
            f"{random.choice(['Happy', 'Curious', 'Creative', 'Passionate'])} about {random.choice(['life', 'art', 'technology', 'science', 'music'])}",
            f"{random.choice(['Thoughts are my own', 'Views = mine', 'Personal account'])}",
            f"Graduated from {random.choice(['University of X', 'X College', 'School of Y'])}",
            f"{random.choice(['Follow for', 'Sharing', 'Talking about'])} {random.choice(['tech', 'food', 'travel', 'sports', 'politics'])}",
            f"{random.choice(['She/her', 'He/him', 'They/them'])} | {random.choice(['Introvert', 'Extrovert', 'Ambivert'])}",
            f"Just here for {random.choice(['the memes', 'fun', 'good vibes', 'learning', 'connecting'])}"
        ]
        bio = random.choice(normal_bios)
    
    # Return simulated profile data
    return {
        'username': username,
        'display_name': username.title(),
        'url': f"https://twitter.com/{username}",
        'bio': bio,
        'location': random.choice(['New York', 'London', 'Tokyo', 'San Francisco', 'Paris', '', 'Remote', 'Earth']),
        'creation_date': creation_date.strftime("%Y-%m-%d"),
        'account_age_days': account_age_days,
        'followers_count': followers_count,
        'following_count': following_count,
        'post_count': post_count,
        'profile_pic_url': profile_pic_url,
        'verified': not is_suspicious and random.random() < 0.1,  # 10% chance of being verified if not suspicious
        'posts': posts,
        'has_external_url': is_suspicious and random.random() < 0.8,  # Suspicious accounts often have external URLs
        'is_private': not is_suspicious and random.random() < 0.2,  # 20% chance of being private if not suspicious
        'data_source': 'simulated'
    }

def fetch_live_instagram_profile(username: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to scrape live, authentic profile details directly from Instagram's public profile page.
    Extracts real followers, following, posts, bio, and profile picture.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    url = f"https://www.instagram.com/{username}/"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            logger.warning(f"Live Instagram request returned HTTP {r.status_code} for user: {username}")
            return None
        
        text = r.text
        
        # Look for og:description tag
        desc_m = re.search(r'<meta[^>]+(?:property|name)=["\']og:description["\']\s+content=["\']([^"\']+)["\']', text)
        if not desc_m:
            desc_m = re.search(r'content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:description["\']', text)
            
        if not desc_m:
            logger.warning(f"Could not find og:description metadata for Instagram user: {username}")
            return None
            
        og_content = html.unescape(desc_m.group(1))
        # Matches format: "1,237 Followers, 392 Following, 59 Posts - See Instagram photos..."
        stats_m = re.search(r'([\d,KMkm.]+)\s*Followers?,\s*([\d,KMkm.]+)\s*Following,\s*([\d,KMkm.]+)\s*Posts?', og_content, re.IGNORECASE)
        if not stats_m:
            logger.warning(f"Could not parse numeric follower metrics from og:description: {og_content}")
            return None
            
        def parse_num(s: str) -> int:
            s = s.replace(',', '').strip()
            mult = 1
            if s.lower().endswith('k'):
                mult = 1000
                s = s[:-1]
            elif s.lower().endswith('m'):
                mult = 1000000
                s = s[:-1]
            elif s.lower().endswith('b'):
                mult = 1000000000
                s = s[:-1]
            return int(float(s) * mult)
            
        followers_count = parse_num(stats_m.group(1))
        following_count = parse_num(stats_m.group(2))
        post_count = parse_num(stats_m.group(3))
        
        # Profile picture URL
        img_m = re.search(r'<meta[^>]+(?:property|name)=["\']og:image["\']\s+content=["\']([^"\']+)["\']', text)
        if not img_m:
            img_m = re.search(r'content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:image["\']', text)
        profile_pic_url = html.unescape(img_m.group(1)) if img_m else f"https://instagram.com/p/{username}_avatar.jpg"
        
        # Real bio from description meta tag
        bio_m = re.search(r'on Instagram:\s*&quot;(.*?)(?:&quot;|\")', text, re.DOTALL)
        bio = html.unescape(bio_m.group(1)).strip() if bio_m else ''
        
        # Full name / display title
        title_m = re.search(r'<title>(.*?)</title>', text)
        full_name = username.title()
        if title_m:
            t = html.unescape(title_m.group(1))
            if '(' in t:
                full_name = t.split('(')[0].strip()
            elif '-' in t:
                full_name = t.split('-')[0].strip()
                
        is_private = 'This Account is Private' in text or '"is_private":true' in text
        is_verified = bool(re.search(r'"is_verified":\s*true', text, re.IGNORECASE))
        
        # Realistic account age calculation:
        # If public post count > 0, account has been active. We estimate at least 1-3 years for active profiles.
        est_age_days = max(180, min(3650, post_count * 20 + 365))
        creation_date = (datetime.now() - timedelta(days=est_age_days)).strftime("%Y-%m-%d")
        
        posts = []
        if bio:
            posts.append({
                'caption': bio,
                'text': bio,
                'timestamp': datetime.now().isoformat(),
                'likes': max(1, int(followers_count * 0.05)),
                'comments': max(0, int(followers_count * 0.01))
            })
            
        logger.info(f"Successfully retrieved live Instagram profile for {username}: {followers_count} followers, {following_count} following, {post_count} posts")
        
        return {
            'username': username,
            'full_name': full_name,
            'name': full_name,
            'url': url,
            'bio': bio,
            'external_url': '',
            'creation_date': creation_date,
            'account_age_days': est_age_days,
            'followers_count': followers_count,
            'following_count': following_count,
            'post_count': post_count,
            'profile_pic_url': profile_pic_url,
            'is_verified': is_verified,
            'verified': is_verified,
            'posts': posts,
            'is_private': is_private,
            'has_highlights': False,
            'is_business_account': False,
            'data_source': 'live'
        }
    except Exception as e:
        logger.warning(f"Error fetching live Instagram profile for {username}: {str(e)}")
        return None

def get_instagram_profile_data(username: str) -> Dict[str, Any]:
    """
    Fetch Instagram profile data.
    First attempts to scrape live public profile data.
    Falls back to synthetic simulation if rate-limited or unavailable.
    """
    live_data = fetch_live_instagram_profile(username)
    if live_data:
        return live_data
    
    logger.info(f"Using simulated profile heuristics for Instagram user {username}")
    return get_simulated_instagram_profile_data(username)

def get_simulated_instagram_profile_data(username: str) -> Dict[str, Any]:
    """
    Simulate fetching Instagram profile data for demonstration/fallback purposes.
    """
    # Seed random generator with username for consistency
    seed = int(hash(username) % 10000000)
    random.seed(seed)
    
    # Similar to Twitter but with Instagram-specific fields
    # Generate creation date (between 2010 and now)
    oldest_date = datetime(2010, 10, 6)  # Instagram launch date
    days_since_launch = (datetime.now() - oldest_date).days
    account_age_days = random.randint(1, days_since_launch)
    creation_date = datetime.now() - timedelta(days=account_age_days)
    
    # Determine if account is suspicious
    is_suspicious = random.random() < 0.3  # 30% chance account is suspicious
    
    # Generate follower and following counts
    if is_suspicious:
        followers_count = random.randint(1, 500)
        following_count = random.randint(1000, 7500)
    else:
        followers_base = random.randint(100, 2000)
        following_base = random.randint(100, 1000)
        followers_count = followers_base
        following_count = following_base
    
    # Generate post count
    if is_suspicious:
        if random.random() < 0.5:
            post_count = random.randint(0, 3)
        else:
            post_count = random.randint(100, 500)
    else:
        post_count = random.randint(10, 100)
    
    # Generate posts
    posts = []
    for i in range(min(20, post_count)):
        post_date = creation_date + timedelta(days=random.randint(1, account_age_days))
        
        # Generate engagement metrics
        if is_suspicious:
            likes = random.randint(0, 20)
            comments = random.randint(0, 5)
        else:
            likes = random.randint(10, 200)
            comments = random.randint(0, 50)
        
        # Generate caption
        if is_suspicious:
            # Suspicious accounts often use lots of hashtags
            caption_base = random.choice([
                "Check my bio for exclusive content!",
                "Follow for daily updates!",
                "DM me for collaboration!",
                "Like and follow for more!",
                "Best deals online!",
                "Join now, limited spots!",
                "Click the link in my bio!",
                "Tap the link to learn more!",
                "Free giveaway soon!",
                "Exclusive offer for followers!"
            ])
            hashtags = " ".join([
                "#follow", "#like", "#followback", "#followme", "#likeforlike", 
                "#followforfollow", "#instagood", "#instadaily", "#viral", "#trending"
            ])
            caption = f"{caption_base} {hashtags}"
        else:
            # Regular accounts have more natural captions
            caption_bases = [
                f"Enjoying my {random.choice(['day', 'time', 'vacation', 'weekend'])}!",
                f"Love this {random.choice(['place', 'moment', 'view', 'sunset'])}!",
                f"With my {random.choice(['friends', 'family', 'bestie', 'love'])}!",
                f"New {random.choice(['haircut', 'outfit', 'shoes', 'accessories'])}!",
                f"Just {random.choice(['cooked', 'baked', 'made', 'tried'])} this!",
                f"Happy {random.choice(['birthday', 'anniversary', 'holidays', 'vacation'])}!",
                f"My new {random.choice(['project', 'hobby', 'passion', 'adventure'])}!",
                f"Throwback to {random.choice(['last summer', 'this trip', 'that day', 'my favorite place'])}!",
                f"Can't get enough of {random.choice(['this place', 'these views', 'this food', 'this feeling'])}!",
                f"Finally {random.choice(['visited', 'tried', 'experienced', 'accomplished'])} this!"
            ]
            caption = random.choice(caption_bases)
            
            # Add some hashtags, but fewer than suspicious accounts
            if random.random() < 0.7:
                normal_hashtags = [
                    "#love", "#life", "#happy", "#travel", "#food", "#photography",
                    "#nature", "#friends", "#family", "#fitness", "#art", "#style",
                    "#beauty", "#summer", "#fun", "#music", "#fashion", "#vacation"
                ]
                selected_hashtags = random.sample(normal_hashtags, random.randint(1, 5))
                caption += " " + " ".join(selected_hashtags)
        
        posts.append({
            'caption': caption,
            'timestamp': post_date.isoformat(),
            'likes': likes,
            'comments': comments,
            'image_url': f"https://instagram.com/p/{random.choice('abcdefghijklmnopqrstuvwxyz0123456789')}{random.choice('abcdefghijklmnopqrstuvwxyz0123456789')}{random.choice('abcdefghijklmnopqrstuvwxyz0123456789')}{random.choice('abcdefghijklmnopqrstuvwxyz0123456789')}{random.choice('abcdefghijklmnopqrstuvwxyz0123456789')}{random.choice('abcdefghijklmnopqrstuvwxyz0123456789')}"
        })
    
    # Generate profile picture URL
    if is_suspicious and random.random() < 0.7:
        profile_pic_types = [
            "default_instagram_profile.jpg",
            "stock_model_photo.jpg",
            "ai_generated_portrait.png",
            "blank_instagram_avatar.png"
        ]
        profile_pic_url = f"https://example.com/images/{random.choice(profile_pic_types)}"
    else:
        profile_pic_url = f"https://instagram.com/p/{username}_{random.randint(100, 999)}.jpg"
    
    # Generate bio
    if is_suspicious:
        suspicious_bios = [
            "👑 DM for collab 👑",
            "💰 Make money online 💰",
            "Follow for a follow back!",
            "Check link in bio 🔗",
            "✨ Exclusive content creator ✨",
            "📧 Business inquiries: email@example.com",
            "",  # Empty bio
            "💼 Entrepreneur | 💰 Investor | 🌟 Influencer",
            "🔥 Hot content 🔥 Link in bio 🔥",
            "Verified partner | Official account"
        ]
        bio = random.choice(suspicious_bios)
    else:
        normal_bios = [
            f"{random.choice(['📸', '✏️', '🎨', '🎓', '👩‍💻', '👨‍💻'])} {random.choice(['Photographer', 'Writer', 'Artist', 'Student', 'Developer', 'Designer'])}",
            f"{random.choice(['📍', '🏠', '🌍'])} {random.choice(['NYC', 'London', 'Tokyo', 'LA', 'Paris', 'Berlin', 'Sydney'])}",
            f"{random.choice(['❤️', '💖', '💙'])} {random.choice(['Mom', 'Dad', 'Dog mom', 'Cat dad'])} | {random.choice(['📚', '🏃', '🎮', '🍳', '📷'])} {random.choice(['Reader', 'Runner', 'Gamer', 'Chef', 'Photographer'])}",
            f"{random.choice(['✨', '💼', '📊'])} {random.choice(['Creative', 'Marketing', 'Business'])} @ {random.choice(['Agency', 'Brand', 'Company', 'Self'])}",
            f"{random.choice(['✌️', '🌿', '🌟'])} {random.choice(['Living my best life', 'Plant based', 'Chasing dreams'])}",
            f"{random.choice(['🎓', '📚', '🔬'])} {random.choice(['Grad from', 'Studying at', 'Researching at'])} {random.choice(['University', 'College', 'Institute'])}",
            f"{random.choice(['👻', '📱', '📺'])} {random.choice(['Snapchat', 'TikTok', 'YouTube'])}: {username}",
            f"{random.choice(['🏋️', '🧘', '🚴'])} {random.choice(['Fitness lover', 'Yoga enthusiast', 'Cycling addict'])}",
            f"{random.choice(['🍕', '🍷', '☕'])} {random.choice(['Food lover', 'Wine enthusiast', 'Coffee addict'])}",
            f"{random.choice(['✈️', '🌎', '🧳'])} {random.choice(['Traveler', 'Explorer', 'Adventure seeker'])} | {random.randint(5, 30)} countries"
        ]
        bio = random.choice(normal_bios)
    
    # Return simulated profile data
    return {
        'username': username,
        'full_name': username.title() + (random.choice([' Smith', ' Jones', ' Lee', ' Garcia', ' Kim']) if random.random() < 0.5 else ''),
        'url': f"https://instagram.com/{username}",
        'bio': bio,
        'external_url': f"https://linkin.bio/{username}" if (is_suspicious and random.random() < 0.8) else '',
        'creation_date': creation_date.strftime("%Y-%m-%d"),
        'account_age_days': account_age_days,
        'followers_count': followers_count,
        'following_count': following_count,
        'post_count': post_count,
        'profile_pic_url': profile_pic_url,
        'is_verified': not is_suspicious and random.random() < 0.1,
        'posts': posts,
        'is_private': not is_suspicious and random.random() < 0.3,
        'has_highlights': not is_suspicious and random.random() < 0.7,
        'is_business_account': is_suspicious and random.random() < 0.6,
        'data_source': 'simulated'
    }

def get_facebook_profile_data(username: str) -> Dict[str, Any]:
    """
    Simulate fetching Facebook profile data.
    
    In a real implementation, this would use the Facebook API.
    """
    # Seed random generator with username for consistency
    seed = int(hash(username) % 10000000)
    random.seed(seed)
    
    # Similar to above but with Facebook-specific fields
    # Generate creation date (between 2004 and now)
    oldest_date = datetime(2004, 2, 4)  # Facebook launch date
    days_since_launch = (datetime.now() - oldest_date).days
    account_age_days = random.randint(1, days_since_launch)
    creation_date = datetime.now() - timedelta(days=account_age_days)
    
    # Determine if account is suspicious
    is_suspicious = random.random() < 0.3  # 30% chance account is suspicious
    
    # Generate friend count
    if is_suspicious:
        if random.random() < 0.5:
            friend_count = random.randint(1, 20)
        else:
            friend_count = random.randint(4500, 5000)  # Near friend limit
    else:
        friend_count = random.randint(50, 1000)
    
    # Generate page likes count
    if is_suspicious:
        page_likes_count = random.randint(500, 3000)
    else:
        page_likes_count = random.randint(10, 500)
    
    # Generate post count
    if is_suspicious:
        if random.random() < 0.5:
            post_count = random.randint(0, 5)
        else:
            post_count = random.randint(200, 1000)
    else:
        post_count = random.randint(10, 200)
    
    # Generate posts
    posts = []
    for i in range(min(20, post_count)):
        post_date = creation_date + timedelta(days=random.randint(1, account_age_days))
        
        # Generate engagement metrics
        if is_suspicious:
            likes = random.randint(0, 5)
            comments = random.randint(0, 2)
            shares = random.randint(0, 1)
        else:
            likes = random.randint(5, 100)
            comments = random.randint(0, 30)
            shares = random.randint(0, 10)
        
        # Generate post content
        if is_suspicious:
            suspicious_content = [
                "Check out this amazing offer! Click the link below!",
                "I can't believe how much money I made using this system!",
                "Want to work from home and earn $1000/day? Message me!",
                "FREE iPhone giveaway! Like, share, and comment to enter!",
                "I made $5000 in one week using this simple trick!",
                "This weight loss pill changed my life! Ask me how!",
                "Join my business and become financially independent!",
                "BREAKING NEWS: [Clickbait headline]! Click to read more!",
                "I'm giving away cash to random commenters! Comment now!",
                "This secret investment opportunity won't last long!"
            ]
            content = random.choice(suspicious_content)
        else:
            normal_content = [
                f"Had a great {random.choice(['day', 'time', 'weekend', 'vacation'])} with {random.choice(['friends', 'family', 'loved ones', 'colleagues'])}!",
                f"Happy {random.choice(['birthday', 'anniversary', 'graduation', 'promotion'])} to {random.choice(['me', 'my friend', 'my partner', 'my child', 'my parent'])}!",
                f"Just {random.choice(['watched', 'read', 'finished', 'started'])} this amazing {random.choice(['movie', 'book', 'show', 'game'])}!",
                f"Feeling {random.choice(['happy', 'blessed', 'grateful', 'excited', 'proud'])} today!",
                f"New {random.choice(['job', 'home', 'car', 'pet', 'hobby'])} announcement!",
                f"Throwback to {random.choice(['last summer', 'our trip', 'the good old days', 'that amazing event'])}!",
                f"Just {random.choice(['cooked', 'baked', 'made', 'created'])} this {random.choice(['meal', 'dessert', 'project', 'artwork'])}!",
                f"Looking forward to {random.choice(['the weekend', 'vacation', 'this event', 'the holidays'])}!",
                f"Anyone else {random.choice(['watching this show', 'reading this book', 'playing this game', 'following this news'])}?",
                f"Beautiful {random.choice(['sunset', 'view', 'day', 'moment'])} at {random.choice(['the beach', 'the park', 'home', 'this place'])}!"
            ]
            content = random.choice(normal_content)
        
        posts.append({
            'text': content,
            'timestamp': post_date.isoformat(),
            'likes': likes,
            'comments': comments,
            'shares': shares
        })
    
    # Generate profile picture URL
    if is_suspicious and random.random() < 0.7:
        profile_pic_types = [
            "default_facebook_silhouette.jpg",
            "stock_person_image.jpg",
            "generic_profile_picture.png",
            "blank_profile.png"
        ]
        profile_pic_url = f"https://example.com/images/{random.choice(profile_pic_types)}"
    else:
        profile_pic_url = f"https://graph.facebook.com/{random.randint(1000000, 9999999)}/picture?type=large"
    
    # Return simulated profile data
    return {
        'username': username,
        'name': username.title() + (random.choice([' Smith', ' Jones', ' Lee', ' Garcia', ' Kim']) if random.random() < 0.5 else ''),
        'url': f"https://facebook.com/{username}",
        'creation_date': creation_date.strftime("%Y-%m-%d"),
        'friend_count': friend_count,
        'page_likes_count': page_likes_count,
        'post_count': post_count,
        'profile_pic_url': profile_pic_url,
        'is_verified': not is_suspicious and random.random() < 0.1,
        'posts': posts,
        'is_private': not is_suspicious and random.random() < 0.6,
        'has_profile_details': not is_suspicious and random.random() < 0.8,
        'location': random.choice(['New York', 'London', 'Tokyo', 'San Francisco', 'Paris', '', 'Remote', 'Earth']) if (not is_suspicious or random.random() < 0.3) else '',
        'work': random.choice(['Software Engineer at Tech Co', 'Teacher at School', 'Owner at Business', 'Student at University', 'Self-employed', '']) if (not is_suspicious or random.random() < 0.3) else '',
        'education': random.choice(['University of X', 'College Y', 'High School Z', '']) if (not is_suspicious or random.random() < 0.3) else '',
        'relationship_status': random.choice(['Single', 'In a relationship', 'Married', 'It\'s complicated', '']) if (not is_suspicious or random.random() < 0.3) else ''
    }