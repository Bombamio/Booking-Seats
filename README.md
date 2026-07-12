# BookingSeats

[![CI](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4/actions/workflows/style_check.yml/badge.svg?branch=develop)](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4/actions/workflows/style_check.yml)
[![Deploy](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4/actions/workflows/deploy.yml/badge.svg?branch=develop)](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4/actions/workflows/deploy.yml)

REST API для бронирования мест в кафе: заведения, столы, временные слоты, меню, акции и бронирования с предзаказом блюд. Проект команды **№ 4 потока 68–69** курса **Яндекс Практикум**.

Базовый URL API: **`/api/v1`**.

---

## Оглавление

- [О проекте](#о-проекте)
- [Функциональность](#функциональность)
- [Технологии](#технологии)
- [CI/CD](#cicd)
- [Быстрый старт](#быстрый-старт)
- [DevContainer](#devcontainer)
- [Структура проекта](#структура-проекта)
- [API](#api)
- [Ошибки и валидация](#ошибки-и-валидация)
- [Роли](#роли)
- [OpenAPI](#openapi)
- [Команда](#команда)

---

## О проекте

**BookingSeats** — backend на FastAPI для сети кафе. Сервис предоставляет:

- JWT-авторизацию (email или телефон);
- CRUD для кафе, столов, слотов, блюд, акций и пользователей;
- бронирования с выбором стола/слота и предзаказом блюд;
- загрузку и отдачу медиа (JPG/PNG);
- health-check (PostgreSQL, Redis);
- фоновые задачи Celery (уведомления и напоминания).

При старте приложения создаются учётные записи ADMIN / MANAGER / USER (см. `src/core/initial_data.py`).

---

## Функциональность

| Модуль | Описание |
|--------|----------|
| **Auth** | `POST /auth/login` → JWT Bearer |
| **Пользователи** | Регистрация, профиль `/users/me`, список для staff |
| **Кафе** | CRUD, привязка менеджеров, фильтр `show_active` (ADMIN) |
| **Столы / слоты** | Вложенные в кафе; проверка пересечения слотов |
| **Блюда / акции** | M2M с кафе; кеш меню и акций в Redis |
| **Бронирования** | Дата, гости, стол+слот, предзаказ; проверка конфликтов |
| **Медиа** | Multipart upload, отдача JPEG по ID |
| **Health** | Liveness `/health/`, readiness `/health/ready` |
| **Celery** | Email-уведомления, напоминания о брони |

---

## Технологии

| Категория | Стек |
|-----------|------|
| Язык | Python 3.12 |
| Web | FastAPI, Uvicorn |
| БД | SQLAlchemy 2 (async), asyncpg, PostgreSQL 17 |
| Миграции | Alembic (`alembic/`) |
| Валидация | Pydantic v2, pydantic-settings |
| Auth | PyJWT, Argon2 |
| Кеш | Redis 7 |
| Очереди | Celery, RabbitMQ 3.13, Flower |
| Медиа | Pillow |
| Логи | Loguru, единый формат HTTP/Celery |
| Контейнеры | Docker, Docker Compose |
| Пакеты | [uv](https://docs.astral.sh/uv/) |
| Линтер | [Ruff](https://astral.sh/ruff) |
| CI | GitHub Actions |

---

## CI/CD

Workflows в [`.github/workflows/`](.github/workflows/):

| Workflow | Триггер | Действие |
|----------|---------|----------|
| [`style_check.yml`](.github/workflows/style_check.yml) | push/PR → `develop`, `main`, `master` | `ruff check ./src` |
| [`deploy.yml`](.github/workflows/deploy.yml) | push → `develop`, `main`, `master` | Сборка и push Docker-образа |

Бейджи в шапке README привязаны к ветке **`develop`** — на ней запускаются проверки.

### Production-стек

[`infra/docker-compose.yaml`](infra/docker-compose.yaml):

| Сервис | Назначение |
|--------|------------|
| `app` | FastAPI (порт `8000`) |
| `db` | PostgreSQL 17 |
| `redis` | Кеш |
| `rabbitmq` | Брокер (`5672`, UI `15672`) |
| `celery_worker` | Фоновые задачи |
| `flower` | Мониторинг Celery (`5555`) |

Старт контейнера `app` ([`entrypoint.sh`](entrypoint.sh)): ожидание БД → `alembic upgrade head` → Uvicorn.

```bash
git clone https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4.git
cd 68_69_booking_seats_team_4
cp infra/.env.example infra/.env   # заполнить переменные
cd infra && docker compose up --build -d
curl http://localhost:8000/api/v1/health/ready
```

Основные переменные — в [`infra/.env.example`](infra/.env.example): PostgreSQL, RabbitMQ, SMTP.

---

## Быстрый старт

```bash
cd infra
docker compose up --build -d
```

Корень приложения:

```bash
curl http://localhost:8000/
```

```json
{
  "app": "Приложение BookingSeats команды № 4 потока 68-69 (0.0.1)",
  "description": "Приложение для управления бронированием мест в кафе...",
  "status": "OK"
}
```

---

## DevContainer

Разработка в **VS Code Dev Container** (см. [`.devcontainer/`](.devcontainer/)).

1. Установить Docker и расширение [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
2. Создать `infra/.env` из `infra/.env.example`; `POSTGRES_SERVER=db`.
3. `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**.
4. Запуск:
   - **F5** — отладка (`.vscode/launch.json`);
   - `PYTHONPATH=/workspace .venv/bin/python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`.

DevContainer поднимает PostgreSQL, Redis, RabbitMQ и Flower.

---

## Структура проекта

```
.
├── .devcontainer/              # Dev Container
├── .github/workflows/          # CI (Ruff) и deploy (Docker Hub)
├── alembic/                    # Миграции БД
│   └── versions/
├── infra/
│   ├── docker-compose.yaml     # Production Compose
│   └── .env.example
├── src/
│   ├── api/
│   │   ├── endpoints/          # auth, user, cafe, table, slot, dish, action, booking, media, health
│   │   ├── openapi_examples.py # Примеры успешных ответов в OpenAPI
│   │   ├── error_responses.py  # Группы ошибок для документации
│   │   ├── routers.py          # main_router → /api/v1
│   │   └── validators.py       # Depends: роли, активный пользователь
│   ├── core/                   # settings, db, cache, celery, security, logger, error_handlers
│   ├── crud/                   # Слой доступа к данным
│   ├── models/                 # ORM-модели
│   ├── schemas/                # Pydantic-схемы
│   ├── services/               # Бизнес-логика (BaseService, ensure_ids_exist)
│   ├── tasks/                  # Celery: notifications, reminders
│   ├── media/                  # Хранилище загруженных изображений
│   └── main.py                 # Точка входа FastAPI
├── Dockerfile
├── entrypoint.sh
├── pyproject.toml
├── uv.lock
└── ruff.toml
```

---

## API

Префикс: **`/api/v1`**. Защищённые маршруты: `Authorization: Bearer <token>`.

### Health

| Метод | Путь | Auth |
|-------|------|------|
| GET | `/health/` | — |
| GET | `/health/ready` | — |

### Основные ресурсы

| Группа | Методы | Примечания |
|--------|--------|------------|
| `/auth/login` | POST | JWT |
| `/users/`, `/users/me`, `/users/{id}` | GET, POST, PATCH | Регистрация без auth |
| `/cafes/`, `/cafes/{id}` | GET, POST, PATCH | `show_active` для ADMIN |
| `/cafes/{id}/tables`, `.../tables/{table_id}` | GET, POST, PATCH | |
| `/cafes/{id}/time_slots/`, `.../time_slots/{slot_id}` | GET, POST, PATCH | Без пересечений |
| `/dishes/`, `/dishes/{id}` | GET, POST, PATCH | Query: `cafe_id`, `show_active` |
| `/actions/`, `/actions/{id}` | GET, POST, PATCH | |
| `/booking`, `/booking/{id}` | GET, POST, PATCH | Предзаказ блюд |
| `/media/`, `/media/{id}` | POST, GET | Upload: Admin/Manager |

Полные схемы, примеры ответов и коды ошибок — в [Swagger UI](http://localhost:8000/docs).

---

## Ошибки и валидация

Все ошибки API возвращаются в формате **`CustomError`**:

```json
{
  "code": 404,
  "message": "Данные не найдены"
}
```

| Код | Когда |
|-----|-------|
| **400** | Несуществующий parent/related ID (`cafe_id` в path, `managers_id`, `cafes_id`, `table_id` в брони и т.д.) |
| **401** | Нет или невалидный JWT |
| **403** | Недостаточно прав (в т.ч. смена своей роли) |
| **404** | Целевой ресурс по ID не найден; стол/слот в брони из другого кафе |
| **422** | Валидация тела запроса, конфликт брони, дубликат кафе, медиа |

Код **409** в API не используется.

---

## Роли

| Роль | Возможности |
|------|-------------|
| **USER** | Свои брони; просмотр активных кафе, меню, акций |
| **MANAGER** | Управление своим кафе; брони кафе; список пользователей |
| **ADMIN** | Полный доступ; `show_active=true/false` на списках; смена **чужой** роли |

Смена роли (эскалация и понижение) **своей** учётной записи запрещена для всех ролей → **403**. Менять роль другого пользователя может только **ADMIN**.

---

## OpenAPI

| Ресурс | URL |
|--------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

---

## Команда

[Репозиторий](https://github.com/Yandex-Practicum-Students/68_69_booking_seats_team_4) — команда **4**, поток **68–69**, Яндекс Практикум.

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
