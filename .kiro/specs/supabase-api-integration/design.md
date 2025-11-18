# Design Document

## Overview

This design transforms the existing Reddit scraper from a command-line tool into a production-ready FastAPI service with Supabase integration. The architecture maintains the existing scraper logic while adding database persistence, REST API endpoints, duplicate detection, and Railway deployment capabilities.

The system will expose two primary endpoints: one for triggering scrapes that save to Supabase, and another for retrieving recent suggestions. The design prioritizes minimal changes to existing scraper code while adding the necessary infrastructure for production use.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   API Client    │
│  (Product Team) │
└────────┬────────┘
         │
         │ HTTP Requests
         ▼
┌─────────────────────────────────────┐
│       FastAPI Service               │
│  ┌──────────────────────────────┐  │
│  │  POST /scrape                │  │
│  │  GET /suggestions            │  │
│  │  GET /health                 │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Existing Scraper Logic      │  │
│  │  - fetch_reddit_posts        │  │
│  │  - classify_posts_relevance  │  │
│  │  - fetch_and_attach_comments │  │
│  │  - generate_ovarra_replies   │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Supabase Client Layer       │  │
│  │  - insert_suggestion         │  │
│  │  - check_duplicate           │  │
│  │  - get_recent_suggestions    │  │
│  └──────────────────────────────┘  │
└─────────────┬───────────────────────┘
              │
              │ Supabase Client
              ▼
┌─────────────────────────────────────┐
│         Supabase Database           │
│  ┌──────────────────────────────┐  │
│  │  reddit_suggestions table    │  │
│  │  - id (uuid, PK)             │  │
│  │  - reddit_name (text)        │  │
│  │  - reddit_url (text, unique) │  │
│  │  - suggested_response (text) │  │
│  │  - status (text)             │  │
│  │  - created_at (timestamp)    │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Component Layers

1. **API Layer** (FastAPI): Handles HTTP requests, validation, and response formatting
2. **Business Logic Layer**: Existing scraper pipeline with minimal modifications
3. **Data Access Layer**: Supabase client wrapper for database operations
4. **Database Layer**: Supabase PostgreSQL with new reddit_suggestions table

## Components and Interfaces

### 1. FastAPI Application (`main.py`)

**Purpose**: Entry point for the API service, defines routes and handles HTTP lifecycle

**Key Components**:
- FastAPI app instance with CORS middleware
- Route handlers for /scrape, /suggestions, /health
- Environment variable loading and validation
- Startup/shutdown event handlers

**Interface**:
```python
# POST /scrape
Request Body:
{
  "subreddits": ["CamGirlProblems", "OnlyFansAdvice"],  # optional, defaults to DEFAULT_SUBREDDITS
  "keywords": ["leak", "stolen", "dmca"],                # optional, defaults to DEFAULT_KEYWORDS
  "post_limit": 10,                                      # optional, default 10
  "max_age_days": 120                                    # optional, default 120
}

Response:
{
  "status": "success",
  "processed": 15,
  "skipped": 3,
  "failed": 0,
  "message": "Scraping completed successfully"
}

# GET /suggestions?hours=24
Response:
{
  "suggestions": [
    {
      "id": "uuid",
      "reddit_name": "Post title",
      "reddit_url": "https://reddit.com/...",
      "suggested_response": "Generated reply text",
      "status": "new",
      "created_at": "2025-11-18T10:30:00Z"
    }
  ],
  "count": 5,
  "time_window_hours": 24
}

# GET /health
Response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-18T10:30:00Z"
}
```

### 2. Supabase Client Module (`supabase_client.py`)

**Purpose**: Abstraction layer for all Supabase database operations

**Key Functions**:

```python
def init_supabase_client() -> Client:
    """Initialize and return Supabase client using env vars"""
    
def check_duplicate(reddit_url: str) -> bool:
    """Check if reddit_url already exists in database"""
    
def insert_suggestion(reddit_name: str, reddit_url: str, suggested_response: str) -> dict:
    """Insert new suggestion into database, return inserted row"""
    
def get_recent_suggestions(hours: int = 24) -> list[dict]:
    """Retrieve suggestions created within last N hours"""
    
def test_connection() -> bool:
    """Test database connectivity for health checks"""
```

