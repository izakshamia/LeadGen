# Utility Scripts

Helper scripts for working with the Reddit Ovarra pipeline without re-running the entire flow.

## Scripts

### 1. `list_posts.py` - View Posts
List all posts from checkpoint files with their details.

```bash
# List posts with comments
python3 scripts/list_posts.py

# List from a specific file
python3 scripts/list_posts.py --file relevant_posts.json

# Show existing replies
python3 scripts/list_posts.py --show-replies

# Show comment counts
python3 scripts/list_posts.py --show-comments
```

### 2. `regenerate_replies.py` - Regenerate All Replies
Regenerate Ovarra replies for all existing relevant posts without re-running scraping/classification.

```bash
# Regenerate all replies
python3 scripts/regenerate_replies.py

# With debug output
python3 scripts/regenerate_replies.py --debug

# Custom input/output files
python3 scripts/regenerate_replies.py --input posts_with_comments.json --output final_posts.json
```

**Use cases:**
- Testing new reply prompts
- Updating reply tone/style
- Fixing replies that didn't work well

### 3. `regenerate_single.py` - Regenerate One Reply
Regenerate reply for a specific post by index or URL.

### 4. `view_analytics.py` - Subreddit Performance Analytics
View performance metrics and discover high-converting subreddits.

```bash
# Regenerate post #3
python3 scripts/regenerate_single.py --index 3

# Regenerate by URL
python3 scripts/regenerate_single.py --url "https://reddit.com/r/CamGirlProblems/..."

# With debug output
python3 scripts/regenerate_single.py --index 5 --debug
```

**Use cases:**
- Testing reply generation on specific posts
- Iterating on difficult posts
- Quick testing without processing all posts

```bash
# View current analytics
python3 scripts/view_analytics.py

# Update analytics from latest pipeline run
python3 scripts/view_analytics.py --update

# Export stats to JSON
python3 scripts/view_analytics.py --export stats_backup.json
```

**Features:**
- Track conversion rates per subreddit
- Identify top-performing subreddits
- Discover new subreddits mentioned in posts
- Find low-performing subreddits to remove
- Get recommendations for next run

## Workflow Examples

### Example 1: Test New Reply Prompt
```bash
# 1. Edit api_utils.py to change the reply prompt
# 2. Regenerate all replies
python3 scripts/regenerate_replies.py --debug

# 3. Review results
python3 scripts/list_posts.py --show-replies
```

### Example 2: Fix One Bad Reply
```bash
# 1. List posts to find the index
python3 scripts/list_posts.py --show-replies

# 2. Regenerate that specific post
python3 scripts/regenerate_single.py --index 7 --debug

# 3. Check the new reply
python3 scripts/list_posts.py --show-replies
```

### Example 3: Quick Testing
```bash
# Test on just one post before regenerating all
python3 scripts/regenerate_single.py --index 1 --debug

# If it looks good, regenerate all
python3 scripts/regenerate_replies.py
```

## File Locations

All scripts work from the `Reddit Ovarra/` directory and use these checkpoint files:
- `scraped_posts.json` - All scraped posts
- `relevant_posts.json` - Classified as relevant
- `posts_with_comments.json` - With comments fetched
- `final_posts.json` - With Ovarra replies

## Notes

- Scripts automatically import from parent directory
- Run from `Reddit Ovarra/` directory
- Requires `.env` file with `GEMINI_API_KEY`
- Uses same API configuration as main pipeline
