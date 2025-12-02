# Database Migrations Guide

## Required Migrations for Social Links & Approve Button

You need to run **2 migrations** to enable all the new features:

---

## Migration 1: Add Contacted Status Fields

This enables the Approve/Reject button functionality.

**File:** `Reddit Ovarra/migrations/002_add_contacted_status.sql`

```sql
ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS contacted_status TEXT DEFAULT 'pending' 
CHECK (contacted_status IN ('pending', 'approved', 'contacted', 'responded', 'rejected'));

ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS contacted_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS notes TEXT;

CREATE INDEX IF NOT EXISTS idx_target_redditors_contacted_status ON target_redditors(contacted_status);

COMMENT ON COLUMN target_redditors.contacted_status IS 'Manual outreach status: pending, approved, contacted, responded, rejected';
COMMENT ON COLUMN target_redditors.contacted_at IS 'Timestamp when redditor was marked as contacted/approved';
COMMENT ON COLUMN target_redditors.notes IS 'Optional notes about this redditor or outreach attempts';
```

---

## Migration 2: Add Social Links Field

This enables storing and displaying social media links (Instagram, Twitter, OnlyFans, TikTok, etc.)

**File:** `Reddit Ovarra/migrations/003_add_social_links.sql`

```sql
ALTER TABLE target_redditors 
ADD COLUMN IF NOT EXISTS social_links JSONB DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS idx_target_redditors_social_links ON target_redditors USING GIN (social_links);

COMMENT ON COLUMN target_redditors.social_links IS 'JSON object with social media links (platform: url), e.g. {"instagram": "https://instagram.com/user", "twitter": "https://twitter.com/user"}';
```

---

## How to Run Migrations

### Option 1: Via Supabase Dashboard (Recommended)

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **SQL Editor** in the left sidebar
4. Copy **Migration 1** SQL above
5. Paste into the editor
6. Click **Run** (or press Cmd/Ctrl + Enter)
7. Wait for success message
8. Repeat steps 4-7 for **Migration 2**

### Option 2: Via psql Command Line

If you have PostgreSQL client installed:

```bash
# Set your database connection string
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.isipparnnrkuffstlhta.supabase.co:5432/postgres"

# Run migration 1
psql $DATABASE_URL -f "Reddit Ovarra/migrations/002_add_contacted_status.sql"

# Run migration 2
psql $DATABASE_URL -f "Reddit Ovarra/migrations/003_add_social_links.sql"
```

---

## Verify Migrations

After running both migrations, verify they worked:

```sql
-- Check new columns exist
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'target_redditors' 
AND column_name IN ('contacted_status', 'contacted_at', 'notes', 'social_links');
```

You should see 4 rows returned.

---

## What These Enable

### Migration 1 (contacted_status):
- ✓ Approve button functionality
- ✗ Reject button functionality
- ↺ Reset to Pending button
- Status badges (color-coded)
- Timestamp tracking

### Migration 2 (social_links):
- 📷 Instagram links
- 🐦 Twitter/X links
- 🔞 OnlyFans links
- 🎵 TikTok links
- ▶️ YouTube links
- 🎮 Twitch links
- And more...

---

## Troubleshooting

### Error: "column already exists"
This is fine! The migrations use `IF NOT EXISTS` so they're safe to run multiple times.

### Error: "permission denied"
Make sure you're using the correct Supabase credentials with admin access.

### Social links not showing up?
1. Make sure Migration 2 ran successfully
2. Run the scraper to fetch new redditor profiles
3. Or click "Fetch Profiles" button in the UI to update existing redditors

---

## Next Steps

After running migrations:

1. Restart your backend API (if running)
2. Refresh your frontend UI
3. Test the Approve button on a redditor
4. Run the scraper to populate social links automatically
