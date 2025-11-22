# Reddit Ovarra UI - Design Specification

## Overview
A simple, single-page dashboard for managing Reddit post suggestions with AI-generated Ovarra replies.

## Tech Stack Recommendation
- **Framework**: React (with Vite) or Next.js
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios or Fetch API
- **State Management**: React hooks (useState, useEffect)
- **Deployment**: Vercel or Netlify (free tier)

## UI Layout

### 1. Header Section
```
┌─────────────────────────────────────────────────────────┐
│  🎯 Reddit Ovarra Dashboard                             │
│  Status: ● Connected to API                             │
└─────────────────────────────────────────────────────────┘
```

### 2. Control Panel (Top Section)
```
┌─────────────────────────────────────────────────────────┐
│  🔍 Scrape New Posts                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Subreddits: [CamGirlProblems, OnlyFansAdvice]  │   │
│  │ Keywords: [leak, dmca, stolen]                  │   │
│  │ Post Limit: [5] ▼    Max Age: [30 days] ▼      │   │
│  │                                                  │   │
│  │  [🚀 Start Scraping]                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Last Scrape: 2 minutes ago | Processed: 3 | Skipped: 2│
└─────────────────────────────────────────────────────────┘
```

### 3. Filters & Stats (Middle Section)
```
┌─────────────────────────────────────────────────────────┐
│  📊 Suggestions Dashboard                               │
│  ┌──────────┬──────────┬──────────┬──────────┐        │
│  │   New    │ Approved │   Sent   │ Ignored  │        │
│  │    6     │    0     │    0     │    0     │        │
│  └──────────┴──────────┴──────────┴──────────┘        │
│                                                          │
│  Time Window: [24 hours] ▼   Status: [All] ▼           │
│  🔄 Refresh                                             │
└─────────────────────────────────────────────────────────┘
```

### 4. Suggestions List (Main Content)
```
┌─────────────────────────────────────────────────────────┐
│  📝 Suggestions (6 total)                               │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🆕 NEW                                          │   │
│  │ clarification on leaks                          │   │
│  │ r/onlyfansadvice • 2 hours ago                  │   │
│  │                                                  │   │
│  │ 💬 Suggested Reply:                             │   │
│  │ Hey, creator. DMs vs. feeds, leaks happen...    │   │
│  │ [Show Full Reply ▼]                             │   │
│  │                                                  │   │
│  │ [🔗 View Post] [✅ Approve] [📋 Copy] [🗑️ Ignore]│   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🆕 NEW                                          │   │
│  │ Dress up in disguise                            │   │
│  │ r/onlyfansadvice • 3 hours ago                  │   │
│  │ ...                                              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  [Load More]                                            │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Scraping Control
- **Input Fields**:
  - Subreddits (comma-separated or multi-select)
  - Keywords (comma-separated or multi-select)
  - Post Limit (dropdown: 5, 10, 20, 50)
  - Max Age (dropdown: 7, 30, 60, 120 days)
- **Actions**:
  - Start Scraping button
  - Loading indicator during scrape
  - Success/error toast notifications
  - Display scrape results (processed, skipped, failed)

### 2. Dashboard Stats
- **Status Cards**:
  - Count by status (New, Approved, Sent, Ignored)
  - Color-coded badges
  - Click to filter by status
- **Filters**:
  - Time window dropdown (1h, 6h, 24h, 48h, 7d)
  - Status filter (All, New, Approved, Sent, Ignored)
  - Refresh button with auto-refresh toggle

### 3. Suggestions List
- **Card Display**:
  - Status badge (color-coded)
  - Reddit post title
  - Subreddit and timestamp
  - Truncated reply with "Show Full" toggle
  - Action buttons
- **Actions**:
  - View Post (opens Reddit in new tab)
  - Approve (changes status to "approved")
  - Copy Reply (copies to clipboard)
  - Ignore (changes status to "ignored")
  - Edit Reply (inline editing)

### 4. Additional Features
- **Search**: Filter suggestions by title or content
- **Sorting**: By date, subreddit, or status
- **Pagination**: Load more or infinite scroll
- **Dark Mode**: Toggle between light/dark themes
- **Export**: Download suggestions as CSV/JSON

## Color Scheme

### Light Mode
- Background: #F9FAFB (gray-50)
- Cards: #FFFFFF
- Primary: #3B82F6 (blue-500)
- Success: #10B981 (green-500)
- Warning: #F59E0B (amber-500)
- Danger: #EF4444 (red-500)
- Text: #111827 (gray-900)

### Dark Mode
- Background: #111827 (gray-900)
- Cards: #1F2937 (gray-800)
- Primary: #60A5FA (blue-400)
- Success: #34D399 (green-400)
- Warning: #FBBF24 (amber-400)
- Danger: #F87171 (red-400)
- Text: #F9FAFB (gray-50)

## Status Badge Colors
- **New**: Blue (#3B82F6)
- **Approved**: Green (#10B981)
- **Sent**: Purple (#8B5CF6)
- **Ignored**: Gray (#6B7280)

## API Integration

### Endpoints to Use
1. **GET /health** - Check API status
2. **POST /scrape** - Trigger scraping
3. **GET /suggestions?hours=24** - Fetch suggestions
4. **PATCH /suggestions/{id}** - Update status (if implemented)

### API Base URL
```javascript
const API_BASE_URL = 'https://web-production-3fe3.up.railway.app';
```

## Component Structure

```
App
├── Header
│   ├── Logo
│   └── StatusIndicator
├── ScrapePanel
│   ├── ScrapeForm
│   └── ScrapeResults
├── Dashboard
│   ├── StatsCards
│   └── Filters
└── SuggestionsList
    ├── SuggestionCard (repeated)
    │   ├── StatusBadge
    │   ├── PostInfo
    │   ├── ReplyText
    │   └── ActionButtons
    └── LoadMore
