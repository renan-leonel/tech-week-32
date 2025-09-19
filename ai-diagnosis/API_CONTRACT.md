# Sensor Data API Contract

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Add Sensor Data
**POST** `/sensors/add`

Adds new sensor data to the database.

#### Request Body
```json
{
  "asset_id": "string (optional)",
  "sampled_at": "datetime (required)",
  "sensor_id": "string (optional)",
  "accel_peak_x": "number (optional)",
  "accel_peak_y": "number (optional)",
  "accel_peak_z": "number (optional)",
  "temperature": "number (optional)",
  "temperature_accelerometer": "number (optional)",
  "gateway_signal": "integer (optional)"
}
```

#### Response (201 Created)
```json
{
  "id": "uuid",
  "asset_id": "string | null",
  "sampled_at": "datetime",
  "sensor_id": "string | null",
  "accel_peak_x": "number | null",
  "accel_peak_y": "number | null",
  "accel_peak_z": "number | null",
  "temperature": "number | null",
  "temperature_accelerometer": "number | null",
  "gateway_signal": "integer | null"
}
```

#### Example Request
```json
{
  "asset_id": "GPD9132",
  "sampled_at": "2025-01-19T10:30:00Z",
  "sensor_id": "SENSOR_001",
  "accel_peak_x": 0.03318444,
  "accel_peak_y": 0.028964927,
  "accel_peak_z": 0.028806016,
  "temperature": 23.795675,
  "temperature_accelerometer": 19.323671,
  "gateway_signal": -75
}
```

---

### 2. Get All Sensor Data
**GET** `/sensors/all`

Retrieves all sensor data records from the database, ordered by most recent first.

#### Response (200 OK)
```json
[
  {
    "id": "uuid",
    "asset_id": "string | null",
    "sampled_at": "datetime",
    "sensor_id": "string | null",
    "accel_peak_x": "number | null",
    "accel_peak_y": "number | null",
    "accel_peak_z": "number | null",
    "temperature": "number | null",
    "temperature_accelerometer": "number | null",
    "gateway_signal": "integer | null"
  }
]
```

#### Example Response
```json
[
  {
    "id": "14632df0-0ac5-52b6-ba44-6aba394ff5a8",
    "asset_id": "GPD9132",
    "sampled_at": "2025-01-19T10:30:00Z",
    "sensor_id": "SENSOR_001",
    "accel_peak_x": 0.03318444,
    "accel_peak_y": 0.028964927,
    "accel_peak_z": 0.028806016,
    "temperature": 23.795675,
    "temperature_accelerometer": 19.323671,
    "gateway_signal": -75
  }
]
```

---

### 3. Get Data by Sensor ID
**GET** `/sensors/by-sensor/{sensor_id}`

Retrieves all data for a specific sensor ID, ordered by most recent first.

#### Path Parameters
- `sensor_id` (string, required): The ID of the sensor to query

#### Response (200 OK)
```json
[
  {
    "id": "uuid",
    "asset_id": "string | null",
    "sampled_at": "datetime",
    "sensor_id": "string | null",
    "accel_peak_x": "number | null",
    "accel_peak_y": "number | null",
    "accel_peak_z": "number | null",
    "temperature": "number | null",
    "temperature_accelerometer": "number | null",
    "gateway_signal": "integer | null"
  }
]
```

#### Response (404 Not Found)
```json
{
  "detail": "No data found for sensor_id: {sensor_id}"
}
```

#### Example Request
```
GET /sensors/by-sensor/SENSOR_001
```

---

### 4. Clear All Sensor Data
**DELETE** `/sensors/clear-all`

Removes all sensor data samples from the database.

#### Response (200 OK)
```json
{
  "message": "All sensor data cleared successfully",
  "records_deleted": "integer"
}
```

#### Response (500 Internal Server Error)
```json
{
  "detail": "Failed to clear sensor data: {error_message}"
}
```

#### Example Request
```
DELETE /sensors/clear-all
```

---

### 5. Populate Database with Sample Data
**POST** `/sensors/populate`

Populate the database with all sample data from sample_data.json.

#### Request Body
```json
{
  "clear_existing": "boolean (default false)"
}
```

#### Response (200 OK)
```json
{
  "message": "Successfully inserted 280 records",
  "records_inserted": 280,
  "clear_existing": false
}
```

#### Response (500 Internal Server Error)
```json
{
  "detail": "Failed to populate database: {error_message}"
}
```

#### Example Request
```json
POST /sensors/populate
{
  "clear_existing": true
}
```

#### Example Response
```json
{
  "message": "All sensor data cleared successfully",
  "records_deleted": 150
}
```

---

## MCP (LLM Database Access) Endpoints

### 5. Search Sensor Data
**POST** `/mcp/search`

