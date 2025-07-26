# Reddit Ovarra Pipeline (Minimal, Checkpointed)

This directory contains a minimal, robust pipeline for collecting, classifying, and responding to Reddit posts related to DMCA takedowns, OnlyFans leaks, and unauthorized adult content distribution. The workflow is designed to help identify and support users affected by these issues, including generating empathetic founder-signed replies.

## Pipeline Overview

1. **Scrape Reddit Posts**
   - Fetches posts from target subreddits using keywords.
   - Checkpoint: `scraped_posts.json`
2. **Classify Relevance**
   - Uses OpenAI to classify posts as relevant or not to DMCA/leaks/non-consensual content.
   - Checkpoint: `relevant_posts.json`
3. **Fetch Comments**
   - Fetches all comments and subcomments (full comment tree) from Reddit and attaches them to the post.
   - Checkpoint: `posts_with_comments.json`
4. **Generate Empathetic Replies**
   - Sends the full thread (post + comments) to OpenAI and generates an empathetic, founder-signed reply.
   - Checkpoint: `final_posts.json`

## Checkpointing
- The pipeline saves progress after each major step.
- If a step fails, you can resume from the last successful checkpoint without repeating previous API calls.
- Use `--force` to ignore checkpoints and re-run all steps from scratch.

## Usage

```bash
cd Reddit\ Ovarra
python pipeline.py [--subreddits SUB1 SUB2 ...] [--discover] [--seed-subreddit SEED] [--keywords KW1 KW2 ...] [--post-limit N] [--debug] [--force]
```

- `--subreddits`: List of subreddits to search (default: common subreddits)
- `--discover`: Discover related subreddits from a seed
- `--seed-subreddit`: Subreddit to start discovery from (default: CamGirlProblems)
- `--keywords`: Keywords to search for (default: dmca leak takedown copyright)
- `--post-limit`: Number of posts per keyword (default: 10)
- `--debug`: Print debug information
- `--force`: Ignore checkpoints and re-run all steps

## Requirements
- Python 3.8+
- OpenAI API key (set in `.env` as `OPENAI_API_KEY`)
- Reddit API credentials are not required for public scraping
- See `requirements.txt` for package list

## File Structure
- `pipeline.py`: Main entry point for the pipeline
- `api_utils.py`: All Reddit/OpenAI API and utility logic
- `models.py`: Data models for posts and comments
- `requirements.txt`: Python dependencies
- `README.md`: This file

## Output
- Final results with Ovarra replies are printed and saved to `final_posts.json`
