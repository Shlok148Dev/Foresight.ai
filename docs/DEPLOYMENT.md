# Foresight — Deployment Guide (Railway + Vercel + Supabase)

> **Total cost: $0/month** using free tiers of all three services.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Vercel     │     │   Railway    │     │  Supabase    │
│  Frontend    │────→│  Backend     │────→│  PostgreSQL  │
│  Next.js 15  │     │  FastAPI     │     │  + pgvector  │
│  (Free)      │     │  (Free)      │     │  (Free)      │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────┴──────┐
                    │ Local Only  │
                    │ Redis       │
                    │ Elasticsearch│
                    └─────────────┘
```

---

## Step 1: Supabase Setup

See [docs/SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for full instructions.

**Quick version:**
1. Create project at [supabase.com](https://supabase.com)
2. Run `backend/db/supabase_migration.sql` in SQL Editor
3. Copy credentials to `.env`

---

## Step 2: Deploy Backend to Railway

### Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

### Initialize project
```bash
cd backend
railway init
```

### Set environment variables
```bash
railway variables set \
  DATABASE_URL="postgresql+asyncpg://postgres.xxx:password@pooler.supabase.com:6543/postgres" \
  SUPABASE_URL="https://your-project.supabase.co" \
  SUPABASE_SERVICE_ROLE_KEY="your-service-role-key" \
  SECRET_KEY="$(openssl rand -hex 32)" \
  APP_ENV="production" \
  CORS_ORIGINS="https://your-app.vercel.app"
```

### Deploy
```bash
railway up
```

### Verify
```bash
curl https://your-backend.railway.app/health
# → {"status":"healthy","version":"0.1.0",...}
```

---

## Step 3: Deploy Frontend to Vercel

### Install Vercel CLI
```bash
npm install -g vercel
cd frontend
vercel login
```

### Set environment variables
```bash
vercel env add NEXT_PUBLIC_API_URL          # → https://your-backend.railway.app
vercel env add NEXT_PUBLIC_SUPABASE_URL     # → https://your-project.supabase.co
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY # → your anon key
```

### Deploy
```bash
vercel --prod
```

---

## Step 4: Verify Deployment

```bash
# Backend health
curl https://your-backend.railway.app/health

# API docs
open https://your-backend.railway.app/docs

# Frontend
open https://your-app.vercel.app

# Supabase dashboard
open https://supabase.com/dashboard/project/your-project-id
```

---

## CI/CD (Automatic Deploys)

- **Railway:** Auto-deploys on push to `main` (connect GitHub repo)
- **Vercel:** Auto-deploys on push to `main` (connect GitHub repo)
- **Supabase:** Migrations run manually via SQL Editor or Supabase CLI

### GitHub Secrets Required

Add these to **GitHub → Settings → Secrets → Actions**:

| Secret | Value |
|--------|-------|
| `SUPABASE_URL` | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `your-service-role-key` |
| `SUPABASE_DATABASE_URL` | `postgresql+asyncpg://...` |
| `SECRET_KEY` | `openssl rand -hex 32` |
| `RAILWAY_TOKEN` | From Railway dashboard |
| `VERCEL_TOKEN` | From Vercel dashboard |

---

## Conventional Commits

Use these commit messages for the migration:

```
feat(db): migrate from local PostgreSQL to Supabase cloud
feat(db): add Supabase Python client for REST API access
refactor(config): update connection pooling for Supabase free tier
refactor(docker): remove PostgreSQL container (now on Supabase)
refactor(ci): remove Postgres service, add Supabase integration tests
feat(db): add Supabase SQL migration with RLS policies
docs: add Supabase setup guide and deployment instructions
test: add Supabase integration tests
chore: update requirements.txt with supabase-py
```
