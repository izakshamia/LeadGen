import os
import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import dotenv
from typing import Dict, Any, List, Optional
import re
import logging
import time
import argparse
from functools import wraps
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random

# Environment variables
GOOGLE_API_KEY = None
GOOGLE_CSE_ID = None
SUPABASE_URL = None
SUPABASE_KEY = None
SUPABASE_TABLE = None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 2):
    """Decorator to retry a function with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    logger.warning(f"Attempt {attempts}/{max_attempts} failed: {e}")
                    time.sleep(delay * (2 ** (attempts - 1)))
        return wrapper
    return decorator

def load_environment():
    """Load environment variables"""
    # Load environment variables from .env file
    dotenv.load_dotenv()
    
    # Get required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_TABLE']
    
    # Validate required environment variables
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            raise ValueError(f"Missing required environment variable: {var}")
    
    # Set global variables
    global GOOGLE_API_KEY, GOOGLE_CSE_ID, SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE
    
    # Load from environment
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_TABLE = os.getenv('SUPABASE_TABLE')
    
    # Validate Google API credentials
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        logger.warning("Google API credentials not found. Results may be limited.")

    # Log environment variables
    logger.info("\nEnvironment variables loaded:")
    logger.info(f"SUPABASE_URL: {SUPABASE_URL}")
    logger.info(f"SUPABASE_KEY: {SUPABASE_KEY[:5]}... (truncated for security)")
    logger.info(f"SUPABASE_TABLE: {SUPABASE_TABLE}")
    
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        logger.info(f"GOOGLE_API_KEY: {GOOGLE_API_KEY[:5]}... (truncated for security)")
        logger.info(f"GOOGLE_CSE_ID: {GOOGLE_CSE_ID}")

from name_cleaner import get_name_cleaner

# Get singleton instance of name cleaner
name_cleaner = get_name_cleaner()

def get_supabase_usernames(limit=20):
    """Fetch and clean usernames from Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_TABLE:
        raise ValueError("Please set all required environment variables in your .env file:\n"
                        "SUPABASE_URL, SUPABASE_KEY, and SUPABASE_TABLE")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    params = {
        'select': 'username',
        'limit': 100,  # Fetch more than needed to ensure unique usernames
        'order': 'created_at.desc,username.asc'
    }
    
    logger.info(f"Fetching from URL: {url}")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    # Get unique usernames
    usernames = response.json()
    unique_usernames = set()
    
    # Add cleaned usernames until we have enough unique ones
    for user in usernames:
        if 'username' in user and user['username']:
            cleaned_name = name_cleaner.clean_name(user['username'])
            if cleaned_name:  # Only add if we have a valid cleaned name
                unique_usernames.add(cleaned_name)
                if len(unique_usernames) >= limit:
                    break
    
    # Convert set back to list and return
    return [{'username': username} for username in unique_usernames]

@retry(max_attempts=3, delay=2)
def google_search(query, num_results=7):
    """Perform a Google search and return results"""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        logger.warning("Google API credentials not found. Using web scraping instead.")
        return scrape_google(query, num_results)
    
    try:
        # Add delay to avoid rate limiting
        time.sleep(1 + random.uniform(0, 2))  # Random delay between 1-3 seconds
        
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            num=num_results,
            safe='medium'
        ).execute()
        
        if 'items' not in result:
            logger.warning("No results found")
            return []
            
        return result['items']
    except HttpError as e:
        if e.resp.status == 429:  # Quota exceeded
            logger.warning("Google API quota exceeded. Falling back to web scraping.")
            return scrape_google(query, num_results)
        logger.error(f"HTTP error during Google search: {e}")
        return []
    except Exception as e:
        logger.error(f"Error during Google search: {e}")
        return []

def scrape_google(query, num_results=7):
    """Scrape Google search results using web scraping"""
    try:
        # Format the Google search URL
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={num_results}"
        
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add random delay to avoid rate limiting
        delay = random.uniform(2, 5)  # Random delay between 2-5 seconds
        logger.info(f"Waiting {delay:.1f} seconds before scraping...")
        time.sleep(delay)
        
        # Get the search results page
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all search result divs
        results = []
        for result in soup.select('.tF2Cxc')[:num_results]:
            title = result.select_one('.LC20lb.DKV0Md')
            link = result.select_one('.yuRUbf a')
            snippet = result.select_one('.VwiC3b.yXK7lf.MUxGbd.yDYNvb.lyLwlb')
            
            if title and link:
                results.append({
                    'title': title.get_text(),
                    'link': link.get('href'),
                    'snippet': snippet.get_text() if snippet else ''
                })
        
        return results
    except Exception as e:
        logger.error(f"Error scraping Google: {e}")
        return []

