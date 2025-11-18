# Quick Start Guide - Run the API Now!

This guide shows you how to run the Reddit Ovarra API and see it in action.

## Prerequisites Check

✅ Your `.env` file is already configured with:
- `GEMINI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Step 1: Start the API Server

Open a terminal and run:

```bash
cd "Reddit Ovarra"
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The API is now running at **http://localhost:8000**

## Step 2: View Interactive API Documentation

Open your browser and go to:
- **http://localhost:8000/docs** - Interactive Swagger UI
- **http://localhost:8000/redoc** - Alternative ReDoc UI

You can test all endpoints directly from the browser!

## Step 3: Test the Endpoints

### Option A: Use the Browser (Easiest)

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in parameters (or leave defaults)
5. Click "Execute"
6. See the response!

### Option B: Use curl (Command Line)

Open a **new terminal** (keep the server running in the first one):

#### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-18T10:30:00Z"
}
```

#### Test 2: Get Recent Suggestions
```bash
curl http://localhost:8000/suggestions?hours=24
```

Expected response:
```json
{
  "suggestions": [],
  "count": 0,
  "time_window_hours": 24
}
```
(Empty at first, will have data after scraping)

#### Test 3: Trigger a Scrape (This is the fun part!)
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["CamGirlProblems"],
    "keywords": ["leak"],
    "post_limit": 3,
    "max_age_days": 30
  }'
```

This will:
1. Scrape Reddit for posts
2. Classify them for relevance
3. Generate Ovarra replies
4. Save to Supabase
5. Return statistics

Expected response:
```json
{
  "status": "success",
  "processed": 2,
  "skipped": 1,
  "failed": 0,
  "message": "Scraping completed successfully"
}
```

#### Test 4: Get Suggestions Again (Now with data!)
```bash
curl http://localhost:8000/suggestions?hours=24
```

Now you should see the suggestions that were just scraped!

## Step 4: View Data in Supabase

1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Select your project
3. Click **Table Editor** in the sidebar
4. Click on the `reddit_suggestions` table
5. See all the scraped posts with generated replies!

## Step 5: Run the Integration Tests

To verify everything works end-to-end:

```bash
cd "Reddit Ovarra"
python3 test_integration.py
```

This runs comprehensive tests:
- ✅ Complete scrape-to-database flow
- ✅ Duplicate prevention
- ✅ Recent-only filtering
- ✅ Error handling

## Quick Demo Script

Want to see it all in action? Run this:

```bash
cd "Reddit Ovarra"

# Start the server in the background
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test health
echo "=== Testing Health ==="
curl http://localhost:8000/health
echo -e "\n"

# Trigger a scrape
echo "=== Triggering Scrape ==="
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"post_limit": 2, "max_age_days": 30}'
echo -e "\n"

# Get suggestions
echo "=== Getting Suggestions ==="
curl http://localhost:8000/suggestions?hours=24
echo -e "\n"

# Stop the server
kill $SERVER_PID
```

## Troubleshooting

### "All posts were already in database"
This means the duplicate prevention is working! All posts found were already scraped before.

**To see new posts being processed:**
```bash
# Option 1: Clear recent test data
python3 clear_test_data.py

# Option 2: Try different subreddits/keywords
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"subreddits": ["OnlyFansAdvice"], "keywords": ["dmca"], "post_limit": 5}'

# Option 3: Increase the time window
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_age_days": 7, "post_limit": 10}'
```

### Port already in use
If you see "Address already in use", either:
- Stop the existing process: `pkill -f "uvicorn main:app"`
- Use a different port: `uvicorn main:app --port 8001`

### Database connection failed
- Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
- Verify the Supabase table exists (see `SUPABASE_SETUP.md`)

### Import errors
Make sure dependencies are installed:
```bash
cd "Reddit Ovarra"
pip install -r requirements.txt
```

### No posts found
- Reddit may not have recent posts matching your keywords
- Try broader keywords: "leak", "stolen", "dmca"
- Try different subreddits: "CamGirlProblems", "OnlyFansAdvice", "CreatorsAdvice"
- Increase max_age_days to look further back

## What's Happening Behind the Scenes?

When you trigger a scrape:

1. **Scraping** - Fetches posts from Reddit using keywords
2. **Classification** - AI determines if posts are relevant to DMCA/leaks
3. **Duplicate Check** - Skips posts already in database
4. **Comment Fetching** - Gets full comment threads
5. **Reply Generation** - AI creates empathetic Ovarra responses
6. **Database Save** - Stores everything in Supabase

All of this happens in one API call!

## Next Steps

- Deploy to Railway (see README.md)
- Integrate with your frontend
- Set up scheduled scraping
- Monitor the Supabase dashboard

Enjoy! 🚀
