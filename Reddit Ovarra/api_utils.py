import os
import json
import time
import requests
import google.generativeai as genai
from typing import List, Dict, Any, Set
from dataclasses import asdict
from dotenv import load_dotenv
from textblob import TextBlob
from models import RedditPost, RedditComment

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Reddit API constants
BASE_URL = "https://www.reddit.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; OvarraBot/1.0)'
}

# --- Reddit API Helpers ---
def fetch_reddit_posts(subreddit: str, keyword: str, limit: int = 100, max_age_days: int = None) -> List[Dict]:
    url = f"{BASE_URL}/r/{subreddit}/search.json"
    params = {'q': keyword, 'sort': 'new', 'limit': limit, 'restrict_sr': 1}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if resp.status_code == 200:
            posts = resp.json().get('data', {}).get('children', [])
            
            # Filter by age if max_age_days is specified
            if max_age_days:
                import time
                cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
                filtered_posts = []
                for post in posts:
                    created_utc = post.get('data', {}).get('created_utc', 0)
                    if created_utc >= cutoff_time:
                        filtered_posts.append(post)
                return filtered_posts
            
            return posts
    except Exception as e:
        print(f"Error fetching posts: {e}")
    return []

def discover_subreddits(seed_subreddit: str, keywords: List[str], post_limit: int) -> Set[str]:
    discovered = set()
    for keyword in keywords:
        posts = fetch_reddit_posts(seed_subreddit, keyword, post_limit)
        for post in posts:
            data = post.get('data', {})
            sub_name = data.get('subreddit')
            if sub_name and sub_name.lower() != seed_subreddit.lower():
                discovered.add(sub_name)
            text = data.get('selftext', '').lower()
            for word in text.split():
                if word.startswith('r/') and len(word) > 2:
                    sub = word[2:].split('/')[0].split('?')[0].split(')')[0]
                    if sub and sub.lower() != seed_subreddit.lower():
                        discovered.add(sub)
    return discovered

def fetch_and_attach_comments(posts: List[RedditPost], max_retries: int = 3) -> List[RedditPost]:
    for post in posts:
        post_url = post.url.rstrip('/') + '/.json'
        for attempt in range(max_retries):
            try:
                resp = requests.get(post_url, headers=HEADERS, timeout=10)
                if resp.status_code == 429:
                    time.sleep(int(resp.headers.get('Retry-After', 30)))
                    continue
                resp.raise_for_status()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    post.comments = []
                    break
                time.sleep(5 * (attempt + 1))
        if resp.status_code != 200:
            continue
        try:
            data = resp.json()
            def extract_comment_tree(comment) -> RedditComment:
                if comment['kind'] != 't1':
                    return None
                d = comment['data']
                rc = RedditComment(
                    author=d.get('author', '[deleted]'),
                    body=d.get('body', ''),
                    replies=[]
                )
                replies = d.get('replies')
                if replies and isinstance(replies, dict):
                    children = replies.get('data', {}).get('children', [])
                    rc.replies = [extract_comment_tree(child) for child in children if child.get('kind') == 't1']
                return rc
            comments = []
            if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
                for c in data[1]['data']['children']:
                    comment_tree = extract_comment_tree(c)
                    if comment_tree:
                        comments.append(comment_tree)
            post.comments = comments
        except Exception as e:
            post.comments = []
        time.sleep(2)
    return posts

# --- Gemini Helpers ---
def classify_posts_relevance(posts: List[RedditPost], batch_size: int = 3, debug: bool = False) -> List[RedditPost]:
    relevant_posts = []
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    for i in range(0, len(posts), batch_size):
        batch = posts[i:i+batch_size]
        system_prompt = (
            "You are a specialist in identifying posts from OnlyFans creators, adult content creators, and NSFW creators "
            "who are dealing with content leaks, unauthorized sharing, or need help with DMCA takedowns. "
            "ONLY mark posts as relevant if they are from creators asking for help with: "
            "- Their OnlyFans/OF content being leaked or stolen "
            "- Adult content being shared without permission "
            "- NSFW content being reposted elsewhere "
            "- DMCA takedown help for adult/NSFW content "
            "- Privacy violations related to adult content "
            "Do NOT mark general DMCA discussions, gaming copyright, music copyright, or other non-adult content issues as relevant. "
            "Return only relevant posts as JSON array."
        )
        posts_data = [asdict(p) for p in batch]
        user_prompt = f"{system_prompt}\n\nAnalyze these posts. ONLY mark as relevant if they are from OnlyFans/NSFW creators asking for help with content leaks, unauthorized sharing, or DMCA takedowns for adult content. Ignore general copyright discussions. Posts: {json.dumps(posts_data, ensure_ascii=False)}"
        try:
            if debug:
                print(f"Sending batch {i//batch_size+1}: {user_prompt[:200]}...")
            response = model.generate_content(user_prompt)
            content = response.text.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
            for item in parsed:
                if item.get('relevance'):
                    relevant_posts.append(RedditPost(
                        url=item.get('url', ''),
                        relevance=True,
                        title=item.get('title', ''),
                        subtitle=item.get('subtitle', ''),
                        comments=[],
                        ovarra_reply=None
                    ))
        except Exception as e:
            if debug:
                print(f"Gemini error: {e}")
            continue
        time.sleep(1.5)
    return relevant_posts

