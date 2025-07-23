import os
from name_cleaner import get_name_cleaner
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_TABLE = os.getenv('SUPABASE_TABLE')

def get_usernames_from_db(limit=20):
    """Fetch usernames from Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_TABLE:
        raise ValueError("Please set all required environment variables in your .env file")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    params = {
        'select': 'username',
        'limit': limit,
        'order': 'created_at.desc'
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    usernames = response.json()
    return [user['username'] for user in usernames if 'username' in user and user['username']]

def main():
    # Initialize the name cleaner
    name_cleaner = get_name_cleaner()
    
    # Get real usernames from the database
    try:
        usernames = get_usernames_from_db(20)
        print(f"Found {len(usernames)} usernames from the database")
        print("\nOriginal Username -> Cleaned Name")
        print("-" * 50)
        
        # Clean each username and print results
        for username in usernames:
            cleaned_name = name_cleaner.clean_name(username)
            print(f"{username} -> {cleaned_name if cleaned_name else 'None'}")
            
    except Exception as e:
        print(f"Error fetching usernames: {str(e)}")

if __name__ == "__main__":
    main()
