# AI-ассистент рекомендаций докладов JUG.RU

**MVP** в рамках курса **ML Engineering** от ITMO x Karpov.Courses

Этот проект представляет собой полноценную, асинхронную рекомендательную систему для подбора технических докладов с конференций от **JUG.RU**.  
Пользователь описывает свои интересы текстом → система возвращает топ-5 наиболее релевантных докладов на основе гибридной модели: **семантическое сходство + категория + спикер + компания**.

---

## Ключевые особенности:

- **Интерфейс чата (Streamlit)**: пользователь пишет запрос → получает рекомендации  
- **Гибридная рекомендательная модель**: оптимизирована через Optuna, **Relevance@5 = 0.777**  
- **Полная аутентификация**: JWT + bcrypt + OAuth2PasswordRequestForm  
- **Асинхронная обработка**: RabbitMQ + 3 масштабируемых ML-воркера  
- **История взаимодействий**: все запросы и ответы сохраняются в PostgreSQL  
- **Тестирование**: покрыто интеграционными тестами (`pytest`)  
- **Контейнеризация**: Docker Compose для быстрого развёртывания  

---

## Модель и данные

### Датасет
- Источник: `dataset_jug.csv` — **76 докладов** с полями:  
  `title`, `speaker`, `companies`, `category`, `conf`, `text`
- После фильтрации (удалены категории с <3 докладов) → **70 докладов**
- Примеры категорий: `Infrastructure`, `AI`, `Architecture`, `Security`, `Best Practices`

### Векторизация
- **Sentence-BERT**: `paraphrase-multilingual-MiniLM-L12-v2`
- Эмбеддинги сохранены в `Lesson6.MVP/data/sbert_embeddings.npy`
- Модель SBERT сохранена локально в `Lesson6.MVP/data/sbert_model/`

### Гибридная рекомендация

Оптимизирована через **Optuna** (`n_trials=50`):

Качество модели:

| Модель                | Relevance@5 | Diversity | Composite |
|----------------------|-------------|-----------|-----------|
| TF-IDF               | 0.160       | 0.616     | 0.297     |
| Word2Vec             | 0.074       | 0.627     | 0.240     |
| Sentence-BERT        | 0.186       | 0.509     | 0.283     |
| **Hybrid (Optuna-tuned)** | **0.777**   | **0.588** | **0.720** |

> **Relevance@5** = доля рекомендаций из той же категории, что и запрос пользователя.  
> **Composite Score** = `0.7 * Relevance@5 + 0.3 * Diversity`

---

## Архитектура системы

```
User → Streamlit UI → FastAPI → RabbitMQ → ML Worker → PostgreSQL
                         ↑              ↖_____________↗
                      Auth (JWT)         (async task queue)
```


## Технологический стек

| Категория        | Технологии                                                                 |
|------------------|---------------------------------------------------------------------------|
| Backend          | Python 3.10, FastAPI, SQLModel, Pydantic, uvicorn                        |
| Frontend         | Streamlit                                                                |
| ML               | Sentence-BERT, scikit-learn, pandas, numpy, Optuna                       |
| База данных      | PostgreSQL 16                                                            |
| Очереди          | RabbitMQ 3.13                          |
| Аутентификация   | JWT (HS256), bcrypt, passlib                                             |
| Инфраструктура   | Docker, Docker Compose, Nginx                                            |
| Тестирование     | pytest, requests                                                         |

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

## Установка и запуск

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

### 4. Тестирование

### Запуск интеграционных тестов

```bash
docker exec -it event-planner-app bash
pytest tests/ 
```

## Пример использования

1. **Регистрация**:  
   Email: `user@example.com`, Пароль: `strongpassword123`
2. **Вход в систему**
3. **Запрос в чате**:  
   `"Я дата-сайентист, люблю LLM и архитектуру нейросетей"`

**Результат**:
```
1. [AI] Новая эра мобильной разработки: запускаем LLM на устройстве — Самир Ахмедов (Surf)
2. [AI] LLM в продакшене: как не сгореть — Анна Иванова (Yandex)
3. [Architecture] Архитектура микросервисов для ML-продуктов — Дмитрий Петров (Ozon)
...
```

---

### Запуск тестов
```bash
cd app
docker compose exec backend pytest tests/ -v
```

## Результаты по тестам
```bash
============================================== test session starts ==============================================
platform linux -- Python 3.10.19, pytest-9.0.2, pluggy-1.6.0
rootdir: /app
plugins: anyio-4.12.0
collected 6 items                                                                                               

tests/test_api.py ......                                                                                  [100%]

=============================================== 6 passed in 2.76s ===============================================
```

---

## Планы по развитию

- **Telegram-бот**: замена Streamlit на Telegram-интерфейс  
- **Векторная БД**: миграция с файловых эмбеддингов на Qdrant или OpenSearch  
- **Обратная связь**: система лайков/дизлайков для персонализации  
- **Реальное время**: автоматическая рекомендация актуальных докладов во время конференций   

