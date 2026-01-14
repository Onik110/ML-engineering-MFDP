import pika
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from models.ml_task import MLTask, TaskStatus
from models.prediction import MLPrediction
from services.prediction_service import PredictionService
from services.user_service import UserService
from database.database import SessionLocal

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === ЗАГРУЗКА РЕКОМЕНДАТЕЛЬНОЙ МОДЕЛИ ===
BASE_DIR = Path(__file__).parent.parent.parent  # -> MFDP/ML_engineering/Lesson6.MVP
DATA_DIR = BASE_DIR / "data"

# Загружаем данные докладов
df = pd.read_csv(DATA_DIR / "dataset_processed.csv")
sbert_embeddings = np.load(DATA_DIR / "sbert_embeddings.npy")

# Загружаем SBERT-модель для кодирования текста пользователя
sbert_model = SentenceTransformer(str(DATA_DIR / "sbert_model"))

logger.info(f"✅ Recommender system loaded: {len(df)} presentations")

# === Параметры RabbitMQ ===
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_VIRTUAL_HOST = os.getenv("RABBITMQ_VIRTUAL_HOST", "/")

connection_params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    virtual_host=RABBITMQ_VIRTUAL_HOST,
    credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
    heartbeat=30,
    blocked_connection_timeout=60
)


def update_task_status(session, task, status, result_id=None):
    task.status = status
    task.updated_at = datetime.now()
    if status == TaskStatus.DONE:
        task.completed_at = task.updated_at
    if result_id:
        task.result_id = result_id
    session.add(task)
    session.commit()
    logger.info(f"Task {task.id} → status={status.value}, result_id={result_id}")


def fail_task(session, task, reason="Unknown error", ch=None, method=None):
    logger.error(f"Task {task.id} failed: {reason}")
    update_task_status(session, task, TaskStatus.FAILED)
    if ch and method:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def callback(ch, method, properties, body):
    session = SessionLocal()
    try:
        task_data = json.loads(body.decode('utf-8'))
        task_id = task_data["task_id"]
        user_id = task_data["user_id"]
        model_name = task_data["model_name"]
        input_data = task_data["input_data"]

        logger.info(f"📥 Processing task {task_id} from user {user_id}")

        task = session.get(MLTask, task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return

        if task.status != TaskStatus.PENDING:
            logger.warning(f"Task {task_id} already processed ({task.status})")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        update_task_status(session, task, TaskStatus.PROCESSING)

        # Валидация входных данных
        if not input_data or not input_data.strip():
            fail_task(
                session=session,
                task=task,
                reason="Empty input data",
                ch=ch, method=method
            )
            return

        # Получаем пользователя
        user = UserService(session).get_by_id(user_id)
        if not user:
            fail_task(
                session=session,
                task=task,
                reason=f"User {user_id} not found",
                ch=ch, method=method
            )
            return

        # === РЕКОМЕНДАЦИЯ ПО ТЕКСТУ ИНТЕРЕСОВ ПОЛЬЗОВАТЕЛЯ ===
        try:
            user_interests = input_data.strip()
            if not user_interests:
                raise ValueError("User interests cannot be empty")

            # Кодируем интересы пользователя в вектор
            user_embedding = sbert_model.encode([user_interests], convert_to_tensor=False)[0]

            # Сравниваем с эмбеддингами докладов
            scores = cosine_similarity([user_embedding], sbert_embeddings)[0]

            # Берём топ-5
            top_k = 5
            top_idxs = np.argsort(-scores)[:top_k]

            # Формируем читаемый результат
            recommendations = []
            for idx in top_idxs:
                rec = df.iloc[idx]
                recommendations.append({
                    "title": rec["title"],
                    "speaker": rec["speaker"],
                    "category": rec["category"],
                    "conf": rec["conf"]
                })

            prediction_result = "\n".join([
                f"{i+1}. [{rec['category']}] {rec['title']} — {rec['speaker']} ({rec['conf']})"
                for i, rec in enumerate(recommendations)
            ])

        except Exception as e:
            fail_task(
                session=session,
                task=task,
                reason=f"Recommender error: {str(e)}",
                ch=ch, method=method
            )
            return
        # ================================================

        # Сохраняем результат в БД
        try:
            prediction = PredictionService(session).add_prediction(
                MLPrediction(
                    user_id=user_id,
                    model_name=model_name,
                    prediction_result=prediction_result
                )
            )
            update_task_status(session, task, TaskStatus.DONE, result_id=prediction.id)
            logger.info(f"✅ Task {task_id} completed. Sample: {prediction_result.splitlines()[0][:60]}...")

        except Exception as e:
            fail_task(
                session=session,
                task=task,
                reason=f"Failed to save prediction: {str(e)}",
                ch=ch, method=method
            )
            return

        # Успешно — подтверждаем обработку в RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"💥 Unexpected error in worker: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    finally:
        session.close()


if __name__ == "__main__":
    try:
        logger.info("🚀 Starting ML Worker...")
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue='ml_task', durable=True)
        channel.basic_consume(queue='ml_task', on_message_callback=callback, auto_ack=False)
        logger.info("🧠 ML Worker ready. Waiting for tasks...")
        channel.start_consuming()
    except Exception as e:
        logger.critical(f"❌ Worker failed to start: {e}")
        exit(1)