from fastapi import APIRouter
from routes.llm import router as llm_router
from routes.database import router as database_router
from routes.setup import router as setup_router

router = APIRouter()
router.include_router(llm_router)
router.include_router(database_router)
router.include_router(setup_router)
