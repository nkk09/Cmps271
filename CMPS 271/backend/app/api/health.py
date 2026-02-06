from fastapi import APIRouter
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/health")
def health():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}
