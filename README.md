# Reddit Ovarra - AI-Powered DMCA Response System

A complete system for discovering, classifying, and responding to Reddit posts about content leaks and DMCA issues, with AI-generated empathetic replies.

## 🎯 What It Does

- **Scrapes Reddit** for posts about content leaks, DMCA takedowns, and copyright issues
- **Classifies Posts** using AI to identify relevant content creator problems
- **Generates Replies** with tactical, expert-level advice using Google Gemini
- **Stores in Supabase** with duplicate detection and status management
- **Provides REST API** for integration with frontends and automation

## 🚀 Quick Start

### API Server (Production)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/.env.example .env
# Edit .env with your API keys

# Run the API
uvicorn api.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### CLI Tool (Development)
```bash
# Run the scraping pipeline
python -m cli.pipeline --post-limit 10 --max-age-days 30

# View analytics
python -m cli.subreddit_analytics
```

## 📦 Project Structure

```
LeadGen/
├── api/                    # FastAPI REST API
│   ├── main.py            # API endpoints
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
│
├── cli/                   # Command-line tools
│   ├── pipeline.py        # Main scraping pipeline
│   └── subreddit_analytics.py
│
├── scripts/               # Utility scripts
│   ├── discover_subreddits.py
│   ├── clear_test_data.py
│   └── test_scrape_debug.py
│
├── tests/                 # All tests
│   ├── test_api.py
│   ├── test_integration.py
│   └── test_scraper_service.py
│
├── database/              # Database schemas
│   └── supabase_schema.sql
│
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── ui/               # UI design specs
│   ├── deployment/       # Deployment guides
│   ├── specs/            # Feature specifications
│   └── guides/           # User guides
│
├── deployment/           # Deployment configuration
│   ├── Procfile
│   ├── runtime.txt
│   └── nixpacks.toml
│
└── config/               # Configuration
    └── .env.example
```

## 🔌 API Endpoints

### Live API
**Production**: https://web-production-3fe3.up.railway.app

### Endpoints

#### Health Check
```bash
GET /health
```
Returns API and database status.

#### Trigger Scraping
```bash
POST /scrape
Content-Type: application/json

{
  "subreddits": ["CamGirlProblems", "OnlyFansAdvice"],
  "keywords": ["leak", "dmca", "stolen"],
  "post_limit": 10,
  "max_age_days": 30
}
```
Scrapes Reddit, classifies posts, generates replies, and saves to database.

#### Get Suggestions
```bash
GET /suggestions?hours=24
```
Retrieves recent suggestions with AI-generated replies.

## 🎨 UI Design

Complete UI design specifications are available in `docs/ui/`:
- **UI_DESIGN_SPEC.md** - Detailed component specifications
- **UI_MOCKUP.md** - Visual mockups
- **UI_QUICK_START.md** - Implementation guide
- **UI_SUMMARY.md** - Executive overview

Estimated build time: 6-9 hours for complete UI.

## 🗄️ Database

Uses Supabase PostgreSQL with the following schema:

```sql
CREATE TABLE reddit_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reddit_name TEXT NOT NULL,
    reddit_url TEXT NOT NULL UNIQUE,
    suggested_response TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

See `database/supabase_schema.sql` for complete schema.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run integration tests
python tests/test_integration.py

# Run API tests
python tests/test_api.py

# Test scraper service
python tests/test_scraper_service.py
```

## 🚀 Deployment

### Railway (Recommended)
1. Connect GitHub repository
2. Add environment variables:
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Deploy automatically

See `docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md` for detailed instructions.

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp config/.env.example .env
# Edit .env with your credentials

# Run API server
uvicorn api.main:app --reload --port 8000

