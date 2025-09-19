import json
from pathlib import Path
from sqlalchemy.orm import Session
from services.database import engine, Base
from services.models import SensorData

def create_table():
    """Create the sensor_data table if it doesn't exist."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Table created successfully or already exists")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

def populate_database(db: Session):
    """Populate the database with sample data if it's empty."""
    try:
        # Check if data already exists
        count = db.query(SensorData).count()
        if count > 1:
            print(f"✅ Database already contains {count} records. Skipping population.")
            return True
        
        # Load sample data
        data = load_data_from_file()
        if not data:
            print("❌ No sample data to load")
            return False
        
        # Insert data
        for record in data:
            sensor_data = SensorData(
                # Don't set id - let the database generate a unique UUID automatically
                asset_id=record.get('asset_id'),
                sampled_at=record.get('sampled_at'),
                sensor_id=record.get('sensor_id'),
                accel_peak_x=record.get('accel_peak_x'),
                accel_peak_y=record.get('accel_peak_y'),
                accel_peak_z=record.get('accel_peak_z'),
                temperature=record.get('temperature'),
                temperature_accelerometer=record.get('temperature_accelerometer'),
                gateway_signal=record.get('gateway_signal')
            )
            db.add(sensor_data)
        
        db.commit()
        print(f"✅ Successfully inserted {len(data)} records into the database.")
        return True
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        db.rollback()
        return False

def load_data_from_file():
    """Load sample data from JSON file."""
    json_path = Path(__file__).parent.parent / "routes" / "sample_data.json"
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} records from {json_path}")
        return data
    except FileNotFoundError:
        print(f"❌ Sample data file not found at: {json_path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {json_path}")
        return None
