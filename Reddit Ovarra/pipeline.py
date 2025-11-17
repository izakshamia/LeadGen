import os
import argparse
from typing import List
from models import RedditPost
from api_utils import (
    fetch_reddit_posts, discover_subreddits, fetch_and_attach_comments,
    classify_posts_relevance, generate_ovarra_replies,
    posts_to_json, posts_from_json
)

CHECKPOINTS = [
    ("scraped_posts.json", "Scraping posts", "scrape_posts"),
    ("relevant_posts.json", "Classifying relevance", "classify_relevance"),
    ("posts_with_comments.json", "Fetching comments", "fetch_comments"),
    ("final_posts.json", "Generating Ovarra replies", "generate_replies")
]

DEFAULT_SUBREDDITS = ["CamGirlProblems", "OnlyFansAdvice", "CreatorAdvice", "SexWorkersOnly", "LegalAdvice"]
DEFAULT_KEYWORDS = ["onlyfans leak", "content stolen", "dmca help", "nsfw leak", "privacy violation", "content removal"]

# Subreddits where promotional replies are NOT allowed
NO_PROMO_SUBREDDITS = ["CamGirlProblems", "SexWorkersOnly"]


def scrape_posts(subreddits: List[str], keywords: List[str], post_limit: int, max_age_days: int, debug: bool) -> List[RedditPost]:
    posts = []
    for subreddit in subreddits:
        for keyword in keywords:
            if debug:
                print(f"Scraping r/{subreddit} for '{keyword}' (last {max_age_days} days)...")
            raw_posts = fetch_reddit_posts(subreddit, keyword, post_limit, max_age_days)
            for post in raw_posts:
                data = post.get('data', {})
                posts.append(RedditPost(
                    url=data.get('url', ''),
                    relevance=False,
                    title=data.get('title', ''),
                    subtitle=data.get('selftext', ''),
                    comments=[]
                ))
    if debug:
        print(f"Scraped {len(posts)} posts (filtered to last {max_age_days} days).")
    return posts

def main():
    parser = argparse.ArgumentParser(description="Reddit Ovarra Pipeline with Checkpoints")
    parser.add_argument('--subreddits', nargs='+', help='List of subreddits to search')
    parser.add_argument('--discover', action='store_true', help='Discover related subreddits')
    parser.add_argument('--seed-subreddit', default='CamGirlProblems', help='Seed subreddit for discovery')
    parser.add_argument('--keywords', nargs='+', default=DEFAULT_KEYWORDS, help='Keywords to search for')
    parser.add_argument('--post-limit', type=int, default=10, help='Posts per keyword')
    parser.add_argument('--max-age-days', type=int, default=120, help='Only fetch posts from last N days (default: 120 = 4 months)')
    parser.add_argument('--debug', action='store_true', help='Enable debug prints')
    parser.add_argument('--force', action='store_true', help='Ignore checkpoints and re-run all steps')
    args = parser.parse_args()

    debug = args.debug
    force = args.force

    # Step 1: Subreddit selection
    if args.discover:
        if debug:
            print(f"Discovering subreddits from seed: {args.seed_subreddit}...")
        subreddits = list(discover_subreddits(args.seed_subreddit, args.keywords, args.post_limit))
        if debug:
            print(f"Discovered subreddits: {subreddits}")
    else:
        subreddits = args.subreddits if args.subreddits else DEFAULT_SUBREDDITS
        if debug:
            print(f"Using subreddits: {subreddits}")

    # Pipeline with checkpoints
    data = None
    for idx, (ckpt_file, step_desc, step_key) in enumerate(CHECKPOINTS):
        if not force and os.path.exists(ckpt_file):
            if debug:
                print(f"[Checkpoint] Loading {step_desc} from {ckpt_file}")
                if step_key == "scrape_posts":
                    print(f"💡 Tip: Using cached posts. To re-scrape with --max-age-days filter, use --force flag")
            data = posts_from_json(ckpt_file)
            continue
        if debug:
            print(f"[Step] {step_desc}...")
        if step_key == "scrape_posts":
            data = scrape_posts(subreddits, args.keywords, args.post_limit, args.max_age_days, debug)
        elif step_key == "classify_relevance":
            data = classify_posts_relevance(data, debug=debug)
        elif step_key == "fetch_comments":
            data = fetch_and_attach_comments(data)
        elif step_key == "generate_replies":
            data = generate_ovarra_replies(data, debug=debug)
        posts_to_json(data, ckpt_file)
        if debug:
            print(f"[Checkpoint] Saved {step_desc} to {ckpt_file}")

    # Print summary
    print("\nPipeline complete! Final posts with Ovarra replies:")
    for i, post in enumerate(data, 1):
        print(f"\nPost #{i}")
        print(f"Title: {post.title}")
        print(f"URL: {post.url}")
        print(f"Ovarra Reply: {post.ovarra_reply}")

if __name__ == "__main__":
    main() 