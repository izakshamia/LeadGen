import requests
import json
from collections import defaultdict
from textblob import TextBlob
from datetime import datetime
import time
from typing import Dict, List

# Reddit API base URL
BASE_URL = "https://www.reddit.com"

# Headers for Reddit API requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_comments(author: str) -> List[Dict]:
    """Fetch comments for a specific Reddit user"""
    try:
        url = f"{BASE_URL}/user/{author}/comments.json"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['data']['children']
        return []
    except Exception as e:
        print(f"Error fetching comments for {author}: {str(e)}")
        return []

def analyze_comments(comments: List[Dict]) -> Dict:
    """Analyze comments for sentiment and topics"""
    if not comments:
        return {}
    
    subreddit_counts = defaultdict(int)
    sentiment_scores = []
    
    for comment in comments:
        try:
            # Extract subreddit
            subreddit = comment['data']['subreddit']
            subreddit_counts[subreddit] += 1
            
            # Analyze sentiment
            text = comment['data']['body']
            blob = TextBlob(text)
            sentiment_scores.append(blob.sentiment.polarity)
        except:
            continue
    
    # Calculate average sentiment
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    return {
        'total_comments': len(comments),
        'average_sentiment': avg_sentiment,
        'top_subreddits': dict(sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
        'activity_timestamp': datetime.now().isoformat()
    }

def analyze_all_users(users_data: List[Dict]) -> Dict:
    """Analyze comments for all users in the list"""
    results = {}
    
    for user in users_data:
        author = user['author']
        print(f"Analyzing {author}...")
        comments = fetch_comments(author)
        analysis = analyze_comments(comments)
        results[author] = analysis
        
        # Add a small delay to avoid hitting rate limits
        time.sleep(1)
    
    return results

def main():
    # Read users data from stdin
    users_data = json.loads(sys.stdin.read())
    
    # Validate input format
    if not isinstance(users_data, list):
        raise ValueError("Input must be a list of user objects")
    
    for user in users_data:
        if not isinstance(user, dict) or 'author' not in user:
            raise ValueError("Each user object must contain an 'author' field")

    print("Starting analysis for {} users...".format(len(users_data)))
    results = analyze_all_users(users_data)
    
    # Save results to JSON file
    with open('reddit_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save readable analysis to text file
    with open('reddit_analysis_results.txt', 'w') as f:
        f.write("Reddit Analysis Results\n")
        f.write("=" * 50 + "\n\n")
        
        # Write individual user results
        for user, result in results.items():
            f.write(f"Author: {user}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total Comments: {result.get('total_comments', 0)}\n")
            f.write(f"Average Sentiment: {result.get('avg_sentiment', 0):.2f}\n\n")
            
            f.write("Top Subreddits:\n")
            for subreddit, count in result.get('top_subreddits', {}).items():
                f.write(f"  {subreddit}: {count} comments\n")
            f.write("\n\n")
        
        # Write overall subreddit statistics
        f.write("Overall Subreddit Statistics\n")
        f.write("=" * 50 + "\n\n")
        
        all_subreddits = defaultdict(int)
        for user_result in results.values():
            for subreddit, count in user_result.get('top_subreddits', {}).items():
                all_subreddits[subreddit] += count
        
        sorted_subreddits = sorted(all_subreddits.items(), key=lambda x: x[1], reverse=True)
        for subreddit, count in sorted_subreddits:
            f.write(f"{subreddit}: {count} total comments\n")
    
    print("Analysis complete. Results saved to reddit_analysis_results.json and reddit_analysis_results.txt")
    
    print("\nTop subreddits across all users:")
    for subreddit, count in sorted(all_subreddits.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{subreddit}: {count} comments")

if __name__ == "__main__":
    main()
