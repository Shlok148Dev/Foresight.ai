# Foresight — Supabase Setup Guide

> **Supabase Free Tier:** 500MB storage, unlimited API calls, 50K monthly active users

---

## 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **"New Project"**
3. Set:
   - **Name:** `foresight`
   - **Database Password:** (save this — you'll need it for `DATABASE_URL`)
   - **Region:** Choose closest to your users (e.g., `us-east-1`)
4. Click **"Create new project"** and wait ~2 minutes

---

## 2. Get Your Credentials

Go to **Project Settings → API** and copy:

| Credential | Where to Find | Usage |
|-----------|---------------|-------|
| **Project URL** | Settings → API → Project URL | `SUPABASE_URL` |
| **anon public key** | Settings → API → Project API keys | `SUPABASE_ANON_KEY` (frontend) |
| **service_role key** | Settings → API → Project API keys | `SUPABASE_SERVICE_ROLE_KEY` (backend) |

Go to **Settings → Database → Connection string → URI** and copy:

| Credential | Where to Find | Usage |
|-----------|---------------|-------|
| **Connection string** | Settings → Database → URI (Transaction mode, port 6543) | `DATABASE_URL` |

> ⚠️ Replace `[YOUR-PASSWORD]` in the connection string with your database password.

---

## 3. Enable pgvector Extension

1. Go to **Database → Extensions** in the Supabase Dashboard
2. Search for **"vector"**
3. Click **Enable**

Or run in SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 4. Run the Database Migration

1. Go to **SQL Editor** in the Supabase Dashboard
2. Click **"New Query"**
3. Paste the contents of `backend/db/supabase_migration.sql`
4. Click **"Run"**

This creates:
- 6 tables: `users`, `signals`, `detections`, `forecasts`, `simulations`, `saved_signals`
- 3 extensions: `vector`, `uuid-ossp`, `pg_trgm`
- 15+ indexes for query performance
- Row Level Security policies
- Auto-updating timestamp triggers

---

## 5. Configure Your Environment

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

```env
# Supabase credentials
SUPABASE_URL=https://abcdefghijk.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Direct connection string (Transaction mode, port 6543)
DATABASE_URL=postgresql+asyncpg://postgres.abcdefghijk:YOUR-PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

---

## 6. Verify Connection

### Quick test (Python):
```python
from supabase import create_client
client = create_client("https://your-project.supabase.co", "your-service-role-key")
result = client.table("users").select("id").limit(1).execute()
print(f"Connected! Rows: {len(result.data)}")
```

### Via backend:
```bash
cd backend
python -c "from app.db.database import get_supabase; sb = get_supabase(); print('Supabase connected!' if sb else 'Failed')"
```

---

## 7. Local Development

You have two options:

### Option A: Use Supabase Cloud (Recommended)
- Just set the env vars in `.env` and run:
```bash
docker compose up -d    # Starts Redis + Elasticsearch only
cd backend && uvicorn app.main:app --reload
```

### Option B: Supabase Local (CLI)
```bash
# Install Supabase CLI
npm install -g supabase
supabase init
supabase start   # Starts local Supabase (Docker required)
# Connection: postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
```

---

## 8. Connection Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Foresight Backend                    │
│                                                        │
│  SQLAlchemy ORM ──→ Supabase PostgreSQL (port 6543)   │
│  (asyncpg)          via Supavisor connection pooler    │
│                                                        │
│  supabase-py ────→ Supabase REST API                  │
│  (optional)         Auth, Storage, Realtime            │
└────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Supabase   │
                    │   Cloud     │
                    │             │
                    │ PostgreSQL  │  ← Your tables + pgvector
                    │ Auth        │  ← Optional (we use custom JWT)
                    │ Storage     │  ← File uploads (future)
                    │ Realtime    │  ← WebSocket (future)
                    │ Edge Funcs  │  ← Serverless (future)
                    └─────────────┘
```

---

## 9. Supabase Free Tier Limits

| Resource | Limit | Notes |
|----------|-------|-------|
| Database | 500MB | Plenty for MVP |
| API requests | Unlimited | No rate limits on REST API |
| Bandwidth | 5GB/month | Sufficient for dev + staging |
| Auth users | 50K MAU | More than enough |
| Realtime | 200 concurrent | Good for dev |
| Edge Functions | 500K invocations | — |
| File Storage | 1GB | — |

---

## 10. Deployment to Railway

Add these environment variables to your Railway service:

```bash
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_SERVICE_ROLE_KEY=your-key
railway variables set DATABASE_URL=postgresql+asyncpg://postgres.xxx:password@pooler.supabase.com:6543/postgres
railway variables set SECRET_KEY=$(openssl rand -hex 32)
```
