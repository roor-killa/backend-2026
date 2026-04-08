
CREATE SCHEMA IF NOT EXISTS rc_schema;

CREATE TABLE IF NOT EXISTS rc_schema.rci_articles (
    id          BIGSERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT,
    photo       TEXT,
    infos       TEXT,
    body        TEXT NOT NULL,
    url         TEXT NOT NULL UNIQUE,
    depth       INTEGER NOT NULL DEFAULT 1 CHECK (depth >= 0),
    scraped_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rci_articles_url ON rc_schema.rci_articles(url);
CREATE INDEX IF NOT EXISTS idx_rci_articles_depth ON rc_schema.rci_articles(depth);
CREATE INDEX IF NOT EXISTS idx_rci_articles_scraped_at ON rc_schema.rci_articles(scraped_at DESC);

CREATE OR REPLACE VIEW rc_schema.v_rci_latest AS
SELECT id, title, author, url, depth, scraped_at, updated_at
FROM rc_schema.rci_articles
ORDER BY scraped_at DESC;
