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

# Default: Last 4 months of posts
python pipeline.py --debug

# Custom time range: Last 7 days (fresh posts only)
python pipeline.py --max-age-days 7 --debug

# Last 30 days
python pipeline.py --max-age-days 30 --debug

# Last 6 months
python pipeline.py --max-age-days 180 --debug

# Full command with all options
python pipeline.py [--subreddits SUB1 SUB2 ...] [--discover] [--seed-subreddit SEED] [--keywords KW1 KW2 ...] [--post-limit N] [--max-age-days N] [--debug] [--force]
```

- `--subreddits`: List of subreddits to search (default: common subreddits)
- `--discover`: Discover related subreddits from a seed
- `--seed-subreddit`: Subreddit to start discovery from (default: CamGirlProblems)
- `--keywords`: Keywords to search for (default: dmca leak takedown copyright)
- `--post-limit`: Number of posts per keyword (default: 10)
- `--max-age-days`: Only fetch posts from last N days (default: 120 = 4 months)
- `--debug`: Print debug information
- `--force`: Ignore checkpoints and re-run all steps

## Requirements
- Python 3.8+
- OpenAI API key (set in `.env` as `OPENAI_API_KEY`)
- Reddit API credentials are not required for public scraping
- See `requirements.txt` for package list

## File Structure
- `pipeline.py`: Main entry point for the pipeline
- `api_utils.py`: All Reddit/Gemini API and utility logic
- `models.py`: Data models for posts and comments
- `subreddit_analytics.py`: Analytics and performance tracking
- `requirements.txt`: Python dependencies
- `scripts/`: Utility scripts for working with results
  - `list_posts.py`: View posts from checkpoint files
  - `regenerate_replies.py`: Regenerate all replies
  - `regenerate_single.py`: Regenerate one specific reply
  - `view_analytics.py`: View subreddit performance analytics
- `docs/`: Documentation
  - `FEATURES.md`: Complete feature list
  - `SCRIPTS.md`: Utility scripts documentation
  - `ANALYTICS_EXAMPLE.md`: Analytics guide with examples
- `README.md`: This file

## Output
- Final results with Ovarra replies are printed and saved to `final_posts.json`

## Utility Scripts

After running the pipeline, use these helper scripts:

```bash
# List all posts with details
python3 scripts/list_posts.py --show-replies

# Regenerate all replies (useful for testing new prompts)
python3 scripts/regenerate_replies.py --debug

# Regenerate one specific reply
python3 scripts/regenerate_single.py --index 3 --debug

# View subreddit performance analytics
python3 scripts/view_analytics.py
```

See `docs/SCRIPTS.md` for more details.

## Subreddit Analytics

The pipeline automatically tracks subreddit performance:
- **Conversion rates** (relevant posts / total posts)
- **Top performers** to prioritize
- **Low performers** to remove
- **New subreddit discoveries** from post mentions

View analytics anytime:
```bash
python3 scripts/view_analytics.py
```

See `docs/ANALYTICS_EXAMPLE.md` for detailed examples.

## Documentation

- **[README.md](README.md)** - Main documentation (this file)
- **[docs/FEATURES.md](docs/FEATURES.md)** - Complete feature list and roadmap
- **[docs/SCRIPTS.md](docs/SCRIPTS.md)** - Utility scripts guide
- **[docs/ANALYTICS_EXAMPLE.md](docs/ANALYTICS_EXAMPLE.md)** - Analytics examples and usage
