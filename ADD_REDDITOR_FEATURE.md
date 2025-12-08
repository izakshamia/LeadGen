# Add Redditor Manually - Feature Documentation

## Overview

Added functionality to manually add a redditor to the target list by username. The system fetches their complete profile from Reddit API and adds them to the database with all the same information as automatically discovered redditors.

## How It Works

### User Flow

1. **Navigate to Target Redditors tab**
2. **See "Add Redditor Manually" box at the top**
3. **Enter username** (with or without u/ prefix)
4. **Click "Add Redditor"** or press Enter
5. **System fetches profile** from Reddit API
6. **Redditor is added** to database with full profile
7. **New card appears** in the list below

### What Gets Fetched

When you add a redditor, the system automatically fetches:

- ✅ **Account age** (in days)
- ✅ **Total karma**
- ✅ **Comment karma**
- ✅ **Post karma**
- ✅ **Active status**
- ✅ **Social media links** (Instagram, Twitter, OnlyFans, TikTok, etc.)
- ✅ **Profile information**

### Default Values

Manually added redditors get these defaults:

- **Authenticity Score:** 50 (medium)
- **Need Score:** 50 (medium)
- **Priority:** Medium
- **Status:** Pending
- **Is Authentic:** True (assumed for manual additions)
- **Source Posts:** Empty (no source posts)
- **Notes:** "Manually added"

## UI Design

### Add Redditor Box

```
┌─────────────────────────────────────────────────┐
│ ➕ Add Redditor Manually                        │
│                                                 │
│ Enter a Reddit username to fetch their profile │
│ and add them to your target list.              │
│                                                 │
│ ┌──────────────────────────┐ ┌──────────────┐ │
│ │ u/ [username_________]   │ │ Add Redditor │ │
│ └──────────────────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────┘
```

### Features

- **u/ prefix** - Automatically shown, optional to type
- **Enter key** - Press Enter to submit
- **Loading state** - Shows "Adding..." with spinner
- **Disabled state** - Button disabled when empty or loading
- **Auto-refresh** - List refreshes after successful addition

## API Endpoint

### POST `/redditors/add-by-username`

**Query Parameters:**
- `username` (required) - Reddit username (with or without u/ prefix)

**Response (Success):**
```json
{
  "success": true,
  "message": "Successfully added u/username",
  "redditor": {
    "id": "uuid",
    "username": "username",
    "account_age_days": 365,
    "total_karma": 5000,
    "comment_karma": 3000,
    "post_karma": 2000,
    "authenticity_score": 50,
    "need_score": 50,
    "priority": "medium",
    "is_authentic": true,
    "is_active": true,
    "source_posts": [],
    "social_links": {
      "instagram": "https://instagram.com/...",
      "twitter": "https://twitter.com/..."
    },
    "contacted_status": "pending",
    "notes": "Manually added",
    "first_seen": "2024-12-08T10:00:00Z",
    "last_updated": "2024-12-08T10:00:00Z"
  }
}
```

**Error Responses:**

**404 Not Found:**
```json
{
  "detail": "Redditor u/username not found on Reddit or profile is private"
}
```

**409 Conflict:**
```json
{
  "detail": "Redditor u/username already exists in database"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to add redditor: [error message]"
}
```

## User Messages

### Success
```
✓ Successfully added u/username!

Account age: 365 days
Total karma: 5000
```

### Already Exists
```
u/username is already in the database.
```

### Not Found
```
u/username not found on Reddit or profile is private.
```

### Error
```
Error adding redditor: [error message]
```

## Technical Implementation

### Backend (api/main.py)

**New endpoint:** `POST /redditors/add-by-username`

**Process:**
1. Clean username (remove u/ prefix)
2. Check if already exists in database
3. Fetch profile from Reddit API using `fetch_redditor_profile()`
4. Prepare redditor data with defaults
5. Insert into `target_redditors` table
6. Return created redditor data

**Reuses existing functionality:**
- `fetch_redditor_profile()` - Fetches Reddit profile
- `fetch_social_links()` - Scrapes social media links
- Supabase client - Database operations

### Frontend (RedditorsList.jsx)

**New state:**
- `addUsername` - Input value
- `isAdding` - Loading state

**New function:**
- `handleAddRedditor()` - Handles form submission

**Features:**
- Input validation
- Loading state
- Error handling
- Auto-refresh on success
- Enter key support

## Use Cases

### 1. Manual Prospecting
You found a potential lead on Reddit and want to add them to your list:
```
1. Copy their username
2. Go to Target Redditors tab
3. Paste username
4. Click Add Redditor
5. Review their profile in the new card
```

### 2. Competitor Research
Add competitors' customers to analyze:
```
1. Find users in competitor discussions
2. Add them one by one
3. Review their profiles and social links
4. Mark for outreach if relevant
```

### 3. Referral Additions
Someone referred a potential lead:
```
1. Get their Reddit username
2. Add them manually
3. System fetches all their info
4. Review and approve for outreach
```

## Validation

### Username Cleaning
The system automatically handles:
- ✅ `username` → `username`
- ✅ `u/username` → `username`
- ✅ `/u/username` → `username`
- ✅ Extra whitespace → trimmed

### Duplicate Prevention
- Checks database before fetching from Reddit
- Returns 409 Conflict if already exists
- Prevents wasted API calls

### Profile Validation
- Verifies user exists on Reddit
- Checks if profile is accessible
- Returns 404 if not found or private

## Limitations

### Rate Limits
- Reddit API has rate limits
- Adding many users quickly may fail
- Wait a few seconds between additions

### Private Profiles
- Cannot fetch private/suspended accounts
- Will return 404 error
- User must be public on Reddit

### Social Links
- Social links may not always be found
- Depends on user's profile setup
- Some links may be in bio text

## Testing

### Test Cases

**1. Valid Username:**
```
Input: "spez"
Expected: Successfully adds Reddit CEO's profile
```

**2. Username with u/ prefix:**
```
Input: "u/spez"
Expected: Strips prefix and adds successfully
```

**3. Non-existent User:**
```
Input: "thisuserdoesnotexist12345"
Expected: Error - "not found on Reddit"
```

**4. Duplicate:**
```
Input: [existing username]
Expected: Error - "already exists in database"
```

**5. Empty Input:**
```
Input: ""
Expected: Button disabled, alert "Please enter a username"
```

## Future Enhancements

### Possible Improvements

1. **Bulk Import** - Add multiple usernames at once
2. **CSV Upload** - Upload a CSV file of usernames
3. **Custom Scoring** - Set custom scores during addition
4. **Custom Notes** - Add notes during addition
5. **Source Tracking** - Track where you found them
6. **Auto-categorization** - Automatically categorize by subreddit activity
7. **Validation Preview** - Show profile preview before adding
8. **Undo** - Ability to undo recent additions

## Files Changed

### Backend
- `api/main.py` - Added `/redditors/add-by-username` endpoint

### Frontend
- `reddit-ovarra-ui/src/components/RedditorsList.jsx` - Added UI and logic

### Reused
- `api/services/redditor_profile_fetcher.py` - Existing profile fetching
- `api/services/supabase_client.py` - Existing database operations

## Summary

The "Add Redditor Manually" feature allows you to:
- ✅ Add any Reddit user to your target list
- ✅ Automatically fetch their complete profile
- ✅ Get all the same data as auto-discovered redditors
- ✅ See them immediately in the list below
- ✅ Reuses existing profile fetching functionality
- ✅ Simple, intuitive UI
- ✅ Proper error handling
- ✅ Duplicate prevention

Perfect for manual prospecting, referrals, and competitor research! 🎯
