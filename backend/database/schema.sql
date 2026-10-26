-- Stargazing Planner database schema
-- Run with: psql -d stargazing -f database/schema.sql
-- Safe to re-run: it drops and recreates every table.

SET client_min_messages = warning;  -- hide "does not exist" notices

DROP TABLE IF EXISTS observations, predictions, forecasts, trips, favorites, sites, users CASCADE;

-- People who create accounts
CREATE TABLE users (
    id             SERIAL PRIMARY KEY,
    email          VARCHAR(255) NOT NULL UNIQUE,
    password_hash  TEXT         NOT NULL,              -- bcrypt hash, never the real password
    display_name   VARCHAR(100),
    is_admin       BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Dark-sky stargazing spots
CREATE TABLE sites (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(120)     NOT NULL UNIQUE,
    region        VARCHAR(80)      NOT NULL,
    state         CHAR(2)          NOT NULL CHECK (state IN ('WA', 'OR')),
    latitude      DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude     DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    elevation_ft  INTEGER,
    bortle        SMALLINT         NOT NULL CHECK (bortle BETWEEN 1 AND 9),  -- 1 = darkest sky, 9 = city
    road_access   VARCHAR(20)      NOT NULL CHECK (road_access IN ('Year-round', 'Seasonal')),
    notes         TEXT,
    created_at    TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- A user's saved spots (one row per user + site)
CREATE TABLE favorites (
    user_id     INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    site_id     INTEGER     NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, site_id)
);

-- Saved / shared trip plans
CREATE TABLE trips (
    id                 SERIAL PRIMARY KEY,
    user_id            INTEGER          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    share_code         VARCHAR(12)      NOT NULL UNIQUE,   -- used in the shareable link
    name               VARCHAR(120)     NOT NULL,
    start_latitude     DOUBLE PRECISION NOT NULL,
    start_longitude    DOUBLE PRECISION NOT NULL,
    max_drive_minutes  INTEGER          NOT NULL CHECK (max_drive_minutes > 0),
    site_id            INTEGER          REFERENCES sites(id) ON DELETE SET NULL,
    night              DATE,
    created_at         TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

-- Hourly weather forecasts downloaded every 6 hours (Open-Meteo)
CREATE TABLE forecasts (
    id             BIGSERIAL PRIMARY KEY,
    site_id        INTEGER     NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    forecast_hour  TIMESTAMPTZ NOT NULL,                  -- the hour this forecast is for
    cloud_low      SMALLINT CHECK (cloud_low  BETWEEN 0 AND 100),
    cloud_mid      SMALLINT CHECK (cloud_mid  BETWEEN 0 AND 100),
    cloud_high     SMALLINT CHECK (cloud_high BETWEEN 0 AND 100),
    cloud_total    SMALLINT CHECK (cloud_total BETWEEN 0 AND 100),
    humidity       SMALLINT CHECK (humidity BETWEEN 0 AND 100),
    visibility_m   INTEGER,
    downloaded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (site_id, forecast_hour)                       -- newest download replaces the old one
);

-- The app's score for each site and night (saved so accuracy can be checked later)
CREATE TABLE predictions (
    id              BIGSERIAL PRIMARY KEY,
    site_id         INTEGER  NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    night           DATE     NOT NULL,
    score           SMALLINT NOT NULL CHECK (score BETWEEN 0 AND 100),
    cloud_score     SMALLINT,
    moon_score      SMALLINT,
    darkness_score  SMALLINT,
    light_score     SMALLINT,
    predicted_on    DATE     NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (site_id, night, predicted_on)
);

-- What the weather actually did (used for the accuracy check)
CREATE TABLE observations (
    id                 BIGSERIAL PRIMARY KEY,
    site_id            INTEGER  NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    night              DATE     NOT NULL,
    avg_cloud_percent  SMALLINT CHECK (avg_cloud_percent BETWEEN 0 AND 100),
    recorded_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (site_id, night)
);

CREATE INDEX idx_forecasts_site_hour   ON forecasts (site_id, forecast_hour);
CREATE INDEX idx_predictions_site_night ON predictions (site_id, night);
