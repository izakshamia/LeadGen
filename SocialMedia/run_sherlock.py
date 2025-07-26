import subprocess
from name_cleaner import get_name_cleaner
import logging
import os
import time
from typing import List, Dict, Optional
import requests
from urllib3.exceptions import InsecureRequestWarning

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sherlock_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
SHERLOCK_TIMEOUT = 300  # 5 minutes
SHERLOCK_FLAGS = [
    '--print-found',
    '--timeout', '10',
    '--print-all',
    '--nsfw'
]

# URL separators to try in Sherlock output
URL_SEPARATORS = [": ", " : ", " :", ":", " - "]

def generate_username_variations(cleaned_name: str) -> List[str]:
    """Generate different variations of a cleaned username."""
    return [
        cleaned_name.replace(' ', '_'),
        cleaned_name.replace(' ', '.'),
        cleaned_name.replace(' ', '-'),
        cleaned_name.lower(),
        cleaned_name.lower().replace(' ', '')
    ]

def read_social_media_sites() -> List[str]:
    """Read supported social media sites from configuration file."""
    try:
        sites = []
        with open('sherlock_sites.txt', 'r') as f:
            for line in f:
                site = line.strip()
                if site and not site.startswith('#'):
                    # Remove any special characters and spaces
                    site = ''.join(c for c in site if c.isalnum() or c in ['.', '-'])
                    site = site.lower()
                    sites.append(site)
        logger.info(f"Loaded {len(sites)} supported sites: {sites}")
        return sites
    except Exception as e:
        logger.error(f"Error reading sites file: {str(e)}")
        return []

def build_sherlock_command(usernames: List[str], sites: List[str]) -> List[str]:
    """
    Build the Sherlock command with specified usernames and sites.
    
    Args:
        usernames: List of usernames to search
        sites: List of sites to search
        
    Returns:
        List of command parts
    """
    cmd = ['sherlock'] + SHERLOCK_FLAGS
    cmd.extend(usernames)
    for site in sites:
        cmd.extend(['--site', f'"{site}"'])
    logger.debug(f"Sherlock command: {' '.join(cmd)}")
    return cmd

