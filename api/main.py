"""
FastAPI application for Reddit Ovarra API service.
Provides endpoints for scraping Reddit posts and retrieving suggestions from Supabase.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Reddit Ovarra API",
    description="API service for scraping Reddit posts and managing Ovarra reply suggestions",
    version="1.0.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI application initialized successfully")


# ============================================================================
# Pydantic Models
# ============================================================================

class ScrapeRequest(BaseModel):
    """Request model for POST /scrape endpoint"""
    subreddits: Optional[List[str]] = Field(
        None,
        description="List of subreddit names to search"
    )
    keywords: Optional[List[str]] = Field(
        None,
        description="List of keywords to search for"
    )
    post_limit: Optional[int] = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of posts per keyword (1-100)"
    )
    max_age_days: Optional[int] = Field(
        120,
        ge=1,
        le=365,
        description="Only fetch posts from last N days (1-365)"
    )


class ScrapeAcceptedResponse(BaseModel):
    """Response model for POST /scrape when accepted"""
    message: str = Field(description="Message indicating that the scrape has been started")

class SuggestionResponse(BaseModel):
    """Response model for individual suggestion"""
    id: str = Field(description="Unique identifier (UUID)")
    reddit_name: str = Field(description="Reddit post title")
    reddit_url: str = Field(description="Reddit post URL")
    suggested_response: str = Field(description="Generated Ovarra reply")
    status: str = Field(description="Suggestion status (new, approved, sent, ignored)")
    created_at: datetime = Field(description="Timestamp when suggestion was created")


class SuggestionsListResponse(BaseModel):
    """Response model for GET /suggestions endpoint"""
    suggestions: List[SuggestionResponse] = Field(description="List of suggestions")
    count: int = Field(description="Number of suggestions returned")
    time_window_hours: int = Field(description="Time window used for filtering")


class HealthResponse(BaseModel):
    """Response model for GET /health endpoint"""
    status: str = Field(description="Service status (healthy, unhealthy)")
    database: str = Field(description="Database connection status (connected, disconnected)")
    timestamp: datetime = Field(description="Current server timestamp")


class RedditorResponse(BaseModel):
    """Response model for individual target redditor"""
    id: str = Field(description="Unique identifier (UUID)")
    username: str = Field(description="Reddit username")
    account_age_days: Optional[int] = Field(None, description="Account age in days")
    total_karma: Optional[int] = Field(None, description="Total karma")
    comment_karma: Optional[int] = Field(None, description="Comment karma")
    post_karma: Optional[int] = Field(None, description="Post karma")
    authenticity_score: int = Field(description="Authenticity score (0-100)")
    need_score: int = Field(description="Need score (0-100)")
    priority: str = Field(description="Priority level (high, medium, low)")
    is_authentic: bool = Field(description="Whether account is authentic")
    is_active: bool = Field(description="Whether account is active")
    source_posts: List[str] = Field(description="URLs where redditor was found")
    first_seen: datetime = Field(description="First time redditor was discovered")
    last_updated: datetime = Field(description="Last time redditor data was updated")
    social_links: Optional[Dict] = Field(None, description="Social media links (platform: url)")


class RedditorsListResponse(BaseModel):
    """Response model for GET /redditors endpoint"""
    redditors: List[RedditorResponse] = Field(description="List of target redditors")
    count: int = Field(description="Number of redditors returned")
    limit: int = Field(description="Limit used for pagination")
    offset: int = Field(description="Offset used for pagination")


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/scrape", response_model=ScrapeAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def scrape_reddit(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Trigger Reddit scraping in the background.
    
    This endpoint adds the scraping task to a background queue
    and returns immediately with a 202 Accepted response.
    
    Args:
        request: ScrapeRequest with optional parameters
        background_tasks: FastAPI background tasks dependency
        
    Returns:
        ScrapeAcceptedResponse confirming the task has started
    """
    from services.scraper_service import scrape_and_save
    from cli.pipeline import DEFAULT_SUBREDDITS, DEFAULT_KEYWORDS
    
    # Use defaults from pipeline.py if not provided
    subreddits = request.subreddits if request.subreddits else DEFAULT_SUBREDDITS
    keywords = request.keywords if request.keywords else DEFAULT_KEYWORDS
    post_limit = request.post_limit if request.post_limit else 10
    max_age_days = request.max_age_days if request.max_age_days else 120
    
    logger.info(f"POST /scrape - Adding scrape task to background: subreddits={subreddits}, keywords={keywords}")
    
    # Add the long-running task to the background
    background_tasks.add_task(
        scrape_and_save,
        subreddits=subreddits,
        keywords=keywords,
        post_limit=post_limit,
        max_age_days=max_age_days
    )
    
    return ScrapeAcceptedResponse(message="Scraping process started in the background.")


