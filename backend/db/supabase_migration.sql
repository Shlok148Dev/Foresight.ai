-- ==========================================================
-- Foresight — Supabase Initial Migration
-- ==========================================================
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- This creates all tables, indexes, and extensions.
-- Supabase auto-manages: backups, replication, connection pooling.
-- ==========================================================

-- ── Extensions ──────────────────────────────────────────────

-- pgvector: vector embeddings for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trigram index for fuzzy/full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- ── Enums ───────────────────────────────────────────────────

DO $$ BEGIN
    CREATE TYPE spread_stage AS ENUM ('embryonic', 'emerging', 'accelerating', 'peaking', 'declining');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('free', 'pro', 'team', 'enterprise', 'admin');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE platform_type AS ENUM ('twitter', 'reddit', 'discord', 'tiktok', 'telegram', 'github', 'youtube', 'hackernews', 'substack', 'other');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- ── Users ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    role user_role DEFAULT 'free' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    domains TEXT[] DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);


-- ── Detections ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic VARCHAR(500) NOT NULL,
    description TEXT,
    stage spread_stage DEFAULT 'embryonic' NOT NULL,
    confidence FLOAT DEFAULT 0.0 NOT NULL,
    signal_count INTEGER DEFAULT 0,
    velocity FLOAT DEFAULT 0.0,
    platforms TEXT[] DEFAULT '{}',
    communities TEXT[] DEFAULT '{}',
    keywords TEXT[] DEFAULT '{}',
    action_prompt TEXT,
    metadata JSONB DEFAULT '{}',
    first_seen TIMESTAMP DEFAULT NOW() NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_detections_topic ON detections(topic);
CREATE INDEX IF NOT EXISTS idx_detections_stage ON detections(stage);
CREATE INDEX IF NOT EXISTS idx_detections_confidence ON detections(confidence);
CREATE INDEX IF NOT EXISTS idx_detections_first_seen ON detections(first_seen);
CREATE INDEX IF NOT EXISTS idx_detections_velocity ON detections(velocity);


-- ── Signals ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    text TEXT NOT NULL,
    platform platform_type NOT NULL,
    author VARCHAR(255),
    author_followers INTEGER,
    url VARCHAR(500),
    language VARCHAR(10) DEFAULT 'en',
    engagement JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    ingested_at TIMESTAMP DEFAULT NOW() NOT NULL,
    detection_id UUID REFERENCES detections(id)
);

CREATE INDEX IF NOT EXISTS idx_signals_platform_created ON signals(platform, created_at);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at);
CREATE INDEX IF NOT EXISTS idx_signals_detection_id ON signals(detection_id);


-- ── Forecasts ───────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    detection_id UUID NOT NULL REFERENCES detections(id),
    forecast_date TIMESTAMP NOT NULL,
    predicted_mentions INTEGER,
    predicted_stage spread_stage,
    predicted_velocity FLOAT,
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    model_version VARCHAR(50) DEFAULT 'prophet-v1',
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_forecasts_detection_id ON forecasts(detection_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_forecast_date ON forecasts(forecast_date);


-- ── Simulations ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    detection_id UUID NOT NULL REFERENCES detections(id),
    agent_count INTEGER DEFAULT 1000,
    monte_carlo_runs INTEGER DEFAULT 50,
    simulation_data JSONB DEFAULT '{}',
    spread_path JSONB DEFAULT '{}',
    virality_coefficient FLOAT,
    decay_probability FLOAT,
    mainstream_eta_hours FLOAT,
    accuracy_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_simulations_detection_id ON simulations(detection_id);
CREATE INDEX IF NOT EXISTS idx_simulations_created_at ON simulations(created_at);


-- ── Saved Signals (User ↔ Detection) ────────────────────────

CREATE TABLE IF NOT EXISTS saved_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    detection_id UUID NOT NULL REFERENCES detections(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_saved_user_id ON saved_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_detection_id ON saved_signals(detection_id);


-- ── Row Level Security (Supabase best practice) ─────────────

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_signals ENABLE ROW LEVEL SECURITY;

-- Service role (backend) has full access
CREATE POLICY "Service role full access on users"
    ON users FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on signals"
    ON signals FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on detections"
    ON detections FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on forecasts"
    ON forecasts FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on simulations"
    ON simulations FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on saved_signals"
    ON saved_signals FOR ALL
    USING (auth.role() = 'service_role');


-- ── Auto-update timestamps ──────────────────────────────────

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_detections_updated_at
    BEFORE UPDATE ON detections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();


-- ══════════════════════════════════════════════════════════════
-- ✅ Migration complete. All tables created with:
--   - pgvector extension (for semantic search embeddings)
--   - Row Level Security (Supabase best practice)
--   - Auto-updating timestamps
--   - Comprehensive indexes for query performance
-- ══════════════════════════════════════════════════════════════
