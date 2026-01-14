from sqlmodel import Session
from database.config import get_settings
from database.database import init_db, get_database_engine
from services.user_service import UserService
from services.prediction_service import PredictionService
from services.ml_task_service import MLTaskService


def create_demo_data():
    
    engine = get_database_engine()
    
    with Session(engine) as session:

        user_service = UserService(session)
        prediction_service = PredictionService(session)
        ml_task_service = MLTaskService(session)


        print("Создаем демо-пользователя")
        user = user_service.create_user("test@yandex.ru", "password123")
        print(f"Создан пользователь: {user.email} (ID: {user.id})")


        task = ml_task_service.run_query(user.id, "<название модели>", "<Текст запроса>")
        print(f"Создана ml-задача: {task.model_name}")

        admin = user_service.create_user("admin@yandex.ru", "admin123")
        print(f"Создан администратор: {admin.email}")

        print("\n--- История предсказаний ---")
        for p in prediction_service.get_history(user.id):
            print(p)



if __name__ == "__main__":
    settings = get_settings()

    print(settings.DB_HOST)
    print(settings.DB_NAME)
    print(settings.DB_USER)

    init_db(drop_all=False)
    print("Init DB has been success")

    create_demo_data()