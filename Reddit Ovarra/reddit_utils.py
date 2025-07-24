import requests
from collections import defaultdict
from textblob import TextBlob

BASE_URL = "https://www.reddit.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_comments(author: str):
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

def analyze_comments(comments):
    """Analyze comments for sentiment and topics"""
    if not comments:
        return {}
    subreddit_counts = defaultdict(int)
    sentiment_scores = []
    for comment in comments:
        data = comment.get('data', {})
        subreddit = data.get('subreddit')
        body = data.get('body', '')
        if subreddit:
            subreddit_counts[subreddit] += 1
        if body:
            sentiment = TextBlob(body).sentiment.polarity
            sentiment_scores.append(sentiment)
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    return {
        'total_comments': len(comments),
        'average_sentiment': avg_sentiment,
        'top_subreddits': dict(sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True))
    }
