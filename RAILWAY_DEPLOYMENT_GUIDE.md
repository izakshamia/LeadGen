# Railway Deployment Guide

## Your Railway Project
**Project ID**: `7905e1ed-92f6-487c-a8cd-b5588412ab14`

## Step-by-Step Deployment

### Step 1: Access Your Railway Project
Go to: https://railway.app/project/7905e1ed-92f6-487c-a8cd-b5588412ab14

### Step 2: Connect GitHub Repository

1. In your Railway project, click **"New Service"** or **"+ New"**
2. Select **"GitHub Repo"**
3. Choose repository: **`izakshamia/LeadGen`**
4. Select branch: **`main`**
5. Railway will automatically detect the configuration files

### Step 3: Configure Environment Variables

Click on your service → **"Variables"** tab → Add these three variables:

#### Variable 1: GEMINI_API_KEY
```
AIzaSyDM7F0yv1t0txFZZWWluuCNNOdlDhKHl4g
```

#### Variable 2: SUPABASE_URL
```
https://isipparnnrkuffstlhta.supabase.co
```

#### Variable 3: SUPABASE_KEY
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlzaXBwYXJubnJrdWZmc3RsaHRhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU3ODE4NjQsImV4cCI6MjA2MTM1Nzg2NH0.MLRMcvKSVL4Nrads1v5Y4LqAfE6X0hiJJt0iuRPvv38
```

### Step 4: Deploy

Railway will automatically deploy after you add the variables. Watch the deployment logs:

1. Click on the **"Deployments"** tab
2. Click on the latest deployment
3. Watch the build logs

Expected output:
```
✓ Building with Nixpacks
✓ Installing Python 3.10
✓ Installing dependencies from requirements.txt
✓ Starting uvicorn server
✓ Deployment successful
```

### Step 5: Get Your Service URL

After deployment succeeds:

1. Go to the **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"** if not already generated
4. Copy your service URL (e.g., `https://leadgen-production.up.railway.app`)

### Step 6: Test Your Deployment

Replace `YOUR_RAILWAY_URL` with your actual URL:

```bash
# Health check
curl https://YOUR_RAILWAY_URL/health

# Should return:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2025-11-18T..."
# }
```

```bash
# View API documentation
# Open in browser: https://YOUR_RAILWAY_URL/docs
```

```bash
# Test scraping
curl -X POST https://YOUR_RAILWAY_URL/scrape \
  -H "Content-Type: application/json" \
  -d '{"post_limit": 3, "max_age_days": 30}'
```

```bash
# Get suggestions
curl https://YOUR_RAILWAY_URL/suggestions?hours=24
```

## What Railway Will Do

1. **Detect Configuration**
   - Reads `railway.json` for build/deploy commands
   - Reads `nixpacks.toml` for Python environment
   - Uses `Reddit Ovarra/requirements.txt` for dependencies

2. **Build Process**
   - Install Python 3.10
   - Change to `Reddit Ovarra` directory
   - Install all dependencies from `requirements.txt`

3. **Deploy Process**
   - Start uvicorn server in `Reddit Ovarra` directory
   - Bind to Railway's `$PORT` environment variable
   - Enable auto-restart on failure (max 10 retries)

4. **Auto-Deploy**
   - Watches your GitHub `main` branch
   - Automatically redeploys on new commits
   - Shows deployment status in dashboard

## Configuration Files

### railway.json
Tells Railway how to build and deploy from the `Reddit Ovarra` subdirectory.

### nixpacks.toml
Specifies Python 3.10 and installation commands.

### Reddit Ovarra/Procfile
Backup configuration (Railway uses railway.json instead).

### Reddit Ovarra/requirements.txt
All Python dependencies with pinned versions.

## Monitoring Your Service

### View Logs
1. Go to your service in Railway
2. Click **"Logs"** tab
3. See real-time application logs

### Check Metrics
1. Click **"Metrics"** tab
2. View CPU, memory, and network usage

### Deployment History
1. Click **"Deployments"** tab
2. See all past deployments
3. Rollback if needed

## Troubleshooting

### Build Fails

**Check build logs for errors:**
- Missing dependencies → Update `requirements.txt`
- Python version issues → Verify `nixpacks.toml` uses Python 3.10
- Path issues → Verify `railway.json` has correct directory

### Deployment Fails

**Check runtime logs for errors:**
- Missing environment variables → Add in Variables tab
- Import errors → Check all files are committed to GitHub
- Port binding issues → Verify using `$PORT` in start command

### Database Connection Fails

**Verify Supabase credentials:**
- Check `SUPABASE_URL` is correct
- Check `SUPABASE_KEY` is the anon/public key
- Test connection from Railway logs

### Health Check Returns 503

**Database is not connected:**
- Verify Supabase credentials in Railway variables
- Check Supabase project is active
- Verify `reddit_suggestions` table exists

## Environment Variables Reference

| Variable | Description | Where to Get It |
|----------|-------------|-----------------|
| `GEMINI_API_KEY` | Google Gemini API key for AI | https://aistudio.google.com/app/apikey |
| `SUPABASE_URL` | Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Supabase anon/public key | Supabase Dashboard → Settings → API |
| `PORT` | Server port (auto-set by Railway) | Automatically provided by Railway |

## Post-Deployment Checklist

- [ ] Service deployed successfully
- [ ] Health check returns 200 OK
- [ ] Database status shows "connected"
- [ ] API docs accessible at `/docs`
- [ ] Test scrape completes successfully
- [ ] Suggestions endpoint returns data
- [ ] Logs show no errors
- [ ] Domain generated and accessible

## Next Steps After Deployment

1. **Set Up Monitoring**
   - Configure Railway alerts for downtime
   - Set up log aggregation if needed

2. **Schedule Scraping**
   - Use Railway cron jobs (if available)
   - Or use external scheduler (GitHub Actions, cron-job.org)

3. **Connect Frontend**
   - Use your Railway URL as API base URL
   - Implement authentication if needed

4. **Scale if Needed**
   - Railway auto-scales based on usage
   - Monitor metrics to optimize

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Project Logs**: Check Railway dashboard for detailed logs

## Quick Commands

```bash
# View your Railway project
railway open

# View logs (if Railway CLI installed)
railway logs

# Link local project to Railway
railway link 7905e1ed-92f6-487c-a8cd-b5588412ab14
```

---

**Ready to deploy!** Follow the steps above and your Reddit Ovarra API will be live on Railway. 🚀
