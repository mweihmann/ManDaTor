-- Create table for raw usage stats with timezone support
CREATE TABLE usage_stats (
    hour TIMESTAMPTZ NOT NULL PRIMARY KEY,
    community_produced DOUBLE PRECISION NOT NULL,
    community_used DOUBLE PRECISION NOT NULL,
    grid_used DOUBLE PRECISION NOT NULL
);

-- Create table for calculated percentage stats with timezone support
CREATE TABLE usage_stats_percentage (
    hour TIMESTAMPTZ NOT NULL PRIMARY KEY,
    community_depleted DOUBLE PRECISION NOT NULL,
    grid_portion DOUBLE PRECISION NOT NULL
);
