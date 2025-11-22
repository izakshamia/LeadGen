"""
Test script for scraper_service.py
Tests the integration between scraper and Supabase
"""

import os
from dotenv import load_dotenv
from scraper_service import scrape_and_save

# Load environment variables
load_dotenv()

def test_scrape_and_save():
    """
    Test the scrape_and_save function with minimal parameters.
    This is a basic integration test to verify the pipeline works.
    """
    print("Testing scrape_and_save function...")
    print("=" * 60)
    
    # Test with minimal parameters
    subreddits = ["CamGirlProblems"]
    keywords = ["leak"]
    post_limit = 2  # Small limit for testing
    max_age_days = 30
    
    print(f"Test parameters:")
    print(f"  Subreddits: {subreddits}")
    print(f"  Keywords: {keywords}")
    print(f"  Post limit: {post_limit}")
    print(f"  Max age: {max_age_days} days")
    print()
    
    try:
        result = scrape_and_save(
            subreddits=subreddits,
            keywords=keywords,
            post_limit=post_limit,
            max_age_days=max_age_days
        )
        
        print("\n" + "=" * 60)
        print("Test Results:")
        print(f"  Status: {result['status']}")
        print(f"  Processed: {result['processed']}")
        print(f"  Skipped: {result['skipped']}")
        print(f"  Failed: {result['failed']}")
        print("=" * 60)
        
        # Verify result structure
        assert 'processed' in result, "Missing 'processed' in result"
        assert 'skipped' in result, "Missing 'skipped' in result"
        assert 'failed' in result, "Missing 'failed' in result"
        assert 'status' in result, "Missing 'status' in result"
        assert result['status'] in ['success', 'partial', 'failure'], f"Invalid status: {result['status']}"
        
        print("\n✅ Test passed! All assertions successful.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'GEMINI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        exit(1)
    
    print("Environment variables check: ✅")
    print()
    
    success = test_scrape_and_save()
    exit(0 if success else 1)
