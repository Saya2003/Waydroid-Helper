-- settings.db schema

-- Table for user preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);

-- Table for Waydroid apps
CREATE TABLE IF NOT EXISTS waydroid_apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT NOT NULL UNIQUE,
    app_name TEXT NOT NULL,
    visible INTEGER DEFAULT 1, -- 1 for visible, 0 for hidden
    last_used TIMESTAMP,
    install_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for resource usage logs
CREATE TABLE IF NOT EXISTS resource_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_usage REAL,
    ram_usage REAL,
    storage_usage REAL
);

-- Table for container status logs
CREATE TABLE IF NOT EXISTS container_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL, -- e.g., 'start', 'stop', 'freeze', 'unfreeze'
    status TEXT NOT NULL, -- e.g., 'success', 'failure'
    message TEXT
);

-- Insert default preferences
INSERT OR IGNORE INTO user_preferences (key, value) VALUES ('auto_start', 'false');
INSERT OR IGNORE INTO user_preferences (key, value) VALUES ('auto_update', 'true');
INSERT OR IGNORE INTO user_preferences (key, value) VALUES ('notification_enabled', 'true');
INSERT OR IGNORE INTO user_preferences (key, value) VALUES ('resource_logging_interval', '300'); -- in seconds