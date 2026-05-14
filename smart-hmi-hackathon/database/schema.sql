-- ============================================================
-- ARIA - Adaptive Real-time Intelligence Assistant
-- Database Schema
-- ============================================================

-- Sensors table
CREATE TABLE IF NOT EXISTS sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    zone VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,          -- 'temperature', 'pressure', 'flow', 'vibration'
    unit VARCHAR(20) NOT NULL,          -- 'C', 'bar', 'L/min', 'mm/s'
    value FLOAT NOT NULL,
    min_threshold FLOAT NOT NULL,
    max_threshold FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'normal', -- 'normal', 'warning', 'critical'
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL,      -- 'low', 'medium', 'high', 'critical'
    zone VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,   -- 'operator', 'engineer', 'manager'
    description TEXT
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Sensor history table (for trend/predictive analysis)
CREATE TABLE IF NOT EXISTS sensor_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    value FLOAT NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- ============================================================
-- SEED DATA
-- ============================================================

INSERT OR IGNORE INTO roles (name, description) VALUES
    ('operator', 'Plant floor operator - sees live sensor data and active alerts'),
    ('engineer', 'Process engineer - sees detailed analytics and predictive data'),
    ('manager', 'Plant manager - sees KPI summary and high-level dashboard');

INSERT OR IGNORE INTO sensors (name, zone, type, unit, value, min_threshold, max_threshold, status) VALUES
    ('Pump 1 Temp',    'Zone A', 'temperature', 'C',     72.5, 0.0, 80.0, 'warning'),
    ('Pump 2 Temp',    'Zone A', 'temperature', 'C',     45.0, 0.0, 80.0, 'normal'),
    ('Pump 3 Temp',    'Zone B', 'temperature', 'C',     88.0, 0.0, 80.0, 'critical'),
    ('Valve 1 Press',  'Zone A', 'pressure',    'bar',   4.2,  1.0,  5.0, 'normal'),
    ('Valve 4 Press',  'Zone B', 'pressure',    'bar',   4.9,  1.0,  5.0, 'warning'),
    ('Coolant Flow',   'Zone C', 'flow',        'L/min', 120.0, 80.0, 200.0, 'normal'),
    ('Motor Vibration','Zone B', 'vibration',   'mm/s',  6.8,  0.0,  5.0, 'critical'),
    ('Pipe Pressure',  'Zone C', 'pressure',    'bar',   3.1,  1.0,  5.0, 'normal');

INSERT OR IGNORE INTO alerts (sensor_id, title, description, severity, zone, status) VALUES
    (3, 'Critical: Pump 3 Overheating', 'Pump 3 temperature reached 88°C, exceeding 80°C threshold.', 'critical', 'Zone B', 'active'),
    (7, 'Critical: Motor Vibration High', 'Motor vibration at 6.8 mm/s - bearing failure imminent.', 'critical', 'Zone B', 'active'),
    (1, 'Warning: Pump 1 Temp Rising', 'Pump 1 temperature at 72.5°C and rising. Approaching limit.', 'high', 'Zone A', 'active'),
    (5, 'Warning: Valve 4 Pressure High', 'Valve 4 pressure at 4.9 bar, near 5.0 bar max.', 'medium', 'Zone B', 'active'),
    (2, 'Info: Pump 2 Scheduled Maintenance', 'Pump 2 due for maintenance in 48 hours.', 'low', 'Zone A', 'active');
