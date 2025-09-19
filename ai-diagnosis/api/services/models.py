from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from services.database import Base
import uuid

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String(255))
    sampled_at = Column(DateTime(timezone=True), nullable=False)
    sensor_id = Column(String(255))
    accel_peak_x = Column(Float)
    accel_peak_y = Column(Float)
    accel_peak_z = Column(Float)
    temperature = Column(Float)
    temperature_accelerometer = Column(Float)
    gateway_signal = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