# Run CLI pipeline
python -m cli.pipeline --debug
```

## 📚 Documentation

### API Documentation
- [API README](docs/api/README.md) - Complete API guide
- [Quick Start](docs/api/QUICKSTART.md) - Get started quickly
- [How to Run](docs/api/HOW_TO_RUN.md) - Detailed running instructions
- [Supabase Setup](docs/api/SUPABASE_SETUP.md) - Database configuration

### UI Documentation
- [UI Design Spec](docs/ui/UI_DESIGN_SPEC.md) - Complete UI specifications
- [UI Mockups](docs/ui/UI_MOCKUP.md) - Visual mockups
- [UI Quick Start](docs/ui/UI_QUICK_START.md) - Build the UI
- [UI Summary](docs/ui/UI_SUMMARY.md) - Executive overview

### Deployment Documentation
- [Railway Deployment](docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md) - Deploy to Railway
- [Environment Variables](docs/deployment/RAILWAY_ENV_VARS.md) - Configuration guide

### Feature Specifications
- [Requirements](docs/specs/supabase-api-integration/requirements.md) - EARS-compliant requirements
- [Design](docs/specs/supabase-api-integration/design.md) - System design
- [Tasks](docs/specs/supabase-api-integration/tasks.md) - Implementation plan

### Guides
- [Subreddit List](docs/guides/SUBREDDIT_LIST.md) - Target subreddits
- [Subreddit Discovery](docs/guides/SUBREDDIT_DISCOVERY.md) - Finding new subreddits
- [Integration Tests](docs/guides/INTEGRATION_TEST_RESULTS.md) - Test results

## 🔧 Configuration

### Required Environment Variables

```bash
# Google Gemini API (for AI classification and reply generation)
GEMINI_API_KEY=your_gemini_api_key

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key
```

See `config/.env.example` for complete configuration template.

## 🛠️ Development

### Prerequisites
- Python 3.10+
- pip
- Supabase account
- Google Gemini API key

### Setup
```bash
# Clone repository
git clone https://github.com/izakshamia/LeadGen.git
cd LeadGen

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example .env
# Edit .env with your credentials

# Set up database
# Run database/supabase_schema.sql in Supabase SQL editor

# Run tests
python -m pytest tests/

# Start development server
uvicorn api.main:app --reload
```

## 📊 Features

### Core Features
- ✅ Reddit post scraping with keyword search
- ✅ AI-powered relevance classification
- ✅ Duplicate detection and prevention
- ✅ Comment thread fetching
- ✅ AI-generated tactical replies
- ✅ Supabase database integration
- ✅ REST API with FastAPI
- ✅ Time-based filtering
- ✅ Status management (new, approved, sent, ignored)
- ✅ Comprehensive testing suite

### CLI Features
- ✅ Checkpoint-based pipeline
- ✅ Subreddit discovery
- ✅ Analytics and performance tracking
- ✅ Debug mode
- ✅ Force re-run option

### API Features
- ✅ Health check endpoint
- ✅ Scraping trigger endpoint
- ✅ Suggestions retrieval endpoint
- ✅ Interactive API documentation (Swagger UI)
- ✅ CORS support
- ✅ Error handling and logging

## 🎯 Use Cases

1. **Content Creator Support** - Help creators dealing with leaks
2. **DMCA Assistance** - Provide tactical takedown advice
3. **Community Monitoring** - Track discussions about content protection
4. **Automated Outreach** - Generate personalized responses at scale
5. **Analytics** - Understand common creator problems

## 🤝 Contributing

This is a private project. For questions or issues, contact the repository owner.

## 📄 License

Private - All rights reserved.

## 🔗 Links

- **Live API**: https://web-production-3fe3.up.railway.app
- **API Docs**: https://web-production-3fe3.up.railway.app/docs
- **GitHub**: https://github.com/izakshamia/LeadGen

## 📞 Support

For documentation, see the `docs/` directory:
- API questions → `docs/api/`
- UI questions → `docs/ui/`
- Deployment questions → `docs/deployment/`
- Feature specs → `docs/specs/`

---

**Built with**: Python, FastAPI, Supabase, Google Gemini AI

**Status**: ✅ Production-ready and deployed

**Last Updated**: November 2025