@app.get("/suggestions", response_model=SuggestionsListResponse, status_code=status.HTTP_200_OK)
async def get_suggestions(hours: int = 24):
    """
    Retrieve recent suggestions from Supabase.
    
    Returns suggestions created within the specified time window,
    ordered by creation time (newest first).
    
    Args:
        hours: Time window in hours (default: 24)
        
    Returns:
        SuggestionsListResponse with filtered suggestions
        
    Raises:
        HTTPException: 500 if database query fails
    """
    from services.supabase_client import get_recent_suggestions
    
    logger.info(f"GET /suggestions - hours={hours}")
    
    try:
        # Retrieve suggestions from database
        suggestions_data = get_recent_suggestions(hours=hours)
        
        # Convert to response models
        suggestions = [
            SuggestionResponse(
                id=s["id"],
                reddit_name=s["reddit_name"],
                reddit_url=s["reddit_url"],
                suggested_response=s["suggested_response"],
                status=s["status"],
                created_at=s["created_at"]
            )
            for s in suggestions_data
        ]
        
        response = SuggestionsListResponse(
            suggestions=suggestions,
            count=len(suggestions),
            time_window_hours=hours
        )
        
        logger.info(f"GET /suggestions completed - returned {len(suggestions)} suggestions")
        return response
        
    except Exception as e:
        logger.error(f"GET /suggestions failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve suggestions: {str(e)}"
        )


@app.get("/redditors", response_model=RedditorsListResponse, status_code=status.HTTP_200_OK)
async def get_redditors(limit: int = 50, offset: int = 0):
    """
    Retrieve target Redditors from the database.
    
    Returns Redditors sorted by need_score (highest first) to prioritize
    the most promising leads for outreach campaigns.
    
    Args:
        limit: Maximum number of redditors to return (default: 50)
        offset: Number of records to skip for pagination (default: 0)
        
    Returns:
        RedditorsListResponse with filtered redditors
        
    Raises:
        HTTPException: 500 if database query fails
    """
    from services.supabase_client import get_target_redditors
    
    logger.info(f"GET /redditors - limit={limit}, offset={offset}")
    
    try:
        # Retrieve redditors from database
        redditors_data = get_target_redditors(limit=limit, offset=offset)
        
        # Convert to response models
        redditors = [
            RedditorResponse(
                id=r["id"],
                username=r["username"],
                account_age_days=r.get("account_age_days"),
                total_karma=r.get("total_karma"),
                comment_karma=r.get("comment_karma"),
                post_karma=r.get("post_karma"),
                authenticity_score=r["authenticity_score"],
                need_score=r["need_score"],
                priority=r["priority"],
                is_authentic=r["is_authentic"],
                is_active=r["is_active"],
                source_posts=r["source_posts"],
                first_seen=r["first_seen"],
                last_updated=r["last_updated"],
                social_links=r.get("social_links")
            )
            for r in redditors_data
        ]
        
        response = RedditorsListResponse(
            redditors=redditors,
            count=len(redditors),
            limit=limit,
            offset=offset
        )
        
        logger.info(f"GET /redditors completed - returned {len(redditors)} redditors")
        return response
        
    except Exception as e:
        logger.error(f"GET /redditors failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve redditors: {str(e)}"
        )


@app.post("/redditors/fetch-profiles")
async def fetch_redditor_profiles():
    """
    Fetch Reddit profile data for redditors without profile info.
    
    Finds redditors with missing profile data (account_age_days = 0 or total_karma = 0)
    and fetches their real profile data from Reddit API.
    
    Returns:
        Dictionary with fetch results (total, success, failed, not_found)
        
    Raises:
        HTTPException: 500 if fetch fails
    """
    try:
        from services.redditor_profile_fetcher import fetch_profiles_for_new_redditors
        
        logger.info("POST /redditors/fetch-profiles - starting profile fetch")
        
        results = fetch_profiles_for_new_redditors()
        
        logger.info(f"POST /redditors/fetch-profiles completed - {results}")
        return results
        
    except Exception as e:
        logger.error(f"POST /redditors/fetch-profiles failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profiles: {str(e)}"
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check service and database health status.
    
    Verifies that the API service is running and can connect to
    the Supabase database.
    
    Returns:
        HealthResponse with service and database status
        
    Status Codes:
        200: Service is healthy and database is connected
        503: Service is running but database is unavailable
    """
    from services.supabase_client import test_connection
    
    logger.info("GET /health - checking service status")
    
    # Test database connection
    db_connected = test_connection()
    
    # Determine overall status
    if db_connected:
        service_status = "healthy"
        db_status = "connected"
        response_status = status.HTTP_200_OK
    else:
        service_status = "unhealthy"
        db_status = "disconnected"
        response_status = status.HTTP_503_SERVICE_UNAVAILABLE
    
    response = HealthResponse(
        status=service_status,
        database=db_status,
        timestamp=datetime.utcnow()
    )
    
    logger.info(f"GET /health completed - status={service_status}, database={db_status}")
    
    # Return with appropriate status code
    if response_status == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(
            status_code=response_status,
            detail=response.model_dump()
        )
    
    return response