**Error Handling**:
- Catch and log Supabase API errors
- Return None or empty list on failures
- Raise custom exceptions for critical failures (connection issues)

### 3. Scraper Integration Module (`scraper_service.py`)

**Purpose**: Bridge between existing scraper logic and new API/database requirements

**Key Functions**:

```python
def scrape_and_save(
    subreddits: list[str],
    keywords: list[str],
    post_limit: int,
    max_age_days: int
) -> dict:
    """
    Execute scraper pipeline and save results to Supabase
    Returns: {processed: int, skipped: int, failed: int}
    """
    # 1. Scrape posts using existing fetch_reddit_posts
    # 2. Classify relevance using existing classify_posts_relevance
    # 3. For each relevant post:
    #    a. Check if duplicate (skip if exists)
    #    b. Fetch comments using existing fetch_and_attach_comments
    #    c. Generate reply using existing generate_ovarra_replies
    #    d. Insert to Supabase
    # 4. Return summary statistics
```

**Design Decision**: This module wraps the existing pipeline functions rather than modifying them directly, preserving the ability to run the scraper as a CLI tool if needed.

### 4. Modified Pipeline Module (`pipeline.py`)

**Changes Required**:
- Extract core functions into reusable units (already done)
- No structural changes needed - existing functions remain intact
- CLI functionality preserved for local testing

**Rationale**: The existing `api_utils.py` already provides well-structured functions that can be imported and used by the new service layer.

## Data Models

### Database Schema

```sql
CREATE TABLE reddit_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reddit_name TEXT NOT NULL,
    reddit_url TEXT NOT NULL UNIQUE,
    suggested_response TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'approved', 'sent', 'ignored')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for efficient recent queries
CREATE INDEX idx_reddit_suggestions_created_at ON reddit_suggestions(created_at DESC);

-- Index for duplicate checking
CREATE UNIQUE INDEX idx_reddit_suggestions_url ON reddit_suggestions(reddit_url);
```

### Pydantic Models

```python
# Request models
class ScrapeRequest(BaseModel):
    subreddits: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    post_limit: Optional[int] = 10
    max_age_days: Optional[int] = 120

# Response models
class SuggestionResponse(BaseModel):
    id: str
    reddit_name: str
    reddit_url: str
    suggested_response: str
    status: str
    created_at: datetime

class ScrapeResponse(BaseModel):
    status: str
    processed: int
    skipped: int
    failed: int
    message: str

class SuggestionsListResponse(BaseModel):
    suggestions: List[SuggestionResponse]
    count: int
    time_window_hours: int

class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime
```

## Error Handling

### Error Categories and Responses

1. **Client Errors (4xx)**
   - Invalid request parameters → 400 Bad Request
   - Missing required fields → 422 Unprocessable Entity
   - Example: `{"detail": "post_limit must be between 1 and 100"}`

2. **Server Errors (5xx)**
   - Database connection failures → 503 Service Unavailable
   - Supabase API errors → 500 Internal Server Error
   - Gemini API failures → 500 Internal Server Error (log and continue for individual posts)

3. **Partial Failures**
   - Some posts fail to process → Return 200 with failure count in response
   - Example: `{"status": "partial", "processed": 10, "failed": 2}`

### Logging Strategy

```python
# Use Python logging module with structured logs
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log levels:
# INFO: API requests, successful operations, summary statistics
# WARNING: Skipped duplicates, partial failures
# ERROR: Database errors, API failures, unexpected exceptions
# DEBUG: Detailed scraper progress (disabled in production)
```

### Retry Logic

- **Reddit API**: Already implemented in existing code (max 3 retries with exponential backoff)
- **Gemini API**: Already implemented (rate limit handling with 60s wait)
- **Supabase**: Add retry for transient network errors (max 2 retries with 5s delay)

## Testing Strategy

### Unit Tests

**Target Coverage**: Core business logic and data access layer

```python
# tests/test_supabase_client.py
- test_check_duplicate_exists()
- test_check_duplicate_not_exists()
- test_insert_suggestion_success()
- test_insert_suggestion_duplicate()
- test_get_recent_suggestions_24h()
- test_get_recent_suggestions_empty()

# tests/test_scraper_service.py
- test_scrape_and_save_success()
- test_scrape_and_save_skip_duplicates()
- test_scrape_and_save_partial_failure()
```

