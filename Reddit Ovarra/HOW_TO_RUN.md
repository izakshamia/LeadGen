# How to Run the Reddit Ovarra API - Complete Guide

## What Just Happened?

You got a "failure" message, but **everything is actually working perfectly!** 

The system found 2 posts, classified them as relevant, but they were **already in your database** (duplicates). The duplicate prevention feature is working exactly as designed.

## Understanding the Response

```json
{
  "status": "success",  // Now shows success when all posts are duplicates
  "processed": 0,       // No NEW posts (all were duplicates)
  "skipped": 2,         // 2 posts skipped because they already exist
  "failed": 0,          // No errors
  "message": "Scraping completed - all 2 posts were already in database"
}
```

This is **good news** - it means:
- ✅ Reddit scraping works
- ✅ AI classification works
- ✅ Duplicate detection works
- ✅ Database connection works

## How to See It Process New Posts

### Option 1: Clear Test Data (Recommended for Testing)

```bash
cd "Reddit Ovarra"
python3 clear_test_data.py
```

Choose option 1 to clear the last 24 hours, then run the scrape again.

### Option 2: Try Different Subreddits/Keywords

```bash
# Try a different subreddit
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["OnlyFansAdvice", "CreatorsAdvice"],
    "keywords": ["dmca", "stolen"],
    "post_limit": 5,
    "max_age_days": 30
  }'
```

### Option 3: Look Further Back in Time

```bash
# Search last 6 months instead of 4 months
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "max_age_days": 180,
    "post_limit": 10
  }'
```

## Complete Workflow Demo

Here's a complete demo showing everything working:

```bash
cd "Reddit Ovarra"

# 1. Start the server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
SERVER_PID=$!
sleep 3

# 2. Check health
echo "=== Health Check ==="
curl http://localhost:8000/health | jq
echo ""

# 3. Clear test data (optional)
echo "=== Clearing Test Data ==="
python3 -c "from clear_test_data import clear_recent_data; clear_recent_data(24)"
echo ""

# 4. Trigger a scrape
echo "=== Triggering Scrape ==="
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "subreddits": ["CamGirlProblems", "OnlyFansAdvice"],
    "keywords": ["leak", "dmca"],
    "post_limit": 5,
    "max_age_days": 60
  }' | jq
echo ""

# 5. Get suggestions
echo "=== Getting Suggestions ==="
curl http://localhost:8000/suggestions?hours=24 | jq
echo ""

# 6. Stop the server
kill $SERVER_PID
```

## What Happens During a Scrape?

1. **Scraping** (5-10 seconds)
   - Fetches posts from Reddit matching your keywords
   - Filters by age (max_age_days)

2. **Classification** (5-10 seconds)
   - AI analyzes each post to determine relevance
   - Only keeps posts about OnlyFans/NSFW content leaks

3. **Duplicate Check** (instant)
   - Checks if post URL already exists in database
   - Skips if duplicate (this is what happened to you!)

4. **Comment Fetching** (2-5 seconds per post)
   - Gets full comment threads for context

5. **Reply Generation** (2-5 seconds per post)
   - AI generates tactical Ovarra response

6. **Database Save** (instant)
   - Stores suggestion in Supabase

**Total time**: 30-60 seconds for 5 posts

## Viewing Results

### In Browser
1. Go to http://localhost:8000/docs
2. Try the GET /suggestions endpoint
3. See all suggestions with generated replies

### In Supabase Dashboard
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "Table Editor" → "reddit_suggestions"
4. See all data with timestamps, URLs, replies, status

### Via API
```bash
# Get last 24 hours
curl http://localhost:8000/suggestions?hours=24 | jq

# Get last week
curl http://localhost:8000/suggestions?hours=168 | jq

# Pretty print with specific fields
curl http://localhost:8000/suggestions?hours=24 | jq '.suggestions[] | {title: .reddit_name, url: .reddit_url, status: .status}'
```

