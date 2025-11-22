# Reddit Ovarra UI - Quick Start Guide

## 🎯 What You're Building

A clean, modern dashboard to:
- ✅ Trigger Reddit scraping with custom parameters
- ✅ View AI-generated reply suggestions
- ✅ Filter and search suggestions
- ✅ Copy replies to clipboard
- ✅ Manage suggestion status (approve/ignore)

## 🚀 Fastest Way to Get Started

### Option 1: React + Vite (Recommended - Fastest)

```bash
# Create project
npm create vite@latest reddit-ovarra-ui -- --template react
cd reddit-ovarra-ui

# Install dependencies
npm install
npm install axios
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Start development
npm run dev
```

**Time to first screen**: 5 minutes

### Option 2: Next.js (More Features)

```bash
# Create project
npx create-next-app@latest reddit-ovarra-ui
cd reddit-ovarra-ui

# Install dependencies
npm install axios

# Start development
npm run dev
```

**Time to first screen**: 5 minutes

### Option 3: Plain HTML + JavaScript (Simplest)

Just create an `index.html` file - no build tools needed!

**Time to first screen**: 2 minutes

## 📦 What's Included in the Design

### Core Features
1. **Scrape Control Panel**
   - Input fields for subreddits, keywords, limits
   - Start scraping button
   - Real-time status updates

2. **Stats Dashboard**
   - Count by status (New, Approved, Sent, Ignored)
   - Quick filters
   - Time window selector

3. **Suggestions List**
   - Card-based layout
   - Expandable replies
   - Action buttons (View, Approve, Copy, Ignore)

4. **Responsive Design**
   - Desktop, tablet, mobile optimized
   - Dark mode support

## 🎨 Design Highlights

- **Clean & Modern**: Tailwind CSS styling
- **User-Friendly**: Intuitive layout and actions
- **Fast**: Optimized API calls and caching
- **Accessible**: Keyboard navigation and screen reader support

## 📱 Responsive Breakpoints

- **Mobile**: < 768px (stacked layout)
- **Tablet**: 768px - 1024px (2-column)
- **Desktop**: > 1024px (full layout)

## 🔌 API Integration

Your API is already live at:
```
https://web-production-3fe3.up.railway.app
```

### Endpoints to Use:
```javascript
// Health check
GET /health

// Trigger scraping
POST /scrape
Body: {
  "subreddits": ["CamGirlProblems"],
  "keywords": ["leak"],
  "post_limit": 10,
  "max_age_days": 30
}

// Get suggestions
GET /suggestions?hours=24
```

## 🎯 Implementation Steps

### Step 1: Set Up Project (5 min)
```bash
npm create vite@latest reddit-ovarra-ui -- --template react
cd reddit-ovarra-ui
npm install
npm install axios
```

### Step 2: Configure Tailwind (5 min)
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Update `tailwind.config.js`:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Add to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 3: Create API Service (10 min)
Create `src/services/api.js`:
```javascript
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

### Step 4: Build Components (2-3 hours)

Create these components:
- `Header.jsx` - Top navigation
- `ScrapePanel.jsx` - Scraping controls
- `Dashboard.jsx` - Stats and filters
- `SuggestionCard.jsx` - Individual suggestion
- `SuggestionsList.jsx` - List of suggestions

### Step 5: Add State Management (30 min)

Use React hooks in `App.jsx`:
```javascript
const [suggestions, setSuggestions] = useState([]);
const [loading, setLoading] = useState(false);
const [timeWindow, setTimeWindow] = useState(24);
```

### Step 6: Test & Deploy (30 min)

```bash
# Build for production
npm run build

# Deploy to Vercel
npx vercel

# Or deploy to Netlify
npx netlify deploy
```

## 🎨 Styling Quick Reference

### Colors
```javascript
// Tailwind classes
bg-blue-500    // Primary blue
bg-green-500   // Success green
bg-red-500     // Danger red
bg-gray-100    // Light background
bg-gray-800    // Dark background
```

### Common Patterns
```jsx
// Card
<div className="bg-white rounded-lg shadow-md p-6">

// Button
<button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">

// Input
<input className="border border-gray-300 rounded-lg px-4 py-2 w-full focus:border-blue-500">

// Badge
<span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
```

## 📊 Sample Data Structure

### Suggestion Object
```javascript
{
  id: "ced06a16-a63e-493d-a932-c4e8bb68fc30",
  reddit_name: "clarification on leaks",
  reddit_url: "https://www.reddit.com/r/onlyfansadvice/comments/...",
  suggested_response: "Hey, creator. DMs vs. feeds...",
  status: "new",
  created_at: "2025-11-18T17:29:31.630302Z"
}
```

### Scrape Result
```javascript
{
  status: "success",
  processed: 3,
  skipped: 2,
  failed: 0,
  message: "Scraping completed successfully - 3 new suggestions saved"
}
```

## 🚀 Deployment Options

### Vercel (Recommended)
- **Pros**: Free, fast, auto-deploy from GitHub
- **Setup**: 2 minutes
- **URL**: `your-app.vercel.app`

```bash
npm install -g vercel
vercel
```

### Netlify
- **Pros**: Free, drag-and-drop deploy
- **Setup**: 2 minutes
- **URL**: `your-app.netlify.app`

```bash
npm run build
npx netlify deploy --prod
```

### Railway (Same as API)
- **Pros**: Everything in one place
- **Setup**: 5 minutes
- **URL**: `your-app.up.railway.app`

## 📚 Resources

### Documentation
- React: https://react.dev
- Tailwind CSS: https://tailwindcss.com
- Vite: https://vitejs.dev

### UI Components (Optional)
- Headless UI: https://headlessui.com
- Radix UI: https://www.radix-ui.com
- shadcn/ui: https://ui.shadcn.com

### Icons
- Heroicons: https://heroicons.com
- Lucide: https://lucide.dev
- Emoji: Built-in (🎯 🚀 ✅ 📋 etc.)

## 🎯 MVP Checklist

Build these features first:

- [ ] Basic layout with header
- [ ] API health check indicator
- [ ] Scrape form with submit
- [ ] Display list of suggestions
- [ ] Copy reply to clipboard
- [ ] Time window filter
- [ ] Loading states
- [ ] Error handling

**Estimated time**: 3-4 hours

## 🔥 Quick Wins

### 1. Use the Browser's Fetch API
No need for axios if you want to keep it simple:
```javascript
const response = await fetch(url);
const data = await response.json();
```

### 2. Use Emoji Instead of Icon Libraries
```javascript
🎯 🚀 ✅ 📋 🗑️ 🔗 📊 🔍 💬 🆕
```

### 3. Copy to Clipboard
```javascript
navigator.clipboard.writeText(text);
```

### 4. Toast Notifications
Use a simple library like `react-hot-toast`:
```bash
npm install react-hot-toast
```

## 💡 Pro Tips

1. **Start Simple**: Build the MVP first, add features later
2. **Use Tailwind**: Faster than writing custom CSS
3. **Test Early**: Connect to the API from day 1
4. **Mobile First**: Design for mobile, scale up
5. **Dark Mode**: Add it early, users love it

## 🎬 Next Steps

1. **Choose your stack** (React + Vite recommended)
2. **Set up project** (5 minutes)
3. **Build MVP** (3-4 hours)
4. **Deploy** (5 minutes)
5. **Share with users** 🎉

## 📞 Need Help?

- Check `UI_DESIGN_SPEC.md` for detailed specifications
- Check `UI_MOCKUP.md` for visual reference
- Your API is live and ready to use!

**Ready to build?** Start with Option 1 (React + Vite) and you'll have a working UI in a few hours!
