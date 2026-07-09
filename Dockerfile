FROM python:3.12-slim

SHELL ["/bin/sh", "-exc"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /usr/local/bin/uv

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g ${GROUP_ID} devuser && \
    useradd -u ${USER_ID} -g devuser -m -s /bin/bash devuser

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

RUN chown -R devuser:devuser /app

USER devuser

ENV UV_PYTHON=python3.12 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

RUN uv sync --no-dev --frozen

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH=/app

# Копируем проект
COPY --chown=devuser:devuser src ./src
COPY --chown=devuser:devuser alembic ./alembic
COPY --chown=devuser:devuser alembic.ini .
COPY --chown=devuser:devuser entrypoint.sh .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
