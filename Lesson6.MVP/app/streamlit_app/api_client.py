import requests
from typing import Optional, Dict, List
import streamlit as st

BASE_URL = "http://app:8080/api" 


def login(username: str, password: str) -> Optional[str]:
    print(f"Попытка входа: {username}")
    response = requests.post(
        f"{BASE_URL}/users/signin",
        data={          
            "username": username,   # OAuth2PasswordRequestForm использует "username"
            "password": password
        }
    )

    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        if token:
            print(f"Успешно получили токен: {token[:20]}...")
            return token
        else:
            print("Токен не найден в ответе")
            return None
    else:
        print(f"Ошибка входа: {response.status_code} {response.text}")
        return None

def send_ml_task(token: str, user_id: int, input_data: str, model_name: str = "jug_recommender") -> tuple[bool, str]:
    """
    Отправляет задачу на ML-воркер.
    model_name теперь всегда 'jug_recommender'
    """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"{BASE_URL}/ml/send_task",
            json={
                "user_id": user_id,          
                "input_data": input_data,
                "model_name": model_name  
            },
            headers=headers
        )

        if response.status_code == 201:
            return True, "Задача отправлена"
        
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Некорректные данные")
            return False, f"❌ Ошибка ввода: {error_detail}"
        
        elif response.status_code == 403:
            return False, "❌ Доступ запрещён. Проверьте токен."
        
        elif response.status_code == 404:
            return False, "❌ Пользователь не найден."
        
        elif response.status_code == 500:
            return False, "❌ Ошибка сервера при обработке запроса."
        
        else:
            return False, f"❌ Ошибка: {response.status_code}"

    except requests.exceptions.ConnectionError:
        return False, "Нет соединения с сервером ML."
    except requests.exceptions.Timeout:
        return False, "Таймаут подключения."
    except Exception as e:
        return False, f"Неизвестная ошибка: {str(e)}"
    
def get_predictions(token: str, user_id: int) -> List[dict]:
    """GET /predictions/all/{user_id}"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{BASE_URL}/predictions/all/{user_id}",  
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []


def signup(email: str, password: str) -> tuple[bool, str]:
    try:
        response = requests.post(
            f"{BASE_URL}/users/signup",
            json={
                "email": email,
                "password": password
            }
        )

        if response.status_code == 201:
            return True, "✅ Регистрация успешна! Войдите в систему."

        elif response.status_code == 409:
            # Пользователь уже существует
            error_detail = response.json().get("detail", "User with this email already exists")
            return False, f"❌ {error_detail}"

        elif response.status_code == 400:
            # Невалидный email или пароль
            error_detail = response.json().get("detail", "Invalid input")
            if "Invalid email format" in error_detail:
                return False, "❌ Неверный формат email. Пример: user@example.com"
            elif "password" in error_detail.lower():
                return False, f"❌ {error_detail}"
            else:
                return False, f"❌ Ошибка ввода: {error_detail}"

        else:
            return False, f"❌ Ошибка сервера: {response.status_code}"

    except requests.exceptions.ConnectionError:
        return False, "Нет соединения с сервером. Проверьте подключение."
    except requests.exceptions.Timeout:
        return False, "Таймаут подключения к серверу."
    except Exception as e:
        return False, f"Неизвестная ошибка: {str(e)}"