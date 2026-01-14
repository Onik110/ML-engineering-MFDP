from typing import Dict
from fastapi import APIRouter, HTTPException

home_route = APIRouter()

@home_route.get(
    "/",
    response_model=Dict[str, str],
    summary="ROOT ENDPOINT",
    description="Returns a welcome message"
)
async def index() -> Dict[str, str]:
    try:
        return {"message": "Welcome to event planner Api!!!"}
    except Exception as e:
        return HTTPException(status_code=500, detail="Internal server error!")
    
@home_route.get(
    "/health",
    response_model=Dict[str, str],
    summary="Health check ENDPOINT",
    description="Returns health status"
)
async def health_check() -> Dict[str, str]:
    try:
        return {"status": "healthy!"}
    except Exception as e:
        return HTTPException(
            status_code=503, 
            detail="Server unavailable!"
        )
    
