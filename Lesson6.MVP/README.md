# Рекомендательная система докладов JUG Ru

Сервис рекомендует пользователю релевантные технические доклады с конференций JUG Ru на основе его интересов (например: *«Я дата-сайентист и люблю послушать новинки про LLM»*). 

---
## Функционал

- Регистрация и аутентификация пользователей (JWT)
- Интерфейс чата на Streamlit: пользователь описывает свои интересы — получает рекомендации
- Рекомендательная система на основе:
  - **SBERT-эмбеддингов** для семантической близости текста
  - Косинусного сходства между запросом и докладами
- Хранение истории запросов и рекомендаций в PostgreSQL
- Асинхронная обработка через **RabbitMQ** и **3 ML-воркеры**
- Покрытие тестами 

## Стек технологий

| Компонент | Технология |
|---------|-----------|
| Backend | FastAPI (Python) |
| Frontend | Streamlit |
| БД | PostgreSQL |
| Очереди | RabbitMQ |
| Контейнеризация | Docker + Docker Compose |
| Тестирование | pytest, requests |
| Аутентификация | JWT (OAuth2PasswordRequestForm) |

---

## Структура проекта
```
.
├── app/
│   ├── api.py                 # Точка входа FastAPI
│   ├── database/              # Подключение к PostgreSQL
│   ├── models/                # Pydantic и SQLModel
│   ├── routes/                # Эндпоинты
│   ├── services/              # Бизнес-логика
│   ├── ml_worker/             # Воркер для обработки рекомендаций
│   └── streamlit_app/         # UI-интерфейс (временный)
├── data/
│   ├── dataset_processed.csv  # Обработанные доклады
│   ├── sbert_embeddings.npy   # Эмбеддинги докладов
│   └── sbert_model/           # Сохранённая SBERT-модель
├── docker-compose.yaml        # Оркестрация сервисов
└── README.md
```

## Как запустить проект

### 1. Установка зависимостей

```bash
# Убедитесь, что установлен Docker и Docker Compose
docker --version
docker compose version
```

### 2. app/.env файл

```bash
# Переменные для подключения к БД 
DB_HOST=db_host
DB_USER=db_user_name
DB_PASS=db_password
DB_PORT=db_port
DB_NAME=db_name

# Переменные для подключения к RabbitMQ 
RABBITMQ_USER=rabbitmq_user_name
RABBITMQ_PASS=rabbitmq_password
RABBITMQ_HOST=rabbitmq_host
RABBITMQ_PORT=5672
RABBITMQ_VIRTUAL_HOST=/

# Для JWT
SECRET_KEY=your_secret_jwt_key

# Для API
APP_NAME=server_name
APP_DESCRIPTION=app_description
API_VERSION=api_version
```

### 3. Запуск всего проекта

```bash
cd app
docker compose up --build
```

* Открой http://localhost:8501
* Зарегистрируйся
* Войди и опиши свои интересы (например: «люблю LLM и архитектуру нейросетей»)
* Получи топ-5 рекомендованных докладов c конференций JUG.ru

### 4. Тестирование

### Запуск интеграционных тестов

```bash
docker exec -it event-planner-app bash
pytest tests/ 
```
### Результаты по тестам
```bash
============================================== test session starts ==============================================
platform linux -- Python 3.10.19, pytest-9.0.2, pluggy-1.6.0
rootdir: /app
plugins: anyio-4.12.0
collected 6 items                                                                                               

tests/test_api.py ......                                                                                  [100%]

=============================================== 6 passed in 2.76s ===============================================
```

## Планы по развитию
1. Telegram-бот: интерфейс рекомендаций через чат
2. Хранение эмбеддингов в Qdrant: переход от файловой системы к векторной базе данных
3. Интеграция с конференциями в реальном времени: автоматическая рекомендация актуальных докладов во время ивентов
4. Система лайков/дизлайков: персонализация рекомендаций на основе обратной связи
5. Автоматическое обновление датасета: добавление новых докладов без перезапуска сервиса