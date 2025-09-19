"""
MCP (Model Context Protocol) routes for LLM database access
Allows LLM to search sensor data but only update sampled_at column
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from services.database import get_db
from services.models import SensorData

router = APIRouter(prefix="/mcp", tags=["MCP - LLM Database Access"])

# Pydantic models for validation
class SensorDataSearch(BaseModel):
    sensor_id: Optional[str] = Field(None, description="Filter by sensor ID")
    asset_id: Optional[str] = Field(None, description="Filter by asset ID")
    start_date: Optional[str] = Field(None, description="Start date filter (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date filter (YYYY-MM-DD)")
    limit: int = Field(1000, ge=1, le=10000, description="Maximum number of records to return")
    order_by: str = Field("sampled_at", description="Column to order by")
    order_desc: bool = Field(True, description="Order in descending order")

class SensorDataUpdate(BaseModel):
    id: str = Field(..., description="UUID of the record to update")
    sampled_at: datetime = Field(..., description="New sampled_at timestamp")

class SensorSummaryRequest(BaseModel):
    sensor_id: Optional[str] = Field(None, description="Filter by sensor ID (optional)")

@router.post("/search")
def search_sensor_data(search_params: SensorDataSearch, db: Session = Depends(get_db)):
    """
    Search sensor data with optional filters
    LLM can use this to find specific sensor records
    """
    try:
        # Build query
        query = db.query(SensorData)
        
        if search_params.sensor_id:
            query = query.filter(SensorData.sensor_id == search_params.sensor_id)
        
        if search_params.asset_id:
            query = query.filter(SensorData.asset_id == search_params.asset_id)
        
        # Add date filtering
        if search_params.start_date:
            from datetime import datetime
            start_datetime = datetime.fromisoformat(search_params.start_date)
            query = query.filter(SensorData.sampled_at >= start_datetime)
        
        if search_params.end_date:
            from datetime import datetime
            end_datetime = datetime.fromisoformat(search_params.end_date)
            query = query.filter(SensorData.sampled_at <= end_datetime)
        
        # Add ordering
        order_column = getattr(SensorData, search_params.order_by, SensorData.sampled_at)
        if search_params.order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # Add limit
        query = query.limit(search_params.limit)
        
        # Execute query
        results = query.all()
        
        # Convert to JSON-serializable format
        data = []
        for record in results:
            record_dict = {
                "id": str(record.id),
                "asset_id": record.asset_id,
                "sampled_at": record.sampled_at.isoformat() if record.sampled_at else None,
                "sensor_id": record.sensor_id,
                "accel_peak_x": record.accel_peak_x,
                "accel_peak_y": record.accel_peak_y,
                "accel_peak_z": record.accel_peak_z,
                "temperature": record.temperature,
                "temperature_accelerometer": record.temperature_accelerometer,
                "gateway_signal": record.gateway_signal,
                "created_at": record.created_at.isoformat() if record.created_at else None
            }
            data.append(record_dict)
        
        return {
            "success": True,
            "count": len(data),
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/update-sampled-at")
def update_sampled_at(update_params: SensorDataUpdate, db: Session = Depends(get_db)):
    """
    Update sampled_at timestamp for a specific record
    SECURITY: Only allows updating the sampled_at column
    """
    try:
        # Check if record exists
        record = db.query(SensorData).filter(SensorData.id == update_params.id).first()
        
        if not record:
            raise HTTPException(status_code=404, detail=f"Record with ID {update_params.id} not found")
        
        # Update only the sampled_at column
        record.sampled_at = update_params.sampled_at
        db.commit()
        db.refresh(record)
        
        return {
            "success": True,
            "message": f"Successfully updated sampled_at for record {record.id}",
            "updated_record": {
                "id": str(record.id),
                "sampled_at": record.sampled_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

@router.post("/summary")
def get_sensor_summary(summary_params: SensorSummaryRequest, db: Session = Depends(get_db)):
    """
    Get summary statistics for sensor data
    LLM can use this to understand data patterns
    """
    try:
        query = db.query(SensorData)
        
        if summary_params.sensor_id:
            query = query.filter(SensorData.sensor_id == summary_params.sensor_id)
        
        # Get basic counts
        total_records = query.count()
        
        if total_records == 0:
            return {
                "success": True,
                "summary": {
                    "total_records": 0,
                    "message": "No data found"
                }
            }
        
        # Get date range
        earliest = query.order_by(SensorData.sampled_at.asc()).first()
        latest = query.order_by(SensorData.sampled_at.desc()).first()
        
        # Get averages for numeric fields
        from sqlalchemy import func
        
        stats = query.with_entities(
            func.avg(SensorData.temperature).label('avg_temperature'),
            func.avg(SensorData.accel_peak_x).label('avg_accel_x'),
            func.avg(SensorData.accel_peak_y).label('avg_accel_y'),
            func.avg(SensorData.accel_peak_z).label('avg_accel_z'),
            func.avg(SensorData.gateway_signal).label('avg_signal'),
            func.count(SensorData.sensor_id.distinct()).label('unique_sensors')
        ).first()
        
        summary = {
            "total_records": total_records,
            "unique_sensors": stats.unique_sensors if stats.unique_sensors else 0,
            "earliest_sample": earliest.sampled_at.isoformat() if earliest and earliest.sampled_at else None,
            "latest_sample": latest.sampled_at.isoformat() if latest and latest.sampled_at else None,
            "averages": {
                "temperature": round(float(stats.avg_temperature), 2) if stats.avg_temperature else None,
                "accel_peak_x": round(float(stats.avg_accel_x), 2) if stats.avg_accel_x else None,
                "accel_peak_y": round(float(stats.avg_accel_y), 2) if stats.avg_accel_y else None,
                "accel_peak_z": round(float(stats.avg_accel_z), 2) if stats.avg_accel_z else None,
                "gateway_signal": round(float(stats.avg_signal), 2) if stats.avg_signal else None
            }
        }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")

@router.get("/tools")
def list_mcp_tools():
    """
    List available MCP tools for LLM
    This endpoint describes what the LLM can do
    """
    tools = [
        {
            "name": "search_sensor_data",
            "description": "Search sensor data with optional filters",
            "endpoint": "POST /mcp/search",
            "parameters": {
                "sensor_id": "string (optional) - Filter by sensor ID",
                "asset_id": "string (optional) - Filter by asset ID", 
                "limit": "integer (1-100, default 10) - Maximum records to return",
                "order_by": "string (default 'sampled_at') - Column to order by",
                "order_desc": "boolean (default true) - Order in descending order"
            },
            "security": "READ-ONLY - Can only read data"
        },
        {
            "name": "update_sampled_at",
            "description": "Update the sampled_at timestamp for a specific record",
            "endpoint": "POST /mcp/update-sampled-at",
            "parameters": {
                "id": "string (required) - UUID of the record to update",
                "sampled_at": "datetime (required) - New sampled_at timestamp"
            },
            "security": "LIMITED WRITE - Can only update sampled_at column"
        },
        {
            "name": "get_sensor_summary",
            "description": "Get summary statistics for sensor data",
            "endpoint": "POST /mcp/summary",
            "parameters": {
                "sensor_id": "string (optional) - Filter by sensor ID"
            },
            "security": "READ-ONLY - Can only read aggregated data"
        }
    ]
    
    return {
        "success": True,
        "mcp_tools": tools,
        "security_note": "LLM can only read data and update the sampled_at column. All other modifications are restricted."
    }
