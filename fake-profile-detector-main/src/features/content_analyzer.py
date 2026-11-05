import logging
import re
import string
from typing import Dict, List, Any, Set, Optional
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """
    Analyzes text content from social media profiles to detect patterns
    associated with fake accounts.
    
    This includes:
    - Sentiment analysis of posts
    - Content diversity measurement
    - Suspicious keyword detection
    - Spam pattern identification
    """
    
    def __init__(self):
        """Initialize the ContentAnalyzer with necessary resources."""
        logger.info("Initializing ContentAnalyzer")
        
        # Load suspicious keywords
        self.suspicious_keywords = self._load_suspicious_keywords()
        
        # Common spam patterns as regex
        self.spam_patterns = [
            r'(earn|make)(\s+)?\$\d+(\s+)?(per|a)(\s+)?(day|week|month|hour)',
            r'free\s+money',
            r'work\s+from\s+home',
            r'(click|tap)\s+here',
            r'(check|see)(\s+)?(my|this)(\s+)?profile',
            r'follow(\s+)?(me|back)',
            r'(dm|message)(\s+)?me',
            r'dating',
            r'hot\s+(singles|girls|guys)',
            r'(bitcoin|crypto)(\s+)?(investment|trading)',
            r'get\s+rich',
            r'lose\s+weight',
            r'diet\s+pill',
            r'miracle\s+cure',
            r'[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+',  # Email pattern
            r'https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/\S*)?'     # URL pattern
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.spam_patterns]
        
        logger.info("ContentAnalyzer initialized successfully")
    
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the content from a profile to determine possible fake indicators.
        
        Args:
            profile_data: Dictionary containing profile information including posts
            
        Returns:
            Dictionary with content analysis results
        """
        logger.info(f"Analyzing content for profile: {profile_data.get('username', 'Unknown')}")
        
        # Get posts from profile data
        posts = profile_data.get('posts', [])
        if not posts:
            logger.warning("No posts found for content analysis")
            return {
                'content_analysis_performed': False,
                'sentiment_score': 0.5,  # Neutral
                'content_diversity': 1.0,  # Maximum diversity (no repetition)
                'suspicious_content_score': 0.0,  # No suspicious content detected
                'spam_pattern_matches': 0
            }
        
        # Extract text content from posts
        post_texts = []
        for post in posts:
            if isinstance(post, dict):
                post_texts.append(post.get('text', ''))
            elif isinstance(post, str):
                post_texts.append(post)
        
        # Remove empty posts
        post_texts = [text for text in post_texts if text.strip()]
        
        if not post_texts:
            logger.warning("No text content found in posts")
            return {
                'content_analysis_performed': False,
                'sentiment_score': 0.5,
                'content_diversity': 1.0,
                'suspicious_content_score': 0.0,
                'spam_pattern_matches': 0
            }
        
        # Perform analysis
        sentiment_score = self._analyze_sentiment(post_texts)
        content_diversity = self._calculate_content_diversity(post_texts)
        spam_pattern_matches = self._detect_spam_patterns(post_texts)
        suspicious_keywords_count = self._count_suspicious_keywords(post_texts)
        
        # Calculate overall suspicious content score
        total_words = sum(len(self._tokenize(text)) for text in post_texts)
        if total_words > 0:
            keyword_ratio = suspicious_keywords_count / total_words
        else:
            keyword_ratio = 0
            
        # Combine different metrics for overall suspiciousness score
        suspicious_content_score = self._calculate_suspicious_score(
            sentiment_score, 
            content_diversity,
            spam_pattern_matches,
            keyword_ratio,
            len(post_texts)
        )
        
        logger.info(f"Content analysis complete for {profile_data.get('username', 'Unknown')}")
        
        return {
            'content_analysis_performed': True,
            'sentiment_score': sentiment_score,
            'content_diversity': content_diversity,
            'suspicious_content_score': suspicious_content_score,
            'spam_pattern_matches': spam_pattern_matches,
            'suspicious_keywords_count': suspicious_keywords_count,
            'keyword_ratio': keyword_ratio
        }
    
    def _analyze_sentiment(self, texts: List[str]) -> float:
        """
        Analyze the sentiment of posts.
        
        Returns a score from 0.0 (negative) to 1.0 (positive)
        with 0.5 being neutral.
        
        Note: This is a simplified version. In a real implementation,
        a proper NLP library like NLTK, TextBlob, or a pre-trained model
        would be used.
        """
        try:
            # Simplified sentiment analysis
            # Check for positive and negative words
            positive_words = {
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'best',
                'love', 'happy', 'awesome', 'nice', 'fantastic', 'beautiful',
                'perfect', 'enjoy', 'thanks', 'thank', 'appreciated', 'like',
                'excited', 'glad', 'pleased', 'impressive', 'impressive', 'well'
            }
            
            negative_words = {
                'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate',
                'dislike', 'poor', 'disappointed', 'disappointing', 'sucks',
                'suck', 'sad', 'angry', 'upset', 'unfortunate', 'wrong',
                'never', 'problem', 'issue', 'fail', 'failed', 'failure'
            }
            
            positive_count = 0
            negative_count = 0
            
            for text in texts:
                words = self._tokenize(text.lower())
                positive_count += sum(1 for word in words if word in positive_words)
                negative_count += sum(1 for word in words if word in negative_words)
            
            total = positive_count + negative_count
            if total == 0:
                return 0.5  # Neutral if no sentiment words found
                
            # Scale to 0.0-1.0 range
            return 0.5 + ((positive_count - negative_count) / (2 * total))
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}", exc_info=True)
            return 0.5  # Return neutral on error
    
    def _calculate_content_diversity(self, texts: List[str]) -> float:
        """
        Calculate how diverse or repetitive the content is.
        
        Returns a score from 0.0 (completely repetitive) to 
        1.0 (completely diverse).
        """
        try:
            if not texts:
                return 1.0
                
            # Tokenize all texts
            all_tokens = []
            for text in texts:
                all_tokens.extend(self._tokenize(text.lower()))
                
            if not all_tokens:
                return 1.0
                
            # Count token frequencies
            token_counts = Counter(all_tokens)
            
            # Calculate diversity score based on token frequency distribution
            unique_tokens = len(token_counts)
            total_tokens = len(all_tokens)
            
            if total_tokens == 0:
                return 1.0
                
            # Type-token ratio (TTR) as measure of lexical diversity
            ttr = unique_tokens / total_tokens
            
            # Adjust for short texts (TTR tends to be higher for shorter texts)
            adjusted_ttr = ttr * (1 - 0.5 * (1 / (1 + len(texts))))
            
            return adjusted_ttr
            
        except Exception as e:
            logger.error(f"Error calculating content diversity: {str(e)}", exc_info=True)
            return 1.0  # Return maximum diversity on error
    
    def _detect_spam_patterns(self, texts: List[str]) -> int:
        """
        Detect common spam patterns in the texts.
        
        Returns the count of spam pattern matches found.
        """
        try:
            spam_matches = 0
            
            for text in texts:
                for pattern in self.compiled_patterns:
                    if pattern.search(text):
                        spam_matches += 1
            
            return spam_matches
            
        except Exception as e:
            logger.error(f"Error detecting spam patterns: {str(e)}", exc_info=True)
            return 0
    
    def _count_suspicious_keywords(self, texts: List[str]) -> int:
        """
        Count occurrences of suspicious keywords in the texts.
        
        Returns the total count of suspicious keywords found.
        """
        try:
            keyword_count = 0
            
            for text in texts:
                words = set(self._tokenize(text.lower()))
                keyword_count += sum(1 for word in words if word in self.suspicious_keywords)
            
            return keyword_count
            
        except Exception as e:
            logger.error(f"Error counting suspicious keywords: {str(e)}", exc_info=True)
            return 0
    
    def _calculate_suspicious_score(self, sentiment_score: float, 
                                 content_diversity: float,
                                 spam_matches: int,
                                 keyword_ratio: float,
                                 post_count: int) -> float:
        """
        Calculate overall suspicious content score based on various factors.
        
        Returns a score from 0.0 (not suspicious) to 1.0 (highly suspicious).
        """
        try:
            # Convert sentiment to suspiciousness factor
            # Very positive or very negative content can be suspicious
            sentiment_factor = 2 * abs(sentiment_score - 0.5)
            
            # Lack of content diversity is suspicious
            diversity_factor = 1 - content_diversity
            
            # Normalize spam matches relative to post count
            if post_count > 0:
                spam_factor = min(1.0, spam_matches / post_count)
            else:
                spam_factor = 0
                
            # Combine factors with different weights
            weights = {
                'sentiment': 0.1,      # Extreme sentiment is slightly suspicious
                'diversity': 0.35,     # Low diversity is moderately suspicious
                'spam': 0.35,          # Spam patterns are moderately suspicious
                'keywords': 0.2        # Suspicious keywords are somewhat suspicious
            }
            
            suspicious_score = (
                weights['sentiment'] * sentiment_factor +
                weights['diversity'] * diversity_factor +
                weights['spam'] * spam_factor +
                weights['keywords'] * min(1.0, keyword_ratio * 10)
            )
            
            return suspicious_score
            
        except Exception as e:
            logger.error(f"Error calculating suspicious content score: {str(e)}", exc_info=True)
            return 0.0
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens (words), removing punctuation and whitespace.
        """
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        
        # Split into words and filter out empty strings
        return [word for word in text.split() if word]
    
    def _load_suspicious_keywords(self) -> Set[str]:
        """
        Load suspicious keywords associated with fake accounts.
        
        In a real implementation, this would load from a file or database
        that is regularly updated.
        """
        return {
            # Money and financial terms
            'money', 'cash', 'earn', 'income', 'rich', 'wealthy', 'profit',
            'investment', 'invest', 'bitcoin', 'crypto', 'cryptocurrency',
            'forex', 'trading', 'trader', 'stocks', 'bitcoin', 'btc', 'eth',
            
            # Marketing and offers
            'offer', 'free', 'discount', 'deal', 'promo', 'promotion',
            'limited', 'exclusive', 'opportunity', 'chance', 'lifetime',
            
            # Employment
            'job', 'career', 'hiring', 'remote', 'work', 'home', 'online',
            'passive', 'income', 'salary', 'payday', 'loan', 'loans',
            
            # Adult content
            'hot', 'sexy', 'dating', 'date', 'single', 'chat', 'meet',
            'hookup', 'adult', 'cam', 'webcam', 'girl', 'girls', 'boys',
            
            # Call to actions
            'click', 'tap', 'join', 'register', 'sign', 'subscribe',
            'follow', 'dm', 'pm', 'message', 'contact', 'link', 'bio',
            
            # Health and beauty
            'weight', 'loss', 'diet', 'slim', 'fat', 'burn', 'health',
            'pill', 'supplement', 'vitamin', 'detox', 'cleanse', 'inches',
            
            # Urgency
            'urgent', 'hurry', 'quick', 'fast', 'immediately', 'now',
            'today', 'tonight', 'soon', 'limited', 'act', 'action'
        }