Search sensor data with optional filters for LLM access.

#### Request Body
```json
{
  "sensor_id": "string (optional)",
  "asset_id": "string (optional)",
  "limit": "integer (1-100, default 10)",
  "order_by": "string (default 'sampled_at')",
  "order_desc": "boolean (default true)"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "count": "integer",
  "data": [
    {
      "id": "uuid",
      "asset_id": "string",
      "sampled_at": "datetime",
      "sensor_id": "string",
      "accel_peak_x": "number",
      "accel_peak_y": "number",
      "accel_peak_z": "number",
      "temperature": "number",
      "temperature_accelerometer": "number",
      "gateway_signal": "integer",
      "created_at": "datetime"
    }
  ]
}
```

---

### 6. Update Sampled At
**POST** `/mcp/update-sampled-at`

Update the sampled_at timestamp for a specific record. **SECURITY: Only this column can be modified.**

#### Request Body
```json
{
  "id": "string (required)",
  "sampled_at": "datetime (required)"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "string",
  "updated_record": {
    "id": "uuid",
    "sampled_at": "datetime"
  }
}
```

#### Response (404 Not Found)
```json
{
  "detail": "Record with ID {id} not found"
}
```

---

### 7. Get Sensor Summary
**POST** `/mcp/summary`

Get summary statistics for sensor data.

#### Request Body
```json
{
  "sensor_id": "string (optional)"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "summary": {
    "total_records": "integer",
    "unique_sensors": "integer",
    "earliest_sample": "datetime",
    "latest_sample": "datetime",
    "averages": {
      "temperature": "number",
      "accel_peak_x": "number",
      "accel_peak_y": "number",
      "accel_peak_z": "number",
      "gateway_signal": "number"
    }
  }
}
```

---

### 8. List MCP Tools
**GET** `/mcp/tools`

List available MCP tools for LLM with security restrictions.

#### Response (200 OK)
```json
{
  "success": true,
  "mcp_tools": [
    {
      "name": "search_sensor_data",
      "description": "Search sensor data with optional filters",
      "endpoint": "POST /mcp/search",
      "parameters": "object",
      "security": "READ-ONLY - Can only read data"
    },
    {
      "name": "update_sampled_at",
      "description": "Update the sampled_at timestamp for a specific record",
      "endpoint": "POST /mcp/update-sampled-at",
      "parameters": "object",
      "security": "LIMITED WRITE - Can only update sampled_at column"
    },
    {
      "name": "get_sensor_summary",
      "description": "Get summary statistics for sensor data",
      "endpoint": "POST /mcp/summary",
      "parameters": "object",
      "security": "READ-ONLY - Can only read aggregated data"
    }
  ],
  "security_note": "LLM can only read data and update the sampled_at column. All other modifications are restricted."
}
```

---

## Health Analysis Endpoints

### 4. Get Sensor Health Analysis
**GET** `/health/analysis/{sensor_id}`

Analyzes the health status of a specific sensor based on connectivity, acceleration, and temperature data.

#### Path Parameters
- `sensor_id` (string, required): The ID of the sensor to analyze

#### Response (200 OK)
```json
{
  "sensor_id": "string",
  "analysis_timestamp": "datetime",
  "health_status": {
    "sensor_id": "string",
    "timestamp": "datetime",
    "connectivity_ok": "boolean",
    "acceleration_ok": "boolean",
    "temperature_ok": "boolean",
    "overall_health": "string",
    "connectivity_signal": "integer | null",
    "max_acceleration": "number | null",
    "max_temperature": "number | null",
    "issues": ["string"]
  },
  "recommendations": ["string"]
}
```

#### Response (404 Not Found)
```json
{
  "detail": "No data found for sensor_id: {sensor_id}"
}
```

#### Example Response
```json
{
  "sensor_id": "SENSOR_001",
  "analysis_timestamp": "2025-01-19T10:35:00Z",
  "health_status": {
    "sensor_id": "SENSOR_001",
    "timestamp": "2025-01-19T10:30:00Z",
    "connectivity_ok": true,
    "acceleration_ok": true,
    "temperature_ok": false,
    "overall_health": "warning",
    "connectivity_signal": -75,
    "max_acceleration": 0.033,
    "max_temperature": 95.5,
    "issues": ["High temperature: 95.5°C"]
  },
  "recommendations": [
    "Check cooling systems and ventilation",
    "Monitor for overheating conditions"
  ]
}
```

---

### 5. Get All Sensors Health Analysis
**GET** `/health/analysis`

Analyzes the health status of all sensors in the system.

