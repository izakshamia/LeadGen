"""
Redditor extraction service for identifying potential customers from Reddit posts.
Extracts Redditor usernames from posts and comments, consolidates duplicates,
and saves to database.
"""

import logging
from datetime import datetime
from typing import List, Dict, Set
from collections import defaultdict

from api.models.reddit_post import RedditPost, RedditComment, RedditorCandidate
from api.services.supabase_client import init_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_redditors_from_posts(posts: List[RedditPost]) -> List[RedditorCandidate]:
    """
    Extract Redditor usernames from posts and their comment trees.
    
    Traverses post authors and all comment authors (including nested replies)
    to create RedditorCandidate objects with source tracking.
    
    Args:
        posts: List of RedditPost objects to extract from
        
    Returns:
        List of RedditorCandidate objects (may contain duplicates)
    """
    candidates = []
    extraction_time = datetime.utcnow()
    
    logger.info(f"Starting extraction from {len(posts)} posts")
    
    for post in posts:
        # Extract post author from title metadata
        # The author is typically in the post URL or we need to parse it
        # For now, we'll skip post authors since RedditPost doesn't have an author field
        # and focus on comment authors which we have access to
        
        # Extract all comment authors recursively
        def extract_from_comments(comments: List[RedditComment], source_url: str):
            """Recursively extract authors from comment tree"""
            comment_candidates = []
            
            for comment in comments:
                # Skip deleted or removed authors
                if comment.author and comment.author not in ['[deleted]', '[removed]', 'AutoModerator']:
                    candidate = RedditorCandidate(
                        username=comment.author,
                        source_post_url=source_url,
                        extraction_timestamp=extraction_time,
                        is_post_author=False
                    )
                    comment_candidates.append(candidate)
                
                # Recursively process replies
                if comment.replies:
                    comment_candidates.extend(
                        extract_from_comments(comment.replies, source_url)
                    )
            
            return comment_candidates
        
        # Extract from this post's comments
        if post.comments:
            post_candidates = extract_from_comments(post.comments, post.url)
            candidates.extend(post_candidates)
    
    logger.info(f"Extracted {len(candidates)} candidate Redditors (including duplicates)")
    return candidates


def consolidate_duplicates(candidates: List[RedditorCandidate]) -> List[Dict]:
    """
    Consolidate duplicate Redditors by username.
    
    Groups candidates by username, merges source_posts arrays,
    and keeps the earliest extraction timestamp.
    
    Args:
        candidates: List of RedditorCandidate objects (may contain duplicates)
        
    Returns:
        List of consolidated Redditor dictionaries ready for database insertion
    """
    # Group by username
    username_map = defaultdict(lambda: {
        'source_posts': set(),
        'earliest_timestamp': None,
        'is_post_author': False
    })
    
    for candidate in candidates:
        username = candidate.username
        entry = username_map[username]
        
        # Add source post URL
        entry['source_posts'].add(candidate.source_post_url)
        
        # Track earliest timestamp
        if entry['earliest_timestamp'] is None or candidate.extraction_timestamp < entry['earliest_timestamp']:
            entry['earliest_timestamp'] = candidate.extraction_timestamp
        
        # Track if ever a post author
        if candidate.is_post_author:
            entry['is_post_author'] = True
    
    # Convert to list of dictionaries for database insertion
    consolidated = []
    for username, data in username_map.items():
        redditor = {
            'username': username,
            'source_posts': list(data['source_posts']),
            'first_seen': data['earliest_timestamp'],
            'last_updated': datetime.utcnow(),
            'is_active': True
        }
        consolidated.append(redditor)
    
    logger.info(f"Consolidated {len(candidates)} candidates into {len(consolidated)} unique Redditors")
    return consolidated


