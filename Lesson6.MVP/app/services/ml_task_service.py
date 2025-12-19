from sqlmodel import Session
from models.ml_task import MLTask, TaskStatus
from models.prediction import MLPrediction
from services.user_service import UserService
from services.prediction_service import PredictionService

class MLTaskService:
    def __init__(self, session: Session):
        self.session = session
        self.user_service = UserService(session)
        self.prediction_service = PredictionService(session)

    def create_task(self, user_id: int, model_name: str, input_data: str) -> MLTask:
        task = MLTask(
            user_id=user_id,
            model_name=model_name,
            input_data=input_data
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def run_task(self, task_id: int) -> dict:
        task = self.session.get(MLTask, task_id)
        if not task:
            raise ValueError("Task not found")

        if task.status == TaskStatus.PENDING:
            return {"status": "PENDING", "message": "Task is still pending"}

        if task.status == TaskStatus.FAILED:
            return {"status": "FAILED", "message": "Task failed"}

        if task.status == TaskStatus.DONE and task.result_id:
            prediction = self.session.get(MLPrediction, task.result_id)
            if prediction:
                return {
                    "model_name": prediction.model_name,
                    "prediction_result": prediction.prediction_result
                }
            else:
                return {"status": "DONE", "message": "Result not found"}
        else:
            return {"status": task.status.value}



    def get_task_history(self, user_id: int):

        tasks = (
            self.session.query(MLTask)
            .filter(MLTask.user_id == user_id)
            .order_by(MLTask.created_at.asc()) 
            .all()
        )
        
        result = []
        for task in tasks:
            # Определяем текст ответа
            if task.status == TaskStatus.DONE and task.result_id:
                prediction = self.session.get(MLPrediction, task.result_id)
                prediction_result = prediction.prediction_result if prediction else "Ответ недоступен"
            elif task.status == TaskStatus.FAILED:
                prediction_result = "Задача завершилась с ошибкой"
            else:
                prediction_result = "Ответ в обработке..."

            result.append({
                "id": task.id,
                "input_data": task.input_data,
                "prediction_result": prediction_result,
                "model_name": task.model_name,
                "status": task.status.value,
                "timestamp": task.created_at.isoformat()
            })
        
        return result