# BookingSeats

[![CI/CD](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4/actions/workflows/style_check.yml/badge.svg)](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4/actions/workflows/style_check.yml)

REST API для бронирования мест в кафе: управление заведениями, столами, временными слотами, меню, акциями и бронированиями с предзаказом блюд. Проект создан в рамках курса **Яндекс Практикум**  и предназначен для развёртывания на сервере в Docker-контейнерах с проверкой качества кода через GitHub Actions.

---

## Оглавление

- [О проекте](#о-проекте)
- [Функциональность](#функциональность)
- [Технологии](#технологии)
- [CI/CD и развёртывание](#cicd-и-развёртывание)
- [OpenAPI-документация](#openapi-документация)
- [Быстрый старт (production)](#быстрый-старт-production)
- [Работа с проектом в DevContainer](#работа-с-проектом-в-devcontainer)
- [Структура проекта](#структура-проекта)
- [API: обзор эндпоинтов](#api-обзор-эндпоинтов)
- [Примеры запросов и ответов](#примеры-запросов-и-ответов)
- [Роли пользователей](#роли-пользователей)
- [Команда](#команда)

---

## О проекте

**BookingSeats** — backend-сервис на FastAPI для системы бронирования столиков в сети кафе. Приложение предоставляет API для:

- регистрации и авторизации пользователей (JWT);
- управления кафе, столами и временными слотами;
- работы с меню (блюда) и акциями;
- создания и изменения бронирований с предзаказом блюд;
- загрузки и отдачи медиафайлов (фото кафе, блюд, акций);
- фоновых задач (уведомления и напоминания через Celery).

Базовый URL API: `/api/v1`.

---

## Функциональность

| Модуль | Описание |
|--------|----------|
| **Аутентификация** | Вход по email или телефону, выдача JWT-токена |
| **Пользователи** | CRUD, профиль `/users/me`, роли ADMIN / MANAGER / USER |
| **Кафе** | Список, создание и редактирование заведений |
| **Столы** | Столики внутри кафе с указанием количества мест |
| **Временные слоты** | Интервалы времени для бронирования |
| **Блюда** | Меню с привязкой к одному или нескольким кафе |
| **Акции** | Промо-акции с привязкой к кафе |
| **Бронирования** | Бронь столов на дату, предзаказ блюд, статусы |
| **Медиа** | Загрузка JPG/PNG (до 5 МБ), отдача по ID |
| **Health** | Liveness и readiness (PostgreSQL, Redis) |
| **Celery** | Асинхронные уведомления и напоминания о брони |

Кеширование меню и акций выполняется через **Redis**. Очередь задач — **RabbitMQ**, мониторинг воркеров — **Flower**.

---

## Технологии

| Категория | Стек |
|-----------|------|
| Язык | Python 3.12 |
| Web-фреймворк | FastAPI, Uvicorn, Starlette |
| ORM / БД | SQLAlchemy 2 (async), asyncpg, PostgreSQL 17 |
| Миграции | Alembic |
| Валидация | Pydantic v2, pydantic-settings |
| Аутентификация | PyJWT, Argon2 |
| Кеш | Redis 7 |
| Очереди | Celery, RabbitMQ 3.13 |
| Медиа | Pillow |
| Логирование | Loguru |
| Контейнеризация | Docker, Docker Compose |
| Менеджер пакетов | [uv](https://docs.astral.sh/uv/) |
| Линтер | [Ruff](https://astral.sh/ruff) |
| Pre-commit | pre-commit |
| CI | GitHub Actions |

---

## CI/CD и развёртывание

### GitHub Actions

При каждом push и pull request в ветки `develop`, `main`, `master` запускается workflow [`style_check.yml`](.github/workflows/style_check.yml):

- установка Python 3.12;
- проверка стиля кода командой `ruff check ./src`.

### Развёртывание на сервере

Production-окружение описано в [`infra/docker-compose.yaml`](infra/docker-compose.yaml). Стек включает:

- **app** — FastAPI-приложение (порт `8000`);
- **db** — PostgreSQL 17;
- **redis** — кеш;
- **rabbitmq** — брокер сообщений (порты `5672`, `15672` — management UI);
- **celery_worker** — обработчик фоновых задач;
- **flower** — мониторинг Celery (порт `5555`).

При старте контейнера `app` скрипт [`entrypoint.sh`](entrypoint.sh):

1. ожидает готовности PostgreSQL;
2. выполняет `alembic upgrade head`;
3. запускает Uvicorn на `0.0.0.0:8000`.

**Шаги развёртывания на сервере:**

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4.git
cd 68_69_booking_seats_team_4

# 2. Настроить переменные окружения
cp infra/.env.example infra/.env
# заполнить infra/.env (см. раздел «Переменные окружения»)

# 3. Запустить стек
cd infra
docker compose up --build -d

# 4. Проверить health
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/ready
```

### Переменные окружения

Файл [`infra/.env.example`](infra/.env.example):

| Переменная | Описание |
|------------|----------|
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_DB` | Имя базы данных |
| `POSTGRES_SERVER` | Хост БД (`db` внутри Docker Compose) |
| `POSTGRES_PORT` | Порт PostgreSQL (по умолчанию `5432`) |
| `RABBITMQ_USER` / `RABBITMQ_PASSWORD` | Учётные данные RabbitMQ |
| `RABBITMQ_HOST` / `RABBITMQ_PORT` | Хост и порт RabbitMQ |
| `EMAIL_ADDRESS` / `EMAIL_PASSWORD` | SMTP для email-уведомлений |

---

## OpenAPI-документация

После запуска приложения интерактивная документация доступна по адресам:

| Ресурс | URL (локально) |
|--------|----------------|
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) |
| **OpenAPI JSON** | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) |

На production-сервере замените `localhost:8000` на актуальный домен или IP.

---

## Быстрый старт (production)

```bash
cd infra
docker compose up --build -d
```

API будет доступен на порту **8000**. Корневая страница:

```bash
curl http://localhost:8000/
```

Пример ответа:

```json
{
  "app": "Базовый набор FastAPI+SQLAlchemy+Postgres (0.0.1)",
  "description": "Основа для приложения",
  "status": "OK"
}
```

---

## Работа с проектом в DevContainer

Разработка ведётся в **Dev Container** VS Code. Ниже — инструкция из предыдущей версии README (актуальна для локальной разработки).

### Перед началом работы

1. Убедитесь, что установлены:
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - расширение [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) для VS Code

2. В папке `infra` на основе `.env.example` создайте `.env` и заполните:
   - `POSTGRES_USER` — имя пользователя;
   - `POSTGRES_PASSWORD` — пароль;
   - `POSTGRES_DB` — название базы;
   - `POSTGRES_SERVER` — хост БД (см. ниже);
   - `POSTGRES_PORT` — порт (по умолчанию `5432`).

3. В `.devcontainer/docker-compose.yml` задайте:
   - `name` в корневом блоке;
   - `PROJECT_NAME` в блоке `remoteEnv`.

4. **Настройка `docker-compose`**

   В `.devcontainer/docker-compose.yml` и `infra/docker-compose.yaml` сервис PostgreSQL по умолчанию называется `db`. Это имя укажите в `POSTGRES_SERVER` файла `infra/.env`, чтобы из DevContainer можно было подключаться к базе.

5. **Изменение версии Python** (не рекомендуется)

   Версию Python задают в двух местах — они должны совпадать:
   - `.devcontainer/devcontainer.json` → `PYTHON_VERSION`;
   - `Dockerfile` → строка `FROM` (версия после `:`).

### Создание DevContainer

1. `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**
2. Дождитесь сборки образа (uv, venv, зависимости).

> Линтер VS Code может временно не видеть установленные пакеты. Подождите или перезапустите VS Code, не выходя из DevContainer.

### Подготовка Git и SSH внутри контейнера

```bash
git config --global user.name "Ваше имя"
git config --global user.email "your@email.com"
```

SSH-ключи:

- **Вариант 1:** скопировать ключи с хоста в `/home/vscode/.ssh` (права: `-rw-------` для private, `-rw-r--r--` для public);
- **Вариант 2:** создать новую пару ключей в контейнере и добавить public key в GitHub → Settings → SSH and GPG keys.

### Запуск приложения

| Способ | Действие |
|--------|----------|
| **Отладка** | `F5` или Run and Debug → порт `8000` (см. `.vscode/launch.json`) |
| **Локально в терминале** | `cd src && python main.py` → порт `8000` |
| **Production-стек на хосте** | Выйти из DevContainer → `cd infra && docker compose up --build` |

DevContainer поднимает дополнительно Redis, RabbitMQ, Flower и PostgreSQL (см. [`.devcontainer/docker-compose.yml`](.devcontainer/docker-compose.yml)).

---

## Структура проекта

```
.
├── .devcontainer/              # Dev Container: Dockerfile, docker-compose, devcontainer.json
├── .github/
│   └── workflows/
│       └── style_check.yml     # CI: проверка Ruff
├── .vscode/
│   └── launch.json             # Конфигурация отладки
├── alembic/                    # Миграции БД (Alembic)
│   └── versions/
├── infra/
│   ├── docker-compose.yaml     # Production Docker Compose
│   └── .env.example            # Шаблон переменных окружения
├── scripts/
│   ├── test_endpoints.py       # Smoke-тесты API
│   └── test_openapi_compliance.py
├── src/
│   ├── api/
│   │   ├── endpoints/          # Роуты: auth, booking, cafe, dish, ...
│   │   ├── routers.py          # Сборка main_router (/api/v1)
│   │   ├── validators.py       # Depends: роли, активный пользователь
│   │   └── error_responses.py  # Общие схемы ошибок OpenAPI
│   ├── core/                   # settings, db, cache, celery, security, logger
│   ├── crud/                   # CRUD-слой SQLAlchemy
│   ├── models/                 # ORM-модели
│   ├── schemas/                # Pydantic-схемы запросов/ответов
│   ├── services/               # Бизнес-логика
│   ├── tasks/                  # Celery: notifications, reminders
│   ├── media/                  # Загруженные изображения
│   ├── logs/                   # Лог-файлы приложения
│   └── main.py                 # Точка входа FastAPI
├── Dockerfile                  # Production-образ приложения
├── entrypoint.sh               # Старт: migrate + uvicorn
├── pyproject.toml              # Зависимости (uv)
├── uv.lock
├── ruff.toml
├── .pre-commit-config.yaml
├── README.md                   # Эта документация
└── README.old.md               # Предыдущая версия README
```

---

## API: обзор эндпоинтов

Базовый префикс: **`/api/v1`**. Защищённые маршруты требуют заголовок `Authorization: Bearer <token>`.

### Health

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/health/` | — | Liveness |
| GET | `/health/ready` | — | Readiness (БД + Redis) |

### Аутентификация

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| POST | `/auth/login` | — | Получение JWT-токена |

### Пользователи

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/users/` | Admin/Manager | Список пользователей |
| POST | `/users/` | — | Регистрация |
| GET | `/users/me` | User+ | Текущий пользователь |
| PUT | `/users/me` | User+ | Обновление профиля |
| GET | `/users/{user_id}` | Admin/Manager | Пользователь по ID |
| PUT | `/users/{user_id}` | Admin/Manager | Обновление пользователя |

### Кафе

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/cafes/` | User+ | Список кафе |
| POST | `/cafes/` | Admin/Manager | Создание кафе |
| GET | `/cafes/{cafe_id}` | User+ | Кафе по ID |
| PATCH | `/cafes/{cafe_id}` | Admin/Manager | Обновление кафе |

### Столы

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/cafes/{cafe_id}/tables` | User+ | Список столов |
| POST | `/cafes/{cafe_id}/tables` | Admin/Manager | Создание стола |
| GET | `/cafes/{cafe_id}/tables/{table_id}` | User+ | Стол по ID |
| PATCH | `/cafes/{cafe_id}/tables/{table_id}` | Admin/Manager | Обновление стола |

### Временные слоты

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/cafes/{cafe_id}/time_slots/` | User+ | Список слотов |
| POST | `/cafes/{cafe_id}/time_slots/` | Admin/Manager | Создание слота |
| GET | `/cafes/{cafe_id}/time_slots/{slot_id}` | User+ | Слот по ID |
| PATCH | `/cafes/{cafe_id}/time_slots/{slot_id}` | Admin/Manager | Обновление слота |

### Блюда

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/dishes/` | User+ | Список блюд (`cafe_id`, `show_active`) |
| POST | `/dishes/` | Admin/Manager | Создание блюда |
| GET | `/dishes/{dish_id}` | User+ | Блюдо по ID |
| PATCH | `/dishes/{dish_id}` | Admin/Manager | Обновление блюда |

### Акции

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/actions/` | User+ | Список акций |
| POST | `/actions/` | Admin/Manager | Создание акции |
| GET | `/actions/{action_id}` | User+ | Акция по ID |
| PATCH | `/actions/{action_id}` | Admin/Manager | Обновление акции |

### Бронирования

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/booking` | User+ | Список бронирований |
| POST | `/booking` | User+ | Создание бронирования |
| GET | `/booking/{booking_id}` | User+ | Бронирование по ID |
| PATCH | `/booking/{booking_id}` | User+ | Обновление бронирования |

### Медиа

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| POST | `/media/` | Admin/Manager | Загрузка изображения (multipart) |
| GET | `/media/{media_id}` | — | Получение изображения (binary) |

---

## Примеры запросов и ответов

Успешное **создание** ресурса возвращает `201 Created`. Запросы без создания сущности (авторизация, health-check) — `200 OK`.

### Регистрация пользователя

**Запрос:**

```http
POST /api/v1/users/
Content-Type: application/json

{
  "username": "ivan",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "password": "securePass1"
}
```

**Ответ `201 Created`:**

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "ivan",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "role": "USER",
  "is_active": true
}
```

### Авторизация

**Запрос:**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "login": "ivan@example.com",
  "password": "securePass1"
}
```

**Ответ `200 OK`:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

### Создание кафе

**Запрос:**

```http
POST /api/v1/cafes/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Coffee House",
  "address": "ул. Пушкина, 10",
  "phone": "+74951234567",
  "description": "Уютное кафе в центре"
}
```

**Ответ `201 Created`:**

```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "name": "Coffee House",
  "address": "ул. Пушкина, 10",
  "phone": "+74951234567",
  "description": "Уютное кафе в центре",
  "is_active": true,
  "created_at": "2026-07-08T10:00:00",
  "updated_at": "2026-07-08T10:00:00"
}
```

### Создание бронирования

**Запрос:**

```http
POST /api/v1/booking
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "cafe_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "booking_date": "2026-07-15",
  "guest_number": 2,
  "note": "Стол у окна",
  "tables_slots": [
    {
      "table_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "slot_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    }
  ],
  "preordered_dishes": [
    {
      "dish_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "quantity": 1
    }
  ]
}
```

**Ответ `201 Created`:**

```json
{
  "id": "d4e5f6a7-b8c9-0123-def0-234567890123",
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "ivan"
  },
  "cafe": {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "name": "Coffee House"
  },
  "tables_slots": [
    {
      "table": { "id": "...", "seat_number": 4 },
      "slot": { "id": "...", "start_time": "12:00:00", "end_time": "13:00:00" }
    }
  ],
  "guest_number": 2,
  "note": "Стол у окна",
  "status": "BOOKING",
  "booking_date": "2026-07-15",
  "is_active": true
}
```

### Health check

**Запрос:**

```http
GET /api/v1/health/ready
```

**Ответ `200 OK`:**

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

### Ошибка авторизации

**Ответ `401 Unauthorized`:**

```json
{
  "detail": "Could not validate credentials"
}
```

Полные схемы запросов, коды ошибок и варианты ответов — в [Swagger UI](http://localhost:8000/docs) и [OpenAPI JSON](http://localhost:8000/openapi.json).

---

## Роли пользователей

| Роль | Возможности |
|------|-------------|
| **USER** | Свои бронирования, просмотр активных кафе/столов/меню/акций |
| **MANAGER** | Управление сущностями своего кафе, все бронирования кафе |
| **ADMIN** | Полный доступ ко всем сущностям системы |

---

## Команда

Проект разработан командой **4** потока **68–69** курса Яндекс Практикум
([репозиторий](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4)).

| Участник |
|----------|
| Aleksandr Shaluho |
| Andrey Tikhonchuk |
| Arthur Fissunov |
| Ekaterina Khomik |
| Vitaly Netesov |
| Yausei Ilya |
| Александров Роман |
| Яна Кузьмичева |

---
