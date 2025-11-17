# Reddit Ovarra Pipeline - Documentation

Complete documentation for the Reddit Ovarra lead generation pipeline.

## 📚 Documentation Index

### Getting Started
- **[Main README](../README.md)** - Overview, installation, and basic usage
- **[SETUP.md](../../SETUP.md)** - Detailed setup guide for Gemini API

### Features & Capabilities
- **[FEATURES.md](FEATURES.md)** - Complete feature list, configuration options, and roadmap

### Guides
- **[SCRIPTS.md](SCRIPTS.md)** - Utility scripts documentation
  - List posts
  - Regenerate replies
  - View analytics
  
- **[ANALYTICS_EXAMPLE.md](ANALYTICS_EXAMPLE.md)** - Subreddit analytics guide
  - Performance tracking
  - Conversion rates
  - Subreddit discovery
  - Recommendations

- **[SUBREDDIT_DISCOVERY.md](SUBREDDIT_DISCOVERY.md)** - Find new subreddits
  - 4 discovery methods
  - Automatic scoring
  - Testing workflow
  - Best practices

- **[SUBREDDIT_LIST.md](SUBREDDIT_LIST.md)** - Complete subreddit reference
  - 50+ creator-focused subreddits
  - Organized by priority & category
  - Conversion rate expectations
  - Rules & best practices

## 🚀 Quick Links

### Common Tasks

**First Time Setup:**
1. Read [SETUP.md](../../SETUP.md)
2. Get Gemini API key
3. Create `.env` file
4. Install dependencies
5. Run pipeline

**Running the Pipeline:**
```bash
cd "Reddit Ovarra"
python3 pipeline.py --debug
```

**View Results:**
```bash
python3 scripts/list_posts.py --show-replies
```

**Check Performance:**
```bash
python3 scripts/view_analytics.py
```

**Regenerate Replies:**
```bash
python3 scripts/regenerate_replies.py --debug
```

## 📖 Documentation Structure

```
Reddit Ovarra/
├── README.md                    # Main documentation
├── docs/
│   ├── README.md               # This file
│   ├── FEATURES.md             # Feature list & roadmap
│   ├── SCRIPTS.md              # Utility scripts guide
│   └── ANALYTICS_EXAMPLE.md    # Analytics examples
├── scripts/
│   ├── list_posts.py
│   ├── regenerate_replies.py
│   ├── regenerate_single.py
│   └── view_analytics.py
└── ...
```

## 🔍 Find What You Need

### I want to...

**...understand what this does**
→ Read [Main README](../README.md)

**...set it up for the first time**
→ Follow [SETUP.md](../../SETUP.md)

**...see all features**
→ Check [FEATURES.md](FEATURES.md)

**...use the utility scripts**
→ Read [SCRIPTS.md](SCRIPTS.md)

**...track subreddit performance**
→ See [ANALYTICS_EXAMPLE.md](ANALYTICS_EXAMPLE.md)

**...customize the pipeline**
→ Check [FEATURES.md](FEATURES.md) → Configuration Options

**...understand the reply generation**
→ Read [Main README](../README.md) → Pipeline Overview

**...troubleshoot issues**
→ Enable `--debug` flag and check logs

## 💡 Tips

- Always use `--debug` flag when testing
- Check analytics after each run to optimize subreddit selection
- Use `--force` to re-run with new settings
- Review generated replies before posting manually
- Start with 7-day time filter (`--max-age-days 7`) for fresh posts

## 🆘 Getting Help

1. Check relevant documentation above
2. Enable `--debug` for detailed output
3. Review example outputs in docs
4. Check GitHub issues
5. Read error messages carefully

## 📝 Contributing

When adding new features:
1. Update relevant documentation
2. Add examples if applicable
3. Update FEATURES.md roadmap
4. Keep docs in sync with code

---

**Last Updated:** November 2024
