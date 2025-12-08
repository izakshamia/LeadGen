"""
FastAPI application for Reddit Ovarra API service.
Provides endpoints for scraping Reddit posts and retrieving suggestions from Supabase.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, status
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
    contacted_status: Optional[str] = Field("pending", description="Contact status (pending, approved, contacted, responded, rejected)")
    contacted_at: Optional[datetime] = Field(None, description="When redditor was contacted/approved")
    notes: Optional[str] = Field(None, description="Notes about this redditor")


class UpdateRedditorStatusRequest(BaseModel):
    """Request model for updating redditor contact status"""
    contacted_status: str = Field(description="New status (pending, approved, contacted, responded, rejected)")
    notes: Optional[str] = Field(None, description="Optional notes")


class RedditorsListResponse(BaseModel):
    """Response model for GET /redditors endpoint"""
    redditors: List[RedditorResponse] = Field(description="List of target redditors")
    count: int = Field(description="Number of redditors returned")
    limit: int = Field(description="Limit used for pagination")
    offset: int = Field(description="Offset used for pagination")


# ============================================================================
# API Endpoints
# ============================================================================

class ScrapeResponse(BaseModel):
    """Response model for POST /scrape endpoint"""
    status: str = Field(description="Overall status (success, partial, failure)")
    processed: int = Field(description="Number of suggestions successfully saved")
    skipped: int = Field(description="Number of duplicate posts skipped")
    failed: int = Field(description="Number of posts that failed to process")
    redditors_extracted: int = Field(description="Number of unique redditors extracted")
    redditors_saved: int = Field(description="Number of redditors saved to database")


@app.post("/scrape", response_model=ScrapeResponse, status_code=status.HTTP_200_OK)
async def scrape_reddit(request: ScrapeRequest):
    """
    Trigger Reddit scraping and wait for completion.
    
    This endpoint executes the scraping synchronously and returns
    detailed results when complete. May take 2-5 minutes depending
    on the number of subreddits and keywords.
    
    Args:
        request: ScrapeRequest with optional parameters
        
    Returns:
        ScrapeResponse with detailed scraping results
        
    Raises:
        HTTPException: 500 if scraping fails
    """
    from api.services.scraper_service import scrape_and_save
    from cli.pipeline import DEFAULT_SUBREDDITS, DEFAULT_KEYWORDS
    
    # Use defaults from pipeline.py if not provided
    subreddits = request.subreddits if request.subreddits else DEFAULT_SUBREDDITS
    keywords = request.keywords if request.keywords else DEFAULT_KEYWORDS
    post_limit = request.post_limit if request.post_limit else 10
    max_age_days = request.max_age_days if request.max_age_days else 120
    
    logger.info(f"POST /scrape - Starting synchronous scrape: subreddits={subreddits}, keywords={keywords}")
    
    try:
        # Execute scraping synchronously
        result = scrape_and_save(
            subreddits=subreddits,
            keywords=keywords,
            post_limit=post_limit,
            max_age_days=max_age_days
        )
        
        logger.info(f"POST /scrape completed - {result}")
        
        return ScrapeResponse(
            status=result["status"],
            processed=result["processed"],
            skipped=result["skipped"],
            failed=result["failed"],
            redditors_extracted=result["redditors_extracted"],
            redditors_saved=result["redditors_saved"]
        )
        
    except Exception as e:
        logger.error(f"POST /scrape failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )


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
    from api.services.supabase_client import get_recent_suggestions
    
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
    from api.services.supabase_client import get_target_redditors
    
    logger.info(f"GET /redditors - limit={limit}, offset={offset}")
    
    try:
        # Retrieve redditors from database
        redditors_data = get_target_redditors(limit=limit, offset=offset)
        
        # Convert to response models
        redditors = []
        for r in redditors_data:
            # Handle social_links - convert list to dict if needed
            social_links = r.get("social_links")
            if isinstance(social_links, list):
                # Convert list format to dict format
                social_links_dict = {}
                for link in social_links:
                    if isinstance(link, dict) and 'platform' in link and 'url' in link:
                        social_links_dict[link['platform']] = link['url']
                social_links = social_links_dict if social_links_dict else None
            elif not isinstance(social_links, dict):
                social_links = None
            
            redditors.append(
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
                    social_links=social_links,
                    contacted_status=r.get("contacted_status", "pending"),
                    contacted_at=r.get("contacted_at"),
                    notes=r.get("notes")
                )
            )
        
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
async def fetch_redditor_profiles(fetch_all: bool = False, limit: int = 100):
    """
    Fetch Reddit profile data for redditors.
    
    By default, finds redditors with missing profile data (account_age_days = 0 or total_karma = 0)
    and fetches their real profile data from Reddit API.
    
    If fetch_all=true, fetches profiles for ALL redditors to update social links.
    
    Args:
        fetch_all: If true, fetch profiles for all redditors (default: false)
        limit: Maximum number of redditors to fetch when fetch_all=true (default: 100)
    
    Returns:
        Dictionary with fetch results (total, success, failed, not_found)
        
    Raises:
        HTTPException: 500 if fetch fails
    """
    try:
        if fetch_all:
            from api.services.redditor_profile_fetcher import fetch_profiles_for_all_redditors
            logger.info(f"POST /redditors/fetch-profiles - fetching ALL profiles (limit={limit})")
            results = fetch_profiles_for_all_redditors(limit=limit)
        else:
            from api.services.redditor_profile_fetcher import fetch_profiles_for_new_redditors
            logger.info("POST /redditors/fetch-profiles - fetching profiles for new redditors")
            results = fetch_profiles_for_new_redditors()
        
        logger.info(f"POST /redditors/fetch-profiles completed - {results}")
        return results
        
    except Exception as e:
        logger.error(f"POST /redditors/fetch-profiles failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profiles: {str(e)}"
        )


@app.patch("/redditors/{redditor_id}/status")
async def update_redditor_status(redditor_id: str, request: UpdateRedditorStatusRequest):
    """
    Update the contact status of a target redditor.
    
    Allows manual tracking of outreach progress by updating the contacted_status field.
    When status is changed to 'approved' or 'contacted', the contacted_at timestamp is set.
    
    Args:
        redditor_id: UUID of the redditor to update
        request: UpdateRedditorStatusRequest with new status and optional notes
        
    Returns:
        Updated redditor data
        
    Raises:
        HTTPException: 404 if redditor not found, 500 if update fails
    """
    from api.services.supabase_client import update_redditor_status
    
    logger.info(f"PATCH /redditors/{redditor_id}/status - status={request.contacted_status}")
    
    try:
        # Update status in database
        updated_redditor = update_redditor_status(
            redditor_id=redditor_id,
            contacted_status=request.contacted_status,
            notes=request.notes
        )
        
        if not updated_redditor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Redditor with id {redditor_id} not found"
            )
        
        logger.info(f"PATCH /redditors/{redditor_id}/status completed")
        return updated_redditor
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PATCH /redditors/{redditor_id}/status failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update redditor status: {str(e)}"
        )


@app.post("/redditors/add-by-username")
async def add_redditor_by_username(username: str):
    """
    Add a redditor to the database by username.
    
    Fetches the redditor's profile from Reddit API and adds them to the database
    with default scoring. This allows manual addition of target redditors.
    
    Args:
        username: Reddit username (without u/ prefix)
        
    Returns:
        Dictionary with the created redditor data
        
    Raises:
        HTTPException: 404 if redditor not found, 409 if already exists, 500 if operation fails
    """
    from api.services.redditor_profile_fetcher import fetch_redditor_profile
    from api.services.supabase_client import init_supabase_client
    
    logger.info(f"POST /redditors/add-by-username - username={username}")
    
    try:
        # Initialize Supabase client
        supabase = init_supabase_client()
        
        # Clean username (remove u/ prefix if present)
        clean_username = username.strip().lstrip('u/').lstrip('/u/')
        
        # Check if redditor already exists
        existing = supabase.table('target_redditors').select('id, username').eq('username', clean_username).execute()
        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Redditor u/{clean_username} already exists in database"
            )
        
        # Fetch profile from Reddit
        logger.info(f"Fetching profile for u/{clean_username} from Reddit API")
        profile = fetch_redditor_profile(clean_username)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Redditor u/{clean_username} not found on Reddit or profile is private"
            )
        
        # Convert social_links from list to dict format
        social_links_list = profile.get('social_links', [])
        social_links_dict = {}
        if isinstance(social_links_list, list):
            for link in social_links_list:
                if isinstance(link, dict) and 'platform' in link and 'url' in link:
                    social_links_dict[link['platform']] = link['url']
        elif isinstance(social_links_list, dict):
            social_links_dict = social_links_list
        
        # Prepare redditor data for insertion
        redditor_data = {
            'username': clean_username,
            'account_age_days': profile.get('account_age_days', 0),
            'total_karma': profile.get('total_karma', 0),
            'comment_karma': profile.get('comment_karma', 0),
            'post_karma': profile.get('post_karma', 0),
            'authenticity_score': 50,  # Default score
            'need_score': 50,  # Default score
            'priority': 'medium',  # Default priority
            'is_authentic': True,  # Assume authentic for manually added
            'is_active': profile.get('is_active', True),
            'source_posts': [],  # Manually added, no source posts
            'social_links': social_links_dict,
            'contacted_status': 'pending',
            'notes': 'Manually added'
        }
        
        # Insert into database
        logger.info(f"Inserting u/{clean_username} into database")
        result = supabase.table('target_redditors').insert(redditor_data).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to insert redditor into database"
            )
        
        created_redditor = result.data[0]
        logger.info(f"Successfully added u/{clean_username} to database")
        
        return {
            "success": True,
            "message": f"Successfully added u/{clean_username}",
            "redditor": created_redditor
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"POST /redditors/add-by-username failed with error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add redditor: {str(e)}"
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
    from api.services.supabase_client import test_connection
    
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