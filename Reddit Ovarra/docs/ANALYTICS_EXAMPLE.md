# Subreddit Analytics Example

## What It Tracks

The analytics system automatically tracks:
- **Posts scraped** per subreddit
- **Relevant posts** found (conversion rate)
- **Performance over time** (multiple runs)
- **New subreddit discoveries** from post mentions

## Example Output

```
============================================================
📊 SUBREDDIT ANALYTICS REPORT
============================================================

📈 Total Pipeline Runs: 5
📅 Last Updated: 2024-11-17T22:45:30

🏆 TOP PERFORMING SUBREDDITS:
------------------------------------------------------------
1. r/CamGirlProblems
   Conversion: 27.3% (12/44 posts)
   Runs: 5

2. r/OnlyFansAdvice
   Conversion: 21.1% (8/38 posts)
   Runs: 5

3. r/CreatorAdvice
   Conversion: 15.6% (5/32 posts)
   Runs: 4

4. r/SexWorkersOnly
   Conversion: 8.3% (2/24 posts)
   Runs: 3

5. r/LegalAdvice
   Conversion: 3.3% (1/30 posts)
   Runs: 5

⚠️  LOW PERFORMING SUBREDDITS (Consider removing):
------------------------------------------------------------
   r/LegalAdvice: 3.3% (1/30 posts)

📋 ALL TRACKED SUBREDDITS:
------------------------------------------------------------
r/CamGirlProblems    | Posts:   44 | Relevant:  12 | Rate:  27.3%
r/CreatorAdvice      | Posts:   32 | Relevant:   5 | Rate:  15.6%
r/LegalAdvice        | Posts:   30 | Relevant:   1 | Rate:   3.3%
r/OnlyFansAdvice     | Posts:   38 | Relevant:   8 | Rate:  21.1%
r/SexWorkersOnly     | Posts:   24 | Relevant:   2 | Rate:   8.3%

============================================================

🔍 Discovered 3 new subreddits mentioned in posts:
   • r/OnlyFansCreators (NEW)
   • r/AdultContentCreator (NEW)
   • r/DMCAhelp (NEW)

💡 RECOMMENDED SUBREDDITS FOR NEXT RUN:
------------------------------------------------------------
r/CamGirlProblems, r/OnlyFansAdvice, r/CreatorAdvice
```

## How to Use

### 1. Automatic Tracking
Analytics are automatically updated after each pipeline run:
```bash
python3 pipeline.py --debug
# Analytics updated at the end
```

### 2. View Analytics Anytime
```bash
python3 scripts/view_analytics.py
```

### 3. Update from Latest Results
```bash
python3 scripts/view_analytics.py --update
```

### 4. Export Stats
```bash
python3 scripts/view_analytics.py --export my_stats.json
```

## Key Metrics

### Conversion Rate
**Formula:** `relevant_posts / total_posts`

- **High (>20%):** Excellent subreddit, keep prioritizing
- **Medium (10-20%):** Good subreddit, worth monitoring
- **Low (<10%):** Consider removing or reducing frequency

### Recommendations

Based on your analytics:

1. **Focus on high converters** - Allocate more keywords/time to top performers
2. **Remove low performers** - If a subreddit consistently shows <5% after 20+ posts, remove it
3. **Test new discoveries** - Try subreddits mentioned in posts
4. **Track trends** - Watch for declining conversion rates

## Data Storage

Stats are saved to `subreddit_stats.json`:
```json
{
  "subreddits": {
    "CamGirlProblems": {
      "total_posts": 44,
      "total_relevant": 12,
      "runs": 5,
      "conversion_rate": 0.273,
      "first_seen": "2024-11-17T18:30:00",
      "last_scraped": "2024-11-17T22:45:30"
    }
  },
  "last_updated": "2024-11-17T22:45:30",
  "total_runs": 5
}
```

## Advanced Usage

### Find New Subreddits
The system automatically scans posts for r/subreddit mentions and suggests new ones to try.

### A/B Testing
Run the pipeline with different subreddit combinations and compare conversion rates.

### Historical Tracking
Stats accumulate over time, showing long-term performance trends.
