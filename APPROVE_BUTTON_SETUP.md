# Approve Button Setup Guide

## What Was Implemented

The "Approve" button now works! Here's what was added:

### 1. Database Schema (Migration Required)
- Added `contacted_status` field to track redditor status (pending, approved, contacted, responded, rejected)
- Added `contacted_at` timestamp to track when status changed
- Added `notes` field for optional notes

### 2. Backend API
- New endpoint: `PATCH /redditors/{redditor_id}/status`
- Updates redditor contact status
- Automatically sets `contacted_at` timestamp when approved/contacted

### 3. Frontend UI
- Status badge displayed on each redditor card
- "Approve" button for pending redditors
- "Mark Contacted" button for approved redditors
- "Reject" button to mark as rejected
- Real-time status updates with loading states

## Setup Instructions

### Step 1: Run the Database Migrations

You need to add new columns to your `target_redditors` table:

#### Migration 1: Add contacted_status fields
1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to **SQL Editor** (left sidebar)
4. Copy the contents of `Reddit Ovarra/migrations/002_add_contacted_status.sql`
5. Paste into the SQL Editor
6. Click **Run**

#### Migration 2: Add social_links field
1. In the same SQL Editor
2. Copy the contents of `Reddit Ovarra/migrations/003_add_social_links.sql`
3. Paste into the SQL Editor
4. Click **Run**

### Step 2: Test the Feature

1. Make sure your backend is running:
   ```bash
   cd api
   uvicorn main:app --reload --port 8003
   ```

2. Make sure your frontend is running:
   ```bash
   cd reddit-ovarra-ui
   npm run dev
   ```

3. Navigate to the Redditors tab in your UI

4. You should see:
   - Status badges on each redditor (default: PENDING)
   - "✓ Approve" button for pending redditors
   - "✗ Reject" button

5. Click "Approve" on a redditor:
   - Status changes to "APPROVED"
   - Button changes to "✉️ Mark Contacted"
   - `contacted_at` timestamp is set

## Status Flow

```
PENDING → APPROVED → CONTACTED → RESPONDED
   ↓
REJECTED
```

- **PENDING**: New redditor, not yet reviewed
- **APPROVED**: Manually approved for outreach
- **CONTACTED**: DM/message sent to this redditor
- **RESPONDED**: Redditor replied to outreach
- **REJECTED**: Not a good fit, skip this redditor

## API Usage

### Update Status
```bash
curl -X PATCH http://localhost:8003/redditors/{redditor_id}/status \
  -H "Content-Type: application/json" \
  -d '{
    "contacted_status": "approved",
    "notes": "High priority lead"
  }'
```

### Get Redditors (includes status)
```bash
curl http://localhost:8003/redditors?limit=50
```

## Color Coding

- **Gray**: Pending
- **Green**: Approved
- **Blue**: Contacted
- **Purple**: Responded
- **Red**: Rejected
