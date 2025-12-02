"""
Redditor profile fetcher service.
Fetches real profile data from Reddit API for extracted redditors.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional, List
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_social_links(username: str) -> List[Dict]:
    """
    Fetch social links from Reddit profile page by scraping HTML.
    
    Args:
        username: Reddit username
        
    Returns:
        List of social link dictionaries with 'platform' and 'url' keys
    """
    try:
        from bs4 import BeautifulSoup
        import re
        
        url = f"https://www.reddit.com/user/{username}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch profile page for u/{username}: HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # New Method: Use the user-provided CSS selector to find the social links container
        social_links_container = soup.select_one('#right-sidebar-contents > aside.mt-md.rounded-4.bg-neutral-background-weak > faceplate-tracker > div > div.mb-sm')
        
        links_to_process = []
        if social_links_container:
            logger.info(f"Found social links container for u/{username}")
            links_to_process = social_links_container.find_all('a', href=True)
        else:
            logger.info(f"Could not find social links container for u/{username}, falling back to page-wide search.")
            # Fallback Method: Find all links in the page
            links_to_process = soup.find_all('a', href=True)

        social_links = []
        found_urls = set()

        for link in links_to_process:
            href = link.get('href', '')
            if href:
                found_urls.add(href)
        
        # Method 2: Also search in the raw HTML for URLs that might not be in <a> tags
        html_text = response.text
        
        # Define social media patterns
        patterns = {
            'instagram': [
                r'instagram\.com/([a-zA-Z0-9._]+)',
                r'instagr\.am/([a-zA-Z0-9._]+)'
            ],
            'twitter': [
                r'twitter\.com/([a-zA-Z0-9_]+)',
                r'x\.com/([a-zA-Z0-9_]+)'
            ],
            'onlyfans': [
                r'onlyfans\.com/([a-zA-Z0-9_]+)'
            ],
            'tiktok': [
                r'tiktok\.com/@([a-zA-Z0-9._]+)',
                r'tiktok\.com/([a-zA-Z0-9._]+)'
            ],
            'youtube': [
                r'youtube\.com/(@?[a-zA-Z0-9_]+)',
                r'youtu\.be/([a-zA-Z0-9_-]+)'
            ],
            'twitch': [
                r'twitch\.tv/([a-zA-Z0-9_]+)'
            ],
            'linktree': [
                r'linktr\.ee/([a-zA-Z0-9_]+)'
            ],
            'snapchat': [
                r'snapchat\.com/add/([a-zA-Z0-9._]+)'
            ]
        }
        
        found_urls = set()
        
        # Search in <a> tags
        for link in all_links:
            href = link.get('href', '')
            if href:
                found_urls.add(href)
        
        # Search in raw HTML with regex
        for platform, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, html_text, re.IGNORECASE)
                for match in matches:
                    # Reconstruct full URL
                    if platform == 'instagram':
                        found_urls.add(f'https://instagram.com/{match}')
                    elif platform == 'twitter':
                        found_urls.add(f'https://twitter.com/{match}')
                    elif platform == 'onlyfans':
                        found_urls.add(f'https://onlyfans.com/{match}')
                    elif platform == 'tiktok':
                        found_urls.add(f'https://tiktok.com/@{match}')
                    elif platform == 'youtube':
                        found_urls.add(f'https://youtube.com/{match}')
                    elif platform == 'twitch':
                        found_urls.add(f'https://twitch.tv/{match}')
                    elif platform == 'linktree':
                        found_urls.add(f'https://linktr.ee/{match}')
                    elif platform == 'snapchat':
                        found_urls.add(f'https://snapchat.com/add/{match}')
        
        # Categorize found URLs
        for url_str in found_urls:
            url_lower = url_str.lower()
            
            # Skip Reddit's own links
            if 'reddit.com' in url_lower or 'redd.it' in url_lower:
                continue
            
            # Categorize by platform
            if 'instagram.com' in url_lower or 'instagr.am' in url_lower:
                social_links.append({'platform': 'instagram', 'url': url_str})
            elif 'twitter.com' in url_lower or 'x.com' in url_lower:
                social_links.append({'platform': 'twitter', 'url': url_str})
            elif 'onlyfans.com' in url_lower:
                social_links.append({'platform': 'onlyfans', 'url': url_str})
            elif 'tiktok.com' in url_lower:
                social_links.append({'platform': 'tiktok', 'url': url_str})
            elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                social_links.append({'platform': 'youtube', 'url': url_str})
            elif 'twitch.tv' in url_lower:
                social_links.append({'platform': 'twitch', 'url': url_str})
            elif 'linktr.ee' in url_lower:
                social_links.append({'platform': 'linktree', 'url': url_str})
            elif 'snapchat.com' in url_lower:
                social_links.append({'platform': 'snapchat', 'url': url_str})
        
        # Remove duplicates
        seen = set()
        unique_links = []
        for link in social_links:
            key = (link['platform'], link['url'].lower())
            if key not in seen:
                seen.add(key)
                unique_links.append(link)
        
        if unique_links:
            logger.info(f"Found {len(unique_links)} social links for u/{username}: {[l['platform'] for l in unique_links]}")
        else:
            logger.info(f"No social links found for u/{username}")
        
        return unique_links
        
    except Exception as e:
        logger.error(f"Error fetching social links for u/{username}: {e}")
        return []


def fetch_redditor_profile(username: str) -> Optional[Dict]:
    """
    Fetch redditor profile data from Reddit API.
    
    Uses Reddit's public JSON API (no authentication required).
    
    Args:
        username: Reddit username to fetch
        
    Returns:
        Dictionary with profile data if successful, None otherwise
    """
    try:
        # Reddit's public JSON API endpoint
        url = f"https://www.reddit.com/user/{username}/about.json"
        
        # Set user agent (Reddit requires this)
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RedditOvarraBot/1.0)'
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract user data
            user_data = data.get('data', {})
            
            # Calculate account age in days
            created_utc = user_data.get('created_utc', 0)
            if created_utc:
                created_date = datetime.fromtimestamp(created_utc)
                account_age_days = (datetime.utcnow() - created_date).days
            else:
                account_age_days = 0
            
            # Fetch social links (optional, may be slow)
            social_links = fetch_social_links(username)
            
            # Try to get social links from subreddit data (user profile subreddit)
            subreddit_data = user_data.get('subreddit', {})
            
            # Check for social links in various places in the API response
            api_social_links = []
            
            # Some users have social links in their subreddit public_description
            public_desc = subreddit_data.get('public_description', '')
            if public_desc:
                # Extract URLs from description
                import re
                url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?'
                found_urls = re.findall(url_pattern, public_desc)
                for url_match in found_urls:
                    full_url = f"https://{url_match}" if not url_match.startswith('http') else url_match
                    # Categorize
                    if 'instagram.com' in url_match or 'instagr.am' in url_match:
                        api_social_links.append({'platform': 'instagram', 'url': full_url})
                    elif 'twitter.com' in url_match or 'x.com' in url_match:
                        api_social_links.append({'platform': 'twitter', 'url': full_url})
                    elif 'onlyfans.com' in url_match:
                        api_social_links.append({'platform': 'onlyfans', 'url': full_url})
                    elif 'tiktok.com' in url_match:
                        api_social_links.append({'platform': 'tiktok', 'url': full_url})
            
            # Combine API links with scraped links
            all_social_links = api_social_links + social_links
            
            # Remove duplicates
            seen = set()
            unique_social_links = []
            for link in all_social_links:
                key = (link['platform'], link['url'].lower())
                if key not in seen:
                    seen.add(key)
                    unique_social_links.append(link)
            
            profile = {
                'username': user_data.get('name', username),
                'total_karma': user_data.get('total_karma', 0),
                'link_karma': user_data.get('link_karma', 0),  # post karma
                'comment_karma': user_data.get('awardee_karma', 0) + user_data.get('awarder_karma', 0) + user_data.get('comment_karma', 0),
                'post_karma': user_data.get('link_karma', 0),
                'account_age_days': account_age_days,
                'created_utc': created_utc,
                'is_gold': user_data.get('is_gold', False),
                'is_mod': user_data.get('is_mod', False),
                'verified': user_data.get('verified', False),
                'has_verified_email': user_data.get('has_verified_email', False),
                'icon_img': user_data.get('icon_img', ''),
                'subreddit': user_data.get('subreddit', {}),
                'social_links': unique_social_links
            }
            
            logger.info(f"Successfully fetched profile for u/{username} with {len(social_links)} social links")
            return profile
            
        elif response.status_code == 404:
            logger.warning(f"User not found: u/{username}")
            return None
        elif response.status_code == 429:
            logger.warning(f"Rate limited when fetching u/{username}")
            return None
        else:
            logger.error(f"Error fetching u/{username}: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching profile for u/{username}")
        return None
    except Exception as e:
        logger.error(f"Error fetching profile for u/{username}: {e}")
        return None


def update_redditor_with_profile_data(username: str, profile_data: Dict) -> bool:
    """
    Update redditor in database with fetched profile data.
    
    Args:
        username: Reddit username
        profile_data: Profile data from fetch_redditor_profile()
        
    Returns:
        True if update successful, False otherwise
    """
    try:
        from services.supabase_client import init_supabase_client
        
        client = init_supabase_client()
        
        # Convert social links to JSON format for storage
        social_links = profile_data.get('social_links', [])
        social_links_json = {link['platform']: link['url'] for link in social_links}
        
        update_data = {
            'total_karma': profile_data.get('total_karma', 0),
            'comment_karma': profile_data.get('comment_karma', 0),
            'post_karma': profile_data.get('post_karma', 0),
            'account_age_days': profile_data.get('account_age_days', 0),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Only add social_links if the column exists (it may not in current schema)
        if social_links_json:
            update_data['social_links'] = social_links_json
        
        response = client.table('target_redditors') \
            .update(update_data) \
            .eq('username', username) \
            .execute()
        
        if response.data:
            logger.info(f"Updated profile data for u/{username} with {len(social_links)} social links")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error updating profile data for u/{username}: {e}")
        return False


def fetch_and_update_redditor_profiles(usernames: List[str], delay: float = 2.0) -> Dict:
    """
    Fetch and update profile data for multiple redditors.
    
    Includes rate limiting to avoid hitting Reddit's API limits.
    
    Args:
        usernames: List of Reddit usernames to fetch
        delay: Delay in seconds between requests (default: 2.0)
        
    Returns:
        Dictionary with success/failure counts
    """
    results = {
        'total': len(usernames),
        'success': 0,
        'failed': 0,
        'not_found': 0
    }
    
    logger.info(f"Starting profile fetch for {len(usernames)} redditors")
    
    for idx, username in enumerate(usernames, 1):
        logger.info(f"Fetching profile {idx}/{len(usernames)}: u/{username}")
        
        # Fetch profile data
        profile_data = fetch_redditor_profile(username)
        
        if profile_data:
            # Update database
            if update_redditor_with_profile_data(username, profile_data):
                results['success'] += 1
            else:
                results['failed'] += 1
        else:
            results['not_found'] += 1
        
        # Rate limiting - wait between requests
        if idx < len(usernames):
            time.sleep(delay)
    
    logger.info(f"Profile fetch complete: {results}")
    return results


def fetch_profiles_for_new_redditors() -> Dict:
    """
    Fetch profiles for redditors that don't have profile data yet.
    
    Finds redditors with account_age_days = 0 or total_karma = 0
    and fetches their real profile data.
    
    Returns:
        Dictionary with fetch results
    """
    try:
        from services.supabase_client import init_supabase_client
        
        client = init_supabase_client()
        
        # Find redditors without profile data
        response = client.table('target_redditors') \
            .select('username') \
            .or_('account_age_days.eq.0,total_karma.eq.0') \
            .limit(50) \
            .execute()
        
        if not response.data:
            logger.info("No redditors need profile updates")
            return {'total': 0, 'success': 0, 'failed': 0, 'not_found': 0}
        
        usernames = [r['username'] for r in response.data]
        logger.info(f"Found {len(usernames)} redditors needing profile updates")
        
        # Fetch and update profiles
        return fetch_and_update_redditor_profiles(usernames)
        
    except Exception as e:
        logger.error(f"Error in fetch_profiles_for_new_redditors: {e}")
        return {'total': 0, 'success': 0, 'failed': 0, 'not_found': 0, 'error': str(e)}
