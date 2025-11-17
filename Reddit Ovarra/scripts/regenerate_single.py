#!/usr/bin/env python3
"""
Regenerate reply for a single specific post by index or URL.
Useful for testing and iterating on specific posts.
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_utils import generate_ovarra_replies, posts_from_json, posts_to_json


def main():
    parser = argparse.ArgumentParser(description="Regenerate reply for a specific post")
    parser.add_argument('--index', type=int, help='Post index (1-based) to regenerate')
    parser.add_argument('--url', help='Post URL to regenerate')
    parser.add_argument('--input', default='posts_with_comments.json',
                        help='Input file (default: posts_with_comments.json)')
    parser.add_argument('--output', default='final_posts.json',
                        help='Output file (default: final_posts.json)')
    parser.add_argument('--debug', action='store_true', help='Enable debug prints')
    args = parser.parse_args()

    if not args.index and not args.url:
        print("❌ Error: Must specify either --index or --url")
        print("Examples:")
        print("  python3 regenerate_single.py --index 3")
        print("  python3 regenerate_single.py --url 'https://reddit.com/...'")
        return

    # Load posts
    try:
        posts = posts_from_json(args.input)
        print(f"✅ Loaded {len(posts)} posts from {args.input}")
    except FileNotFoundError:
        print(f"❌ Error: {args.input} not found!")
        return

    # Find the specific post
    target_post = None
    target_index = None

    if args.index:
        if 1 <= args.index <= len(posts):
            target_post = posts[args.index - 1]
            target_index = args.index - 1
            print(f"🎯 Found post #{args.index}")
        else:
            print(f"❌ Error: Index {args.index} out of range (1-{len(posts)})")
            return
    elif args.url:
        for i, post in enumerate(posts):
            if args.url in post.url or post.url in args.url:
                target_post = post
                target_index = i
                print(f"🎯 Found post at index #{i + 1}")
                break
        if not target_post:
            print(f"❌ Error: Post with URL '{args.url}' not found")
            return

    # Show post info
    print(f"\n📋 Post Details:")
    print(f"   Title: {target_post.title}")
    print(f"   URL: {target_post.url}")
    print(f"   Comments: {len(target_post.comments) if target_post.comments else 0}")
    if target_post.ovarra_reply:
        print(f"   Old Reply: {target_post.ovarra_reply}")

    # Generate new reply
    print(f"\n🤖 Generating new reply...")
    posts_with_new_reply = generate_ovarra_replies([target_post], debug=args.debug)
    
    # Update the post in the list
    posts[target_index] = posts_with_new_reply[0]

    # Save all posts
    posts_to_json(posts, args.output)
    print(f"\n✅ Saved updated posts to {args.output}")

    # Show new reply
    print(f"\n💬 New Reply:")
    print("=" * 50)
    print(posts_with_new_reply[0].ovarra_reply)
    print("=" * 50)


if __name__ == "__main__":
    main()
