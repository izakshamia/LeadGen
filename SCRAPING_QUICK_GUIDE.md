# Quick Guide: How Scraping Works Now

## What Changed?

### ❌ Before (Broken)
```
Click "Start Scraping"
  ↓
API returns immediately (202 Accepted)
  ↓
Success toast appears ← TOO EARLY!
  ↓
Scraping still running in background...
  ↓
No new posts appear
```

### ✅ After (Fixed)
```
Click "Start Scraping"
  ↓
Progress box shows:
  "Scraping 5 subreddits × 3 keywords = 15 searches
   Estimated time: 6 minutes"
  ↓
Backend processes everything (wait 2-10 min)
  ↓
API returns with results
  ↓
Frontend refreshes data
  ↓
Success toast with actual stats
  ↓
New posts appear immediately!
```

## What You'll See

### 1. Click "Start Scraping"
- Button changes to "Scraping..." with spinner
- Form fields become disabled

### 2. Progress Box Appears
```
┌─────────────────────────────────────────────────┐
│ 🔄 Scraping 5 subreddit(s) × 3 keyword(s) = 15 │
│    searches                                     │
│    Estimated time: 6 minutes                    │
│                                                 │
│    ⏳ Searching Reddit posts...                 │
│    🤖 Classifying relevance with AI...          │
│    💬 Fetching comments...                      │
│    ✍️ Generating replies...                     │
│    👥 Extracting redditors...                   │
│                                                 │
│    Please keep this tab open and wait.          │
└─────────────────────────────────────────────────┘
```

### 3. Wait (Don't Close Tab!)
- Backend is working hard
- Processing each subreddit/keyword combo
- Takes ~25 seconds per combination
- Total time depends on your settings

### 4. Success Toast
```
┌─────────────────────────────────────────┐
│ ✓ Scraping completed successfully!     │
│   5 new, 2 duplicates, 0 failed         │
│   8 new redditors discovered            │
└─────────────────────────────────────────┘
```

### 5. Data Refreshes Automatically
- Suggestions list updates
- Redditors list updates
- New posts are visible immediately

## Time Estimates

| Subreddits | Keywords | Searches | Est. Time |
|------------|----------|----------|-----------|
| 1          | 3        | 3        | ~1.5 min  |
| 3          | 3        | 9        | ~4 min    |
| 5          | 3        | 15       | ~6 min    |
| 5          | 5        | 25       | ~10 min   |
| 10         | 5        | 50       | ~20 min   |

**Formula:** `(subreddits × keywords × 25 seconds) / 60 = minutes`

## Tips for Best Results

### ✅ Do This
- Keep the browser tab open during scraping
- Start with fewer subreddits/keywords to test
- Use specific keywords for better relevance
- Check "Suggestions" tab after completion
- Check "Target Redditors" tab for new leads

### ❌ Don't Do This
- Don't close the tab while scraping
- Don't refresh the page during scraping
- Don't click "Start Scraping" multiple times
- Don't use too many subreddits at once (start small)

## Troubleshooting

### "No new posts found"
- Keywords might be too specific
- Try broader keywords like "help", "advice", "question"
- Increase "Max Post Age" to 60 or 120 days
- Check if subreddits are active

### "Request timed out"
- Too many subreddits/keywords (reduce to 5×5 max)
- Network issues (check internet connection)
- Try again with fewer parameters

### "All posts skipped as duplicates"
- You've already scraped these posts before
- Try different keywords
- Increase "Max Post Age" to find older posts
- Try different subreddits

## Example Configurations

### Quick Test (1-2 minutes)
```
Subreddits: CamGirlProblems
Keywords: leak, dmca, help
Post Limit: 10
Max Age: 30 days
```

### Balanced Search (5-7 minutes)
```
Subreddits: CamGirlProblems, OnlyFansAdvice, SexWorkers
Keywords: leak, stolen, dmca, help, advice
Post Limit: 10
Max Age: 30 days
```

### Deep Search (15-20 minutes)
```
Subreddits: CamGirlProblems, OnlyFansAdvice, AdultContentCreators, 
            SexWorkers, CreatorsAdvice
Keywords: leak, stolen, dmca, help, advice, piracy, copyright
Post Limit: 20
Max Age: 60 days
```

## What Gets Saved

After scraping completes, you'll have:

1. **Suggestions** (in Suggestions tab)
   - Reddit post title
   - Reddit post URL
   - AI-generated Ovarra reply
   - Status: "new"
   - Created timestamp

2. **Target Redditors** (in Target Redditors tab)
   - Username
   - Account age and karma
   - Authenticity score
   - Need score
   - Priority level
   - Source posts where they were found
   - Social media links (if available)

## Need Help?

If scraping isn't working:
1. Check the browser console for errors (F12)
2. Verify API is running (check header status indicator)
3. Try with minimal settings first (1 subreddit, 1 keyword)
4. Check the backend logs for detailed error messages
