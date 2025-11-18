#!/usr/bin/env python3
"""
Simple test script for supabase_client module.
Tests all core functions to verify implementation.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=str(env_path))

# Import after loading env vars
from supabase_client import (
    init_supabase_client,
    check_duplicate,
    insert_suggestion,
    get_recent_suggestions,
    test_connection
)

def main():
    print("=" * 60)
    print("Testing Supabase Client Module")
    print("=" * 60)
    
    # Test 1: Initialize client
    print("\n1. Testing client initialization...")
    try:
        client = init_supabase_client()
        print("   ✓ Client initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize client: {e}")
        return
    
    # Test 2: Test connection
    print("\n2. Testing database connection...")
    if test_connection():
        print("   ✓ Database connection successful")
    else:
        print("   ✗ Database connection failed")
        return
    
    # Test 3: Check duplicate (should not exist)
    print("\n3. Testing duplicate check...")
    test_url = "https://reddit.com/r/test/comments/test_post_12345"
    is_duplicate = check_duplicate(test_url)
    print(f"   URL: {test_url}")
    print(f"   Is duplicate: {is_duplicate}")
    
    # Test 4: Insert suggestion
    print("\n4. Testing suggestion insertion...")
    result = insert_suggestion(
        reddit_name="Test Post - Supabase Client Module Test",
        reddit_url=test_url,
        suggested_response="This is a test response from the supabase_client module."
    )
    if result:
        print(f"   ✓ Suggestion inserted successfully")
        print(f"   ID: {result.get('id')}")
    else:
        print("   ✗ Failed to insert suggestion (may be duplicate)")
    
    # Test 5: Check duplicate again (should exist now)
    print("\n5. Testing duplicate check after insertion...")
    is_duplicate = check_duplicate(test_url)
    print(f"   Is duplicate: {is_duplicate}")
    if is_duplicate:
        print("   ✓ Duplicate detection working correctly")
    else:
        print("   ✗ Duplicate not detected")
    
    # Test 6: Get recent suggestions
    print("\n6. Testing recent suggestions retrieval...")
    suggestions = get_recent_suggestions(hours=24)
    print(f"   Retrieved {len(suggestions)} suggestions from last 24 hours")
    if suggestions:
        print(f"   Most recent: {suggestions[0].get('reddit_name', 'N/A')[:50]}...")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
