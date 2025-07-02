-- Create table for raw usage stats
CREATE TABLE usage_stats (
    hour TIMESTAMP NOT NULL PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    community_produced DOUBLE PRECISION NOT NULL,
    community_used DOUBLE PRECISION NOT NULL,
    grid_used DOUBLE PRECISION NOT NULL
);

-- Create table for calculated percentage stats
CREATE TABLE usage_stats_percentage (
    hour TIMESTAMP NOT NULL PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    community_depleted DOUBLE PRECISION NOT NULL,
    grid_portion DOUBLE PRECISION NOT NULL
);
