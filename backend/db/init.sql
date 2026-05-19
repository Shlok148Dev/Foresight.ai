-- ================================================
-- Foresight — Database Initialization (Legacy)
-- ================================================
-- NOTE: This file is kept for version control only.
-- For Supabase deployments, use: backend/db/supabase_migration.sql
-- This file runs only in local Docker Compose (if using local Postgres).
-- ================================================

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable trigram index for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Foresight database initialized with pgvector, uuid-ossp, pg_trgm extensions';
END $$;
