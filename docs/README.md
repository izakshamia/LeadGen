# Reddit Ovarra Documentation

Complete documentation for the Reddit Ovarra AI-powered DMCA response system.

## 📚 Documentation Structure

### API Documentation (`api/`)
Complete guides for the REST API service.

- **[README.md](api/README.md)** - Complete API documentation
- **[QUICKSTART.md](api/QUICKSTART.md)** - Quick start guide
- **[HOW_TO_RUN.md](api/HOW_TO_RUN.md)** - Detailed running instructions
- **[SUPABASE_SETUP.md](api/SUPABASE_SETUP.md)** - Database setup guide

### UI Documentation (`ui/`)
Complete specifications for building the user interface.

- **[UI_DESIGN_SPEC.md](ui/UI_DESIGN_SPEC.md)** - Detailed component specifications
- **[UI_MOCKUP.md](ui/UI_MOCKUP.md)** - Visual mockups for all screens
- **[UI_QUICK_START.md](ui/UI_QUICK_START.md)** - Step-by-step implementation guide
- **[UI_SUMMARY.md](ui/UI_SUMMARY.md)** - Executive overview

### Deployment Documentation (`deployment/`)
Guides for deploying to production.

- **[RAILWAY_DEPLOYMENT_GUIDE.md](deployment/RAILWAY_DEPLOYMENT_GUIDE.md)** - Complete Railway deployment guide
- **[RAILWAY_ENV_VARS.md](deployment/RAILWAY_ENV_VARS.md)** - Environment variables reference

### Feature Specifications (`specs/`)
Detailed specifications for implemented features.

- **[supabase-api-integration/](specs/supabase-api-integration/)** - Supabase API integration spec
  - **[requirements.md](specs/supabase-api-integration/requirements.md)** - EARS-compliant requirements
  - **[design.md](specs/supabase-api-integration/design.md)** - System design document
  - **[tasks.md](specs/supabase-api-integration/tasks.md)** - Implementation task list

### User Guides (`guides/`)
Practical guides for using the system.

- **[SUBREDDIT_LIST.md](guides/SUBREDDIT_LIST.md)** - List of target subreddits
- **[SUBREDDIT_DISCOVERY.md](guides/SUBREDDIT_DISCOVERY.md)** - How to discover new subreddits
- **[INTEGRATION_TEST_RESULTS.md](guides/INTEGRATION_TEST_RESULTS.md)** - Integration test results

## 🚀 Quick Links

### Getting Started
1. [API Quick Start](api/QUICKSTART.md) - Get the API running in 5 minutes
2. [Supabase Setup](api/SUPABASE_SETUP.md) - Set up your database
3. [How to Run](api/HOW_TO_RUN.md) - Complete running guide

### Building the UI
1. [UI Quick Start](ui/UI_QUICK_START.md) - Build the UI in 3-4 hours
2. [UI Design Spec](ui/UI_DESIGN_SPEC.md) - Complete specifications
3. [UI Mockups](ui/UI_MOCKUP.md) - Visual reference

### Deployment
1. [Railway Deployment](deployment/RAILWAY_DEPLOYMENT_GUIDE.md) - Deploy to Railway
2. [Environment Variables](deployment/RAILWAY_ENV_VARS.md) - Configuration guide

## 📖 Documentation by Role

### For Developers
- [API README](api/README.md) - Complete API documentation
- [Feature Specs](specs/supabase-api-integration/) - Technical specifications
- [Integration Tests](guides/INTEGRATION_TEST_RESULTS.md) - Test results

### For Designers
- [UI Design Spec](ui/UI_DESIGN_SPEC.md) - Complete UI specifications
- [UI Mockups](ui/UI_MOCKUP.md) - Visual mockups
- [UI Summary](ui/UI_SUMMARY.md) - Executive overview

