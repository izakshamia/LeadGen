import argparse
from typing import List
from models import RedditPost
from api_utils import (
    fetch_reddit_posts, discover_subreddits, fetch_and_attach_comments,
    classify_posts_relevance, generate_ovarra_replies
)

DEFAULT_SUBREDDITS = ["CamGirlProblems", "OnlyFansAdvice", "CreatorAdvice", "SexWorkersOnly", "LegalAdvice"]
DEFAULT_KEYWORDS = ["onlyfans leak", "content stolen", "dmca help", "nsfw leak", "privacy violation", "content removal"]


def scrape_posts(subreddits: List[str], keywords: List[str], post_limit: int, debug: bool) -> List[RedditPost]:
    """Scrape posts from Reddit and return as RedditPost objects"""
    posts = []
    total_combinations = len(subreddits) * len(keywords)
    current_combination = 0
    
    for subreddit in subreddits:
        for keyword in keywords:
            current_combination += 1
            print(f"   [{current_combination}/{total_combinations}] Scraping r/{subreddit} for '{keyword}'...")
            raw_posts = fetch_reddit_posts(subreddit, keyword, post_limit)
            posts_found = len(raw_posts)
            print(f"      Found {posts_found} posts")
            
            for post in raw_posts:
                data = post.get('data', {})
                posts.append(RedditPost(
                    url=data.get('url', ''),
                    relevance=False,
                    title=data.get('title', ''),
                    subtitle=data.get('selftext', ''),
                    comments=[]
                ))
    
    return posts


def main():
    print("🚀 Starting Reddit Ovarra Pipeline (Objects Only)")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(description="Reddit Ovarra Pipeline - Objects Only")
    parser.add_argument('--subreddits', nargs='+', help='List of subreddits to search')
    parser.add_argument('--discover', action='store_true', help='Discover related subreddits')
    parser.add_argument('--seed-subreddit', default='CamGirlProblems', help='Seed subreddit for discovery')
    parser.add_argument('--keywords', nargs='+', default=DEFAULT_KEYWORDS, help='Keywords to search for')
    parser.add_argument('--post-limit', type=int, default=10, help='Posts per keyword')
    parser.add_argument('--debug', action='store_true', help='Enable debug prints')
    args = parser.parse_args()

    debug = args.debug
    
    print(f"📋 Configuration:")
    print(f"   Keywords: {args.keywords}")
    print(f"   Post limit per keyword: {args.post_limit}")
    print(f"   Debug mode: {debug}")

    # Step 1: Subreddit selection
    print(f"\n🔍 Step 1: Subreddit Selection")
    print("-" * 30)
    if args.discover:
        print(f"🔎 Discovering subreddits from seed: r/{args.seed_subreddit}")
        subreddits = list(discover_subreddits(args.seed_subreddit, args.keywords, args.post_limit))
        print(f"✅ Discovered {len(subreddits)} subreddits: {subreddits}")
    else:
        subreddits = args.subreddits if args.subreddits else DEFAULT_SUBREDDITS
        print(f"📂 Using {len(subreddits)} subreddits: {subreddits}")

    # Step 2: Scrape posts (creates RedditPost objects)
    print(f"\n📥 Step 2: Scraping Posts")
    print("-" * 30)
    posts = scrape_posts(subreddits, args.keywords, args.post_limit, debug)
    print(f"✅ Scraped {len(posts)} total posts")
    
    # Step 3: Classify relevance
    print(f"\n🎯 Step 3: Classifying Relevance")
    print("-" * 30)
    posts = classify_posts_relevance(posts, debug=debug)
    relevant_count = len([p for p in posts if p.relevance])
    print(f"✅ Classified {relevant_count}/{len(posts)} posts as relevant")
    
    # Step 4: Fetch comments
    print(f"\n💬 Step 4: Fetching Comments")
    print("-" * 30)
    posts = fetch_and_attach_comments(posts)
    posts_with_comments = len([p for p in posts if p.comments])
    print(f"✅ Fetched comments for {posts_with_comments}/{len(posts)} posts")
    
    # Step 5: Generate Ovarra replies
    print(f"\n🤖 Step 5: Generating Ovarra Replies")
    print("-" * 30)
    posts = generate_ovarra_replies(posts, debug=debug)
    posts_with_replies = len([p for p in posts if p.ovarra_reply])
    print(f"✅ Generated replies for {posts_with_replies}/{len(posts)} posts")

    # Print results
    print(f"\n🎉 Pipeline Complete!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   Total posts processed: {len(posts)}")
    print(f"   Relevant posts: {len([p for p in posts if p.relevance])}")
    print(f"   Posts with comments: {len([p for p in posts if p.comments])}")
    print(f"   Posts with Ovarra replies: {len([p for p in posts if p.ovarra_reply])}")
    
    # Show final posts with Ovarra replies
    posts_with_replies = [p for p in posts if p.ovarra_reply]
    if posts_with_replies:
        print(f"\n📝 Final Posts with Ovarra Replies:")
        print("-" * 50)
        for i, post in enumerate(posts_with_replies, 1):
            print(f"\n📌 Post #{i}")
            print(f"   Title: {post.title}")
            print(f"   URL: {post.url}")
            print(f"   Comments: {len(post.comments)}")
            print(f"   Ovarra Reply: {post.ovarra_reply}")
    else:
        print(f"\n⚠️  No posts with Ovarra replies generated")
    
    print(f"\n✅ Pipeline finished successfully!")
    print(f"💡 Tip: The posts are returned as Python objects for further processing")
    
    # Return the posts objects for further use
    return posts


if __name__ == "__main__":
    final_posts = main() 