**Mocking Strategy**:
- Mock Supabase client for unit tests
- Mock Reddit API responses
- Mock Gemini API responses

### Integration Tests

**Target**: End-to-end API flows with real Supabase (test database)

```python
# tests/test_api_integration.py
- test_scrape_endpoint_success()
- test_scrape_endpoint_validation()
- test_suggestions_endpoint_recent()
- test_suggestions_endpoint_time_window()
- test_health_endpoint()
```

### Manual Testing Checklist

1. Deploy to Railway staging environment
2. Trigger scrape with default parameters
3. Verify data appears in Supabase
4. Query suggestions endpoint
5. Trigger duplicate scrape (verify skips)
6. Test with invalid parameters
7. Monitor logs for errors

## Deployment Configuration

### Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GEMINI_API_KEY=your-gemini-key

# Optional (Railway provides PORT)
PORT=8000
```

### Railway Configuration

**Option 1: Procfile**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Option 2: railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Dependencies (`requirements.txt`)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
supabase==2.0.3
python-dotenv==1.0.0
pydantic==2.5.0
requests==2.31.0
google-generativeai==0.3.1
textblob==0.17.1
```

### Project Structure

```
Reddit Ovarra/
├── main.py                    # FastAPI app entry point
├── supabase_client.py         # Database operations
├── scraper_service.py         # Scraper integration
├── api_utils.py               # Existing scraper functions (unchanged)
├── models.py                  # Existing data models (unchanged)
├── pipeline.py                # Existing CLI tool (unchanged)
├── requirements.txt           # Python dependencies
├── Procfile                   # Railway start command
├── .env                       # Local environment variables (gitignored)
├── .env.example               # Template for env vars
└── README.md                  # Updated with API documentation
```

## Design Decisions and Rationale

### 1. FastAPI over Flask
**Decision**: Use FastAPI
**Rationale**: 
- Built-in request validation with Pydantic
- Automatic OpenAPI documentation
- Better async support for future scaling
- Type hints improve code quality

### 2. Duplicate Check Before Processing
**Decision**: Check for duplicates before generating responses
**Rationale**:
- Saves Gemini API costs (avoid generating responses for known posts)
- Reduces processing time
- Unique constraint on reddit_url provides database-level safety

### 3. Preserve Existing CLI Tool
**Decision**: Keep pipeline.py unchanged, create new service layer
**Rationale**:
- Allows local testing without API overhead
- Maintains backward compatibility
- Separation of concerns (CLI vs API)

### 4. No Authentication Initially
**Decision**: Deploy without API authentication
**Rationale**:
- Aaron's requirement focuses on core functionality first
- Can add API keys or OAuth later if needed
- Railway provides network-level security

### 5. Synchronous Processing
**Decision**: Process scrapes synchronously (blocking)
**Rationale**:
- Simpler implementation for MVP
- Scraping typically completes in 1-2 minutes
- Can add async/background tasks later if needed

### 6. Status Field Design
**Decision**: Use simple text enum for status
**Rationale**:
- Product team needs to track lifecycle
- Simple values easy to filter and update
- Can extend with more statuses later (e.g., "failed", "retrying")

## Migration Path

### Phase 1: Local Development
1. Create new API files (main.py, supabase_client.py, scraper_service.py)
2. Test locally with Supabase
3. Verify existing CLI tool still works

### Phase 2: Railway Deployment
1. Create Railway project
2. Add environment variables
3. Deploy and test endpoints
4. Monitor logs for issues

### Phase 3: Product Integration
1. Share API documentation with product team
2. Product team integrates GET /suggestions endpoint
3. Set up scheduled scraping (cron job or Railway cron)

## Security Considerations

1. **Environment Variables**: Never commit SUPABASE_KEY or GEMINI_API_KEY
2. **SQL Injection**: Supabase client handles parameterization
3. **Rate Limiting**: Consider adding rate limits to prevent abuse (future enhancement)
4. **CORS**: Configure allowed origins for production
5. **Input Validation**: Pydantic models validate all inputs
