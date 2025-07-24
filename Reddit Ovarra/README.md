# Reddit Ovarra Pipeline

This directory contains scripts and utilities for collecting, classifying, and responding to Reddit posts related to DMCA takedowns, OnlyFans leaks, and unauthorized adult content distribution. The workflow is designed to help identify and support users affected by these issues, including generating empathetic founder-signed replies.

## Pipeline Overview

1. **Scrape Reddit Posts**
   - `subreddit_keyword_scraper.py`: Collects posts from target subreddits and saves them as JSON.

2. **Classify Relevance**
   - `reddit_comments_analyzer.py`: Uses OpenAI to classify posts as relevant or not to DMCA/leaks/non-consensual content. Outputs only relevant posts.

3. **Fetch Comments**
   - `fetch_reddit_comments.py`: For each relevant post, fetches all comments and subcomments (full comment tree) from Reddit and attaches them to the post.

4. **Generate Empathetic Replies**
   - `generate_ovarra_replies.py`: Sends the full thread (post + comments) to OpenAI and generates an empathetic, founder-signed reply referencing the user's issue and offering Ovarra support.

5. **Utilities & Analysis**
   - `reddit_utils.py`, `reddit_analyzer.py`: Helper functions and analysis tools for Reddit data.

## Files in This Directory

- `subreddit_keyword_scraper.py`: Scrapes Reddit posts by keyword/subreddit.
- `reddit_comments_analyzer.py`: Classifies posts for DMCA/leak relevance.
- `fetch_reddit_comments.py`: Fetches and attaches full comment trees.
- `generate_ovarra_replies.py`: Generates empathetic Ovarra replies per thread.
- `reddit_utils.py`: Utility functions for Reddit data.
- `reddit_analyzer.py`: Additional analysis tools.
- `requirements.txt`: Python dependencies.
- `README.md`: This file.

## Requirements

- Python 3.8+
- OpenAI API key (set in `.env` as `OPENAI_API_KEY`)
- Reddit API credentials (if using authenticated scraping)
- See `requirements.txt` for package list

## Usage

1. Scrape posts:
   ```bash
   python subreddit_keyword_scraper.py
   ```
2. Classify for relevance:
   ```bash
   python reddit_comments_analyzer.py
   ```
3. Fetch comments:
   ```bash
   python fetch_reddit_comments.py
   ```
4. Generate Ovarra replies:
   ```bash
   python generate_ovarra_replies.py
   ```

## Output Files
- `reddit_relevance_results.json`: Relevant posts only
- `reddit_relevance_results_with_comments.json`: Posts with full comment trees
- `reddit_relevance_results_with_ovarra_reply.json`: Posts with Ovarra founder replies

## Contact
For questions or support, contact the Ovarra team.
