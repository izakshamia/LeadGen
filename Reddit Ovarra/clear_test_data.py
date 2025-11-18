#!/usr/bin/env python3
"""
Clear recent test data from Supabase to allow re-testing the scraper
"""

import os
from dotenv import load_dotenv
from supabase_client import init_supabase_client

load_dotenv()

def clear_recent_data(hours=24):
    """Clear suggestions from the last N hours"""
    try:
        client = init_supabase_client()
        
        # Get count before deletion
        response = client.table('reddit_suggestions').select('id', count='exact').execute()
        total_before = len(response.data)
        
        print(f"Total suggestions in database: {total_before}")
        print(f"\nClearing suggestions from last {hours} hours...")
        
        # Delete recent suggestions
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = client.table('reddit_suggestions') \
            .delete() \
            .gte('created_at', cutoff_time.isoformat()) \
            .execute()
        
        deleted_count = len(result.data) if result.data else 0
        
        print(f"✓ Deleted {deleted_count} recent suggestions")
        print(f"Remaining: {total_before - deleted_count}")
        
        return deleted_count
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 0

def clear_all_data():
    """Clear ALL suggestions (use with caution!)"""
    try:
        client = init_supabase_client()
        
        # Get count before deletion
        response = client.table('reddit_suggestions').select('id', count='exact').execute()
        total_before = len(response.data)
        
        print(f"Total suggestions in database: {total_before}")
        
        confirm = input("\n⚠️  Are you sure you want to delete ALL suggestions? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return 0
        
        print("\nDeleting all suggestions...")
        
        # Delete all
        result = client.table('reddit_suggestions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        
        deleted_count = len(result.data) if result.data else 0
        
        print(f"✓ Deleted {deleted_count} suggestions")
        print(f"Database is now empty")
        
        return deleted_count
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 0

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Clear Test Data from Supabase")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        clear_all_data()
    else:
        print("\nOptions:")
        print("1. Clear last 24 hours")
        print("2. Clear last 48 hours")
        print("3. Clear last 7 days")
        print("4. Clear ALL data (⚠️  dangerous!)")
        
        choice = input("\nEnter choice (1-4): ")
        
        if choice == '1':
            clear_recent_data(24)
        elif choice == '2':
            clear_recent_data(48)
        elif choice == '3':
            clear_recent_data(168)
        elif choice == '4':
            clear_all_data()
        else:
            print("Invalid choice")
    
    print("\n" + "=" * 60)
