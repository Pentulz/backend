FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# --- Deps (cache-friendly)
COPY pyproject.toml poetry.lock* ./
RUN python -m pip install --upgrade pip \
 && pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --only main --no-interaction --no-ansi --no-root

# --- Code
COPY app ./app

# --- Dev (reload, deps dev)
FROM base AS dev
RUN poetry install --with dev --no-interaction --no-ansi
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--reload"]

# --- Prod
FROM base AS prod
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","4"]