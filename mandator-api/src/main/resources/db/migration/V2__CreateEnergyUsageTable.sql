CREATE TABLE IF NOT EXISTS usage_stats (
    hour TIMESTAMP PRIMARY KEY,
    community_produced NUMERIC NOT NULL DEFAULT 0,
    community_used NUMERIC NOT NULL DEFAULT 0,
    grid_used NUMERIC NOT NULL DEFAULT 0,
    community_used_percentage NUMERIC NOT NULL DEFAULT 0
);