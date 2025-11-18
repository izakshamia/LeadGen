# Railway Environment Variables

Copy these environment variables to your Railway project settings.

## Required Environment Variables

Go to Railway Dashboard → Your Service → Variables tab

Add these three variables:

### 1. GEMINI_API_KEY
```
AIzaSyDM7F0yv1t0txFZZWWluuCNNOdlDhKHl4g
```

### 2. SUPABASE_URL
```
https://isipparnnrkuffstlhta.supabase.co
```

### 3. SUPABASE_KEY
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlzaXBwYXJubnJrdWZmc3RsaHRhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU3ODE4NjQsImV4cCI6MjA2MTM1Nzg2NH0.MLRMcvKSVL4Nrads1v5Y4LqAfE6X0hiJJt0iuRPvv38
```

## How to Add Variables in Railway

1. Go to https://railway.app/project/7905e1ed-92f6-487c-a8cd-b5588412ab14
2. Click on your service
3. Go to the **"Variables"** tab
4. Click **"New Variable"**
5. Add each variable name and value
6. Click **"Add"** for each one

## Verification

After adding variables, Railway will automatically redeploy your service.

Check the deployment logs to ensure:
- ✅ Dependencies install successfully
- ✅ Uvicorn starts without errors
- ✅ No missing environment variable errors

## Testing Your Deployment

Once deployed, Railway will give you a URL like:
```
https://your-service-name.up.railway.app
```

Test it with:
```bash
# Health check
curl https://your-service-name.up.railway.app/health

# API docs
# Open in browser: https://your-service-name.up.railway.app/docs
```

## Important Notes

- Railway automatically sets the `PORT` environment variable
- The Procfile uses `$PORT` to bind to the correct port
- Railway will detect changes to your GitHub repo and auto-deploy
- Check the "Deployments" tab to see build logs

## Troubleshooting

If deployment fails:

1. **Check Build Logs** - Look for missing dependencies or Python errors
2. **Check Runtime Logs** - Look for environment variable errors
3. **Verify Variables** - Make sure all 3 variables are set correctly
4. **Check Procfile** - Should be in `Reddit Ovarra/Procfile`

## Root Directory Issue

⚠️ **IMPORTANT**: Railway might deploy from the repository root, but your app is in `Reddit Ovarra/` subdirectory.

You have two options:

### Option A: Add railway.json (Recommended)
Create a `railway.json` file in the repository root to specify the working directory.

### Option B: Move Procfile to Root
Move the Procfile to the repository root and update the command to run from the subdirectory.

Let me know which option you prefer, and I'll help you implement it!
