import requests
import json
import time

INPUT_FILE = "reddit_relevance_results.json"
OUTPUT_FILE = "reddit_relevance_results_with_comments.json"
RATE_LIMIT_DELAY = 1.5  # seconds between Reddit requests

with open(INPUT_FILE, 'r') as f:
    relevant_posts = json.load(f)

for post in relevant_posts:
    post_url = post['url']
    if not post_url.endswith('/'):
        post_url += '/'
    comments_url = post_url + '.json'
    print(f'Fetching comments for {post_url}')
    try:
        resp = requests.get(comments_url, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            data = resp.json()
            def extract_comment_tree(comment):
                if comment['kind'] != 't1':
                    return None
                data = comment['data']
                comment_obj = {
                    'author': data.get('author'),
                    'body': data.get('body'),
                }
                # Recursively extract replies
                replies = data.get('replies')
                if replies and isinstance(replies, dict):
                    children = replies.get('data', {}).get('children', [])
                    subcomments = [extract_comment_tree(child) for child in children if child['kind'] == 't1']
                    # Filter out None
                    subcomments = [sc for sc in subcomments if sc]
                    if subcomments:
                        comment_obj['replies'] = subcomments
                return comment_obj

            comments = []
            for c in data[1]['data']['children']:
                comment_tree = extract_comment_tree(c)
                if comment_tree:
                    comments.append(comment_tree)
            post['comments'] = comments
        else:
            print(f"Failed to fetch comments for {post_url}: status {resp.status_code}")
            post['comments'] = []
    except Exception as e:
        print(f"Error fetching comments for {post_url}: {e}")
        post['comments'] = []
    time.sleep(RATE_LIMIT_DELAY)

with open(OUTPUT_FILE, 'w') as f:
    json.dump(relevant_posts, f, indent=2, ensure_ascii=False)

print(f"Saved posts with comments to {OUTPUT_FILE}")
