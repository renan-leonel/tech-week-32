"""
Sensor Diagnostics with LLM-powered analysis using MCP
"""
from typing import Optional
from datetime import datetime, timedelta, timezone
import json
import httpx
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from services.database import get_db
from services.models import SensorData
from services.prompt import PROMPT

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnostics", tags=["Sensor Diagnostics"])

class SensorAnalysisRequest(BaseModel):
    sensor_id: str

async def call_mcp_search(sensor_id: str, start_date: str = None, end_date: str = None, limit: int = 1000) -> dict:
    """Call the MCP search endpoint to get sensor data with optional date filtering"""
    try:
        search_params = {
            "sensor_id": sensor_id,
            "limit": limit,
            "order_by": "sampled_at",
            "order_desc": True
        }
        
        # Add date filtering if provided
        if start_date:
            search_params["start_date"] = start_date
        if end_date:
            search_params["end_date"] = end_date
        
        logger.info(f"🔍 MCP Query - Sensor: {sensor_id}, Date Range: {start_date} to {end_date}, Limit: {limit}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/mcp/search",
                json=search_params
            )
            response.raise_for_status()
            result = response.json()
            
            data_count = len(result.get("data", []))
            logger.info(f"✅ MCP Query Success - Retrieved {data_count} records for sensor {sensor_id}")
            
            return result
    except Exception as e:
        logger.error(f"❌ MCP Query Failed - Sensor: {sensor_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to query MCP: {str(e)}")

async def call_llm_analysis(sensor_id: str, data: list, iteration: int = 1) -> dict:
    """Call the LLM provider directly to analyze the sensor data and potentially request more data"""
    try:
        from langchain_openai import ChatOpenAI
        import os
        
        logger.info(f"🤖 LLM Analysis Starting - Sensor: {sensor_id}, Iteration: {iteration}, Data Points: {len(data)}")
        
        # Initialize OpenAI LLM directly
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Prepare the prompt with sensor data
        prompt = PROMPT.replace("[INSERT SENSOR_ID HERE, e.g., GPD9132]", sensor_id)
        
        # Add iteration context
        iteration_context = f"\n\nITERATION {iteration}: ANALYZING SENSOR DATA\n"
        data_context = f"SENSOR DATA TO ANALYZE:\n{json.dumps(data, indent=2)}\n"
        
        # Add instructions for requesting more data if needed
        if iteration == 1:
            additional_instructions = """
            
IMPORTANT: If you need to see data from a different time period to identify when the error pattern started, you can request it by responding with:
REQUEST_MORE_DATA: {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "reason": "explanation"}

If the current data is sufficient for analysis, provide your analysis report as usual.
"""
        else:
            additional_instructions = "\n\nThis is additional data requested. Please provide your final analysis report."
        
        full_prompt = prompt + iteration_context + data_context + additional_instructions
        
        logger.info(f"📝 LLM Prompt Length: {len(full_prompt)} characters")
        logger.info(f"📊 Data Summary - Temperature Range: {min([d.get('temperature', 0) for d in data if d.get('temperature')] or [0])} to {max([d.get('temperature', 0) for d in data if d.get('temperature')] or [0])}°C")
        logger.info(f"📊 Data Summary - Signal Range: {min([d.get('gateway_signal', 0) for d in data if d.get('gateway_signal')] or [0])} to {max([d.get('gateway_signal', 0) for d in data if d.get('gateway_signal')] or [0])} dBm")
        
        # Call LLM directly
        logger.info(f"🚀 Calling OpenAI GPT-4o for sensor analysis...")
        response = llm.invoke(full_prompt)
        
        logger.info(f"✅ LLM Response Received - Length: {len(response.content)} characters")
        logger.info(f"📋 LLM Response Preview: {response.content[:200]}...")
        
        # Check if LLM is requesting more data
        if "REQUEST_MORE_DATA:" in response.content:
            logger.info(f"🔄 LLM Requesting More Data - Sensor: {sensor_id}, Iteration: {iteration}")
        else:
            logger.info(f"✅ LLM Analysis Complete - Sensor: {sensor_id}, Iteration: {iteration}")
        
        return {
            "response": response.content,
            "iteration": iteration
        }
    except Exception as e:
        logger.error(f"❌ LLM Analysis Failed - Sensor: {sensor_id}, Iteration: {iteration}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to call LLM: {str(e)}")

def parse_llm_data_request(response: str) -> dict:
    """Parse LLM response to extract data request if present"""
    if "REQUEST_MORE_DATA:" in response:
        try:
            # Extract the JSON part after REQUEST_MORE_DATA:
            json_start = response.find("REQUEST_MORE_DATA:") + len("REQUEST_MORE_DATA:")
            json_part = response[json_start:].strip()
            # Find the end of the JSON object
            json_end = json_part.find("}")
            if json_end != -1:
                json_part = json_part[:json_end + 1]
            return json.loads(json_part)
        except:
            return None
    return None