```

## User Flows

### Flow 1: Scrape New Posts
1. User enters subreddits and keywords
2. User clicks "Start Scraping"
3. Loading indicator appears
4. API call to POST /scrape
5. Success toast shows results
6. Suggestions list auto-refreshes

### Flow 2: Review Suggestions
1. User views list of suggestions
2. User clicks "Show Full Reply" to expand
3. User reads the AI-generated reply
4. User clicks "Copy" to copy reply
5. Success toast confirms copy
6. User clicks "Approve" to mark as reviewed

### Flow 3: Filter & Search
1. User selects time window (e.g., 24 hours)
2. List updates with filtered results
3. User selects status filter (e.g., "New")
4. List shows only new suggestions
5. User types in search box
6. List filters in real-time

## Responsive Design

### Desktop (>1024px)
- Full layout with sidebar stats
- 2-column suggestion cards
- All features visible

### Tablet (768px - 1024px)
- Single column layout
- Collapsible filters
- Full features

### Mobile (<768px)
- Stacked layout
- Bottom sheet for filters
- Simplified action buttons
- Swipe gestures for actions

## Implementation Priority

### Phase 1 (MVP - 2-3 hours)
1. ✅ Basic layout with header
2. ✅ Scrape form with API integration
3. ✅ Suggestions list display
4. ✅ Basic filtering (time window)
5. ✅ Copy to clipboard functionality

### Phase 2 (Enhanced - 2-3 hours)
1. ✅ Status badges and filtering
2. ✅ Stats dashboard
3. ✅ Search functionality
4. ✅ Pagination/infinite scroll
5. ✅ Toast notifications

### Phase 3 (Polish - 1-2 hours)
1. ✅ Dark mode
2. ✅ Responsive design
3. ✅ Loading states
4. ✅ Error handling
5. ✅ Auto-refresh

## Sample Code Structure

### API Service
```javascript
// src/services/api.js
const API_BASE_URL = 'https://web-production-3fe3.up.railway.app';

export const api = {
  async health() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },
  
  async scrape(params) {
    const response = await fetch(`${API_BASE_URL}/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return response.json();
  },
  
  async getSuggestions(hours = 24) {
    const response = await fetch(`${API_BASE_URL}/suggestions?hours=${hours}`);
    return response.json();
  }
};
```

### Main Component
```javascript
// src/App.jsx
import { useState, useEffect } from 'react';
import { api } from './services/api';

function App() {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [timeWindow, setTimeWindow] = useState(24);
  
  useEffect(() => {
    loadSuggestions();
  }, [timeWindow]);
  
  const loadSuggestions = async () => {
    setLoading(true);
    const data = await api.getSuggestions(timeWindow);
    setSuggestions(data.suggestions);
    setLoading(false);
  };
  
  const handleScrape = async (params) => {
    setLoading(true);
    const result = await api.scrape(params);
    // Show toast notification
    await loadSuggestions(); // Refresh list
    setLoading(false);
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <ScrapePanel onScrape={handleScrape} />
      <Dashboard 
        suggestions={suggestions}
        timeWindow={timeWindow}
        onTimeWindowChange={setTimeWindow}
      />
      <SuggestionsList 
        suggestions={suggestions}
        loading={loading}
      />
    </div>
  );
}
```

## Deployment

### Option 1: Vercel (Recommended)
1. Push code to GitHub
2. Connect to Vercel
3. Auto-deploy on push
4. Free SSL and CDN

### Option 2: Netlify
1. Push code to GitHub
2. Connect to Netlify
3. Configure build settings
4. Deploy

### Option 3: Railway (Same as API)
1. Add frontend as new service
2. Configure build command
3. Deploy alongside API

## Next Steps

1. **Choose Framework**: React with Vite (fastest) or Next.js (more features)
2. **Set Up Project**: `npm create vite@latest reddit-ovarra-ui -- --template react`
3. **Install Dependencies**: `npm install axios tailwindcss`
4. **Build Components**: Start with Header → ScrapePanel → SuggestionsList
5. **Test Locally**: Connect to Railway API
6. **Deploy**: Push to Vercel

## Estimated Timeline
- **Setup**: 30 minutes
- **Phase 1 (MVP)**: 2-3 hours
- **Phase 2 (Enhanced)**: 2-3 hours
- **Phase 3 (Polish)**: 1-2 hours
- **Total**: 6-9 hours for complete UI

Would you like me to create a starter template with the basic structure?
