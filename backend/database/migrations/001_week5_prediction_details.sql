-- Week 5: extra details saved with each nightly score (for the site detail page).
-- Run once on an existing database:  psql -d stargazing -f database/migrations/001_week5_prediction_details.sql
-- Safe to re-run. (schema.sql already includes these columns for a fresh database.)
SET client_min_messages = warning;  -- hide "already exists" notices on re-runs

ALTER TABLE predictions
    ADD COLUMN IF NOT EXISTS dark_start   TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS dark_end     TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS dark_hours   REAL,
    ADD COLUMN IF NOT EXISTS moon_percent SMALLINT CHECK (moon_percent BETWEEN 0 AND 100),
    ADD COLUMN IF NOT EXISTS avg_cloud    SMALLINT CHECK (avg_cloud BETWEEN 0 AND 100);
