#!/usr/bin/env python3
"""
Regenerate Ovarra replies for existing relevant posts without re-running the entire pipeline.
This is useful when you want to:
- Test new reply prompts
- Regenerate replies with updated instructions
- Fix replies that didn't work well
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_utils import generate_ovarra_replies, posts_from_json, posts_to_json


def main():
    parser = argparse.ArgumentParser(description="Regenerate Ovarra replies for existing relevant posts")
    parser.add_argument('--input', default='posts_with_comments.json', 
                        help='Input file with posts and comments (default: posts_with_comments.json)')
    parser.add_argument('--output', default='final_posts.json',
                        help='Output file for posts with new replies (default: final_posts.json)')
    parser.add_argument('--debug', action='store_true', help='Enable debug prints')
    args = parser.parse_args()

    print(f"🔄 Regenerating Ovarra replies...")
    print(f"📂 Input: {args.input}")
    print(f"📂 Output: {args.output}")
    print("-" * 50)

    # Load existing posts with comments
    try:
        posts = posts_from_json(args.input)
        print(f"✅ Loaded {len(posts)} posts from {args.input}")
    except FileNotFoundError:
        print(f"❌ Error: {args.input} not found!")
        print(f"💡 Run the full pipeline first: python3 pipeline.py --debug")
        return
    except Exception as e:
        print(f"❌ Error loading posts: {e}")
        return

    if not posts:
        print(f"⚠️  No posts found in {args.input}")
        print(f"💡 Make sure you have relevant posts with comments")
        return

    # Show post info
    print(f"\n📋 Posts to process:")
    for i, post in enumerate(posts, 1):
        comment_count = len(post.comments) if post.comments else 0
        print(f"   {i}. {post.title[:60]}... ({comment_count} comments)")

    # Generate new replies
    print(f"\n🤖 Generating new replies with Gemini...")
    posts = generate_ovarra_replies(posts, debug=args.debug)

    # Save results
    posts_to_json(posts, args.output)
    print(f"\n✅ Saved {len(posts)} posts with new replies to {args.output}")

    # Show results
    print(f"\n📝 Generated Replies:")
    print("=" * 50)
    for i, post in enumerate(posts, 1):
        print(f"\n📌 Post #{i}: {post.title[:60]}...")
        print(f"🔗 URL: {post.url}")
        if post.ovarra_reply:
            print(f"💬 Reply: {post.ovarra_reply}")
        else:
            print(f"⚠️  No reply generated")
        print("-" * 50)

    print(f"\n✨ Done! Replies regenerated successfully.")


if __name__ == "__main__":
    main()