#### Response (200 OK)
```json
[
  {
    "sensor_id": "string",
    "analysis_timestamp": "datetime",
    "health_status": {
      "sensor_id": "string",
      "timestamp": "datetime",
      "connectivity_ok": "boolean",
      "acceleration_ok": "boolean",
      "temperature_ok": "boolean",
      "overall_health": "string",
      "connectivity_signal": "integer | null",
      "max_acceleration": "number | null",
      "max_temperature": "number | null",
      "issues": ["string"]
    },
    "recommendations": ["string"]
  }
]
```

---

### 6. Get Health Summary
**GET** `/health/summary`

Returns an overall health summary across all sensors.

#### Response (200 OK)
```json
{
  "total_sensors": "integer",
  "healthy_sensors": "integer",
  "warning_sensors": "integer",
  "critical_sensors": "integer",
  "overall_status": "string",
  "health_percentage": "number"
}
```

#### Example Response
```json
{
  "total_sensors": 5,
  "healthy_sensors": 3,
  "warning_sensors": 1,
  "critical_sensors": 1,
  "overall_status": "critical",
  "health_percentage": 60.0
}
```

---

## Sensor Diagnostics Endpoints

### 7. Get LLM-Powered Sensor Analysis
**POST** `/diagnostics/sensor/{sensor_id}/analysis`

Performs comprehensive LLM-powered analysis using MCP to query data iteratively. The LLM can request different date ranges to identify when error patterns started.

#### Path Parameters
- `sensor_id` (string, required): The ID of the sensor to analyze

#### Request Body
```json
{
  "sensor_id": "string (required)"
}
```

#### Response (200 OK)
```json
{
  "sensor_id": "string",
  "analysis_timestamp": "datetime",
  "data_points_analyzed": "integer",
  "iterations_performed": "integer",
  "llm_analysis": "string",
  "data_requested_by_llm": "object (optional)"
}
```

#### Response (404 Not Found)
```json
{
  "detail": "No data found for sensor_id: {sensor_id}"
}
```

#### Example Response
```json
{
  "sensor_id": "SENSOR_001",
  "analysis_timestamp": "2025-01-19T10:30:00Z",
  "data_points_analyzed": 150,
  "iterations_performed": 3,
  "llm_analysis": "*** SENSOR ANALYSIS REPORT ***\n\nSENSOR ID: SENSOR_001\nDATA RANGE ANALYZED: 2025-01-17T10:30:00Z to 2025-01-19T10:30:00Z\n\nCURRENT STATUS: Critical\n\nACTIVE ALERTS:\n- Critical Asset Temperature (200.3°C) at 2025-01-19T09:45:00Z, exceeding the 120°C limit.\n- Critical G-force Peak on X-axis (17.0G) at 2025-01-19T09:45:00Z, exceeding the 16G limit.\n\nTREND ANALYSIS:\nThe sensor shows a clear upward trend in temperature starting from 2025-01-18T15:00:00Z, with temperature rising from 85°C to 200°C over 18 hours. Vibration levels also increased significantly during this period, suggesting mechanical stress or bearing failure.\n\nRECOMMENDATION:\n1) Immediate shutdown required due to critical temperature. 2) Check bearing condition and mechanical alignment. 3) Reposition sensor to a location that more accurately reflects the asset's overall operating temperature.\n\n*** END OF REPORT ***",
  "data_requested_by_llm": {
    "start_date": "2025-01-17",
    "end_date": "2025-01-18",
    "reason": "Need to see data from 2 days ago to identify when the temperature trend started"
  }
}
```

---

### 8. Get Basic Sensor Diagnostics
**GET** `/diagnostics/sensor/{sensor_id}`

Returns a simple string explaining what's wrong with the sensor (basic analysis).

#### Path Parameters
- `sensor_id` (string, required): The ID of the sensor to diagnose

#### Response (200 OK)
```json
"string"
```

#### Response (404 Not Found)
```json
{
  "detail": "No data found for sensor_id: {sensor_id}"
}
```

#### Example Responses

**Healthy Sensor:**
```
"All systems operating normally"
```

**Warning Issues:**
```
"WARNING: Weak signal (-87 dBm) - Check antenna positioning and gateway proximity; Elevated temperature (95.5°C) - Monitor cooling systems and check airflow"
```

**Critical Issues:**
```
"CRITICAL: Extreme temperature (155.2°C) - Immediate shutdown required, risk of equipment damage."
```

**Offline Sensor:**
```
"Sensor is OFFLINE - No data received for 2 days, 5 hours. Check sensor power, connectivity, and physical condition."
```

---

## Health Analysis Logic

### Connectivity Analysis
- **Healthy**: Signal strength ≥ -75 dBm
- **Warning**: Signal strength -85 to -75 dBm
- **Critical**: Signal strength < -85 dBm

