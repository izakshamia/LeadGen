-- Redditor DM Targeting System Database Schema
-- This migration creates tables for extracting, scoring, and targeting Redditors
-- for DMCA takedown service outreach campaigns

-- Table: target_redditors
-- Stores Redditor profiles with authenticity and need scores
CREATE TABLE IF NOT EXISTS target_redditors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    account_age_days INTEGER,
    total_karma INTEGER,
    comment_karma INTEGER,
    post_karma INTEGER,
    authenticity_score INTEGER NOT NULL CHECK (authenticity_score >= 0 AND authenticity_score <= 100),
    need_score INTEGER NOT NULL CHECK (need_score >= 0 AND need_score <= 100),
    priority TEXT NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
    is_authentic BOOLEAN NOT NULL DEFAULT true,
    is_active BOOLEAN NOT NULL DEFAULT true,
    source_posts TEXT[] NOT NULL,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_comment_fetch TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for target_redditors
CREATE INDEX IF NOT EXISTS idx_target_redditors_need_score ON target_redditors(need_score DESC);
CREATE INDEX IF NOT EXISTS idx_target_redditors_authenticity_score ON target_redditors(authenticity_score DESC);
CREATE INDEX IF NOT EXISTS idx_target_redditors_priority ON target_redditors(priority);
CREATE INDEX IF NOT EXISTS idx_target_redditors_username ON target_redditors(username);

-- Comments for target_redditors
COMMENT ON TABLE target_redditors IS 'Stores Redditor profiles extracted from posts with authenticity and need scores';
COMMENT ON COLUMN target_redditors.username IS 'Reddit username (unique)';
COMMENT ON COLUMN target_redditors.authenticity_score IS 'Score 0-100 indicating account authenticity (higher = more authentic)';
COMMENT ON COLUMN target_redditors.need_score IS 'Score 0-100 indicating need for DMCA services (higher = more likely customer)';
COMMENT ON COLUMN target_redditors.priority IS 'Priority classification: high (>60), medium (40-60), low (<40)';
COMMENT ON COLUMN target_redditors.source_posts IS 'Array of Reddit post URLs where this Redditor was found';

-- Table: redditor_comments
-- Stores comment history for each Redditor for analysis
CREATE TABLE IF NOT EXISTS redditor_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    redditor_id UUID NOT NULL REFERENCES target_redditors(id) ON DELETE CASCADE,
    comment_id TEXT NOT NULL UNIQUE,
    subreddit TEXT NOT NULL,
    body TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    created_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    permalink TEXT NOT NULL,
    contains_keywords BOOLEAN DEFAULT false,
    sentiment_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for redditor_comments
CREATE INDEX IF NOT EXISTS idx_redditor_comments_redditor_id ON redditor_comments(redditor_id);
CREATE INDEX IF NOT EXISTS idx_redditor_comments_subreddit ON redditor_comments(subreddit);
CREATE INDEX IF NOT EXISTS idx_redditor_comments_keywords ON redditor_comments(contains_keywords);

-- Comments for redditor_comments
COMMENT ON TABLE redditor_comments IS 'Stores comment history for Redditors for scoring and analysis';
COMMENT ON COLUMN redditor_comments.comment_id IS 'Reddit comment ID (unique)';
COMMENT ON COLUMN redditor_comments.contains_keywords IS 'True if comment contains DMCA-related keywords';
COMMENT ON COLUMN redditor_comments.sentiment_score IS 'Sentiment score from -1.0 (negative) to 1.0 (positive)';

-- Table: dm_campaigns
-- Stores DM outreach campaigns
CREATE TABLE IF NOT EXISTS dm_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for dm_campaigns
CREATE INDEX IF NOT EXISTS idx_dm_campaigns_status ON dm_campaigns(status);

-- Comments for dm_campaigns
COMMENT ON TABLE dm_campaigns IS 'Stores DM outreach campaigns for targeting Redditors';
COMMENT ON COLUMN dm_campaigns.status IS 'Campaign status: draft, active, paused, or completed';

-- Table: campaign_redditors
-- Many-to-many relationship between campaigns and Redditors
CREATE TABLE IF NOT EXISTS campaign_redditors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES dm_campaigns(id) ON DELETE CASCADE,
    redditor_id UUID NOT NULL REFERENCES target_redditors(id) ON DELETE CASCADE,
    outreach_status TEXT NOT NULL DEFAULT 'pending' CHECK (outreach_status IN ('pending', 'contacted', 'responded', 'interested', 'failed', 'unreachable')),
    contacted_at TIMESTAMP WITH TIME ZONE,
    responded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(campaign_id, redditor_id)
);

-- Indexes for campaign_redditors
CREATE INDEX IF NOT EXISTS idx_campaign_redditors_campaign_id ON campaign_redditors(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_redditors_redditor_id ON campaign_redditors(redditor_id);
CREATE INDEX IF NOT EXISTS idx_campaign_redditors_status ON campaign_redditors(outreach_status);

-- Comments for campaign_redditors
COMMENT ON TABLE campaign_redditors IS 'Many-to-many relationship between campaigns and Redditors with outreach tracking';
COMMENT ON COLUMN campaign_redditors.outreach_status IS 'Status: pending, contacted, responded, interested, failed, or unreachable';

-- Table: dm_messages
-- Stores DM messages sent and received
CREATE TABLE IF NOT EXISTS dm_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_redditor_id UUID NOT NULL REFERENCES campaign_redditors(id) ON DELETE CASCADE,
    direction TEXT NOT NULL CHECK (direction IN ('outbound', 'inbound')),
    subject TEXT,
    message_body TEXT NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    received_at TIMESTAMP WITH TIME ZONE,
    reddit_message_id TEXT UNIQUE,
    is_interested BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for dm_messages
CREATE INDEX IF NOT EXISTS idx_dm_messages_campaign_redditor_id ON dm_messages(campaign_redditor_id);
CREATE INDEX IF NOT EXISTS idx_dm_messages_direction ON dm_messages(direction);
CREATE INDEX IF NOT EXISTS idx_dm_messages_interested ON dm_messages(is_interested);

-- Comments for dm_messages
COMMENT ON TABLE dm_messages IS 'Stores DM messages sent to and received from Redditors';
COMMENT ON COLUMN dm_messages.direction IS 'Message direction: outbound (sent) or inbound (received)';
COMMENT ON COLUMN dm_messages.is_interested IS 'True if response indicates interest in services';

-- Table: extraction_runs
-- Tracks extraction pipeline runs for monitoring
CREATE TABLE IF NOT EXISTS extraction_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    posts_processed INTEGER NOT NULL DEFAULT 0,
    redditors_extracted INTEGER NOT NULL DEFAULT 0,
    new_redditors INTEGER NOT NULL DEFAULT 0,
    avg_authenticity_score FLOAT,
    avg_need_score FLOAT,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for extraction_runs
CREATE INDEX IF NOT EXISTS idx_extraction_runs_status ON extraction_runs(status);
CREATE INDEX IF NOT EXISTS idx_extraction_runs_started_at ON extraction_runs(started_at DESC);

-- Comments for extraction_runs
COMMENT ON TABLE extraction_runs IS 'Tracks extraction pipeline runs with metrics and status';
COMMENT ON COLUMN extraction_runs.status IS 'Run status: running, completed, or failed';
COMMENT ON COLUMN extraction_runs.new_redditors IS 'Count of newly discovered Redditors in this run';