## Common Scenarios

### Scenario 1: All Duplicates (What You Experienced)
```json
{
  "status": "success",
  "processed": 0,
  "skipped": 5,
  "failed": 0,
  "message": "Scraping completed - all 5 posts were already in database"
}
```
**What it means**: System is working, but no new posts found.

### Scenario 2: New Posts Found
```json
{
  "status": "success",
  "processed": 3,
  "skipped": 2,
  "failed": 0,
  "message": "Scraping completed successfully - 3 new suggestions saved"
}
```
**What it means**: Found 5 posts, 2 were duplicates, 3 were new and saved.

### Scenario 3: Some Failures
```json
{
  "status": "partial",
  "processed": 2,
  "skipped": 1,
  "failed": 2,
  "message": "Scraping completed with 2 failures"
}
```
**What it means**: Found 5 posts, 1 duplicate, 2 saved successfully, 2 failed (maybe API errors).

### Scenario 4: No Posts Found
```json
{
  "status": "failure",
  "processed": 0,
  "skipped": 0,
  "failed": 0,
  "message": "Scraping failed - no posts were processed"
}
```
**What it means**: Reddit had no posts matching your criteria. Try different keywords or longer time window.

## Testing Tips

### Test with Fresh Data
```bash
# Clear database and scrape
python3 clear_test_data.py  # Choose option 1
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" -d '{"post_limit": 3}'
```

### Test Duplicate Prevention
```bash
# Run same scrape twice
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" -d '{"post_limit": 3}'
# Wait a moment
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" -d '{"post_limit": 3}'
# Second run should skip all posts
```

### Test Time Filtering
```bash
# Get suggestions from different time windows
curl http://localhost:8000/suggestions?hours=1 | jq '.count'
curl http://localhost:8000/suggestions?hours=24 | jq '.count'
curl http://localhost:8000/suggestions?hours=168 | jq '.count'
# Counts should increase with larger time windows
```

## Debug Tools

### Check Server Logs
The server prints detailed logs showing each step:
```
INFO - Starting scrape_and_save: subreddits=['CamGirlProblems']...
INFO - Step 1: Scraping posts from Reddit...
INFO - Scraped 2 total posts
INFO - Step 2: Classifying posts for relevance...
INFO - Found 2 relevant posts
INFO - Step 3-6: Processing relevant posts...
INFO - Processing post 1/2: Data protection...
INFO - Duplicate found: https://www.reddit.com/...
INFO - Skipping duplicate post: https://www.reddit.com/...
```

### Run Debug Script
```bash
python3 test_scrape_debug.py
```
Shows detailed step-by-step execution with error messages.

### Run Integration Tests
```bash
python3 test_integration.py
```
Runs comprehensive test suite (takes 2-3 minutes).

## Next Steps

1. **Test locally** - Use the commands above to see it working
2. **Deploy to Railway** - Follow the deployment guide in README.md
3. **Set up scheduled scraping** - Use Railway cron jobs or external scheduler
4. **Build frontend** - Connect to the API endpoints
5. **Monitor Supabase** - Watch the dashboard as data flows in

## Quick Reference

```bash
# Start server
python3 -m uvicorn main:app --reload --port 8000

# Health check
curl http://localhost:8000/health

# Scrape (minimal)
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" -d '{}'

# Scrape (custom)
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" \
  -d '{"subreddits": ["CamGirlProblems"], "keywords": ["leak"], "post_limit": 5}'

# Get suggestions
curl http://localhost:8000/suggestions?hours=24

# Clear test data
python3 clear_test_data.py

# Debug
python3 test_scrape_debug.py

# Full tests
python3 test_integration.py
```

## Summary

Your API is **working perfectly**! The "failure" you saw was actually the duplicate prevention doing its job. I've updated the code so it now returns "success" when all posts are duplicates, with a clear message explaining what happened.

Try clearing the test data and running again to see new posts being processed! 🚀
