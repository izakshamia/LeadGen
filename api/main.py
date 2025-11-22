"""
FastAPI application for Reddit Ovarra API service.
Provides endpoints for scraping Reddit posts and retrieving suggestions from Supabase.
"""

import logging
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
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


class ScrapeResponse(BaseModel):
    """Response model for POST /scrape endpoint"""
    status: str = Field(description="Overall status (success, partial, failure)")
    processed: int = Field(description="Number of successfully saved suggestions")
    skipped: int = Field(description="Number of duplicate posts skipped")
    failed: int = Field(description="Number of posts that failed to save")
    message: str = Field(description="Human-readable status message")


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



# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/scrape", response_model=ScrapeResponse, status_code=status.HTTP_200_OK)
async def scrape_reddit(request: ScrapeRequest):
    """
    Trigger Reddit scraping and save results to Supabase.
    
    This endpoint executes the complete scraping pipeline:
    1. Scrapes Reddit posts from specified subreddits
    2. Classifies posts for relevance
    3. Checks for duplicates (skips existing posts)
    4. Generates Ovarra replies for new posts
    5. Saves suggestions to Supabase database
    
    Args:
        request: ScrapeRequest with optional parameters
        
    Returns:
        ScrapeResponse with processing statistics
        
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
    
    logger.info(f"POST /scrape - subreddits={subreddits}, keywords={keywords}, "
                f"post_limit={post_limit}, max_age_days={max_age_days}")
    
    try:
        # Execute scraping pipeline
        result = scrape_and_save(
            subreddits=subreddits,
            keywords=keywords,
            post_limit=post_limit,
            max_age_days=max_age_days
        )
        
        # Generate human-readable message
        if result["status"] == "success":
            if result["processed"] > 0:
                message = f"Scraping completed successfully - {result['processed']} new suggestions saved"
            else:
                message = f"Scraping completed - all {result['skipped']} posts were already in database"
        elif result["status"] == "partial":
            message = f"Scraping completed with {result['failed']} failures"
        else:
            message = "Scraping failed - no posts were processed"
        
        response = ScrapeResponse(
            status=result["status"],
            processed=result["processed"],
            skipped=result["skipped"],
            failed=result["failed"],
            message=message
        )
        
        logger.info(f"POST /scrape completed - {response.model_dump()}")
        return response
        
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
