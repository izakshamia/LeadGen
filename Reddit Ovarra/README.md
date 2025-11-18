# Reddit Ovarra Pipeline & API

This directory contains a minimal, robust pipeline for collecting, classifying, and responding to Reddit posts related to DMCA takedowns, OnlyFans leaks, and unauthorized adult content distribution. The workflow is designed to help identify and support users affected by these issues, including generating empathetic founder-signed replies.

The system can be used as both a **CLI tool** for local development and as a **REST API service** for production deployment.

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

## API Service

The Reddit Ovarra pipeline is also available as a REST API service for production use.

### API Endpoints

#### POST /scrape
Trigger a scraping operation and save results to Supabase.

**Request Body:**
```json
{
  "subreddits": ["CamGirlProblems", "OnlyFansAdvice"],
  "keywords": ["leak", "stolen", "dmca"],
  "post_limit": 10,
  "max_age_days": 120
}
```

All fields are optional and will use defaults if not provided.

**Response:**
```json
{
  "status": "success",
  "processed": 15,
  "skipped": 3,
  "failed": 0,
  "message": "Scraping completed successfully"
}
```

**Status Codes:**
- `200 OK` - Scraping completed successfully
- `400 Bad Request` - Invalid request parameters
- `500 Internal Server Error` - Server error during scraping

#### GET /suggestions
Retrieve recent Reddit post suggestions from the database.

**Query Parameters:**
- `hours` (optional, default: 24) - Time window in hours for filtering suggestions

**Example:**
```bash
GET /suggestions?hours=48
```

**Response:**
```json
{
  "suggestions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "reddit_name": "Help! My content was leaked",
      "reddit_url": "https://reddit.com/r/CamGirlProblems/comments/abc123",
      "suggested_response": "Hi there! I'm Aaron, founder of Ovarra...",
      "status": "new",
      "created_at": "2025-11-18T10:30:00Z"
    }
  ],
  "count": 1,
  "time_window_hours": 48
}
```

**Status Codes:**
- `200 OK` - Suggestions retrieved successfully (empty list if none found)
- `500 Internal Server Error` - Database error

#### GET /health
Check service and database health status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-18T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Database connection failed

### Local Development Setup

1. **Install dependencies:**
```bash
cd "Reddit Ovarra"
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp ../.env.example ../.env
# Edit .env and add your API keys
```

Required environment variables:
- `GEMINI_API_KEY` - Get from https://aistudio.google.com/app/apikey
- `SUPABASE_URL` - Get from Supabase Project Settings > API
- `SUPABASE_KEY` - Get from Supabase Project Settings > API (anon/public key)

3. **Set up Supabase database:**
```bash
# Run the schema SQL in your Supabase SQL editor
cat supabase_schema.sql
```

See `SUPABASE_SETUP.md` for detailed instructions.

4. **Run the API server locally:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# Trigger a scrape
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"post_limit": 5, "max_age_days": 30}'

# Get recent suggestions
curl http://localhost:8000/suggestions?hours=24
```

6. **View API documentation:**
Open http://localhost:8000/docs in your browser for interactive API documentation.

### Railway Deployment

1. **Create a new Railway project:**
   - Go to https://railway.app
   - Create a new project
   - Connect your GitHub repository

2. **Add environment variables in Railway:**
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

3. **Deploy:**
   - Railway will automatically detect the `Procfile` and deploy
   - The service will be available at your Railway-provided URL

4. **Verify deployment:**
```bash
# Replace YOUR_RAILWAY_URL with your actual Railway URL
curl https://YOUR_RAILWAY_URL/health
```

### Environment Variables

All required environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for AI responses | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon/public key | Yes |
| `PORT` | Port for the API server (auto-set by Railway) | No (default: 8000) |

## Documentation

- **[README.md](README.md)** - Main documentation (this file)
- **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Supabase database setup guide
- **[docs/FEATURES.md](docs/FEATURES.md)** - Complete feature list and roadmap
- **[docs/SCRIPTS.md](docs/SCRIPTS.md)** - Utility scripts guide
- **[docs/ANALYTICS_EXAMPLE.md](docs/ANALYTICS_EXAMPLE.md)** - Analytics examples and usage
