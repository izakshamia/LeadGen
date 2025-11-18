"""
Scraper service integration layer for Reddit Ovarra API.
Bridges existing scraper logic with Supabase database operations.
"""

import logging
from typing import List, Dict, Any
from models import RedditPost
from api_utils import (
    fetch_reddit_posts,
    classify_posts_relevance,
    fetch_and_attach_comments,
    generate_ovarra_replies
)
from supabase_client import check_duplicate, insert_suggestion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_and_save(
    subreddits: List[str],
    keywords: List[str],
    post_limit: int,
    max_age_days: int
) -> Dict[str, Any]:
    """
    Execute scraper pipeline and save results to Supabase.
    
    This function orchestrates the complete scraping workflow:
    1. Scrape posts from Reddit
    2. Classify posts for relevance
    3. Check for duplicates (skip if exists)
    4. Fetch comments for non-duplicate posts
    5. Generate Ovarra replies
    6. Insert suggestions into Supabase
    
    Args:
        subreddits: List of subreddit names to search
        keywords: List of keywords to search for
        post_limit: Maximum number of posts per keyword
        max_age_days: Only fetch posts from last N days
        
    Returns:
        dict: Summary statistics with keys:
            - processed: Number of successfully saved suggestions
            - skipped: Number of duplicate posts skipped
            - failed: Number of posts that failed to save
            - status: Overall status ('success', 'partial', or 'failure')
    """
    # Initialize counters
    processed = 0
    skipped = 0
    failed = 0
    
    logger.info(f"Starting scrape_and_save: subreddits={subreddits}, keywords={keywords}, "
                f"post_limit={post_limit}, max_age_days={max_age_days}")
    
    # Step 1: Scrape posts from Reddit
    logger.info("Step 1: Scraping posts from Reddit...")
    all_posts = []
    for subreddit in subreddits:
        for keyword in keywords:
            logger.info(f"Scraping r/{subreddit} for '{keyword}'...")
            raw_posts = fetch_reddit_posts(subreddit, keyword, post_limit, max_age_days)
            
            for post in raw_posts:
                data = post.get('data', {})
                all_posts.append(RedditPost(
                    url=data.get('url', ''),
                    relevance=False,
                    title=data.get('title', ''),
                    subtitle=data.get('selftext', ''),
                    comments=[]
                ))
    
    logger.info(f"Scraped {len(all_posts)} total posts")
    
    # Step 2: Classify posts for relevance
    logger.info("Step 2: Classifying posts for relevance...")
    relevant_posts = classify_posts_relevance(all_posts, batch_size=3, debug=False)
    logger.info(f"Found {len(relevant_posts)} relevant posts")
    
    # Step 3-6: Process each relevant post
    logger.info("Step 3-6: Processing relevant posts (duplicate check, comments, replies, save)...")
    
    for idx, post in enumerate(relevant_posts, 1):
        logger.info(f"Processing post {idx}/{len(relevant_posts)}: {post.title[:50]}...")
        
        # Step 3: Check for duplicates (before expensive operations)
        if check_duplicate(post.url):
            logger.info(f"Skipping duplicate post: {post.url}")
            skipped += 1
            continue
        
        # Step 4: Fetch comments for this post
        logger.info(f"Fetching comments for: {post.url}")
        posts_with_comments = fetch_and_attach_comments([post])
        post = posts_with_comments[0]
        
        # Step 5: Generate Ovarra reply
        logger.info(f"Generating Ovarra reply for: {post.url}")
        posts_with_replies = generate_ovarra_replies([post], debug=False)
        post = posts_with_replies[0]
        
        # Step 6: Insert into Supabase
        if post.ovarra_reply:
            logger.info(f"Inserting suggestion into Supabase: {post.url}")
            result = insert_suggestion(
                reddit_name=post.title,
                reddit_url=post.url,
                suggested_response=post.ovarra_reply
            )
            
            if result:
                processed += 1
                logger.info(f"Successfully saved suggestion: {post.url}")
            else:
                failed += 1
                logger.error(f"Failed to save suggestion: {post.url}")
        else:
            failed += 1
            logger.warning(f"No reply generated for post: {post.url}")
    
    # Determine overall status
    if processed > 0 and failed == 0:
        status = "success"
    elif processed > 0 and failed > 0:
        status = "partial"
    elif skipped > 0 and failed == 0:
        status = "success"  # All posts were duplicates - this is success, not failure
    else:
        status = "failure"  # No posts found or all failed
    
    summary = {
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "status": status
    }
    
    logger.info(f"Scrape complete: {summary}")
    return summary
