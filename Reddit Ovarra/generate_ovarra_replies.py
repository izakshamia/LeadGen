import openai
import os
import json
import time
from dotenv import load_dotenv

def flatten_comments(comments, depth=0):
    flat = []
    for c in comments:
        flat.append({
            'author': c.get('author'),
            'body': c.get('body'),
            'depth': depth
        })
        if c.get('replies'):
            flat.extend(flatten_comments(c['replies'], depth=depth+1))
    return flat

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
INPUT_FILE = "reddit_relevance_results_with_comments.json"
OUTPUT_FILE = "reddit_relevance_results_with_ovarra_reply.json"
RATE_LIMIT_DELAY = 3
MODEL = "gpt-4.1-mini"

with open(INPUT_FILE, 'r') as f:
    posts = json.load(f)

for post in posts:
    comments = post.get('comments', [])
    flat_comments = flatten_comments(comments)
    # Compose a thread summary string
    thread_text = f"Post title: {post.get('title')}\nPost body: {post.get('subtitle')}\n\nComments:\n"
    for c in flat_comments:
        indent = '  ' * c['depth']
        thread_text += f"{indent}- {c['author']}: {c['body']}\n"
    # Compose OpenAI prompt
    system_prompt = (
        "You are the founder of Ovarra, a DMCA and privacy support service. You are empathetic, supportive, and helpful. "
        "Given the following Reddit post and its full comment thread, generate an empathetic, founder-signed reply. "
        "Your reply should:\n"
        "- Acknowledge the user's situation in a caring way\n"
        "- Briefly reference the core issue (e.g., content leaks, DMCA stress)\n"
        "- Offer a supportive suggestion to try Ovarra\n"
        "- Clearly state you are the founder of Ovarra and are here to help\n"
        "- Be concise and authentic.\n"
        "Do not include any marketing language or generic platitudes."
    )
    user_prompt = (
        f"Reddit thread:\n{thread_text}\n\n"
        "Write a reply as the founder of Ovarra, following the guidelines above."
    )
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        reply = response["choices"][0]["message"]["content"].strip()
        post['ovarra_reply'] = reply
        print(f"Generated Ovarra reply for: {post.get('title')}")
    except Exception as e:
        print(f"OpenAI error for post '{post.get('title')}': {e}")
        post['ovarra_reply'] = ""
    time.sleep(RATE_LIMIT_DELAY)

with open(OUTPUT_FILE, 'w') as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)

print(f"Saved posts with Ovarra replies to {OUTPUT_FILE}")
