# 🔮 Foresight — AI-Powered Trend Intelligence

> **See trends before they break out.** Detect emerging signals across 50+ platforms using multi-agent simulation.

[![CI/CD](https://github.com/Shlok148Dev/Foresight.ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Shlok148Dev/Foresight.ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 What is Foresight?

Foresight is an AI-powered trend intelligence platform that detects emerging signals **48–72 hours before Google Trends** using:

- **Multi-Source NLP Pipeline** — Monitors TikTok, Discord, Reddit, Telegram, GitHub, and 44+ more platforms
- **MiroFish Behavioral Simulation** — 1M+ agents predict exactly how trends spread through communities
- **Predictive Forecasting** — Prophet + time-series models forecast trend trajectories with 85%+ accuracy
- **Action Prompts** — Every signal comes with "the one thing to do right now"

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS 4, Framer Motion |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.x, Pydantic |
| **Database** | Supabase (PostgreSQL + pgvector) |
| **Cache** | Redis |
| **Search** | Elasticsearch |
| **AI/ML** | LangChain, spaCy, scikit-learn, Prophet |
| **LLM** | Groq (Mixtral/Llama) |
| **Monitoring** | Prometheus, Sentry, Grafana |
| **CI/CD** | GitHub Actions |
| **Deployment** | Railway (backend) + Vercel (frontend) |

---

## 📂 Project Structure

```
Foresight.ai/
├── frontend/               # Next.js 15 + React 19 + TypeScript
│   ├── src/app/            # Pages (landing, auth, dashboard)
│   ├── src/lib/            # API client, utilities
│   ├── src/store/          # Zustand state management
│   └── src/test/           # Vitest test setup
│
├── backend/                # FastAPI + Python 3.11
│   ├── app/api/            # Route handlers (auth, signals, monitoring)
│   ├── app/db/             # Database connection (Supabase)
│   ├── app/models/         # SQLAlchemy ORM models
│   ├── app/services/       # Business logic (auth, detection)
│   ├── db/                 # SQL migrations
│   └── tests/              # pytest test suite
│
├── docs/                   # Documentation
│   ├── SUPABASE_SETUP.md   # Supabase configuration guide
│   └── DEPLOYMENT.md       # Railway + Vercel deployment guide
│
├── shared/                 # Cross-stack type contracts
├── tests/                  # E2E + integration tests
├── docker-compose.yml      # Redis + Elasticsearch (local dev)
├── .github/workflows/      # CI/CD pipeline
└── metrics.json            # Ralph Loop performance tracker
```

---

## ⚡ Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker (for Redis + Elasticsearch)

### 1. Clone & Install

```bash
git clone https://github.com/Shlok148Dev/Foresight.ai.git
cd Foresight.ai

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 3. Start Services

```bash
# Start Redis + Elasticsearch
docker compose up -d

# Backend (terminal 1)
cd backend
uvicorn app.main:app --reload

# Frontend (terminal 2)
cd frontend
npm run dev
```

### 4. Open
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest tests/ -v --cov=app

# Frontend tests
cd frontend && npm run test

# E2E tests
cd frontend && npm run test:e2e
```

---

## 📊 Development Methodology

This project uses a 4-tool autonomous development cycle:

| Tool | Purpose |
|------|---------|
| **GSD** (Get Shit Done) | Weekly sprints with daily standups and clear checklists |
| **Antigravity** | Spec-driven code generation from Technical Bible |
| **Ralph Loop** | Weekly metrics tracking (coverage, latency, Lighthouse) |
| **CodeRabbit** | AI-powered code review on every PR |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Shlok Tiwari** — [@Shlok148Dev](https://github.com/Shlok148Dev)
