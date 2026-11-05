import logging
from typing import Dict, List, Any, Set, Tuple
import random  # For demonstration purposes only

# Configure logging
logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """
    Analyzes social network relationships to detect patterns
    associated with fake accounts.
    
    This includes:
    - Follower/following ratio analysis
    - Network structure and clustering
    - Interaction patterns
    - Relationship authenticity
    """
    
    def __init__(self):
        """Initialize the NetworkAnalyzer with necessary resources."""
        logger.info("Initializing NetworkAnalyzer")
        logger.info("NetworkAnalyzer initialized successfully")
    
    def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the social network relationships of a profile.
        
        Args:
            profile_data: Dictionary containing profile information including
                          followers, following, and interactions
            
        Returns:
            Dictionary with network analysis results
        """
        logger.info(f"Analyzing network for profile: {profile_data.get('username', 'Unknown')}")
        
        # Extract network data
        followers_count = profile_data.get('followers_count', 0)
        following_count = profile_data.get('following_count', 0)
        
        # Get follower and following lists if available
        followers = profile_data.get('followers', [])
        following = profile_data.get('following', [])
        
        # Get interactions if available
        interactions = profile_data.get('interactions', [])
        
        # Calculate follower to following ratio
        followers_to_following_ratio = self._calculate_ratio(followers_count, following_count)
        
        # Calculate network isolation score
        if followers or following or interactions:
            network_isolation_score = self._calculate_network_isolation(
                followers, following, interactions, followers_count, following_count
            )
        else:
            # If we don't have detailed network data, estimate based on counts
            network_isolation_score = self._estimate_isolation_from_counts(
                followers_count, following_count
            )
        
        # Analyze mutual connections if data is available
        if followers and following:
            mutual_connection_ratio = self._analyze_mutual_connections(followers, following)
            clustering_coefficient = self._estimate_clustering(followers, following, interactions)
        else:
            mutual_connection_ratio = 0.5  # Neutral value
            clustering_coefficient = 0.5   # Neutral value
        
        # Calculate reciprocity (how many people the user follows also follow back)
        if followers and following:
            reciprocity = self._calculate_reciprocity(followers, following)
        else:
            reciprocity = 0.5  # Neutral value
        
        # Calculate overall network score
        network_score = self._calculate_network_score(
            followers_to_following_ratio,
            network_isolation_score,
            mutual_connection_ratio,
            clustering_coefficient,
            reciprocity,
            followers_count,
            following_count
        )
        
        logger.info(f"Network analysis complete for {profile_data.get('username', 'Unknown')}")
        
        return {
            'network_analysis_performed': True,
            'followers_count': followers_count,
            'following_count': following_count,
            'followers_to_following_ratio': followers_to_following_ratio,
            'network_isolation_score': network_isolation_score,
            'mutual_connection_ratio': mutual_connection_ratio,
            'clustering_coefficient': clustering_coefficient,
            'reciprocity': reciprocity,
            'network_score': network_score
        }
    
    def _calculate_ratio(self, followers: int, following: int) -> float:
        """
        Calculate the ratio of followers to following.
        
        Args:
            followers: Number of followers
            following: Number of accounts being followed
            
        Returns:
            Followers to following ratio
        """
        if following == 0:
            if followers == 0:
                return 1.0  # Equal when both are zero
            else:
                return 100.0  # Very high ratio when following no one but having followers
        
        return followers / following
    
    def _calculate_network_isolation(self, followers: List[Any], following: List[Any],
                                 interactions: List[Any], followers_count: int,
                                 following_count: int) -> float:
        """
        Calculate how isolated a profile is in the social network.
        
        High isolation is suspicious and could indicate fake accounts.
        
        Returns a score from 0.0 (well-connected) to 1.0 (highly isolated).
        """
        # In a real implementation, this would analyze the full network graph
        # For demonstration, we'll use simplified metrics
        
        # If we have the actual lists of followers/following
        if isinstance(followers, list) and isinstance(following, list):
            # Extract usernames or IDs from the lists
            follower_ids = set(self._extract_user_ids(followers))
            following_ids = set(self._extract_user_ids(following))
            
            # Get interaction user IDs
            interaction_ids = set(self._extract_user_ids(interactions))
            
            # Calculate the intersection of followers and interactions
            followers_interacted = len(follower_ids.intersection(interaction_ids))
            
            # Calculate ratio of followers interacted with
            if len(follower_ids) > 0:
                follower_interaction_ratio = followers_interacted / len(follower_ids)
            else:
                follower_interaction_ratio = 0
                
            # Mutual connections
            mutual = len(follower_ids.intersection(following_ids))
            if len(following_ids) > 0:
                mutual_ratio = mutual / len(following_ids)
            else:
                mutual_ratio = 0
                
            # Calculate isolation score
            # More mutual connections and interactions = less isolation
            isolation_score = 1.0 - (0.7 * mutual_ratio + 0.3 * follower_interaction_ratio)
            
            return isolation_score
            
        else:
            # Fall back to estimation based on counts
            return self._estimate_isolation_from_counts(followers_count, following_count)
    
    def _estimate_isolation_from_counts(self, followers_count: int, following_count: int) -> float:
        """
        Estimate network isolation based only on follower/following counts.
        
        Returns:
            Estimated isolation score (0.0 to 1.0)
        """
        # Very few followers is suspicious
        if followers_count < 10:
            follower_factor = 0.8
        elif followers_count < 50:
            follower_factor = 0.5
        elif followers_count < 100:
            follower_factor = 0.3
        else:
            follower_factor = 0.1
            
        # Very high following count with low followers is suspicious
        if following_count > 1000 and followers_count < 100:
            following_factor = 0.7
        elif following_count > 500 and followers_count < 50:
            following_factor = 0.6
        else:
            following_factor = 0.2
            
        # Combine factors
        isolation_score = 0.5 * follower_factor + 0.5 * following_factor
        
        return isolation_score
    
    def _analyze_mutual_connections(self, followers: List[Any], following: List[Any]) -> float:
        """
        Analyze mutual connections between followers and following.
        
        Low mutual connections can indicate isolation or fake networks.
        
        Returns:
            Mutual connection ratio (0.0 to 1.0)
        """
        # Extract user IDs
        follower_ids = set(self._extract_user_ids(followers))
        following_ids = set(self._extract_user_ids(following))
        
        if not following_ids:
            return 0.5  # Neutral value
            
        # Calculate intersection
        mutual = len(follower_ids.intersection(following_ids))
        
        # Calculate ratio
        return mutual / len(following_ids)
    
    def _estimate_clustering(self, followers: List[Any], following: List[Any],
                         interactions: List[Any]) -> float:
        """
        Estimate the clustering coefficient of the user's network.
        
        Low clustering can indicate fake accounts or isolated networks.
        
        Returns:
            Estimated clustering coefficient (0.0 to 1.0)
        """
        # In a real implementation, this would calculate actual clustering
        # based on network graph analysis
        
        # For demonstration, we'll simulate this
        # Extract user IDs
        follower_ids = set(self._extract_user_ids(followers))
        following_ids = set(self._extract_user_ids(following))
        interaction_ids = set(self._extract_user_ids(interactions))
        
        # Calculate overlap between different sets
        follower_following_overlap = len(follower_ids.intersection(following_ids))
        follower_interaction_overlap = len(follower_ids.intersection(interaction_ids))
        following_interaction_overlap = len(following_ids.intersection(interaction_ids))
        
        # Sum all overlaps
        total_overlap = follower_following_overlap + follower_interaction_overlap + following_interaction_overlap
        
        # Sum all set sizes
        total_size = len(follower_ids) + len(following_ids) + len(interaction_ids)
        
        if total_size == 0:
            return 0.5  # Neutral value
            
        # Normalize to 0-1 range
        raw_clustering = total_overlap / total_size
        
        # Adjust to reasonable range (0.05 to 0.8 is typical)
        adjusted_clustering = 0.05 + raw_clustering * 0.75
        
        return adjusted_clustering
    
    def _calculate_reciprocity(self, followers: List[Any], following: List[Any]) -> float:
        """
        Calculate how many people the user follows also follow back.
        
        Low reciprocity can indicate fake engagement or spam following.
        
        Returns:
            Reciprocity score (0.0 to 1.0)
        """
        # Extract user IDs
        follower_ids = set(self._extract_user_ids(followers))
        following_ids = set(self._extract_user_ids(following))
        
        if not following_ids:
            return 0.5  # Neutral value
            
        # Calculate intersection (mutual follows)
        mutual = len(follower_ids.intersection(following_ids))
        
        # Calculate reciprocity
        return mutual / len(following_ids)
    
    def _extract_user_ids(self, users_list: List[Any]) -> List[str]:
        """
        Extract user IDs or usernames from a list of user objects.
        
        Handles different formats of user data.
        """
        result = []
        
        for user in users_list:
            if isinstance(user, dict):
                # Try different possible keys
                user_id = user.get('id') or user.get('user_id') or user.get('username')
                if user_id:
                    result.append(str(user_id))
            elif isinstance(user, str):
                # Already a string ID or username
                result.append(user)
        
        return result
    
    def _calculate_network_score(self, followers_ratio: float, isolation_score: float,
                             mutual_ratio: float, clustering: float, reciprocity: float,
                             followers_count: int, following_count: int) -> float:
        """
        Calculate overall network suspiciousness score.
        
        Returns a score from 0.0 (not suspicious) to 1.0 (highly suspicious).
        """
        # Start with base suspicion level
        suspicion = 0.0
        
        # Very low followers is suspicious
        if followers_count < 10:
            suspicion += 0.3
        elif followers_count < 50:
            suspicion += 0.2
        
        # Very high following to follower ratio is suspicious
        if following_count > 0:
            following_to_follower = followers_count / following_count
            if following_to_follower < 0.1:  # Following 10x more than followers
                suspicion += 0.25
            elif following_to_follower < 0.3:  # Following 3x more than followers
                suspicion += 0.15
        
        # High isolation is suspicious
        suspicion += isolation_score * 0.2
        
        # Low mutual connection ratio is suspicious
        suspicion += (1 - mutual_ratio) * 0.15
        
        # Low clustering is suspicious
        suspicion += (1 - clustering) * 0.1
        
        # Low reciprocity is suspicious
        suspicion += (1 - reciprocity) * 0.1
        
        # Cap at 1.0
        return min(1.0, suspicion)