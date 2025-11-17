# Subreddit Discovery Guide

## Quick Start

Discover new subreddits to add to your pipeline:

```bash
cd "Reddit Ovarra"
python3 scripts/discover_subreddits.py
```

This will use 4 different methods to find relevant subreddits and score them.

## Discovery Methods

### Method 1: Post Mentions
Scans posts in seed subreddit for `r/subreddit` mentions.

**Best for:** Finding communities that users naturally reference

### Method 2: Related Subreddits
Checks subreddit sidebar and description for related communities.

**Best for:** Finding officially linked communities

### Method 3: User Overlap
Finds where the same users post (user activity analysis).

**Best for:** Finding communities with similar audiences

### Method 4: Keyword Search
Searches Reddit-wide for your keywords to find relevant subreddits.

**Best for:** Finding communities you might not know about

## Usage Examples

### Basic Discovery
```bash
python3 scripts/discover_subreddits.py
```

### Custom Seed Subreddit
```bash
python3 scripts/discover_subreddits.py --seed OnlyFansAdvice
```

### Custom Keywords
```bash
python3 scripts/discover_subreddits.py --keywords "leak" "dmca" "stolen content" "piracy"
```

### Specific Methods Only
```bash
# Only use post mentions and user overlap
python3 scripts/discover_subreddits.py --methods posts users

# Only use keyword search
python3 scripts/discover_subreddits.py --methods search
```

### Increase Analysis Depth
```bash
python3 scripts/discover_subreddits.py --limit 100
```

## Scoring System

Subreddits are scored based on:

| Criteria | Points |
|----------|--------|
| Size (1K-100K subscribers) | +3.0 |
| Size (100K-500K subscribers) | +2.0 |
| Size (>500K subscribers) | +1.0 |
| Active users (>50 online) | +2.0 |
| NSFW subreddit | +1.0 |
| Relevant keywords in description | +1.0 each |

**Relevant keywords:** onlyfans, creator, content, cam, model, adult, nsfw, sex work

## Priority Levels

- **High Priority (≥5.0):** Add to DEFAULT_SUBREDDITS immediately
- **Medium Priority (3.0-4.9):** Test with a few runs first
- **Low Priority (<3.0):** Probably not worth it

## Example Output

```
============================================================
🔍 SUBREDDIT DISCOVERY TOOL
============================================================
Seed: r/CamGirlProblems
Keywords: onlyfans leak, dmca, content stolen, cam girl
Methods: all

🔍 Method 1: Scanning r/CamGirlProblems posts for mentions...
   Found 12 subreddits mentioned in posts

🔍 Method 2: Finding related subreddits to r/CamGirlProblems...
   Found 5 related subreddits

🔍 Method 3: Finding subreddits with user overlap...
   Found 8 subreddits with user overlap

🔍 Method 4: Searching Reddit-wide for keywords...
   Found 15 subreddits with relevant content

📊 TOTAL DISCOVERED: 28 unique subreddits

⏳ Fetching subreddit information and scoring...
   [1/28] r/onlyfanscreators: 7.0 points
   [2/28] r/contentcreation: 5.5 points
   [3/28] r/adultcontentcreator: 6.0 points
   ...

============================================================
🏆 TOP RECOMMENDED SUBREDDITS
============================================================

✅ HIGH PRIORITY (Score >= 5.0):

r/OnlyFansCreators
   Score: 7.0
   Subscribers: 45,230
   Active: 120
   NSFW: Yes
   Description: Community for OnlyFans content creators...

r/AdultContentCreator
   Score: 6.0
   Subscribers: 12,450
   Active: 85
   NSFW: Yes
   Description: Support and advice for adult content creators...

⚠️  MEDIUM PRIORITY (Score 3.0-4.9):
   r/ContentCreation        | Score: 5.5 | Subs: 89,234
   r/CreatorAdvice          | Score: 4.2 | Subs: 23,456
   r/DigitalPrivacy         | Score: 3.8 | Subs: 156,789

💡 SUGGESTED DEFAULT_SUBREDDITS:
------------------------------------------------------------
DEFAULT_SUBREDDITS = ['OnlyFansCreators', 'AdultContentCreator', 
                      'ContentCreation', 'CreatorAdvice', 'CamGirlProblems']

============================================================
✅ Discovery complete!
```

