from fastapi import APIRouter, HTTPException, Depends
from database.database import get_session
from models.task_request import TaskRequest
from services.ml_task_service import MLTaskService
from auth.authenticate import get_current_user
from models.user import User
import logging

ml_route = APIRouter()
logger = logging.getLogger(__name__)

@ml_route.post("/send_task", status_code=201)
async def new_request(
    request: TaskRequest,
    current_user: User = Depends(get_current_user),  # получаем из токена
    session=Depends(get_session)
):
    try:
        actual_user_id = current_user.id

        # Проверяем input_data
        if not request.input_data.strip():
            raise HTTPException(status_code=400, detail="Input data cannot be empty or whitespace")

        # Проверяем длину
        if len(request.input_data) > 1000:
            raise HTTPException(status_code=400, detail="Input data too long (max 1000 characters)")

        # Проверяем модель 
        allowed_models = ["jug_recommender"]
        if request.model_name not in allowed_models:
            raise HTTPException(
                status_code=400,
                detail=f"Model not supported. Use one of: {allowed_models}"
            )

        # Создаём задачу
        ml_task_service = MLTaskService(session)
        task = ml_task_service.create_task(
            user_id=actual_user_id,
            model_name=request.model_name,
            input_data=request.input_data.strip()
        )
        task_id = task.id

        # Отправляем в RabbitMQ
        try:
            from services.rm import send_task
            send_task({
                "task_id": task_id,
                "user_id": actual_user_id,
                "model_name": request.model_name,
                "input_data": request.input_data.strip()
            })
            logger.info(f"Task {task_id} sent to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to send task to RabbitMQ: {e}")
            raise HTTPException(status_code=500, detail="Failed to send task to worker")

        return {
            "message": f"Task {task_id} sent to ML workers",
            "task_id": task_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")