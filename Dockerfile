FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# Deps runtime
COPY requirements.txt .
RUN --mount=type=cache,id=s/d98d625d-e34c-4ab8-a5d5-0b58405815f8-/root/.cache/pip,target=/root/.cache/pip \
  python -m pip install --upgrade pip && pip install -r requirements.txt

# Code
COPY app ./app

# Migrations
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

# Dev
FROM base AS dev
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--reload"]

# Prod
FROM base AS prod
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","4"]
