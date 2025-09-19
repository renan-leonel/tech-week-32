import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.llm import router as llm_router
from routes.database import router as database_router
from routes.setup import router as setup_router
from routes.health_analysis import router as health_router
from routes.sensor_diagnostics import router as diagnostics_router
from routes.mcp import router as mcp_router

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


app = FastAPI(
    title="AI Diagnosis System",
    version="0.0.1",
    description="An AI-powered diagnosis system with document RAG and sensor data analysis",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(llm_router)
app.include_router(database_router)
app.include_router(setup_router)
app.include_router(health_router)
app.include_router(diagnostics_router)
app.include_router(mcp_router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Main"])
async def health_check():
    return {"status": "ok"}

