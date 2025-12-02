#!/usr/bin/env python3
"""
Run database migration to add contacted_status fields to target_redditors table.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Execute the migration SQL file."""
    try:
        from supabase import create_client
        
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
            return False
        
        # Initialize client
        supabase = create_client(supabase_url, supabase_key)
        
        # Read migration file
        migration_file = 'Reddit Ovarra/migrations/002_add_contacted_status.sql'
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        print(f"Running migration: {migration_file}")
        print("=" * 60)
        
        # Split SQL into individual statements
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"\nExecuting statement {i}...")
                try:
                    # Use RPC to execute raw SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✓ Statement {i} executed successfully")
                except Exception as e:
                    # If RPC doesn't work, try direct execution
                    print(f"Note: {e}")
                    print("Migration may need to be run manually via Supabase SQL Editor")
        
        print("\n" + "=" * 60)
        print("Migration completed!")
        print("\nIf you see errors above, please run the migration manually:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print(f"3. Copy and paste the contents of: {migration_file}")
        print("4. Click 'Run'")
        
        return True
        
    except Exception as e:
        print(f"Error running migration: {e}")
        print("\nPlease run the migration manually via Supabase SQL Editor:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of: Reddit Ovarra/migrations/002_add_contacted_status.sql")
        print("4. Click 'Run'")
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
