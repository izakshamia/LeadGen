# Supabase Database Setup Guide

This guide walks you through setting up the Supabase database schema for the Reddit Ovarra API service.

## Prerequisites

- A Supabase account (sign up at https://supabase.com)
- A Supabase project created

## Setup Steps

### 1. Access the SQL Editor

1. Log in to your Supabase dashboard
2. Select your project
3. Navigate to the **SQL Editor** in the left sidebar

### 2. Execute the Schema

1. Click **New Query** in the SQL Editor
2. Copy the contents of `supabase_schema.sql`
3. Paste into the SQL Editor
4. Click **Run** or press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

### 3. Verify Table Creation

After running the schema, verify the table was created successfully:

1. Navigate to **Table Editor** in the left sidebar
2. You should see a new table named `reddit_suggestions`
3. Click on the table to view its structure

### 4. Verify Columns

Confirm the following columns exist:

- `id` (uuid, primary key)
- `reddit_name` (text)
- `reddit_url` (text, unique)
- `suggested_response` (text)
- `status` (text, default: 'new')
- `created_at` (timestamptz, default: now())

### 5. Verify Indexes

To verify indexes were created:

1. In the SQL Editor, run:
```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'reddit_suggestions';
```

You should see:
- `reddit_suggestions_pkey` (primary key on id)
- `idx_reddit_suggestions_created_at` (index on created_at DESC)
- `idx_reddit_suggestions_url` (unique index on reddit_url)

### 6. Get Your Supabase Credentials

You'll need these for the API service:

1. Navigate to **Project Settings** (gear icon in sidebar)
2. Click **API** in the settings menu
3. Copy the following values:
   - **Project URL** → This is your `SUPABASE_URL`
   - **Project API keys** → Copy the `anon` `public` key → This is your `SUPABASE_KEY`

### 7. Update Environment Variables

Add these to your `.env` file:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
```

## Testing the Setup

You can test the table by inserting a sample row:

```sql
INSERT INTO reddit_suggestions (reddit_name, reddit_url, suggested_response)
VALUES (
    'Test Post Title',
    'https://reddit.com/r/test/comments/abc123',
    'This is a test response'
);
```

Then query it:

```sql
SELECT * FROM reddit_suggestions;
```

To test the duplicate prevention:

```sql
-- This should fail with a unique constraint violation
INSERT INTO reddit_suggestions (reddit_name, reddit_url, suggested_response)
VALUES (
    'Another Title',
    'https://reddit.com/r/test/comments/abc123',  -- Same URL
    'Another response'
);
```

To test the recent-only filtering:

```sql
-- Get suggestions from last 24 hours
SELECT * FROM reddit_suggestions
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

## Cleanup (Optional)

If you need to drop the table and start over:

```sql
DROP TABLE IF EXISTS reddit_suggestions CASCADE;
```

Then re-run the schema from `supabase_schema.sql`.

## Troubleshooting

### Error: relation "reddit_suggestions" already exists
The table already exists. You can either:
- Drop it first: `DROP TABLE reddit_suggestions CASCADE;`
- Or skip this error if the table structure is correct

### Error: permission denied
Make sure you're using the SQL Editor as an authenticated user, not trying to run DDL commands through the API.

### Indexes not showing up
Indexes are created automatically. Use the verification query above to confirm they exist.

## Next Steps

Once the database is set up:
1. Proceed to task 2: Create Supabase client module
2. Test the connection using the health check endpoint
3. Start implementing the API endpoints