def extract_name(username):
    """Extract first and last name from username"""
    try:
        # Convert to lowercase
        username = username.lower()
        
        # Remove numbers and special characters
        username = re.sub(r'[0-9_]', ' ', username)
        
        # Remove common keywords
        keywords = [
            'onlyfans', 'fansly', 'telegram', 'instagram', 'twitter', 'x',
            'fan', 'fans', 'real', 'official', 'authentic', 'verified',
            'bod', 'girls', 'playboy', 'ddf', 'digital', 'desire', 'exxtra',
            'buggy', 'tnt', 'jenson', 'karate', 'brazzers', 'exxtra',
            'playmate', 'porn', 'xxx', 'sex', 'nude', 'naked', 'strip',
            'drop', 'low', 'tight', 'short', '80g', 'nerd', 'strips',
            'score', 'classic', 'bombshell', 'mix', 'video', 'channel',
            'user', 'here', 'comes', 'trouble', 'virtual', 'taboo',
            'rendezvous', 'oiled', 'up', 'cracow', 'loira', 'tatuada',
            'napoli', 'tamarreide', 'buggy', 'karate', 'exxtra', 'playmate'
        ]
        
        # Remove each keyword
        for keyword in keywords:
            username = username.replace(keyword, '').replace('_', ' ')
        
        # Split by spaces and keep first two words
        words = username.strip().split()
        
        # If we have at least 2 words, use them
        if len(words) >= 2:
            # If third word looks like a name, include it
            if len(words) >= 3 and len(words[2]) >= 3 and words[2].isalpha():
                return ' '.join(words[:3])
            return ' '.join(words[:2])
        
        # If we have only 1 word, return it
        if len(words) == 1:
            return words[0]
        
        # If no words left, return original username
        return username
    except Exception as e:
        logger.error(f"Error extracting name from {username}: {e}")
        return username

def search_social_media(username):
    """Search for social media profiles"""
    try:
        # Extract clean name from username
        clean_name = extract_name(username)
        logger.info(f"Using clean name: {clean_name}")
        
        # Perform Google search
        search_results = google_search(clean_name, num_results=7)
        
        # Define social media platforms and their domains
        platforms = {
            'instagram': r'instagram\.com',
            'twitter': r'(twitter|x)\.com',
            'onlyfans': r'onlyfans\.com',
            'telegram': r'telegram\.(org|me)',
            'linktree': r'linktr\.ee',
            'allmylinks': r'allmylinks\.com',
            'fansly': r'fansly\.com',
            'reddit': r'reddit\.com/user/',
            'snapchat': r'snapchat\.com',
            'youtube': r'youtube\.com/@'
        }
        
        results = []
        
        # Process each search result
        for item in search_results:
            href = item.get('link', '')
            # Check if it's a social media link
            for platform, pattern in platforms.items():
                if re.search(pattern, href):
                    # Skip if we already found this platform
                    if any(p['platform'] == platform for p in results):
                        continue
                    
                    username = extract_username(href, platform)
                    if username:
                        # Calculate confidence score based on multiple factors
                        keywords = clean_name.lower().split()
                        url_match = any(word in href.lower() for word in keywords)
                        title_match = any(word in item.get('title', '').lower() for word in keywords)
                        snippet_match = any(word in item.get('snippet', '').lower() for word in keywords)
                        
                        # Platform-specific verification
                        platform_score = 0.0
                        if platform == 'instagram':
                            # Instagram usually has profile pictures
                            platform_score += 0.2 if 'profile picture' in item.get('snippet', '').lower() else 0
                        elif platform == 'onlyfans':
                            # OnlyFans profiles often mention subscription
                            platform_score += 0.2 if 'subscription' in item.get('snippet', '').lower() else 0
                        elif platform == 'twitter':
                            # Twitter profiles often have tweet counts
                            platform_score += 0.2 if 'tweets' in item.get('snippet', '').lower() else 0
                        elif platform == 'youtube':
                            # YouTube channels often have subscriber counts
                            platform_score += 0.2 if 'subscribers' in item.get('snippet', '').lower() else 0
                        elif platform == 'reddit':
                            # Reddit profiles often mention karma
                            platform_score += 0.2 if 'karma' in item.get('snippet', '').lower() else 0
                        
                        # Base score + bonuses for matches
                        confidence = 0.3  # Base confidence
                        confidence += 0.3 if url_match else 0
                        confidence += 0.2 if title_match else 0
                        confidence += 0.2 if snippet_match else 0
                        confidence += platform_score
                        
                        # Cap at 1.0
                        confidence = min(confidence, 1.0)
                        
                        results.append({
                            'platform': platform,
                            'found': True,
                            'username': username,
                            'url': href,
                            'confidence': confidence,
                            'title': item.get('title', ''),
                            'snippet': item.get('snippet', ''),
                            'search_position': search_results.index(item) + 1
                        })
                        logger.info(f"Found {platform} profile: {username} (confidence: {confidence:.2f})")
                        break
    except Exception as e:
        logger.error(f"Error searching social media for {username}: {e}")
        return []

