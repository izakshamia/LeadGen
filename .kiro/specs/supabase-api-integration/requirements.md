# Requirements Document

## Introduction

This feature transforms the existing Reddit scraper tool into a production-ready API service that stores Reddit post suggestions in Supabase, provides recent-only data retrieval, prevents duplicate processing, and is deployable to Railway. The system will enable the product team to access recent Reddit post suggestions with generated responses while avoiding reprocessing of old or already-known content.

## Glossary

- **Reddit Scraper**: The existing Python tool that searches Reddit for relevant posts from adult content creators seeking help with content leaks and DMCA issues
- **Supabase**: Existing PostgreSQL database service that will have a new table added for storing Reddit post suggestions and their metadata
- **API Service**: FastAPI-based web service that exposes scraper functionality and data retrieval endpoints
- **Railway**: Cloud platform for deploying and hosting the API service
- **Suggestion**: A Reddit post with its generated response, stored as a row in the database
- **Recent Window**: Time period (default 24 hours) for filtering suggestions by creation timestamp
- **Duplicate Detection**: Logic to prevent reprocessing posts that already exist in the database

## Requirements

### Requirement 1: Database Schema Design

**User Story:** As a product developer, I want a well-structured database table to store Reddit suggestions, so that I can track posts, responses, and their lifecycle status.

#### Acceptance Criteria

1. THE API Service SHALL add a new table named "reddit_suggestions" to the existing Supabase database with the following columns: id (uuid primary key), reddit_name (text), reddit_url (text with unique constraint), suggested_response (text), status (text with default "new"), and created_at (timestamp with default now())
2. THE API Service SHALL enforce a unique constraint on the reddit_url column to prevent duplicate entries
3. THE API Service SHALL use uuid type for the id column as the primary key
4. THE API Service SHALL set the status column to accept values: "new", "approved", "sent", or "ignored"
5. THE API Service SHALL automatically populate created_at with the current timestamp when a new row is inserted
6. THE API Service SHALL not modify or interfere with any existing tables in the Supabase database

### Requirement 2: Scraper to Supabase Integration

**User Story:** As a system operator, I want the scraper results to be automatically saved to Supabase, so that the product team can access suggestions without manual file transfers.

#### Acceptance Criteria

1. WHEN the scraper completes processing a Reddit post, THE API Service SHALL extract the post title, URL, and generated response
2. WHEN inserting a new suggestion, THE API Service SHALL populate reddit_name with the post title
3. WHEN inserting a new suggestion, THE API Service SHALL populate reddit_url with the post URL
4. WHEN inserting a new suggestion, THE API Service SHALL populate suggested_response with the generated Ovarra reply
5. THE API Service SHALL use the Supabase Python client library to perform INSERT operations
6. IF the INSERT operation fails due to network or database errors, THEN THE API Service SHALL log the error and continue processing remaining posts

### Requirement 3: Recent-Only Data Retrieval

**User Story:** As a product developer, I want to retrieve only recent suggestions, so that the product doesn't query old data that is no longer relevant.

#### Acceptance Criteria

1. THE API Service SHALL provide a query endpoint that filters suggestions by created_at timestamp
2. WHEN querying suggestions, THE API Service SHALL accept a time window parameter in hours (default 24 hours)
3. THE API Service SHALL return only rows where created_at is greater than or equal to (current time - time window)
4. THE API Service SHALL order results by created_at in descending order (newest first)
5. THE API Service SHALL return results in JSON format with all table columns included

### Requirement 4: Duplicate Prevention

**User Story:** As a system operator, I want to skip posts that already exist in the database, so that we don't waste resources reprocessing the same content.

#### Acceptance Criteria

1. WHEN processing a new Reddit post, THE API Service SHALL query the database to check if reddit_url already exists
2. IF the reddit_url exists in the database, THEN THE API Service SHALL skip inserting the post and log a skip message
3. IF the reddit_url does not exist in the database, THEN THE API Service SHALL proceed with the INSERT operation
4. THE API Service SHALL perform the duplicate check before generating the suggested response to save API costs
5. THE API Service SHALL return a summary of processed, skipped, and failed posts after each scrape operation

### Requirement 5: FastAPI Service Implementation

**User Story:** As a product developer, I want a REST API to trigger scraping and retrieve suggestions, so that I can integrate the scraper with other services.

#### Acceptance Criteria

1. THE API Service SHALL implement a POST /scrape endpoint that accepts parameters: subreddits (list), keywords (list), post_limit (integer), and max_age_days (integer)
2. WHEN the POST /scrape endpoint is called, THE API Service SHALL execute the scraping pipeline and save results to Supabase
3. THE API Service SHALL implement a GET /suggestions endpoint that accepts an optional hours parameter (default 24)
4. WHEN the GET /suggestions endpoint is called, THE API Service SHALL return recent suggestions filtered by the time window
5. THE API Service SHALL implement a GET /health endpoint that returns service status and database connectivity
6. THE API Service SHALL return appropriate HTTP status codes (200 for success, 400 for bad requests, 500 for server errors)
7. THE API Service SHALL include request validation using Pydantic models
8. THE API Service SHALL log all API requests with timestamps and parameters

### Requirement 6: Railway Deployment Preparation

**User Story:** As a DevOps engineer, I want the service to be deployment-ready for Railway, so that I can deploy it with minimal configuration.

#### Acceptance Criteria

1. THE API Service SHALL include a requirements.txt file with all Python dependencies and their versions
2. THE API Service SHALL start with the command "uvicorn main:app --host 0.0.0.0 --port 8000"
3. THE API Service SHALL read configuration from environment variables: SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY
4. THE API Service SHALL include a Procfile or railway.json configuration file for Railway deployment
5. THE API Service SHALL bind to the PORT environment variable if provided by Railway
6. THE API Service SHALL include a README with deployment instructions and required environment variables
7. THE API Service SHALL handle missing environment variables gracefully with clear error messages
