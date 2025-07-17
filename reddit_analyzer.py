import requests
import json
from collections import defaultdict
from textblob import TextBlob
from datetime import datetime, timedelta
import time
import argparse
import logging
import openai
import os
from dotenv import load_dotenv
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reddit_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not found. Please set it in your .env file.")
openai.api_key = OPENAI_API_KEY

# Reddit API base URL
BASE_URL = "https://www.reddit.com"

# Headers for Reddit API requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_reddit_posts(subreddit: str, keyword: str, limit: int = 100) -> List[Dict]:
    """Fetch posts from Reddit containing the specified keyword"""
    try:
        url = f"{BASE_URL}/r/{subreddit}/search.json"
        params = {
            'q': keyword,
            'sort': 'relevance',
            'limit': limit
        }
        
        logger.info(f"Fetching posts for subreddit: {subreddit}, keyword: {keyword}")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data['data']['children']
            logger.info(f"Found {len(posts)} posts containing keyword '{keyword}'")
            return posts
        else:
            logger.error(f"Failed to fetch posts: Status code {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        return []

def fetch_comments(author: str) -> List[Dict]:
    """Fetch comments for a specific Reddit user"""
    try:
        url = f"{BASE_URL}/user/{author}/comments.json"
        logger.info(f"Fetching comments for user: {author}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            comments = data['data']['children']
            logger.info(f"Found {len(comments)} comments for user {author}")
            return comments
        else:
            logger.error(f"Failed to fetch comments for {author}: Status code {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching comments for {author}: {str(e)}")
        return []

def analyze_post_content(posts: List[Dict], client) -> Dict:
    """Analyze post content using OpenAI to extract insights"""
    if not posts:
        return {}
    
    try:
        # Extract top posts content
        post_content = []
        for post in posts[:5]:  # Analyze top 5 posts
            title = post['data']['title']
            selftext = post['data']['selftext']
            if selftext:
                post_content.append(f"Title: {title}\nContent: {selftext}")

        if not post_content:
            return {}

        # Combine content for analysis
        combined_content = "\n\n".join(post_content[:5])  # Limit to top 5 posts
        
        # Define the analysis prompt
        prompt = f"""Analyze the following Reddit posts and extract:
1. User intent
2. Top questions asked
3. Main topics discussed
4. Pain points mentioned

Posts:
{combined_content}

Please provide your analysis in JSON format with the following structure:
{{
    "user_intent": "Description of user intent",
    "top_questions": ["Question 1", "Question 2", "Question 3"],
    "main_topics": ["Topic 1", "Topic 2", "Topic 3"],
    "pain_points": ["Pain point 1", "Pain point 2", "Pain point 3"]
}}

Analysis:"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert analyst who can extract meaningful insights from text data. Please respond in JSON format as requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Get the response content
            response_content = response.choices[0].message.content
            
            # First try to parse as JSON
            try:
                json_response = json.loads(response_content)
                return {
                    'user_intent': json_response.get('user_intent', ''),
                    'top_questions': json_response.get('top_questions', []),
                    'main_topics': json_response.get('main_topics', []),
                    'pain_points': json_response.get('pain_points', [])
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract the JSON-like content
                try:
                    # Extract JSON-like content between curly braces
                    start_idx = response_content.find('{')
                    end_idx = response_content.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_content[start_idx:end_idx]
                        json_response = json.loads(json_str)
                        return {
                            'user_intent': json_response.get('user_intent', ''),
                            'top_questions': json_response.get('top_questions', []),
                            'main_topics': json_response.get('main_topics', []),
                            'pain_points': json_response.get('pain_points', [])
                        }
                except Exception as e:
                    logger.error(f"Error parsing OpenAI response: {str(e)}")
                    logger.error(f"Raw response: {response_content}")
                    return {}
        except Exception as e:
            logger.error(f"Error processing OpenAI response: {str(e)}")
            return {}
    except Exception as e:
        logger.error(f"Error analyzing post content: {str(e)}")
        return {}

def analyze_comments(comments: List[Dict]) -> Dict:
    """Analyze comments for sentiment and topics"""
    if not comments:
        logger.info("No comments to analyze")
        return {}
    
    # Filter comments from the last 365 days
    one_year_ago = datetime.now() - timedelta(days=365)
    recent_comments = []
    
    for comment in comments:
        try:
            created_utc = datetime.fromtimestamp(comment['data']['created_utc'])
            if created_utc >= one_year_ago:
                recent_comments.append(comment)
        except Exception as e:
            logger.error(f"Error processing comment timestamp: {str(e)}")
            continue
    
    if not recent_comments:
        logger.info("No recent comments found in the last 365 days")
        return {}
    
    logger.info(f"Analyzing {len(recent_comments)} recent comments from the last 365 days")
    
    subreddit_counts = defaultdict(int)
    sentiment_scores = []
    
    for comment in recent_comments:
        try:
            subreddit = comment['data']['subreddit']
            subreddit_counts[subreddit] += 1
            
            text = comment['data']['body']
            blob = TextBlob(text)
            sentiment_scores.append(blob.sentiment.polarity)
        except Exception as e:
            logger.error(f"Error processing comment: {str(e)}")
            continue
    
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    logger.info(f"Analysis complete - Average sentiment: {avg_sentiment:.2f}")
    
    return {
        'total_comments': len(recent_comments),
        'average_sentiment': avg_sentiment,
        'top_subreddits': dict(sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
        'activity_timestamp': datetime.now().isoformat()
    }

def main():
    parser = argparse.ArgumentParser(description='Reddit Comments Analyzer')
    parser.add_argument('--subreddit', default='CamGirlProblems', help='Subreddit to search in')
    parser.add_argument('--keywords', nargs='+', default=['DMCA', 'Leak'], help='Keywords to search for')
    parser.add_argument('--limit', type=int, default=3, help='Number of posts to fetch')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Load environment variables
    load_dotenv()

    # API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not found. Please set it in your .env file.")
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    # Reddit API base URL
    BASE_URL = "https://www.reddit.com"

    # Combine results from all keywords
    all_authors = set()
    all_posts = []
    test_authors = set()  # For testing, we'll use a fixed set of authors
    
    # For testing, use a fixed set of keywords and limit to 3 posts per keyword
    test_keywords = ['DMCA']  # Only test with one keyword
    test_limit = 3
    
    for keyword in test_keywords:
        posts = fetch_reddit_posts(args.subreddit, keyword, test_limit)
        all_posts.extend(posts[:test_limit])  # Store only up to test_limit posts
        for post in posts:
            author = post['data']['author']
            if author:  # Skip deleted users
                test_authors.add(author)

    logger.info(f"\nFound {len(test_authors)} unique authors to analyze")
    logger.info(f"Found {len(all_posts)} posts to analyze")

    # Analyze post content first
    post_analysis = analyze_post_content(all_posts, client)
    logger.info("\nPost Content Analysis:")
    for key, value in post_analysis.items():
        logger.info(f"\n{key.replace('_', ' ').title()}")
        logger.info(value)

    # Save post analysis to file
    with open('post_analysis.json', 'w') as f:
        json.dump(post_analysis, f, indent=2)
    logger.info("Saved post analysis to post_analysis.json")
    logger.info(f"Post limit: {test_limit}")

    # Combine results from all keywords
    all_authors = test_authors
    for keyword in args.keywords:
        posts = fetch_reddit_posts(args.subreddit, keyword, args.limit)
        for post in posts:
            author = post['data']['author']
            if author:  # Skip deleted users
                all_authors.add(author)

    logger.info(f"\nFound {len(all_authors)} unique authors to analyze")
    
    results = {}
    for author in all_authors:
        logger.info(f"\nAnalyzing {author}...")
        comments = fetch_comments(author)
        analysis = analyze_comments(comments)
        results[author] = analysis
        time.sleep(1)  # Avoid rate limiting

    # Print results
    logger.info("\nAnalysis Results:")
    for author, result in results.items():
        logger.info(f"\nAuthor: {author}")
        
        # Handle empty results gracefully
        if not result:
            logger.info("No data available for this author")
            continue
            
        logger.info(f"Total Comments: {result.get('total_comments', 0)}")
        logger.info(f"Average Sentiment: {result.get('average_sentiment', 0):.2f}")
        logger.info("Top Subreddits:")
        for subreddit, count in result.get('top_subreddits', {}).items():
            logger.info(f"  {subreddit}: {count} comments")

    # Save results to file
    try:
        # Save main analysis results
        with open('reddit_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        logger.info("Saved results to reddit_analysis_results.json")

        # Save unique authors
        unique_authors = sorted(all_authors)
        with open('unique_authors.txt', 'w') as f:
            for author in unique_authors:
                f.write(f"{author}\n")
        logger.info(f"Saved {len(unique_authors)} unique authors to unique_authors.txt")

        # Save unique subreddits from all results
        all_subreddits = set()
        for result in results.values():
            if result:  # Skip empty results
                all_subreddits.update(result.get('top_subreddits', {}).keys())
        
        unique_subreddits = sorted(all_subreddits)
        with open('unique_subreddits.txt', 'w') as f:
            for subreddit in unique_subreddits:
                f.write(f"{subreddit}\n")
        logger.info(f"Saved {len(unique_subreddits)} unique subreddits to unique_subreddits.txt")

    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    main()