def save_redditors_to_db(redditors: List[Dict]) -> int:
    """
    Save consolidated Redditors to database using upsert logic.
    
    Follows the insert_suggestion() pattern from supabase_client.py.
    Updates existing records if username already exists.
    
    Args:
        redditors: List of Redditor dictionaries to save
        
    Returns:
        Count of successfully saved records
    """
    if not redditors:
        logger.info("No redditors to save")
        return 0
    
    try:
        client = init_supabase_client()
        saved_count = 0
        
        for redditor in redditors:
            try:
                # Check if redditor already exists
                existing = check_redditor_exists(redditor['username'])
                
                if existing:
                    # Update existing record - merge source_posts
                    existing_sources = set(existing.get('source_posts', []))
                    new_sources = set(redditor['source_posts'])
                    merged_sources = list(existing_sources.union(new_sources))
                    
                    # Keep earliest first_seen
                    first_seen = existing.get('first_seen')
                    if first_seen and redditor['first_seen']:
                        # Compare timestamps
                        existing_dt = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
                        if redditor['first_seen'] < existing_dt:
                            first_seen = redditor['first_seen'].isoformat()
                    
                    update_data = {
                        'source_posts': merged_sources,
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    
                    response = client.table('target_redditors') \
                        .update(update_data) \
                        .eq('username', redditor['username']) \
                        .execute()
                    
                    if response.data:
                        saved_count += 1
                        logger.debug(f"Updated existing Redditor: {redditor['username']}")
                else:
                    # Insert new record with default scores
                    insert_data = {
                        'username': redditor['username'],
                        'source_posts': redditor['source_posts'],
                        'first_seen': redditor['first_seen'].isoformat(),
                        'last_updated': redditor['last_updated'].isoformat(),
                        'is_active': True,
                        'is_authentic': True,
                        'authenticity_score': 50,  # Default, will be calculated later
                        'need_score': 0,  # Default, will be calculated later
                        'priority': 'low',  # Default
                        'account_age_days': 0,  # Will be fetched later
                        'total_karma': 0,  # Will be fetched later
                        'comment_karma': 0,
                        'post_karma': 0
                    }
                    
                    response = client.table('target_redditors') \
                        .insert(insert_data) \
                        .execute()
                    
                    if response.data:
                        saved_count += 1
                        logger.debug(f"Inserted new Redditor: {redditor['username']}")
                        
            except Exception as e:
                logger.error(f"Error saving Redditor {redditor['username']}: {e}")
                continue
        
        logger.info(f"Successfully saved {saved_count} of {len(redditors)} Redditors to database")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error in save_redditors_to_db: {e}")
        return 0


def check_redditor_exists(username: str) -> Dict:
    """
    Check if a Redditor already exists in the database.
    
    Args:
        username: Reddit username to check
        
    Returns:
        Existing Redditor record if found, None otherwise
    """
    try:
        client = init_supabase_client()
        
        response = client.table('target_redditors') \
            .select('*') \
            .eq('username', username) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking if Redditor exists ({username}): {e}")
        return None


def insert_redditor(redditor_data: Dict) -> Dict:
    """
    Insert a new Redditor into the database.
    
    Args:
        redditor_data: Dictionary containing Redditor fields
        
    Returns:
        Inserted record if successful, None otherwise
    """
    try:
        client = init_supabase_client()
        
        response = client.table('target_redditors') \
            .insert(redditor_data) \
            .execute()
        
        if response.data and len(response.data) > 0:
            logger.info(f"Successfully inserted Redditor: {redditor_data.get('username')}")
            return response.data[0]
        
        return None
        
    except Exception as e:
        logger.error(f"Error inserting Redditor: {e}")
        return None


def update_redditor_scores(username: str, authenticity_score: int, need_score: int, priority: str) -> bool:
    """
    Update authenticity and need scores for a Redditor.
    
    Args:
        username: Reddit username
        authenticity_score: Calculated authenticity score (0-100)
        need_score: Calculated need score (0-100)
        priority: Priority classification ('high', 'medium', 'low')
        
    Returns:
        True if update successful, False otherwise
    """
    try:
        client = init_supabase_client()
        
        update_data = {
            'authenticity_score': authenticity_score,
            'need_score': need_score,
            'priority': priority,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        response = client.table('target_redditors') \
            .update(update_data) \
            .eq('username', username) \
            .execute()
        
        if response.data:
            logger.info(f"Updated scores for Redditor: {username}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error updating Redditor scores ({username}): {e}")
        return False
