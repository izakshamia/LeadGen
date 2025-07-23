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

•⁠  ⁠DO NOT CLASSIFY POSTS AS "RELEVANT" IF THEY *ONLY IMPLY* THE TOPICS WITHOUT CLEAR EVIDENCE
•⁠  ⁠NEVER GUESS OR INFER INTENTIONS - BASE DECISIONS ON *EXPLICIT STATEMENTS*
•⁠  ⁠AVOID CLASSIFYING RELATIONSHIP DRAMA, JEALOUSY, EMOTIONAL RANTS, OR SEXUAL CONTENT *UNRELATED TO LEAKS/DMCA/NON-CONSENSUAL SHARING* AS "RELEVANT"
•⁠  ⁠NEVER CONSIDER POSTS ABOUT CONSENSUAL ADULT CONTENT AS "RELEVANT" UNLESS *UNAUTHORIZED SHARING* IS MENTIONED
•⁠  ⁠DO NOT FLAG POSTS THAT DISCUSS ONLYFANS IN GENERAL WITHOUT TALKING ABOUT LEAKS OR PIRACY
•⁠  ⁠IF THE POST ONLY MENTIONS WORDS LIKE 'TAKEDOWN' OR 'DMCA' IN A CONTEXT UNRELATED TO DIGITAL RIGHTS, PIRACY, OR UNAUTHORIZED ADULT CONTENT, CLASSIFY AS "NOT RELEVANT".
•⁠  ⁠IGNORE POSTS ABOUT GAMES, SPORTS, MUSIC, OR BIOLOGY, EVEN IF THEY USE THE WORD 'TAKEDOWN'.
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
Return to me a json array of objects such as 

{[
url: 
relevane: true/false,
Title:
subtitle:
]}

if not relevant do not return it as part of the objec

"""
    )
    user_prompt = (
        f"Subreddit: {post.get('subreddit', '')}\n"
        f"Title: {post.get('title', '')}\n"
        f"Content: {post.get('selftext', '')}"
    )
    try:
        
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0
        )
        
        chatgpt_raw = response["choices"][0]["message"]["content"].strip()
        print("ChatGPT returned:", chatgpt_raw)
        answer = chatgpt_raw.lower()
        if "relevant" in answer:
            return "relevant"
        return "not relevant"
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "not relevant"

def export_relevant_posts(input_file):
    with open(input_file, 'r') as f:
        posts = json.load(f)
    output = []
    for post in posts:
        if post.get("relevance", "").lower() == "relevant":
            output.append({
                "url": post.get("url"),
                "relevance": True,
                "Title": post.get("title"),
                "subtitle": post.get("selftext")
            })
    print(json.dumps(output, indent=2, ensure_ascii=False))

def main():
    # Read posts from subreddit_keyword_results.json
    with open(INPUT_FILE, 'r') as f:
        posts = json.load(f)
    # Filter for CamGirlProblems subreddit only
    camgirl_posts = [p for p in posts if p.get('subreddit', '').lower() == 'camgirlproblems']
    if not isinstance(camgirl_posts, list):
        raise ValueError("Input file must be a list of post objects")
    print(f"Loaded {len(camgirl_posts)} posts from {INPUT_FILE}")

    relevant_results = []
    max_posts = 40
    for idx, post in enumerate(camgirl_posts):
        if idx >= max_posts:
            print(f"Stopping after {max_posts} posts as requested.")
            break
        print(f"Classifying post {idx+1}/{len(camgirl_posts)} (subreddit: {post.get('subreddit', '')})...")
        result = classify_post_relevance(post)
        # Accept blank, empty, or [] as not relevant; only add non-empty lists
        if result:
            try:
                parsed = json.loads(result) if isinstance(result, str) else result
                if isinstance(parsed, list) and len(parsed) > 0:
                    relevant_results.extend(parsed)
            except json.JSONDecodeError:
                # Accept empty string, blank, or [] as not relevant; do not print error
                pass
            except Exception as e:
                print(f"Error parsing result: {e}")
        # Save progress after each post
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(relevant_results, f, indent=2, ensure_ascii=False)
        time.sleep(RATE_LIMIT_DELAY)
    print(f"Saved {len(relevant_results)} relevant posts to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
