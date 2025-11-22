#!/usr/bin/env python3
"""
Debug script to test scraping with detailed error output
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("DEBUG: Testing Scraper Service")
print("=" * 70)

# Check environment variables
print("\n1. Checking environment variables...")
required_vars = ['GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"   ✓ {var}: {value[:20]}...")
    else:
        print(f"   ✗ {var}: NOT SET")

# Test imports
print("\n2. Testing imports...")
try:
    from scraper_service import scrape_and_save
    print("   ✓ scraper_service imported")
except Exception as e:
    print(f"   ✗ Failed to import scraper_service: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from api_utils import fetch_reddit_posts
    print("   ✓ api_utils imported")
except Exception as e:
    print(f"   ✗ Failed to import api_utils: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test Reddit API directly
print("\n3. Testing Reddit API directly...")
try:
    posts = fetch_reddit_posts("CamGirlProblems", "leak", limit=2, max_age_days=30)
    print(f"   ✓ Fetched {len(posts)} posts from Reddit")
    if posts:
        print(f"   First post: {posts[0].get('data', {}).get('title', 'N/A')[:50]}...")
    else:
        print("   ⚠ No posts found (this might be normal)")
except Exception as e:
    print(f"   ✗ Failed to fetch posts: {e}")
    traceback.print_exc()

# Test full scraper pipeline
print("\n4. Testing full scraper pipeline...")
try:
    result = scrape_and_save(
        subreddits=["CamGirlProblems"],
        keywords=["leak"],
        post_limit=2,
        max_age_days=30
    )
    
    print(f"\n   Result:")
    print(f"   - Status: {result['status']}")
    print(f"   - Processed: {result['processed']}")
    print(f"   - Skipped: {result['skipped']}")
    print(f"   - Failed: {result['failed']}")
    
    if result['status'] == 'failure':
        print("\n   ⚠ Scraping returned 'failure' status")
        print("   This usually means:")
        print("   - No posts were found on Reddit")
        print("   - All posts were filtered out as not relevant")
        print("   - All posts were duplicates")
        print("   - An error occurred during processing")
        
except Exception as e:
    print(f"\n   ✗ Scraper failed with exception: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
print("Debug test complete")
print("=" * 70)
