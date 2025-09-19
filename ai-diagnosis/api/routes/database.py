import logging
from typing import List, Optional
from datetime import datetime
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.database import get_db
from services.models import SensorData

router = APIRouter(prefix="/sensors", tags=["Database & Sensors"])


class SensorDataRequest(BaseModel):
    asset_id: Optional[str] = None
    sampled_at: datetime
    sensor_id: Optional[str] = None
    accel_peak_x: Optional[float] = None
    accel_peak_y: Optional[float] = None
    accel_peak_z: Optional[float] = None
    temperature: Optional[float] = None
    temperature_accelerometer: Optional[float] = None
    gateway_signal: Optional[int] = None


class SensorDataResponse(BaseModel):
    id: str
    asset_id: Optional[str]
    sampled_at: datetime
    sensor_id: Optional[str]
    accel_peak_x: Optional[float]
    accel_peak_y: Optional[float]
    accel_peak_z: Optional[float]
    temperature: Optional[float]
    temperature_accelerometer: Optional[float]
    gateway_signal: Optional[int]
    
    class Config:
        from_attributes = True


class PopulateRequest(BaseModel):
    clear_existing: bool = False


@router.post("/add", response_model=SensorDataResponse)
def add_sensor_data(data: SensorDataRequest, db: Session = Depends(get_db)):
    """Add new sensor data to the database"""
    try:
        sensor_data = SensorData(
            asset_id=data.asset_id,
            sampled_at=data.sampled_at,
            sensor_id=data.sensor_id,
            accel_peak_x=data.accel_peak_x,
            accel_peak_y=data.accel_peak_y,
            accel_peak_z=data.accel_peak_z,
            temperature=data.temperature,
            temperature_accelerometer=data.temperature_accelerometer,
            gateway_signal=data.gateway_signal
        )
        
        db.add(sensor_data)
        db.commit()
        db.refresh(sensor_data)
        
        return {
            "id": str(sensor_data.id),
            "asset_id": sensor_data.asset_id,
            "sampled_at": sensor_data.sampled_at,
            "sensor_id": sensor_data.sensor_id,
            "accel_peak_x": sensor_data.accel_peak_x,
            "accel_peak_y": sensor_data.accel_peak_y,
            "accel_peak_z": sensor_data.accel_peak_z,
            "temperature": sensor_data.temperature,
            "temperature_accelerometer": sensor_data.temperature_accelerometer,
            "gateway_signal": sensor_data.gateway_signal
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add sensor data: {str(e)}")


@router.get("/all", response_model=List[SensorDataResponse])
def get_all_sensor_data(db: Session = Depends(get_db)):
    """Get all sensor data records from the database"""
    results = db.query(SensorData).order_by(SensorData.sampled_at.desc()).all()
    
    return [
        {
            "id": str(result.id),
            "asset_id": result.asset_id,
            "sampled_at": result.sampled_at,
            "sensor_id": result.sensor_id,
            "accel_peak_x": result.accel_peak_x,
            "accel_peak_y": result.accel_peak_y,
            "accel_peak_z": result.accel_peak_z,
            "temperature": result.temperature,
            "temperature_accelerometer": result.temperature_accelerometer,
            "gateway_signal": result.gateway_signal
        } for result in results
    ]


@router.get("/by-sensor/{sensor_id}", response_model=List[SensorDataResponse])
def get_data_by_sensor_id(sensor_id: str, db: Session = Depends(get_db)):
    """Get all data for a specific sensor ID"""
    results = db.query(SensorData).filter(
        SensorData.sensor_id == sensor_id
    ).order_by(SensorData.sampled_at.desc()).all()
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for sensor_id: {sensor_id}")
    
    return [
        {
            "id": str(result.id),
            "asset_id": result.asset_id,
            "sampled_at": result.sampled_at,
            "sensor_id": result.sensor_id,
            "accel_peak_x": result.accel_peak_x,
            "accel_peak_y": result.accel_peak_y,
            "accel_peak_z": result.accel_peak_z,
            "temperature": result.temperature,
            "temperature_accelerometer": result.temperature_accelerometer,
            "gateway_signal": result.gateway_signal
        } for result in results
    ]


@router.delete("/clear-all")
def clear_all_sensor_data(db: Session = Depends(get_db)):
    """Remove all sensor data samples from the database"""
    try:
        # Count records before deletion
        count_before = db.query(SensorData).count()
        
        # Delete all records
        db.query(SensorData).delete()
        db.commit()
        
        return {
            "message": "All sensor data cleared successfully",
            "records_deleted": count_before
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear sensor data: {str(e)}")


@router.post("/populate")
def populate_from_sample_data(request: PopulateRequest, db: Session = Depends(get_db)):
    """Populate database with all sample data from sample_data.json"""
    try:
        # Clear existing data if requested
        if request.clear_existing:
            db.query(SensorData).delete()
            db.commit()
        
        # Load sample data
        json_path = Path(__file__).parent / "sample_data.json"
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Insert all data
        inserted_count = 0
        for record in data:
            # Parse sampled_at if it's a string
            sampled_at = record.get('sampled_at')
            if isinstance(sampled_at, str):
                sampled_at = datetime.fromisoformat(sampled_at.replace('Z', '+00:00'))
            
            # Debug output for NYS0043
            if record.get('sensor_id') == 'NYS0043':
                logging.info(f"DEBUG: Processing NYS0043 record with gateway_signal: {record.get('gateway_signal')}")
            
            sensor_data = SensorData(
                asset_id=record.get('asset_id'),
                sampled_at=sampled_at,
                sensor_id=record.get('sensor_id'),
                accel_peak_x=record.get('accel_peak_x'),
                accel_peak_y=record.get('accel_peak_y'),
                accel_peak_z=record.get('accel_peak_z'),
                temperature=record.get('temperature'),
                temperature_accelerometer=record.get('temperature_accelerometer'),
                gateway_signal=record.get('gateway_signal')
            )
            db.add(sensor_data)
            inserted_count += 1
        
        db.commit()
        
        return {
            "message": f"Successfully inserted {inserted_count} records",
            "records_inserted": inserted_count,
            "clear_existing": request.clear_existing
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to populate database: {str(e)}")