### Acceleration Analysis
- **Healthy**: Max G-force ≤ 12G
- **Warning**: Max G-force 12-16G
- **Critical**: Max G-force > 16G

### Temperature Analysis
- **Healthy**: Temperature ≤ 90°C
- **Warning**: Temperature 90-120°C
- **Critical**: Temperature > 120°C

### Overall Health Status
- **healthy**: All systems OK
- **warning**: One or more systems in warning state
- **critical**: One or more systems in critical state

---

## Data Types

### SensorData Object
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | UUID | Unique identifier for the record | Auto-generated |
| `asset_id` | String | Asset identifier | No |
| `sampled_at` | DateTime | Timestamp when data was sampled | Yes (for POST) |
| `sensor_id` | String | Sensor identifier | No |
| `accel_peak_x` | Number | Peak acceleration on X-axis (G) | No |
| `accel_peak_y` | Number | Peak acceleration on Y-axis (G) | No |
| `accel_peak_z` | Number | Peak acceleration on Z-axis (G) | No |
| `temperature` | Number | Asset temperature (°C) | No |
| `temperature_accelerometer` | Number | Accelerometer temperature (°C) | No |
| `gateway_signal` | Integer | Gateway signal strength (dBm) | No |

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Frontend Integration Examples

### JavaScript/TypeScript
```typescript
interface SensorData {
  id: string;
  asset_id: string | null;
  sampled_at: string; // ISO datetime
  sensor_id: string | null;
  accel_peak_x: number | null;
  accel_peak_y: number | null;
  accel_peak_z: number | null;
  temperature: number | null;
  temperature_accelerometer: number | null;
  gateway_signal: number | null;
}

interface HealthStatus {
  sensor_id: string;
  timestamp: string; // ISO datetime
  connectivity_ok: boolean;
  acceleration_ok: boolean;
  temperature_ok: boolean;
  overall_health: 'healthy' | 'warning' | 'critical';
  connectivity_signal: number | null;
  max_acceleration: number | null;
  max_temperature: number | null;
  issues: string[];
}

interface HealthAnalysisResponse {
  sensor_id: string;
  analysis_timestamp: string; // ISO datetime
  health_status: HealthStatus;
  recommendations: string[];
}

interface HealthSummary {
  total_sensors: number;
  healthy_sensors: number;
  warning_sensors: number;
  critical_sensors: number;
  overall_status: 'healthy' | 'warning' | 'critical';
  health_percentage: number;
}

// Add sensor data
async function addSensorData(data: Omit<SensorData, 'id'>): Promise<SensorData> {
  const response = await fetch('http://localhost:8000/sensors/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
}

// Get all sensor data
async function getAllSensorData(): Promise<SensorData[]> {
  const response = await fetch('http://localhost:8000/sensors/all');
  return response.json();
}

// Get data by sensor ID
async function getSensorDataById(sensorId: string): Promise<SensorData[]> {
  const response = await fetch(`http://localhost:8000/sensors/by-sensor/${sensorId}`);
  return response.json();
}

// Health Analysis Functions
async function getSensorHealthAnalysis(sensorId: string): Promise<HealthAnalysisResponse> {
  const response = await fetch(`http://localhost:8000/health/analysis/${sensorId}`);
  return response.json();
}

async function getAllSensorsHealthAnalysis(): Promise<HealthAnalysisResponse[]> {
  const response = await fetch('http://localhost:8000/health/analysis');
  return response.json();
}

async function getHealthSummary(): Promise<HealthSummary> {
  const response = await fetch('http://localhost:8000/health/summary');
  return response.json();
}

// Diagnostics Functions
async function getSensorDiagnostics(sensorId: string): Promise<string> {
  const response = await fetch(`http://localhost:8000/diagnostics/sensor/${sensorId}`);
  return response.json();
}

async function getLLMSensorAnalysis(sensorId: string): Promise<{
  sensor_id: string;
  analysis_timestamp: string;
  data_points_analyzed: number;
  iterations_performed: number;
  llm_analysis: string;
  data_requested_by_llm?: {
    start_date: string;
    end_date: string;
    reason: string;
  };
}> {
  const response = await fetch(`http://localhost:8000/diagnostics/sensor/${sensorId}/analysis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sensor_id: sensorId
    })
  });
  return response.json();
}
```

### React Hook Example
```typescript
import { useState, useEffect } from 'react';

function useSensorData() {
  const [data, setData] = useState<SensorData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/sensors/all')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  return { data, loading };
}
```

## Notes
- All datetime fields are in ISO 8601 format
- All numeric fields can be null if not provided
- The API returns data ordered by `sampled_at` in descending order (most recent first)
- UUIDs are generated automatically for new records
- The API uses FastAPI's automatic OpenAPI documentation at `/docs`
