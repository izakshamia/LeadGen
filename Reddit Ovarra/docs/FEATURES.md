# Reddit Ovarra Pipeline - Features

## Core Features

### 1. Intelligent Post Scraping
- ✅ Multi-subreddit support (5 default subreddits)
- ✅ Multi-keyword search (6 default keywords)
- ✅ Time-based filtering (default: 4 months, configurable)
- ✅ Rate limiting to avoid Reddit bans
- ✅ Automatic retry on rate limit errors
- ✅ Checkpoint system (resume from failures)

### 2. AI-Powered Classification
- ✅ Uses Gemini 2.0 Flash (fast & free)
- ✅ Filters for OnlyFans/NSFW creator posts only
- ✅ Ignores general copyright discussions
- ✅ Batch processing for efficiency
- ✅ Configurable batch sizes

### 3. Full Comment Tree Fetching
- ✅ Fetches all comments and nested replies
- ✅ Preserves conversation hierarchy
- ✅ Handles rate limiting gracefully
- ✅ Retry logic for failed requests

### 4. Expert-Level Reply Generation
- ✅ Tactical, actionable advice
- ✅ Authority signals (statistics, experience)
- ✅ Specific search operators and techniques
- ✅ Insider knowledge only practitioners know
- ✅ No generic empathy or promotional content
- ✅ Subreddit rule compliant

### 5. Subreddit Analytics
- ✅ Track conversion rates per subreddit
- ✅ Identify top performers
- ✅ Find low performers to remove
- ✅ Auto-discover new subreddits from mentions
- ✅ Historical performance tracking
- ✅ Recommendations for next run

### 6. Utility Scripts
- ✅ List posts with details
- ✅ Regenerate all replies
- ✅ Regenerate single reply by index/URL
- ✅ View analytics dashboard
- ✅ Export stats to JSON

## Configuration Options

### Command Line Arguments

```bash
--subreddits SUB1 SUB2    # Custom subreddit list
--keywords KW1 KW2        # Custom keywords
--post-limit N            # Posts per keyword (default: 10)
--max-age-days N          # Post age filter (default: 120)
--discover                # Auto-discover related subreddits
--seed-subreddit SUB      # Seed for discovery
--debug                   # Verbose output
--force                   # Ignore checkpoints, re-run all
```

### Environment Variables

```bash
GEMINI_API_KEY           # Google Gemini API key (required)
GOOGLE_API_KEY           # For SocialMedia tools (optional)
GOOGLE_CSE_ID            # For SocialMedia tools (optional)
```

## Checkpoint System

Saves progress after each step:
1. `scraped_posts.json` - After scraping
2. `relevant_posts.json` - After classification
3. `posts_with_comments.json` - After fetching comments
4. `final_posts.json` - After generating replies

Resume from any checkpoint automatically!

## Rate Limiting

### Reddit API
- 3 seconds between search requests
- Automatic retry on 429 errors
- Respects Retry-After headers

### Gemini API
- 1.5 seconds between classification batches
- 2 seconds between reply generations
- Free tier: 15 RPM, 1500 requests/day

## Compliance Features

### Subreddit Rules
- ✅ No promotional content
- ✅ No service/company mentions
- ✅ Educational advice only
- ✅ Peer-to-peer tone
- ✅ Authentic, not corporate

### Best Practices
- ✅ Manual review recommended before posting
- ✅ DM outreach for strict subreddits
- ✅ Build reputation before promoting
- ✅ Track which subreddits allow what

## Performance Metrics

### Typical Run (5 subreddits, 6 keywords, 10 posts each)
- **Scraping:** ~5 minutes (with rate limiting)
- **Classification:** ~2 minutes (50 batches × 1.5s)
- **Comments:** ~3 minutes (depends on post count)
- **Replies:** ~1 minute (depends on relevant posts)
- **Total:** ~10-15 minutes

### API Costs
- **Gemini:** FREE (within 1500 requests/day)
- **Reddit:** FREE (public API)

## Data Privacy

### What's Stored Locally
- Scraped posts (public Reddit data)
- Classification results
- Generated replies
- Analytics stats

### What's NOT Stored
- API keys (in .env, gitignored)
- Personal information
- Private messages

### What's NOT Committed to Git
- .env file
- Checkpoint JSON files
- Analytics stats
- Scraped data

## Future Enhancements (Roadmap)

### Planned Features
- [ ] Automated posting via Reddit API
- [ ] Multi-platform support (Twitter, Discord)
- [ ] Reply quality scoring
- [ ] A/B testing framework
- [ ] Web dashboard for analytics
- [ ] Scheduled runs (cron integration)
- [ ] Email notifications for high-value posts
- [ ] Reply templates library
- [ ] Sentiment analysis
- [ ] Competitor monitoring

### Under Consideration
- [ ] Local LLM support (privacy)
- [ ] Browser extension for manual review
- [ ] Mobile app for notifications
- [ ] Team collaboration features
- [ ] CRM integration

## Support

### Documentation
- `README.md` - Main documentation
- `SETUP.md` - Installation guide
- `scripts/README.md` - Utility scripts
- `ANALYTICS_EXAMPLE.md` - Analytics guide
- `FEATURES.md` - This file

### Getting Help
- Check documentation first
- Review example outputs
- Enable `--debug` flag for troubleshooting
- Check GitHub issues

## License

See LICENSE file in repository.
