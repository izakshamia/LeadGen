# Testing Checklist - Scraping Fix

## Pre-Testing Setup

### 1. Start Backend
```bash
cd api
uvicorn main:app --reload --port 8002
```
**Expected:** Server starts on http://localhost:8002

### 2. Start Frontend
```bash
cd reddit-ovarra-ui
npm run dev
```
**Expected:** Dev server starts on http://localhost:5173

### 3. Open Browser
- Navigate to http://localhost:5173
- Open DevTools (F12) to monitor console

---

## Test Case 1: Quick Scrape (1-2 minutes)

### Setup
- **Subreddits:** `CamGirlProblems`
- **Keywords:** `leak, help`
- **Post Limit:** `10`
- **Max Age:** `30 days`

### Steps
1. [ ] Enter the parameters above
2. [ ] Click "Start Scraping"
3. [ ] Verify button shows "Scraping..." with spinner
4. [ ] Verify progress box appears showing:
   - [ ] "Scraping 1 subreddit(s) × 2 keyword(s) = 2 searches"
   - [ ] "Estimated time: 1 minute"
   - [ ] Step-by-step progress indicators
   - [ ] "Please keep this tab open" warning
5. [ ] Wait for completion (don't close tab!)
6. [ ] Verify success toast appears with stats
7. [ ] Check Suggestions tab - should have new posts
8. [ ] Check Target Redditors tab - should have new redditors

### Expected Results
- ✅ Progress box shows correct calculation
- ✅ Estimated time is reasonable
- ✅ Success toast appears after ~1-2 minutes
- ✅ New posts appear in Suggestions
- ✅ New redditors appear in Target Redditors
- ✅ No premature success messages

---

## Test Case 2: Medium Scrape (4-6 minutes)

### Setup
- **Subreddits:** `CamGirlProblems, OnlyFansAdvice, SexWorkers`
- **Keywords:** `leak, dmca, help`
- **Post Limit:** `10`
- **Max Age:** `30 days`

### Steps
1. [ ] Enter the parameters above
2. [ ] Click "Start Scraping"
3. [ ] Verify progress box shows:
   - [ ] "Scraping 3 subreddit(s) × 3 keyword(s) = 9 searches"
   - [ ] "Estimated time: 4 minutes"
4. [ ] Wait for completion
5. [ ] Verify success toast with detailed stats
6. [ ] Verify new data appears

### Expected Results
- ✅ Takes approximately 4-6 minutes
- ✅ Success toast shows actual counts
- ✅ Multiple new posts appear
- ✅ Multiple new redditors appear

---

## Test Case 3: Duplicate Detection

### Setup
- Use the SAME parameters as Test Case 1
- Run scraping again

### Steps
1. [ ] Enter same parameters as Test Case 1
2. [ ] Click "Start Scraping"
3. [ ] Wait for completion
4. [ ] Check success toast

### Expected Results
- ✅ Success toast shows high "skipped" count
- ✅ Few or no new posts (most are duplicates)
- ✅ Message indicates duplicates were skipped

---

## Test Case 4: Error Handling

### Test 4a: Empty Subreddits
1. [ ] Clear subreddits field
2. [ ] Click "Start Scraping"
3. [ ] Verify error message: "Subreddits are required"

### Test 4b: Empty Keywords
1. [ ] Clear keywords field
2. [ ] Click "Start Scraping"
3. [ ] Verify error message: "Keywords are required"

### Test 4c: Invalid Subreddit
1. [ ] Enter: `ThisSubredditDoesNotExist12345`
2. [ ] Enter keywords: `test`
3. [ ] Click "Start Scraping"
4. [ ] Wait for completion
5. [ ] Verify appropriate error or "0 processed" result

---

## Test Case 5: Progress Indicators

### Steps
1. [ ] Start any scrape
2. [ ] Observe progress box during scraping
3. [ ] Verify all indicators are visible:
   - [ ] ⏳ Searching Reddit posts...
   - [ ] 🤖 Classifying relevance with AI...
   - [ ] 💬 Fetching comments...
   - [ ] ✍️ Generating replies...
   - [ ] 👥 Extracting redditors...
4. [ ] Verify spinner is animated
5. [ ] Verify "Keep this tab open" warning is visible

---

## Test Case 6: Time Estimation Accuracy

### Test Different Configurations

| Config | Expected Time | Actual Time | Pass/Fail |
|--------|--------------|-------------|-----------|
| 1 sub × 2 keywords | ~1 min | _____ min | [ ] |
| 3 subs × 3 keywords | ~4 min | _____ min | [ ] |
| 5 subs × 3 keywords | ~6 min | _____ min | [ ] |

**Note:** Actual time may vary ±30% depending on network and Reddit API

---

## Test Case 7: Data Refresh

### Steps
1. [ ] Note current count in Suggestions tab
2. [ ] Note current count in Target Redditors tab
3. [ ] Run a scrape with new keywords
4. [ ] After completion, verify:
   - [ ] Suggestions count increased
   - [ ] Target Redditors count increased
   - [ ] New posts are visible immediately
   - [ ] No manual refresh needed

---

## Test Case 8: UI State Management

### During Scraping
1. [ ] Button shows "Scraping..." with spinner
2. [ ] Button is disabled
3. [ ] Form fields are disabled
4. [ ] Progress box is visible
5. [ ] Can't submit form again

### After Completion
1. [ ] Button returns to "Start Scraping"
2. [ ] Button is enabled
3. [ ] Form fields are enabled
4. [ ] Progress box disappears
5. [ ] Can submit form again

---

## Test Case 9: Success Message Variations

### Test 9a: All New Posts
- Run scrape with unique keywords
- **Expected:** "✓ Scraping completed successfully! X new, 0 duplicates..."

### Test 9b: All Duplicates
- Run same scrape twice
- **Expected:** "⚠ Scraping completed with some issues. 0 new, X duplicates..."

### Test 9c: Some Failures
- Use invalid subreddit
- **Expected:** Message includes "X failed"

### Test 9d: Redditors Extracted
- Run scrape that finds comments
- **Expected:** Message includes "X new redditors discovered"

---

## Test Case 10: Browser Behavior

### Test 10a: Keep Tab Open
1. [ ] Start scraping
2. [ ] Keep tab open and active
3. [ ] Verify completes successfully

### Test 10b: Switch Tabs (Don't Close)
1. [ ] Start scraping
2. [ ] Switch to another browser tab
3. [ ] Wait for estimated time
4. [ ] Switch back
5. [ ] Verify completed successfully

### Test 10c: Minimize Browser
1. [ ] Start scraping
2. [ ] Minimize browser window
3. [ ] Wait for estimated time
4. [ ] Restore window
5. [ ] Verify completed successfully

---

## Performance Checks

### Backend
1. [ ] Check backend logs for errors
2. [ ] Verify no memory leaks
3. [ ] Confirm API responds after scraping
4. [ ] Check database for new records

### Frontend
1. [ ] Check browser console for errors
2. [ ] Verify no memory leaks
3. [ ] Confirm UI remains responsive
4. [ ] Check network tab for failed requests

---

## Edge Cases

### Large Scrape
- **Config:** 5 subs × 5 keywords = 25 searches
- [ ] Verify doesn't timeout (10 min limit)
- [ ] Verify completes successfully
- [ ] Verify all data is saved

### Network Issues
- [ ] Disconnect internet during scrape
- [ ] Verify appropriate error message
- [ ] Reconnect and try again
- [ ] Verify works after reconnection

### Rapid Clicks
- [ ] Click "Start Scraping" multiple times quickly
- [ ] Verify only one scrape runs
- [ ] Verify button stays disabled during scraping

---

## Acceptance Criteria

All of the following must be true:

- [ ] ✅ No premature success messages
- [ ] ✅ Progress indicators show during scraping
- [ ] ✅ Time estimates are reasonable
- [ ] ✅ Success toast appears only after completion
- [ ] ✅ New posts appear immediately after completion
- [ ] ✅ New redditors appear immediately after completion
- [ ] ✅ Duplicate detection works correctly
- [ ] ✅ Error handling works properly
- [ ] ✅ UI state management is correct
- [ ] ✅ No console errors
- [ ] ✅ No backend errors
- [ ] ✅ Data persists in database

---

## Sign-Off

**Tester:** ___________________  
**Date:** ___________________  
**Result:** [ ] PASS  [ ] FAIL  

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________

---

## If Tests Fail

### Check These First
1. Backend is running on port 8002
2. Frontend is running on port 5173
3. Database connection is working
4. Environment variables are set
5. No firewall blocking requests

### Common Issues
- **Timeout errors:** Reduce number of subreddits/keywords
- **No new posts:** Try different keywords or subreddits
- **All duplicates:** Use different keywords or increase max age
- **API errors:** Check backend logs for details

### Get Help
- Check `SCRAPING_FIX_SUMMARY.md` for overview
- Check `SCRAPING_QUICK_GUIDE.md` for usage tips
- Check `BEFORE_AFTER_COMPARISON.md` for expected behavior
- Check backend logs: `api/logs/` or console output
- Check browser console for frontend errors
