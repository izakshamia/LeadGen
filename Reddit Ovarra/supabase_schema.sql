-- Supabase Database Schema for Reddit Suggestions
-- This schema creates the reddit_suggestions table with all required columns,
-- constraints, and indexes for the Reddit Ovarra API service

-- Create the reddit_suggestions table
CREATE TABLE IF NOT EXISTS reddit_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reddit_name TEXT NOT NULL,
    reddit_url TEXT NOT NULL UNIQUE,
    suggested_response TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'approved', 'sent', 'ignored')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on created_at for efficient recent queries (descending order for newest first)
CREATE INDEX IF NOT EXISTS idx_reddit_suggestions_created_at ON reddit_suggestions(created_at DESC);

-- Create unique index on reddit_url for duplicate checking (already enforced by UNIQUE constraint, but explicit for clarity)
CREATE UNIQUE INDEX IF NOT EXISTS idx_reddit_suggestions_url ON reddit_suggestions(reddit_url);

-- Add comment to table for documentation
COMMENT ON TABLE reddit_suggestions IS 'Stores Reddit post suggestions with generated Ovarra responses for content creator DMCA assistance';

-- Add comments to columns for documentation
COMMENT ON COLUMN reddit_suggestions.id IS 'Unique identifier for each suggestion';
COMMENT ON COLUMN reddit_suggestions.reddit_name IS 'Title of the Reddit post';
COMMENT ON COLUMN reddit_suggestions.reddit_url IS 'URL of the Reddit post (unique constraint prevents duplicates)';
COMMENT ON COLUMN reddit_suggestions.suggested_response IS 'AI-generated Ovarra response for the post';
COMMENT ON COLUMN reddit_suggestions.status IS 'Lifecycle status: new, approved, sent, or ignored';
COMMENT ON COLUMN reddit_suggestions.created_at IS 'Timestamp when the suggestion was created';
