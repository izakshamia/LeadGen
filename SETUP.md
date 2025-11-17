# Setup Guide - Using Gemini AI

## 1. Get Your Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

**Note:** Gemini has a generous free tier (15 requests per minute, 1500 requests per day)

## 2. Create .env File

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

## 3. Install Dependencies

```bash
# Install Python packages
pip3 install -r "Reddit Ovarra/requirements.txt"
```

## 4. Run the Pipeline

```bash
cd "Reddit Ovarra"

# Run with default settings
python3 pipeline.py --debug

# Or continue from where you left off (uses checkpoints)
python3 pipeline.py --debug
```

## What Changed from OpenAI to Gemini

- Replaced `openai` package with `google-generativeai`
- Using `gemini-1.5-flash` model (fast and free)
- Updated API calls in `api_utils.py`
- Changed environment variable from `OPENAI_API_KEY` to `GEMINI_API_KEY`

## Benefits of Gemini

- **Free tier**: 15 RPM, 1500 requests/day
- **Fast**: gemini-1.5-flash is optimized for speed
- **Good quality**: Comparable to GPT-4 for most tasks
- **Large context**: 1M token context window

## Troubleshooting

If you get "API key not found":
- Make sure `.env` file is in the project root
- Check that the key starts with `GEMINI_API_KEY=`
- No quotes needed around the key value

If you get rate limit errors:
- Free tier: 15 requests per minute
- The code already has delays (1.5-2 seconds between requests)
- If needed, increase the `time.sleep()` values in `api_utils.py`
