# Code Reorganization Plan

## Current Structure (Messy)
```
LeadGen/
├── Reddit Ovarra/          # Main app folder (space in name!)
│   ├── *.py files          # Mixed together
│   ├── docs/               # Some docs
│   ├── scripts/            # Some scripts
│   └── tests mixed in
├── .kiro/                  # Spec files
├── UI_*.md                 # UI docs at root
├── *.md                    # Various docs at root
├── main.py                 # Duplicate at root
├── Procfile                # Deployment at root
└── requirements.txt        # At root
```

## New Structure (Clean & Professional)
```
LeadGen/
├── api/                    # FastAPI application
│   ├── __init__.py
│   ├── main.py            # FastAPI app
│   ├── models/            # Data models
│   │   └── reddit_post.py
│   ├── services/          # Business logic
│   │   ├── scraper_service.py
│   │   └── supabase_client.py
│   ├── routes/            # API endpoints (future)
│   │   └── __init__.py
│   └── utils/             # Utilities
│       └── api_utils.py
│
├── cli/                   # CLI tools
│   ├── __init__.py
│   ├── pipeline.py        # Main CLI pipeline
│   └── subreddit_analytics.py
│
├── scripts/               # Utility scripts
│   ├── discover_subreddits.py
│   ├── clear_test_data.py
│   └── test_scrape_debug.py
│
├── tests/                 # All tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_integration.py
│   ├── test_scraper_service.py
│   ├── test_supabase_client.py
│   └── run_integration_tests.sh
│
├── database/              # Database related
│   ├── supabase_schema.sql
│   └── migrations/        # Future migrations
│
├── docs/                  # All documentation
│   ├── api/              # API docs
│   │   ├── README.md
│   │   ├── QUICKSTART.md
│   │   ├── HOW_TO_RUN.md
│   │   └── SUPABASE_SETUP.md
│   ├── ui/               # UI docs
│   │   ├── UI_DESIGN_SPEC.md
│   │   ├── UI_MOCKUP.md
│   │   ├── UI_QUICK_START.md
│   │   └── UI_SUMMARY.md
│   ├── deployment/       # Deployment docs
│   │   ├── RAILWAY_DEPLOYMENT_GUIDE.md
│   │   └── RAILWAY_ENV_VARS.md
│   ├── specs/            # Feature specs
│   │   └── supabase-api-integration/
│   │       ├── requirements.md
│   │       ├── design.md
│   │       └── tasks.md
│   ├── guides/           # User guides
│   │   ├── SUBREDDIT_LIST.md
│   │   ├── SUBREDDIT_DISCOVERY.md
│   │   └── INTEGRATION_TEST_RESULTS.md
│   └── README.md         # Main docs index
│
├── config/               # Configuration
│   └── .env.example
│
├── deployment/           # Deployment files
│   ├── Procfile
│   ├── runtime.txt
│   └── nixpacks.toml
│
├── .gitignore
├── requirements.txt
├── README.md            # Main project README
└── .env                 # Local only (gitignored)
```

## Migration Steps

### Phase 1: Create New Structure
1. Create all new directories
2. Add __init__.py files for Python packages

### Phase 2: Move API Files
1. Move main.py → api/main.py
2. Move scraper_service.py → api/services/
3. Move supabase_client.py → api/services/
4. Move api_utils.py → api/utils/
5. Move models.py → api/models/reddit_post.py

### Phase 3: Move CLI Files
1. Move pipeline.py → cli/
2. Move subreddit_analytics.py → cli/

### Phase 4: Move Scripts
1. Move discover_subreddits.py → scripts/
2. Move clear_test_data.py → scripts/
3. Move test_scrape_debug.py → scripts/

### Phase 5: Move Tests
1. Move all test_*.py → tests/
2. Move run_integration_tests.sh → tests/

### Phase 6: Move Database Files
1. Move supabase_schema.sql → database/

### Phase 7: Move Documentation
1. Move all docs to docs/ with proper structure
2. Create docs/README.md as index

### Phase 8: Move Deployment Files
1. Move Procfile → deployment/
2. Move runtime.txt → deployment/
3. Move nixpacks.toml → deployment/

### Phase 9: Update Imports
1. Update all import statements
2. Update Procfile paths
3. Update test paths

### Phase 10: Clean Up
1. Remove old "Reddit Ovarra" folder
2. Remove duplicate files at root
3. Update .gitignore

## Import Changes Required

### api/main.py
```python
# Old
from scraper_service import scrape_and_save
from pipeline import DEFAULT_SUBREDDITS

# New
from api.services.scraper_service import scrape_and_save
from cli.pipeline import DEFAULT_SUBREDDITS
```

### api/services/scraper_service.py
```python
# Old
from models import RedditPost
from api_utils import fetch_reddit_posts
from supabase_client import check_duplicate

# New
from api.models.reddit_post import RedditPost
from api.utils.api_utils import fetch_reddit_posts
from api.services.supabase_client import check_duplicate
```

### api/services/supabase_client.py
```python
# No changes needed (uses external imports only)
```

## Procfile Changes

### Old
```
web: cd "Reddit Ovarra" && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### New
```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

## Benefits

1. ✅ **Clear Separation**: API, CLI, scripts, tests, docs
2. ✅ **Professional Structure**: Industry-standard layout
3. ✅ **Easy Navigation**: Find files quickly
4. ✅ **Scalable**: Easy to add new features
5. ✅ **Maintainable**: Clear responsibilities
6. ✅ **No Spaces**: Removed "Reddit Ovarra" folder name
7. ✅ **Python Package**: Proper __init__.py files
8. ✅ **Documentation Hub**: All docs in one place

## Testing Plan

After reorganization:
1. Test API locally: `uvicorn api.main:app --reload`
2. Test CLI: `python -m cli.pipeline`
3. Run tests: `python -m pytest tests/`
4. Test Railway deployment
5. Verify all imports work

## Rollback Plan

If anything breaks:
1. Git revert to previous commit
2. Fix specific issues
3. Re-apply changes incrementally
