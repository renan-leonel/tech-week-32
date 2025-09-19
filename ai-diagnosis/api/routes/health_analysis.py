from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.database import get_db
from services.models import SensorData

router = APIRouter(prefix="/health", tags=["Health Analysis"])


class HealthStatus(BaseModel):
    sensor_id: str
    timestamp: datetime
    connectivity_ok: bool
    acceleration_ok: bool
    temperature_ok: bool
    overall_health: str  # "healthy", "warning", "critical"
    connectivity_signal: Optional[int] = None
    max_acceleration: Optional[float] = None
    max_temperature: Optional[float] = None
    issues: List[str] = []


class HealthAnalysisResponse(BaseModel):
    sensor_id: str
    analysis_timestamp: datetime
    health_status: HealthStatus
    recommendations: List[str] = []


@router.get("/analysis/{sensor_id}", response_model=HealthAnalysisResponse)
def get_sensor_health_analysis(sensor_id: str, db: Session = Depends(get_db)):
    """Get health analysis for a specific sensor based on recent data"""
    
    # Get the most recent data for the sensor
    latest_data = db.query(SensorData).filter(
        SensorData.sensor_id == sensor_id
    ).order_by(SensorData.sampled_at.desc()).first()
    
    if not latest_data:
        raise HTTPException(status_code=404, detail=f"No data found for sensor_id: {sensor_id}")
    
    # Analyze connectivity
    connectivity_ok = True
    connectivity_signal = latest_data.gateway_signal
    connectivity_issues = []
    
    if connectivity_signal is not None:
        if connectivity_signal < -85:
            connectivity_ok = False
            connectivity_issues.append(f"Weak signal: {connectivity_signal} dBm (threshold: -85 dBm)")
        elif connectivity_signal < -75:
            connectivity_issues.append(f"Moderate signal: {connectivity_signal} dBm")
    
    # Analyze acceleration
    acceleration_ok = True
    max_acceleration = None
    acceleration_issues = []
    
    if latest_data.accel_peak_x is not None or latest_data.accel_peak_y is not None or latest_data.accel_peak_z is not None:
        max_acceleration = max(
            latest_data.accel_peak_x or 0,
            latest_data.accel_peak_y or 0,
            latest_data.accel_peak_z or 0
        )
        
        if max_acceleration > 16:
            acceleration_ok = False
            acceleration_issues.append(f"High G-force detected: {max_acceleration:.2f}G (threshold: 16G)")
        elif max_acceleration > 12:
            acceleration_issues.append(f"Elevated G-force: {max_acceleration:.2f}G")
    
    # Analyze temperature
    temperature_ok = True
    max_temperature = None
    temperature_issues = []
    
    if latest_data.temperature is not None:
        max_temperature = latest_data.temperature
        if latest_data.temperature > 120:
            temperature_ok = False
            temperature_issues.append(f"Critical temperature: {latest_data.temperature:.1f}°C (threshold: 120°C)")
        elif latest_data.temperature > 90:
            temperature_issues.append(f"High temperature: {latest_data.temperature:.1f}°C")
    
    if latest_data.temperature_accelerometer is not None:
        if latest_data.temperature_accelerometer > 90:
            temperature_ok = False
            temperature_issues.append(f"High accelerometer temperature: {latest_data.temperature_accelerometer:.1f}°C")
        elif latest_data.temperature_accelerometer > 70:
            temperature_issues.append(f"Elevated accelerometer temperature: {latest_data.temperature_accelerometer:.1f}°C")
    
    # Determine overall health
    all_issues = connectivity_issues + acceleration_issues + temperature_issues
    critical_issues = [issue for issue in all_issues if "Critical" in issue or "High G-force" in issue]
    
    if not connectivity_ok or not acceleration_ok or not temperature_ok:
        if critical_issues:
            overall_health = "critical"
        else:
            overall_health = "warning"
    else:
        overall_health = "healthy"
    
    # Generate recommendations
    recommendations = []
    if not connectivity_ok:
        recommendations.append("Check antenna connection and positioning")
        recommendations.append("Verify gateway proximity and signal strength")
    if not acceleration_ok:
        recommendations.append("Inspect equipment for mechanical issues")
        recommendations.append("Check for excessive vibration or impact")
    if not temperature_ok:
        recommendations.append("Check cooling systems and ventilation")
        recommendations.append("Monitor for overheating conditions")
    if overall_health == "healthy":
        recommendations.append("All systems operating normally")
    
    health_status = HealthStatus(
        sensor_id=sensor_id,
        timestamp=latest_data.sampled_at,
        connectivity_ok=connectivity_ok,
        acceleration_ok=acceleration_ok,
        temperature_ok=temperature_ok,
        overall_health=overall_health,
        connectivity_signal=connectivity_signal,
        max_acceleration=max_acceleration,
        max_temperature=max_temperature,
        issues=all_issues
    )
    
    return HealthAnalysisResponse(
        sensor_id=sensor_id,
        analysis_timestamp=datetime.utcnow(),
        health_status=health_status,
        recommendations=recommendations
    )


@router.get("/analysis", response_model=List[HealthAnalysisResponse])
def get_all_sensors_health_analysis(db: Session = Depends(get_db)):
    """Get health analysis for all sensors"""
    
    # Get unique sensor IDs
    sensor_ids = db.query(SensorData.sensor_id).filter(
        SensorData.sensor_id.isnot(None)
    ).distinct().all()
    
    if not sensor_ids:
        return []
    
    results = []
    for (sensor_id,) in sensor_ids:
        try:
            analysis = get_sensor_health_analysis(sensor_id, db)
            results.append(analysis)
        except HTTPException:
            # Skip sensors with no data
            continue
    
    return results


@router.get("/summary")
def get_health_summary(db: Session = Depends(get_db)):
    """Get overall health summary across all sensors"""
    
    # Get all sensor data
    all_data = db.query(SensorData).all()
    
    if not all_data:
        return {
            "total_sensors": 0,
            "healthy_sensors": 0,
            "warning_sensors": 0,
            "critical_sensors": 0,
            "overall_status": "no_data"
        }
    
    # Get unique sensor IDs
    sensor_ids = list(set([data.sensor_id for data in all_data if data.sensor_id]))
    
    healthy_count = 0
    warning_count = 0
    critical_count = 0
    
    for sensor_id in sensor_ids:
        try:
            analysis = get_sensor_health_analysis(sensor_id, db)
            if analysis.health_status.overall_health == "healthy":
                healthy_count += 1
            elif analysis.health_status.overall_health == "warning":
                warning_count += 1
            else:
                critical_count += 1
        except HTTPException:
            continue
    
    total_sensors = len(sensor_ids)
    
    if critical_count > 0:
        overall_status = "critical"
    elif warning_count > 0:
        overall_status = "warning"
    else:
        overall_status = "healthy"
    
    return {
        "total_sensors": total_sensors,
        "healthy_sensors": healthy_count,
        "warning_sensors": warning_count,
        "critical_sensors": critical_count,
        "overall_status": overall_status,
        "health_percentage": round((healthy_count / total_sensors) * 100, 2) if total_sensors > 0 else 0
    }