def extract_username(url, platform):
    """Extract username from URL using platform-specific patterns"""
    try:
        # Platform-specific patterns
        patterns = {
            'instagram': r'instagram\.com/([^/?#]+)',
            'twitter': r'twitter\.com/([^/?#]+)',
            'facebook': r'facebook\.com/([^/?#]+)',
            'tiktok': r'tiktok\.com/@([^/?#]+)',
            'youtube': r'youtube\.com/(?:channel/|user/|@)([^/?#]+)',
            'telegram': r'telegram\.org/([^/?#]+)',
            'onlyfans': r'onlyfans\.com/([^/?#]+)',
            'linktree': r'linktr\.ee/([^/?#]+)',
            'allmylinks': r'allmylinks\.com/([^/?#]+)'
        }
        
        if platform not in patterns:
            return None
            
        match = re.search(patterns[platform], url)
        return match.group(1) if match else None
    except Exception as e:
        logger.error(f"Error extracting username from {url}: {e}")
        return None

def save_results(results, filename):
    """Save results to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """Main function"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Search social media profiles for usernames')
    parser.add_argument('--limit', type=int, default=20, help='Number of usernames to process')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory for results')
    args = parser.parse_args()
    
    load_environment()
    
    try:
        usernames = get_supabase_usernames(limit=args.limit)
        if not usernames:
            logger.warning("No usernames found")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(args.output_dir or f"social_media_results_{timestamp}")
        output_dir.mkdir(exist_ok=True)
        
        all_results = {}
        
        for username_data in usernames:
            if not isinstance(username_data, dict) or 'username' not in username_data:
                continue
                
            username = username_data['username']
            logger.info(f"\nProcessing: {username}")
            
            # Add delay between username processing
            delay = random.uniform(3, 7)  # Random delay between 3-7 seconds
            logger.info(f"Waiting {delay:.1f} seconds before processing next username...")
            time.sleep(delay)
            
            results = search_social_media(username)
            
            # Save individual results
            output_file = output_dir / f"{username.replace(' ', '_')}.json"
            save_results(results, output_file)
            
            # Add to combined results
            all_results[username] = results
            
            # Log summary
            if results:
                logger.info("\nFound profiles:")
                for profile in sorted(results, key=lambda x: x['confidence'], reverse=True):
                    logger.info(f"{profile['platform']}: {profile['username']} (confidence: {profile['confidence']:.2f}, position: {profile['search_position']})")
            else:
                logger.info("\nNo profiles found")
        
        # Save combined results
        save_results(all_results, output_dir / "combined_results.json")
        
        # Log final summary
        logger.info("\nFinal summary:")
        for username, results in all_results.items():
            logger.info(f"\n{username}")
            if results:
                for profile in sorted(results, key=lambda x: x['confidence'], reverse=True):
                    logger.info(f"  {profile['platform']}: {profile['username']} (confidence: {profile['confidence']:.2f}, position: {profile['search_position']})")
            else:
                logger.info("  No profiles found")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
