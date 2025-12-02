-- Add contacted status tracking to target_redditors table
-- This allows manual tracking of outreach without requiring a full campaign

ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS contacted_status TEXT DEFAULT 'pending' 
CHECK (contacted_status IN ('pending', 'approved', 'contacted', 'responded', 'rejected'));

ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS contacted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Index for filtering by status
CREATE INDEX IF NOT EXISTS idx_target_redditors_contacted_status ON target_redditors(contacted_status);

-- Comments
COMMENT ON COLUMN target_redditors.contacted_status IS 'Manual outreach status: pending, approved, contacted, responded, rejected';
COMMENT ON COLUMN target_redditors.contacted_at IS 'Timestamp when redditor was marked as contacted/approved';
COMMENT ON COLUMN target_redditors.notes IS 'Optional notes about this redditor or outreach attempts';
