"""
Supabase client module for Reddit Ovarra API service.
Handles all database operations for reddit_suggestions table.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supabase client will be initialized lazily
_supabase_client = None


def init_supabase_client():
    """
    Initialize and return Supabase client using environment variables.
    
    Reads SUPABASE_URL and SUPABASE_KEY from environment and creates
    a Supabase client instance. Raises ValueError if required environment
    variables are missing.
    
    Returns:
        Client: Initialized Supabase client
        
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY environment variables are not set
        ImportError: If supabase package is not installed
    """
    global _supabase_client
    
    # Return cached client if already initialized
    if _supabase_client is not None:
        return _supabase_client
    
    try:
        from supabase import create_client, Client
    except ImportError:
        logger.error("supabase package not installed. Run: pip install supabase")
        raise ImportError("supabase package is required. Install with: pip install supabase")
    
    # Get environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    # Validate environment variables
    if not supabase_url:
        error_msg = "SUPABASE_URL environment variable is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not supabase_key:
        error_msg = "SUPABASE_KEY environment variable is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Handle incomplete URL format (just project ID)
    if not supabase_url.startswith('http'):
        supabase_url = f"https://{supabase_url}.supabase.co"
        logger.info(f"Formatted Supabase URL: {supabase_url}")
    
    try:
        _supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise


def check_duplicate(reddit_url: str) -> bool:
    """
    Check if a reddit_url already exists in the database.
    
    Queries the reddit_suggestions table to determine if a post with
    the given URL has already been processed and stored.
    
    Args:
        reddit_url: The Reddit post URL to check
        
    Returns:
        bool: True if the URL exists in database, False otherwise
    """
    try:
        client = init_supabase_client()
        
        # Query for existing reddit_url
        response = client.table('reddit_suggestions') \
            .select('id') \
            .eq('reddit_url', reddit_url) \
            .execute()
        
        exists = len(response.data) > 0
        
        if exists:
            logger.info(f"Duplicate found: {reddit_url}")
        
        return exists
        
    except Exception as e:
        logger.error(f"Error checking duplicate for {reddit_url}: {e}")
        # Return False to allow processing to continue on error
        return False


def insert_suggestion(
    reddit_name: str,
    reddit_url: str,
    suggested_response: str
) -> Optional[Dict[str, Any]]:
    """
    Insert a new suggestion into the database.
    
    Creates a new row in reddit_suggestions table with the provided data.
    Handles unique constraint violations gracefully by logging and returning None.
    
    Args:
        reddit_name: The title of the Reddit post
        reddit_url: The URL of the Reddit post (must be unique)
        suggested_response: The generated Ovarra reply text
        
    Returns:
        dict: The inserted row data if successful, None on failure
    """
    try:
        client = init_supabase_client()
        
        # Prepare data for insertion
        data = {
            'reddit_name': reddit_name,
            'reddit_url': reddit_url,
            'suggested_response': suggested_response,
            'status': 'new'  # Default status
        }
        
        # Insert into database
        response = client.table('reddit_suggestions') \
            .insert(data) \
            .execute()
        
        if response.data and len(response.data) > 0:
            inserted_row = response.data[0]
            logger.info(f"Successfully inserted suggestion: {reddit_url}")
            return inserted_row
        else:
            logger.warning(f"Insert returned no data for: {reddit_url}")
            return None
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Handle unique constraint violation
        if 'unique' in error_msg or 'duplicate' in error_msg:
            logger.warning(f"Duplicate URL constraint violation: {reddit_url}")
        else:
            logger.error(f"Error inserting suggestion for {reddit_url}: {e}")
        
        return None


def get_recent_suggestions(hours: int = 24) -> List[Dict[str, Any]]:
    """
    Retrieve suggestions created within the last N hours.
    
    Filters reddit_suggestions by created_at timestamp and returns
    results ordered by creation time (newest first).
    
    Args:
        hours: Number of hours to look back (default: 24)
        
    Returns:
        list: List of suggestion dictionaries, empty list on error
    """
    try:
        client = init_supabase_client()
        
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cutoff_iso = cutoff_time.isoformat()
        
        logger.info(f"Fetching suggestions from last {hours} hours (since {cutoff_iso})")
        
        # Query with time filter and ordering
        response = client.table('reddit_suggestions') \
            .select('*') \
            .gte('created_at', cutoff_iso) \
            .order('created_at', desc=True) \
            .execute()
        
        suggestions = response.data if response.data else []
        logger.info(f"Retrieved {len(suggestions)} recent suggestions")
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error retrieving recent suggestions: {e}")
        return []


def test_connection() -> bool:
    """
    Test database connectivity for health checks.
    
    Attempts a simple query to verify that the database connection
    is working properly.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        client = init_supabase_client()
        
        # Perform a simple query to test connection
        response = client.table('reddit_suggestions') \
            .select('id') \
            .limit(1) \
            .execute()
        
        # If we get here without exception, connection is good
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