def run_sherlock_command(cmd: List[str]) -> subprocess.CompletedProcess:
    """
    Run Sherlock command and capture output.
    
    Args:
        cmd: List of command parts
        
    Returns:
        CompletedProcess object
    """
    try:
        logger.debug(f"Running Sherlock command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        logger.debug(f"Sherlock command completed with return code: {result.returncode}")
        logger.debug(f"Sherlock stdout:")
        logger.debug(result.stdout)
        logger.error(f"Sherlock stderr:")
        logger.error(result.stderr)
        return result
    except subprocess.TimeoutExpired:
        logger.error("Sherlock command timed out")
        return subprocess.CompletedProcess(cmd, 1, stdout='', stderr='')
    except Exception as e:
        logger.error(f"Error running Sherlock: {str(e)}")
        return subprocess.CompletedProcess(cmd, 1, stdout='', stderr=str(e))

def validate_url(url: str) -> bool:
    """
    Validate if a URL exists and is accessible by sending a HEAD request.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid and accessible, False otherwise
    """
    try:
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        # Send HEAD request with timeout
        try:
            response = requests.head(
                url,
                timeout=10,  # Increased timeout
                verify=False,  # Disable SSL verification
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0'}  # Add user agent
            )
            
            # Consider more status codes as valid
            # 200-299: Success
            # 300-399: Redirects
            # 400-499: Client errors (some sites return 404 for non-existent users)
            status_code = response.status_code
            
            # Log the status code for debugging
            logger.debug(f"URL: {url} - Status: {status_code}")
            
            if status_code < 300:  # Success
                logger.info(f"Validated URL (Success): {url}")
                return True
            elif 300 <= status_code < 400:  # Redirect
                logger.info(f"Validated URL (Redirect): {url} -> {response.url}")
                return True
            elif 400 <= status_code < 500:  # Client error
                # Some sites return 404 for non-existent users, so we'll check the content
                try:
                    # Try a GET request to see if it's a profile page
                    response = requests.get(
                        url,
                        timeout=10,
                        verify=False,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    
                    # Check for common profile indicators
                    if any(keyword in response.text.lower() for keyword in ['profile', 'user', 'member']):
                        logger.info(f"Validated URL (Profile): {url} - Status: {response.status_code}")
                        return True
                    else:
                        logger.debug(f"Invalid URL (Not a profile): {url} - Status: {response.status_code}")
                        return False
                except:
                    logger.debug(f"Invalid URL (GET failed): {url}")
                    return False
            else:  # Server error
                logger.debug(f"Invalid URL (Server error): {url} - Status: {status_code}")
                return False
                
        except requests.exceptions.SSLError:
            logger.debug(f"SSL error for URL: {url}")
            return True  # Accept SSL errors
            
        except requests.exceptions.Timeout:
            logger.debug(f"Timeout for URL: {url}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Request error for URL: {url} - Error: {str(e)}")
            return False
            
    except Exception as e:
        logger.debug(f"Could not validate URL {url}: {str(e)}")
        return False

def parse_sherlock_output(stdout: str) -> List[str]:
    """Parse Sherlock output to extract URLs."""
    urls = []
    found_section = False
    
    try:
        for line in stdout.splitlines():
            line = line.strip()
            logger.debug(f"Processing line: {line}")
            
            if line.startswith("[*] Search completed"):
                logger.info("End of search results detected")
                break
                
            if found_section:
                if line.startswith("[+] "):
                    try:
                        # Extract URL from lines like: [+] Instagram: https://instagram.com/username
                        # Try different separators
                        for sep in URL_SEPARATORS:
                            parts = line.split(sep, 1)
                            if len(parts) == 2:
                                url = parts[1].strip()
                                # Remove URL encoding of spaces (%20)
                                url = url.replace('%20', ' ')
                                # Remove any trailing punctuation
                                url = url.rstrip('.,!')
                                
                                # Validate URL before adding
                                if validate_url(url):
                                    urls.append(url)
                                    logger.info(f"Validated URL: {url}")
                                else:
                                    logger.debug(f"Invalid URL: {url}")
                                break
                    except Exception as e:
                        logger.error(f"Error parsing line: {line}")
                        continue
            
            if line.startswith("[*] Found"):
                found_section = True
                logger.info("Found section detected")
        
        # Remove duplicates and limit to first 5 results
        urls = list(dict.fromkeys(urls))[:5]
        logger.info(f"Total unique validated URLs found: {len(urls)}")
        return urls
    except Exception as e:
        logger.error(f"Error parsing output: {str(e)}")
        return []

def write_output_file(cleaned_name: str, cmd: List[str], validated_urls: List[str]) -> None:
    """Write validated URLs to a file."""
    try:
        output_file = f"sherlock_results_{cleaned_name.replace(' ', '_')}.txt"
        output_path = os.path.join(os.getcwd(), output_file)
        logger.debug(f"Output file path: {output_path}")
        
        # Write only the validated URLs
        with open(output_path, 'w') as f:
            for url in validated_urls:
                f.write(f"{url}\n")
        
        logger.info(f"Wrote {len(validated_urls)} validated URLs to {output_path}")
    except Exception as e:
        logger.error(f"Error writing output file: {str(e)}")

def run_sherlock(original_username: str) -> Dict[str, List[str]]:
    """
    Run Sherlock with cleaned name variations and return validated social media URLs
    
    Args:
        original_username: The original username to search for
        
    Returns:
        Dictionary containing:
        - input: Original username
        - cleaned_name: Cleaned version of the name
        - found_urls: List of validated social media URLs
    """
    try:
        logger.info(f"Starting search for username: {original_username}")
        
        # Get the name cleaner singleton
        name_cleaner = get_name_cleaner()
        logger.debug("Name cleaner initialized")
        
        # Clean the name and generate variations
        cleaned = name_cleaner.clean_name(original_username)
        if not cleaned:
            logger.warning(f"Could not clean name: {original_username}")
            return {
                "input": original_username,
                "cleaned_name": "",
                "found_urls": []
            }
        
        # Generate username variations
        usernames = generate_username_variations(cleaned)
        logger.info(f"Generated username variations: {usernames}")
        
        # Read supported social media sites
        sites = read_social_media_sites()
        
        # Build and run Sherlock command
        cmd = build_sherlock_command(usernames, sites)
        result = run_sherlock_command(cmd)
        
        # Parse output and get validated URLs
        urls = parse_sherlock_output(result.stdout)
        
        # Write output file with validated URLs
        write_output_file(cleaned, cmd, urls)
        
        return {
            "input": original_username,
            "cleaned_name": cleaned,
            "found_urls": urls
        }
    except Exception as e:
        logger.error(f"Error running Sherlock: {str(e)}", exc_info=True)
        return {
            "input": original_username,
            "cleaned_name": "",
            "found_urls": []
        }

def main():
    """
    Test the Sherlock integration with sample names
    """
    logger.info("Starting test run")
    test_names = [
        "Sophie Rain",
    
    ]
    
    for name in test_names:
        logger.info(f"\nProcessing: {name}")
        result = run_sherlock(name)
        print(f"Cleaned name: {result['cleaned_name']}")
        print("Found URLs:")
        for url in result['found_urls']:
            print(f"- {url}")
    
    logger.info("Test run completed")

if __name__ == "__main__":
    main()