## Recommended Workflow

### 1. Run Discovery
```bash
python3 scripts/discover_subreddits.py
```

### 2. Test High-Priority Subreddits
Add top 2-3 to your pipeline and test:
```bash
python3 pipeline.py --subreddits CamGirlProblems OnlyFansCreators AdultContentCreator --max-age-days 7 --debug
```

### 3. Check Analytics
```bash
python3 scripts/view_analytics.py
```

### 4. Keep Winners, Drop Losers
After 2-3 runs, check conversion rates:
- Keep subreddits with >10% conversion
- Drop subreddits with <5% conversion after 20+ posts

### 5. Repeat Discovery
Run discovery again every month to find new communities.

## Manual Discovery Tips

### Reddit Search
Search for your keywords and see which subreddits appear:
```
site:reddit.com "onlyfans leak"
site:reddit.com "dmca help"
site:reddit.com "content stolen"
```

### Check Sidebars
Visit high-performing subreddits and check their sidebar for related communities.

### Follow User Activity
Find active users in your target subreddits and see where else they post.

### Monitor Trends
Watch for new subreddits mentioned in posts and comments.

## Subreddit Vetting Checklist

Before adding a new subreddit, check:

- [ ] **Rules allow helpful advice?** (no self-promotion rules)
- [ ] **Active community?** (posts in last 24 hours)
- [ ] **Relevant content?** (DMCA/leak/creator issues)
- [ ] **Size appropriate?** (not too big, not too small)
- [ ] **NSFW-friendly?** (if targeting adult creators)
- [ ] **Moderation active?** (not abandoned)

## Advanced: Niche Discovery

### For Specific Platforms
```bash
# OnlyFans specific
python3 scripts/discover_subreddits.py --seed OnlyFansAdvice --keywords "onlyfans" "OF" "subscribers"

# Cam sites specific
python3 scripts/discover_subreddits.py --seed CamGirlProblems --keywords "chaturbate" "stripchat" "cam"

# General creator issues
python3 scripts/discover_subreddits.py --seed CreatorAdvice --keywords "content" "creator" "monetization"
```

### For Specific Issues
```bash
# DMCA focused
python3 scripts/discover_subreddits.py --keywords "dmca" "copyright" "takedown" "piracy"

# Privacy focused
python3 scripts/discover_subreddits.py --keywords "doxxed" "privacy" "leaked" "exposed"

# Legal focused
python3 scripts/discover_subreddits.py --keywords "legal advice" "lawyer" "copyright law"
```

## Troubleshooting

### "Rate limit hit"
Wait 7 minutes and try again, or reduce `--limit`:
```bash
python3 scripts/discover_subreddits.py --limit 25
```

### "No high-priority subreddits found"
Try different keywords or seed subreddit:
```bash
python3 scripts/discover_subreddits.py --seed OnlyFansAdvice --keywords "help" "advice" "problem"
```

### "Subreddit info fetch failed"
Some subreddits are private or banned. The script will skip them automatically.

## Best Practices

1. **Run discovery monthly** - New communities emerge
2. **Test before committing** - Run 2-3 times before adding permanently
3. **Track performance** - Use analytics to validate choices
4. **Diversify** - Don't rely on just one subreddit
5. **Respect rules** - Always check subreddit rules before engaging
6. **Quality over quantity** - Better to have 3 great subreddits than 10 mediocre ones

---

**Pro Tip:** Combine discovery with analytics. Run discovery to find candidates, test them in the pipeline, then use analytics to keep only the best performers.
