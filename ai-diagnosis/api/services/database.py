import os
import json
from pathlib import Path
import asyncpg
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This global variable will hold the database connection pool
POOL = None

# SQLAlchemy setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # For SQLAlchemy, we can use the standard postgresql:// URL
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
else:
    engine = None
    SessionLocal = None
    Base = None

def get_db():
    """Dependency to get database session."""
    if not SessionLocal:
        raise Exception("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def connect_to_db():
    """Establishes a connection pool to the PostgreSQL database."""
    global POOL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    try:
        # Create a connection pool. This is more efficient than creating new connections for every query.
        POOL = await asyncpg.create_pool(dsn=db_url)
        print("✅ Database connection pool created successfully.")
    except Exception as e:
        print(f"❌ Could not connect to the database: {e}")
        raise

async def close_db_connection():
    """Closes the database connection pool."""
    global POOL
    if POOL:
        await POOL.close()
        print("✅ Database connection pool closed.")

async def populate_database_from_json():
    """
    Loads data from a JSON file and performs a bulk insert into the sensor_data table.
    """
    if not POOL:
        raise Exception("Database connection pool is not available. Call connect_to_db() first.")

    # Use a connection from the pool
    async with POOL.acquire() as conn:
        # 1. Prevent re-populating the database on every server restart
        record_count = await conn.fetchval('SELECT COUNT(*) FROM sensor_data')
        if record_count > 1:
            print(f"✅ Database already contains {record_count} records. Skipping population.")
            return

        # 2. Load the sample data from the JSON file
        json_path = Path(__file__).parent.parent / "routes" / "sample_data.json"
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} records from {json_path}")
        except FileNotFoundError:
            print(f"❌ Sample data file not found at: {json_path}")
            return
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in file: {json_path}")
            return
        
        # 3. Prepare the data for an efficient bulk insert
        # The order of items in the tuple MUST match the order of columns in the INSERT statement
        records_to_insert = [
            (
                r.get('id'), r.get('asset_id'), r.get('sampled_at'), r.get('sensor_id'),
                r.get('accel_peak_x'), r.get('accel_peak_y'), r.get('accel_peak_z'),
                r.get('temperature'), r.get('temperature_accelerometer'), r.get('gateway_signal')
            ) for r in data
        ]
        
        # 4. Execute the bulk insert query using executemany for high performance
        try:
            await conn.executemany("""
                INSERT INTO sensor_data (
                    id, asset_id, sampled_at, sensor_id, accel_peak_x, accel_peak_y,
                    accel_peak_z, temperature, temperature_accelerometer, gateway_signal
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, records_to_insert)
            print(f"✅ Successfully inserted {len(records_to_insert)} records into the database.")
        except Exception as e:
            print(f"❌ An error occurred during data insertion: {e}")
            raise