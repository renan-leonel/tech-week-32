-- AI Diagnosis Database Schema
-- This file will be executed when the PostgreSQL container starts for the first time.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create sensor_data table
CREATE TABLE IF NOT EXISTS sensor_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id VARCHAR(255),
    sampled_at TIMESTAMPTZ NOT NULL,
    sensor_id VARCHAR(255),
    accel_peak_x REAL,
    accel_peak_y REAL,
    accel_peak_z REAL,
    temperature REAL,
    temperature_accelerometer REAL,
    gateway_signal INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_id ON sensor_data(sensor_id);
CREATE INDEX IF NOT EXISTS idx_sensor_data_sampled_at ON sensor_data(sampled_at);
CREATE INDEX IF NOT EXISTS idx_sensor_data_asset_id ON sensor_data(asset_id);