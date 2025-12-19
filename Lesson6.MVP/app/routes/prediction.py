from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from services.ml_task_service import MLTaskService
from services.prediction_service import PredictionService
import logging

logger = logging.getLogger(__name__)

prediction_route = APIRouter()

@prediction_route.get("/all/{user_id}")
async def view_predictions(user_id: int, session=Depends(get_session)):
    ml_task_service = MLTaskService(session)
    try:
        history = ml_task_service.get_task_history(user_id)
        return history
    except Exception as e:
        logger.error(f"Error fetching prediction history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history"
        )

# просмотр ответа на текущий запрос
@prediction_route.get("/{task_id}")
async def get_prediction_result(task_id: int, session=Depends(get_session)):
    try:
        ml_task_service = MLTaskService(session)
        result = ml_task_service.run_task(task_id=task_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or no result available"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task result"
        )
    

