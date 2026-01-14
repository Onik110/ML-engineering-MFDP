import streamlit as st
import api_client
import time
from api_client import BASE_URL
import requests

# Настройка
st.set_page_config(page_title="Личный кабинет", layout="wide")
st.title("AI Ассистент докладов JUG.RU")

# Инициализация session_state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = "home"


def logout():
    st.session_state.clear()
    st.rerun()


def fetch_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    return response.json() if response.status_code == 200 else None


def login_page():
    st.subheader("🔐 Вход")
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        if not username or not password:
            st.error("Заполните все поля")
        else:
            token = api_client.login(username, password)
            if token:
                st.session_state.token = token
                user_info = fetch_user_info(token)  # получаем id и email
                if user_info:
                    st.session_state.user_id = user_info["id"]
                    st.session_state.username = user_info["email"]
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Не удалось загрузить данные пользователя")
            else:
                st.error("Неверный логин или пароль")

    if st.button("← Назад"):
        st.session_state.page = "home"
        st.rerun()


def register_page():
    st.subheader("📝 Создать аккаунт")

    email = st.text_input("Email", placeholder="your@email.com")
    password = st.text_input("Пароль", type="password", placeholder="минимум 8 символов")
    confirm_password = st.text_input("Подтвердите пароль", type="password")

    if st.button("Зарегистрироваться", use_container_width=True):
        if not email or not password:
            st.error("Все поля обязательны")
        elif password != confirm_password:
            st.error("Пароли не совпадают")
        else:
            with st.spinner("Регистрируем..."):
                success, msg = api_client.signup(email, password)
                if success:
                    st.success(msg)
                    time.sleep(1.5)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(msg)  

    if st.button("← Назад", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

def home_page():
    st.markdown("""
    ## Добро пожаловать в AI пространство по рекомендации докладов JUG.ru!
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Войти", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("📝 Регистрация", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

def dashboard():
    st.sidebar.title(f"{st.session_state.username}")
    if st.sidebar.button("Выйти", use_container_width=True):
        logout()

    tabs = st.tabs(["💬 Чат"])

    with tabs[0]:
        st.subheader("💬 AI Ассистент докладов JUG.RU")

        # Кнопка "Обновить чат"
        if st.button("🔄 Обновить чат", key="refresh_chat", help="Нажмите, чтобы обновить историю сообщений"):
            st.rerun()  # Полная перезагрузка страницы с сохранением session_state

        # Загружаем историю
        history = api_client.get_predictions(st.session_state.token, st.session_state.user_id)

        chat_container = st.container()

        with chat_container:
            if not history:
                st.markdown("Пока нет сообщений. Напишите какие доклады Вам были бы интересны:")
            else:
                for item in history:
                    with st.chat_message("user"):
                        st.write(item["input_data"])
                    with st.chat_message("assistant"):
                        st.write(item["prediction_result"])

        # Поле ввода
        user_input = st.chat_input("Опишите ваши интересы, либо пожелания увидеть доклады (например: 'Я дата-сайентист, люблю LLM и архитектуру')")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("🧠 Генерирую рекомендованные доклады..."):
                    success, msg = api_client.send_ml_task(
                        token=st.session_state.token,
                        user_id=st.session_state.user_id,
                        input_data=user_input
                    )
                    if success:
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.write(msg)

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page() 
elif st.session_state.page == "dashboard":
    dashboard()