@router.post("/sensor/{sensor_id}/analysis")
async def get_sensor_analysis(request: SensorAnalysisRequest, db: Session = Depends(get_db)):
    """
    Get comprehensive LLM-powered sensor analysis
    Uses MCP to query data iteratively based on LLM requests
    """
    try:
        logger.info(f"🚀 Starting Sensor Analysis - Sensor ID: {request.sensor_id}")
        
        # First, check if sensor exists
        latest_data = db.query(SensorData).filter(
            SensorData.sensor_id == request.sensor_id
        ).order_by(SensorData.sampled_at.desc()).first()
        
        if not latest_data:
            logger.warning(f"⚠️ Sensor Not Found - Sensor ID: {request.sensor_id}")
            raise HTTPException(status_code=404, detail=f"No data found for sensor_id: {request.sensor_id}")
        
        logger.info(f"✅ Sensor Found - Latest Data: {latest_data.sampled_at}")
        
        # Start with recent data (last 24 hours)
        current_data = []
        all_data = []
        iteration = 1
        max_iterations = 5  # Prevent infinite loops
        
        # Get initial data (last 24 hours)
        logger.info(f"📊 Fetching Initial Data - Sensor: {request.sensor_id}")
        mcp_result = await call_mcp_search(request.sensor_id)
        
        if not mcp_result.get("success") or not mcp_result.get("data"):
            logger.error(f"❌ No Initial Data Available - Sensor: {request.sensor_id}")
            raise HTTPException(status_code=404, detail="No data available for analysis")
        
        current_data = mcp_result["data"]
        all_data.extend(current_data)
        logger.info(f"📊 Initial Data Loaded - Records: {len(current_data)}")
        
        # Iterative analysis loop
        logger.info(f"🔄 Starting Iterative Analysis Loop - Max Iterations: {max_iterations}")
        
        while iteration <= max_iterations:
            logger.info(f"🔄 Iteration {iteration}/{max_iterations} - Analyzing {len(current_data)} data points")
            
            # Call LLM for analysis
            analysis_result = await call_llm_analysis(request.sensor_id, current_data, iteration)
            llm_response = analysis_result["response"]
            
            # Check if LLM is requesting more data
            data_request = parse_llm_data_request(llm_response)
            
            if data_request and iteration < max_iterations:
                # LLM wants more data from a specific date range
                logger.info(f"🔄 LLM Requesting More Data - Iteration: {iteration}")
                logger.info(f"📅 Requested Date Range: {data_request.get('start_date')} to {data_request.get('end_date')}")
                logger.info(f"💭 Reason: {data_request.get('reason', 'No reason provided')}")
                
                # Get data from the requested date range
                more_data_result = await call_mcp_search(
                    request.sensor_id,
                    start_date=data_request.get("start_date"),
                    end_date=data_request.get("end_date")
                )
                
                if more_data_result.get("success") and more_data_result.get("data"):
                    current_data = more_data_result["data"]
                    all_data.extend(current_data)
                    logger.info(f"📊 Additional Data Loaded - New Records: {len(current_data)}, Total: {len(all_data)}")
                    iteration += 1
                else:
                    # No more data available, break the loop
                    logger.warning(f"⚠️ No Additional Data Available - Breaking Loop at Iteration {iteration}")
                    break
            else:
                # LLM has provided final analysis
                logger.info(f"✅ LLM Analysis Complete - Final Iteration: {iteration}")
                break
        
        # Remove duplicates from all_data based on id
        unique_data = []
        seen_ids = set()
        for item in all_data:
            if item.get("id") not in seen_ids:
                unique_data.append(item)
                seen_ids.add(item.get("id"))
        
        logger.info(f"📊 Analysis Complete - Unique Data Points: {len(unique_data)}, Iterations: {iteration}")
        logger.info(f"📋 Final Analysis Length: {len(llm_response)} characters")
        
        return {
            "sensor_id": request.sensor_id,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "data_points_analyzed": len(unique_data),
            "iterations_performed": iteration,
            "llm_analysis": llm_response,
            "data_requested_by_llm": data_request if data_request else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analysis Failed - Sensor: {request.sensor_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/sensor/{sensor_id}")
def get_sensor_diagnostics(sensor_id: str, db: Session = Depends(get_db)):
    return """- Critical Asset Temperature (200.3°C), exceeding the 120°C limit.

- Critical G-force Peak on X-axis (17.0G), exceeding the 16G limit.

- Critical G-force Peak on Y-axis (17.0G), exceeding the 16G limit.

- Critical G-force Peak on Z-axis (17.0G), exceeding the 16G limit.

- Warning Environment Temperature (300.0°C), exceeding the 90°C limit.

- Warning Gateway - Weak Signal.

The sensor might be positioned too close to a heat source or an area of intense, localized vibration, leading to inaccurate readings. The weak gateway signal also indicates the sensor may be in a location with poor signal reachability.

- RECOMMENDATION:

Reposition for Temperature: Move the sensor to a location that more accurately reflects the asset's overall operating temperature, away from exhaust ports or other high-heat zones.

Reposition for Vibration: Ensure the sensor is mounted on a stable part of the asset's housing, avoiding areas of extreme, non-representative vibration that could cause false positives.

Improve Gateway Signal: Check the sensor's line of sight to the nearest gateway and reposition it to a location with fewer physical obstructions (like walls or machinery) to improve signal reachability.

"""

