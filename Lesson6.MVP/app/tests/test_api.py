import requests
import time
import uuid

BASE_URL = "http://app:8080/api"

# 1. Регистрация существующего пользователя 
def test_signup_existing_user():
    email = f"existing_{uuid.uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    # Регистрация
    first = requests.post(f"{BASE_URL}/users/signup", json={"email": email, "password": password})
    assert first.status_code == 201

    # Повторная регистрация 
    second = requests.post(f"{BASE_URL}/users/signup", json={"email": email, "password": password})
    assert second.status_code == 409

# 2. Получение информации о пользователе
def test_get_user_info(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "email" in data
    assert "id" in data

# 3. Отправка ML-задачи 
def test_send_ml_task(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Отправляем задачу
    task_resp = requests.post(
        f"{BASE_URL}/ml/send_task",
        json={
            "input_data": "Я дата-сайентист, люблю LLM и архитектуру нейросетей",
            "model_name": "jug_recommender" 
        },
        headers=headers
    )
    assert task_resp.status_code == 201, f"Ошибка: {task_resp.text}"
    data = task_resp.json()
    assert "task_id" in data
    assert data["task_id"] > 0

# 4. Получение истории рекомендаций
def test_get_predictions_history(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    user_resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    user_id = user_resp.json()["id"]

    time.sleep(2)

    history_resp = requests.get(f"{BASE_URL}/predictions/all/{user_id}", headers=headers)
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert isinstance(history, list)
    if history:  
        item = history[0]
        assert "input_data" in item
        assert "prediction_result" in item
        assert "model_name" in item
        assert item["model_name"] == "jug_recommender"

# 5. Неверная модель
def test_invalid_model_name(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.post(
        f"{BASE_URL}/ml/send_task",
        json={
            "input_data": "Тест",
            "model_name": "llama3:latest" 
        },
        headers=headers
    )
    assert resp.status_code == 400
    assert "Model not supported" in resp.json().get("detail", "")

# 6. Пустой input_data
def test_empty_input_data(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = requests.post(
        f"{BASE_URL}/ml/send_task",
        json={"input_data": "", "model_name": "jug_recommender"},
        headers=headers
    )
    assert resp.status_code == 422 
    # Проверка сообщения необязательна, но можно:
    assert "String should have at least 1 character" in str(resp.json())