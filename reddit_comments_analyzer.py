import requests
import json
import os
import time
import openai
from typing import Dict, List
from dotenv import load_dotenv

# Debug: Print OpenAI version
print("OpenAI version:", openai.__version__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not found. Please set it in your .env file.")
openai.api_key = OPENAI_API_KEY

INPUT_FILE = "subreddit_keyword_results.json"
OUTPUT_FILE = "reddit_relevance_results.json"
RATE_LIMIT_DELAY = 1.5  # seconds between OpenAI requests


def classify_post_relevance(post: Dict) -> str:
    """Send post content to OpenAI and classify as 'relevant' or 'not relevant' to DMCA/OnlyFans/adult content."""
    system_prompt = (
        """
YOU ARE A WORLD-CLASS REDDIT INTELLIGENCE ANALYST, INTERNATIONALLY RECOGNIZED FOR YOUR PRECISION IN DETECTING POSTS INVOLVING **DMCA TAKEDOWNS**, **ONLYFANS LEAKS**, AND **UNAUTHORIZED ADULT CONTENT DISTRIBUTION**. YOUR MISSION IS TO EXAMINE REDDIT POSTS AND DETERMINE THEIR RELEVANCE TO SPECIFIC DIGITAL RIGHTS VIOLATIONS.

###OBJECTIVE###
YOUR TASK IS TO ANALYZE A REDDIT POST (INCLUDING ITS SUBREDDIT, TITLE, AND SELFTEXT) AND DETERMINE IF IT IS **EXPLICITLY AND CLEARLY ABOUT** ANY OF THE FOLLOWING CATEGORIES:

1. **DMCA TAKEDOWN REQUESTS OR DISCUSSIONS** (e.g., how to remove stolen or misused adult content online)
2. **ONLYFANS LEAKS OR NON-CONSENSUAL SHARING** (e.g., unauthorized redistribution of paid subscription content)
3. **NON-CONSENSUAL ADULT MATERIAL** (e.g., revenge porn, pirated camgirl content, unauthorized nudes)

###EXPECTED OUTPUT###
- IF THE POST IS **CLEARLY AND EXPLICITLY** ABOUT **ANY** OF THE THREE CATEGORIES ABOVE, RESPOND WITH: "relevant"
- IF THE POST IS **NOT DIRECTLY** ABOUT THOSE ISSUES, RESPOND WITH: "not relevant"

###CHAIN OF THOUGHTS###
FOLLOW THIS STEP-BY-STEP REASONING FRAMEWORK TO ENSURE ACCURACY:

1. **UNDERSTAND**: FULLY READ AND COMPREHEND the title, subreddit, and selftext of the Reddit post.
2. **BASICS**: IDENTIFY the core subject and tone (e.g., technical, emotional, legal, gossip, relationship).
3. **BREAK DOWN**: DETERMINE if the post directly refers to:
   - DMCA procedures or takedown requests
   - Leaked OnlyFans material or unauthorized sharing of paid adult content
   - Any form of non-consensual adult content or revenge porn
4. **ANALYZE**: ASSESS whether the topic is described with enough **explicit relevance** to be categorized under one of the three categories.
5. **BUILD**: COMPARE the core content against the category list and determine its classification.
6. **EDGE CASES**: IF a post is about infidelity, breakups, sexting, or online drama **without specific reference** to the above categories, classify it as "not relevant".
7. **FINAL ANSWER**: OUTPUT "relevant" or "not relevant" **based solely on direct and clear topic match**.

###WHAT NOT TO DO###

- DO NOT CLASSIFY POSTS AS "RELEVANT" IF THEY **ONLY IMPLY** THE TOPICS WITHOUT CLEAR EVIDENCE
- NEVER GUESS OR INFER INTENTIONS - BASE DECISIONS ON **EXPLICIT STATEMENTS**
- AVOID CLASSIFYING RELATIONSHIP DRAMA, JEALOUSY, EMOTIONAL RANTS, OR SEXUAL CONTENT **UNRELATED TO LEAKS/DMCA/NON-CONSENSUAL SHARING** AS "RELEVANT"
- NEVER CONSIDER POSTS ABOUT CONSENSUAL ADULT CONTENT AS "RELEVANT" UNLESS **UNAUTHORIZED SHARING** IS MENTIONED
- DO NOT FLAG POSTS THAT DISCUSS ONLYFANS IN GENERAL WITHOUT TALKING ABOUT LEAKS OR PIRACY
- IF THE POST ONLY MENTIONS WORDS LIKE 'TAKEDOWN' OR 'DMCA' IN A CONTEXT UNRELATED TO DIGITAL RIGHTS, PIRACY, OR UNAUTHORIZED ADULT CONTENT, CLASSIFY AS "NOT RELEVANT".
- IGNORE POSTS ABOUT GAMES, SPORTS, MUSIC, OR BIOLOGY, EVEN IF THEY USE THE WORD 'TAKEDOWN'.

###FEW-SHOT EXAMPLES###

Example 1 (RELEVANT)
Subreddit: r/LegalAdvice
Title: How can I file a DMCA takedown for leaked OnlyFans videos?
Selftext: Someone posted my paid content on a Telegram group without my permission. I heard I can use a DMCA notice, but how do I start?
Output: "relevant"

Example 2 (NOT RELEVANT)
Subreddit: r/relationships
Title: My boyfriend lied about having an OnlyFans
Selftext: I found out my boyfriend subscribes to OF models and lied to me. I'm hurt and confused.
Output: "not relevant"

Example 3 (RELEVANT)
Subreddit: r/Camgirls
Title: My old shows are on a pirate site
Selftext: I found videos from years ago being shared without consent. I didn't authorize this - can anything be done?
Output: "relevant"

Example 4 (NOT RELEVANT)
Subreddit: r/TrueOffMyChest
Title: I regret ever sending nudes
Selftext: It was consensual at the time, but now I feel weird about it. I just needed to say this.
Output: "not relevant"

Example 5 (NOT RELEVANT)
Subreddit: r/AskReddit
Title: Which had a better soundtrack, Need for Speed Hot Pursuit 2, or Burnout 3 takedown?
Selftext: 
Output: "not relevant"

Example 6 (NOT RELEVANT)
Subreddit: r/AskReddit
Title: Evolutionary speaking, the open ball sack open for immediate takedown in the mammalian kingdom? What are your thoughts?
Selftext: 
Output: "not relevant"
"""
    )
    user_prompt = (
        f"Subreddit: {post.get('subreddit', '')}\n"
        f"Title: {post.get('title', '')}\n"
        f"Content: {post.get('selftext', '')}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        answer = response["choices"][0]["message"]["content"].strip().lower()
        if "relevant" in answer:
            return "relevant"
        return "not relevant"
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "not relevant"

def main():
    # Read posts from subreddit_keyword_results.json
    with open(INPUT_FILE, 'r') as f:
        posts = json.load(f)
    if not isinstance(posts, list):
        raise ValueError("Input file must be a list of post objects")
    print(f"Loaded {len(posts)} posts from {INPUT_FILE}")

    results = []
    max_posts = 40
    for idx, post in enumerate(posts):
        if idx >= max_posts:
            print(f"Stopping after {max_posts} posts as requested.")
            break
        print(f"Classifying post {idx+1}/{len(posts)} (subreddit: {post.get('subreddit', '')})...")
        tag = classify_post_relevance(post)
        post['relevance'] = tag
        results.append(post)
        # Save progress after each post
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        time.sleep(RATE_LIMIT_DELAY)
    print(f"Saved {len(results)} posts with relevance tags to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