### For DevOps
- [Railway Deployment](deployment/RAILWAY_DEPLOYMENT_GUIDE.md) - Deployment guide
- [Environment Variables](deployment/RAILWAY_ENV_VARS.md) - Configuration
- [Supabase Setup](api/SUPABASE_SETUP.md) - Database setup

### For Product Managers
- [Requirements](specs/supabase-api-integration/requirements.md) - Feature requirements
- [Design Document](specs/supabase-api-integration/design.md) - System design
- [UI Summary](ui/UI_SUMMARY.md) - UI overview

## 🎯 Common Tasks

### Running the API
```bash
# See: api/QUICKSTART.md
uvicorn api.main:app --reload
```

### Running the CLI
```bash
# See: api/HOW_TO_RUN.md
python -m cli.pipeline --debug
```

### Building the UI
```bash
# See: ui/UI_QUICK_START.md
npm create vite@latest reddit-ovarra-ui -- --template react
```

### Deploying to Railway
```bash
# See: deployment/RAILWAY_DEPLOYMENT_GUIDE.md
# 1. Connect GitHub repo
# 2. Add environment variables
# 3. Deploy automatically
```

## 📊 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| API README | ✅ Complete | Nov 2025 |
| API Quick Start | ✅ Complete | Nov 2025 |
| How to Run | ✅ Complete | Nov 2025 |
| Supabase Setup | ✅ Complete | Nov 2025 |
| UI Design Spec | ✅ Complete | Nov 2025 |
| UI Mockups | ✅ Complete | Nov 2025 |
| UI Quick Start | ✅ Complete | Nov 2025 |
| UI Summary | ✅ Complete | Nov 2025 |
| Railway Deployment | ✅ Complete | Nov 2025 |
| Environment Variables | ✅ Complete | Nov 2025 |
| Requirements | ✅ Complete | Nov 2025 |
| Design Document | ✅ Complete | Nov 2025 |
| Task List | ✅ Complete | Nov 2025 |
| Integration Tests | ✅ Complete | Nov 2025 |

## 🔍 Search by Topic

### API
- [API Endpoints](api/README.md#api-endpoints)
- [Request/Response Models](api/README.md#request-response-models)
- [Error Handling](api/README.md#error-handling)

### Database
- [Schema](api/SUPABASE_SETUP.md#schema)
- [Setup Instructions](api/SUPABASE_SETUP.md#setup-steps)
- [Testing](api/SUPABASE_SETUP.md#testing-the-setup)

### UI
- [Component Structure](ui/UI_DESIGN_SPEC.md#component-structure)
- [Color Scheme](ui/UI_DESIGN_SPEC.md#color-scheme)
- [Responsive Design](ui/UI_DESIGN_SPEC.md#responsive-design)

### Deployment
- [Railway Setup](deployment/RAILWAY_DEPLOYMENT_GUIDE.md#step-by-step-deployment)
- [Environment Variables](deployment/RAILWAY_ENV_VARS.md#required-environment-variables)
- [Troubleshooting](deployment/RAILWAY_DEPLOYMENT_GUIDE.md#troubleshooting)

## 📞 Need Help?

1. **API Questions** → Check [api/README.md](api/README.md)
2. **UI Questions** → Check [ui/UI_QUICK_START.md](ui/UI_QUICK_START.md)
3. **Deployment Questions** → Check [deployment/RAILWAY_DEPLOYMENT_GUIDE.md](deployment/RAILWAY_DEPLOYMENT_GUIDE.md)
4. **Feature Questions** → Check [specs/](specs/)

## 🔗 External Links

- **Live API**: https://web-production-3fe3.up.railway.app
- **API Docs**: https://web-production-3fe3.up.railway.app/docs
- **GitHub**: https://github.com/izakshamia/LeadGen
- **Supabase**: https://supabase.com
- **Railway**: https://railway.app

---

**Documentation Version**: 1.0
**Last Updated**: November 2025
**Status**: ✅ Complete and up-to-date
