import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import time
import os

# Import fetch_reddit_posts from reddit_analyzer.py
from reddit_analyzer import fetch_reddit_posts, headers, BASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subreddit_keyword_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
KEYWORDS = ["DMCA", "leaks", "Rulta", "Burqi", "takedown"]
DAYS_LIMIT = 365
POST_LIMIT_PER_KEYWORD = 100
OUTPUT_FILENAME = "subreddit_keyword_results.json"
SUBREDDITS_FILE = "unique_subreddits.txt"

# Get current time and cutoff
NOW = datetime(2025, 7, 23, 19, 0, 8)  # Fixed as per user instruction
CUTOFF = NOW - timedelta(days=DAYS_LIMIT)


def read_subreddits(filename: str) -> List[str]:
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def filter_recent_posts(posts: List[Dict], cutoff: datetime) -> List[Dict]:
    filtered = []
    for post in posts:
        data = post.get('data', {})
        created_utc = data.get('created_utc')
        if created_utc:
            created_dt = datetime.utcfromtimestamp(created_utc)
            if created_dt >= cutoff:
                filtered.append(post)
    return filtered


def extract_post_info(post: Dict, subreddit: str) -> Dict:
    data = post.get('data', {})
    return {
        "subreddit": subreddit,
        "title": data.get("title", ""),
        "selftext": data.get("selftext", ""),
        "author": data.get("author", ""),
        "created_utc": data.get("created_utc", None),
        "permalink": f"{BASE_URL}{data.get('permalink', '')}",
        "url": data.get("url", ""),
        "id": data.get("id", "")
    }


def main():
    subreddits = read_subreddits(SUBREDDITS_FILE)
    logger.info(f"Loaded {len(subreddits)} subreddits from {SUBREDDITS_FILE}")
    results = []
    for subreddit in subreddits:
        logger.info(f"Searching subreddit: {subreddit}")
        for keyword in KEYWORDS:
            logger.info(f"  Keyword: {keyword}")
            posts = fetch_reddit_posts(subreddit, keyword, limit=POST_LIMIT_PER_KEYWORD)
            recent_posts = filter_recent_posts(posts, CUTOFF)
            logger.info(f"    {len(recent_posts)} posts found in last {DAYS_LIMIT} days.")
            for post in recent_posts:
                info = extract_post_info(post, subreddit)
                results.append(info)
            time.sleep(1)  # Be nice to Reddit API
    # Save results
    with open(OUTPUT_FILENAME, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved {len(results)} posts to {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
