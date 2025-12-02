-- Add social_links column to target_redditors table
-- Stores social media links extracted from Reddit profiles

ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS social_links JSONB DEFAULT '{}'::jsonb;

-- Index for querying by social links
CREATE INDEX IF NOT EXISTS idx_target_redditors_social_links ON target_redditors USING GIN (social_links);

-- Comment
COMMENT ON COLUMN target_redditors.social_links IS 'JSON object with social media links (platform: url), e.g. {"instagram": "https://instagram.com/user", "twitter": "https://twitter.com/user"}';
