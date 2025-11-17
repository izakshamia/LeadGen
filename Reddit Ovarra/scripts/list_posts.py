#!/usr/bin/env python3
"""
List all posts from checkpoint files with their details.
Useful for seeing what posts are available and their indices.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_utils import posts_from_json


def main():
    parser = argparse.ArgumentParser(description="List posts from checkpoint files")
    parser.add_argument('--file', default='posts_with_comments.json',
                        help='File to list (default: posts_with_comments.json)')
    parser.add_argument('--show-replies', action='store_true',
                        help='Show existing replies')
    parser.add_argument('--show-comments', action='store_true',
                        help='Show comment count details')
    args = parser.parse_args()

    # Load posts
    try:
        posts = posts_from_json(args.file)
        print(f"📂 File: {args.file}")
        print(f"📊 Total posts: {len(posts)}")
        print("=" * 80)
    except FileNotFoundError:
        print(f"❌ Error: {args.file} not found!")
        print(f"\nAvailable checkpoint files:")
        print("  - scraped_posts.json (all scraped posts)")
        print("  - relevant_posts.json (classified as relevant)")
        print("  - posts_with_comments.json (with comments fetched)")
        print("  - final_posts.json (with Ovarra replies)")
        return
    except Exception as e:
        print(f"❌ Error loading posts: {e}")
        return

    if not posts:
        print(f"⚠️  No posts found in {args.file}")
        return

    # List posts
    for i, post in enumerate(posts, 1):
        print(f"\n📌 Post #{i}")
        print(f"   Title: {post.title}")
        print(f"   URL: {post.url}")
        print(f"   Relevant: {'✅ Yes' if post.relevance else '❌ No'}")
        
        if args.show_comments or post.comments:
            comment_count = len(post.comments) if post.comments else 0
            print(f"   Comments: {comment_count}")
        
        if args.show_replies and post.ovarra_reply:
            print(f"   Reply: {post.ovarra_reply[:100]}...")
        elif args.show_replies:
            print(f"   Reply: ⚠️  None")
        
        print("-" * 80)

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total posts: {len(posts)}")
    relevant_count = sum(1 for p in posts if p.relevance)
    print(f"   Relevant: {relevant_count}")
    with_comments = sum(1 for p in posts if p.comments)
    print(f"   With comments: {with_comments}")
    with_replies = sum(1 for p in posts if p.ovarra_reply)
    print(f"   With replies: {with_replies}")


if __name__ == "__main__":
    main()
