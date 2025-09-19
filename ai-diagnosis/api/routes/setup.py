from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.database import get_db, connect_to_db, close_db_connection
from services.setup_database import create_table, populate_database

router = APIRouter(prefix="/setup", tags=["setup"])


@router.post("/database")
async def setup_database(load_sample_data: bool = True, db: Session = Depends(get_db)):
    """
    Initialize the database with tables and optionally load sample data.
    
    Args:
        load_sample_data: Whether to load sample data after creating tables
        db: Database session
    
    Returns:
        Success message with setup details
    """
    try:
        # Create tables
        table_created = create_table()
        if not table_created:
            raise Exception("Failed to create database tables")
        
        # Load sample data if requested
        sample_data_loaded = False
        if load_sample_data:
            sample_data_loaded = populate_database(db)
        
        return {
            "message": "Database setup completed successfully",
            "tables_created": table_created,
            "sample_data_loaded": sample_data_loaded
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database setup failed: {str(e)}"
        )


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Check database connectivity.
    
    Args:
        db: Database session
    
    Returns:
        Database connection status
    """
    try:
        # Simple query to test connection
        db.execute("SELECT 1")
        
        return {"status": "healthy", "database": "connected"}
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )
