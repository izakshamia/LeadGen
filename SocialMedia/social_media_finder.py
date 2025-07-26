import logging
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import os
import time
from name_cleaner import get_name_cleaner

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleFinder:
    """
    Google search implementation using Google Custom Search API
    """
    
    def __init__(self):
        self.name_cleaner = get_name_cleaner()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.cse_id = os.getenv('GOOGLE_CSE_ID')
        self._last_search_time = 0
        self._min_search_interval = 1  # seconds
        
        if not self.api_key or not self.cse_id:
            logger.warning("Google API credentials not found. Results may be limited.")
            
    def _rate_limit(self):
        """Simple rate limiting to avoid API quota issues"""
        current_time = time.time()
        time_since_last = current_time - self._last_search_time
        if time_since_last < self._min_search_interval:
            time.sleep(self._min_search_interval - time_since_last)
        self._last_search_time = time.time()
        
    def _build_variations(self, name: str) -> List[str]:
        """
        Generate search query variations to improve results
        """
        variations = []
        clean_name = self.name_cleaner.clean_name(name)
        if not clean_name:
            return variations
            
        # Add basic name
        variations.append(clean_name)
        
        # Add common social media platforms
        platforms = ['instagram', 'tiktok', 'linkedin', 'twitter']
        for platform in platforms:
            variations.append(f"{clean_name} site:{platform}.com")
            variations.append(f"{clean_name} {platform}")
            
        # Add common profile indicators
        indicators = ['profile', 'about', 'bio']
        for indicator in indicators:
            variations.append(f"{clean_name} {indicator}")
            
        return variations[:3]  # Limit to top 3 variations to stay within free quota
        
    def _parse_result(self, item: dict) -> dict:
        """
        Parse and enrich a single search result
        """
        return {
            'url': item.get('link', ''),
            'title': item.get('title', ''),
            'snippet': item.get('snippet', ''),
            'platform': self._detect_platform(item.get('link', '')),
            'position': item.get('rank', 0)
        }
        
    def _detect_platform(self, url: str) -> str:
        """
        Detect social media platform from URL
        """
        if not url:
            return ''
            
        url = url.lower()
        if 'instagram' in url:
            return 'Instagram'
        elif 'tiktok' in url:
            return 'TikTok'
        elif 'linkedin' in url:
            return 'LinkedIn'
        elif 'twitter' in url:
            return 'Twitter'
        return ''
        
    def find_urls(self, name: str, num_results: int = 5) -> List[Dict]:
        """
        Find URLs for a given name using Google Custom Search API
        """
        if not name:
            return []
            
        try:
            # Generate query variations
            variations = self._build_variations(name)
            if not variations:
                return []
                
            logger.info(f"Searching Google with {len(variations)} variations")
            
            service = build("customsearch", "v1", developerKey=self.api_key)
            all_results = []
            
            # Try each variation
            for query in variations:
                self._rate_limit()  # Apply rate limiting
                logger.info(f"Searching Google: {query}")
                
                result = service.cse().list(
                    q=query,
                    cx=self.cse_id,
                    num=num_results,
                    safe='medium'
                ).execute()
                
                if 'items' in result:
                    parsed_results = [self._parse_result(item) for item in result['items']]
                    all_results.extend(parsed_results)
                    
            # Sort results by platform and position
            all_results.sort(key=lambda x: (x['platform'] != '', x['position']))
            
            logger.info(f"Found {len(all_results)} URLs")
            return all_results[:num_results]  # Return top results
            
        except Exception as e:
            logger.error(f"Error searching Google: {str(e)}")
            return []

# Usage example
def main():
    finder = GoogleFinder()
    name = "aria giovanni"  # Example name
    results = finder.find_urls(name)
    print(f"\nSocial media profiles found for {name}:")
    for result in results:
        print(f"- {result['url']} ({result['platform']})")

if __name__ == "__main__":
    main()
