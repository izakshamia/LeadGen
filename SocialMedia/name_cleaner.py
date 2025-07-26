import logging
from typing import List, Optional

# Set up logging
logger = logging.getLogger(__name__)

class NameCleaner:
    """
    Utility class for cleaning and processing names
    """
    
    def __init__(self):
        self.unwanted_keywords = {
            # Adult content keywords
            'bod', 'girls', 'playboy', 'playmate', 'taboo', 'mix', 'virtual',
            'amp', 'ddf', 'desire', 'rendezvous', 'av', 'idol', 'napoli', 'xl',
            'femjoy', 'trouble', 'cel', 's', 'in', 'up', 'here', 'comes',
            'buggy', 'sexy', 'fields', 'videos', 'photo', 'porn', 'content',
            'club',
            
            # Body parts and adult content
            'model', 'porn', 'nude', 'sex', 'hot', 'sexy', 'girly', 'bikini',
            'lingerie', 'tits', 'ass', 'pussy', 'cum', 'cock', 'dick', 'fuck',
            'pornhub', 'xvideos', 'xxx', 'anal', 'oral', 'blowjob', 'cumshot',
            'orgasm', 'dildo', 'toy', 'masturbate'
        }

    def is_valid_name_part(self, word: str) -> bool:
        """Check if a word looks like a valid name part"""
        # Check if word is alphabetic and not in unwanted keywords
        return word.isalpha() and word not in self.unwanted_keywords

    def clean_name(self, name: str) -> Optional[str]:
        """
        Clean a name by removing unwanted keywords and extracting proper names
        
        Args:
            name: The raw name string to clean
            
        Returns:
            Cleaned name string or None if no valid name could be extracted
        """
        if not name:
            return None
            
        # Convert to lowercase and split into words
        words = name.lower().split()
        
        # Filter out unwanted keywords
        valid_words = [word for word in words if word not in self.unwanted_keywords]
        
        # Take first two valid words if available
        if len(valid_words) >= 2:
            # Capitalize properly and return
            return f"{valid_words[0].capitalize()} {valid_words[1].capitalize()}"
        elif valid_words:
            # Capitalize and return single name if only one valid word
            return valid_words[0].capitalize()
            
        return None

    def clean_names(self, names: List[str]) -> List[str]:
        """
        Clean a list of names
        
        Args:
            names: List of raw name strings to clean
            
        Returns:
            List of cleaned names
        """
        cleaned_names = []
        for name in names:
            cleaned = self.clean_name(name)
            if cleaned:
                cleaned_names.append(cleaned)
        return cleaned_names

# Create a singleton instance
def get_name_cleaner() -> NameCleaner:
    """Get the singleton instance of NameCleaner"""
    if not hasattr(get_name_cleaner, "instance"):
        get_name_cleaner.instance = NameCleaner()
    return get_name_cleaner.instance