def generate_ovarra_replies(posts: List[RedditPost], debug: bool = False) -> List[RedditPost]:
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    for post in posts:
        thread_text = f"Post title: {post.title}\nPost body: {post.subtitle}\n\nComments:\n"
        def flatten_comments(comments, depth=0):
            flat = []
            for c in comments:
                flat.append({'author': getattr(c, 'author', '[deleted]'), 'body': getattr(c, 'body', ''), 'depth': depth})
                if getattr(c, 'replies', []):
                    flat.extend(flatten_comments(c.replies, depth+1))
            return flat
        flat_comments = flatten_comments(post.comments)
        for c in flat_comments:
            indent = '  ' * c['depth']
            thread_text += f"{indent}- {c['author']}: {c['body']}\n"
        prompt = (
            "You are a DMCA/content protection specialist who has handled hundreds of takedowns for adult content creators. "
            "Write a tactical, expert-level Reddit reply that:\n\n"
            "MUST INCLUDE:\n"
            "• Specific, actionable tactics (search operators, technical steps, insider knowledge)\n"
            "• Authority signals (mention experience with leak patterns, statistics, what actually works)\n"
            "• Quick wins (immediate steps they can take today)\n"
            "• Unique insights only a practitioner would know\n\n"
            "AVOID:\n"
            "• Generic empathy ('I'm sorry', 'don't give up', 'leaks are scary')\n"
            "• Basic advice everyone knows (watermarking, reverse image search)\n"
            "• Mentioning any services, companies, or products\n"
            "• Therapy-style validation - focus on tactical information\n\n"
            "TONE:\n"
            "• Confident expert who knows what works\n"
            "• Direct and practical, not emotional\n"
            "• Show specialized knowledge through specifics\n"
            "• 60-80 words max\n\n"
            "EXAMPLES OF GOOD TACTICS:\n"
            "• 'Most OF leaks come from 6 sites - remove from those and 70% of traffic disappears'\n"
            "• 'Use search operators: \"yourusername\" + \"mega.nz\" to find leaks in 10 seconds'\n"
            "• 'If leaks appear within 24h, it's usually Discord scraper bots, not subscribers'\n"
            "• 'Target mirrors, not just main sites - leak networks run 5-20 copies'\n"
            "• 'Remove top 10 search results and 80% of casual viewers never see the rest'\n\n"
            f"Reddit thread:\n{thread_text}\n\n"
            "Write an expert, tactical reply that demonstrates real specialized knowledge:"
        )
        try:
            if debug:
                print(f"Generating reply for: {post.title}")
            response = model.generate_content(prompt)
            reply = response.text.strip()
            post.ovarra_reply = reply
            if debug:
                print(f"Reply: {reply}")
        except Exception as e:
            post.ovarra_reply = ""
            if debug:
                print(f"Gemini error for reply: {e}")
        time.sleep(2)
    return posts

# --- Serialization ---
def posts_to_json(posts: List[RedditPost], path: str):
    def comment_to_dict(c: RedditComment):
        return {'author': c.author, 'body': c.body, 'replies': [comment_to_dict(r) for r in c.replies] if c.replies else []}
    def post_to_dict(p: RedditPost):
        d = {'url': p.url, 'relevance': p.relevance, 'title': p.title, 'subtitle': p.subtitle, 'comments': [comment_to_dict(c) for c in p.comments]}
        if p.ovarra_reply:
            d['ovarra_reply'] = p.ovarra_reply
        return d
    with open(path, 'w') as f:
        json.dump([post_to_dict(p) for p in posts], f, indent=2, ensure_ascii=False)

def posts_from_json(path: str) -> List[RedditPost]:
    def comment_from_dict(d):
        replies = [comment_from_dict(r) for r in d.get('replies', [])] if d.get('replies') else []
        return RedditComment(author=d.get('author', ''), body=d.get('body', ''), replies=replies)
    def post_from_dict(d):
        comments = [comment_from_dict(c) for c in d.get('comments', [])]
        return RedditPost(
            url=d.get('url', ''),
            relevance=d.get('relevance', False),
            title=d.get('title', ''),
            subtitle=d.get('subtitle', ''),
            comments=comments,
            ovarra_reply=d.get('ovarra_reply')
        )
    with open(path, 'r') as f:
        data = json.load(f)
    return [post_from_dict(d) for d in data]

# --- Utility: Sentiment Analysis (optional, for future use) ---
def analyze_comments(comments):
    if not comments:
        return {}
    from collections import defaultdict
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
