# Pentulz Backend - Deployment Guide

## 1. Overview

This project uses **GitHub Actions** and **GitHub Container Registry (GHCR)** for deployment.  
Images are built automatically and pushed to `ghcr.io/pentulz/pentulz-backend`.

## 2. Workflows

- **CI (all branches/PRs)**  
  Runs tests and linting on every push and pull request.  
  Ensures the code is correct before merging.

- **CD Production (tags)**  
  When a Git tag is created (e.g. `v1.0.0`), a production image is pushed:
  - `ghcr.io/pentulz/pentulz-backend:v1.0.0`
  - `ghcr.io/pentulz/pentulz-backend:latest`

## 3. How to Release

1. Make sure all tests/lint checks pass on your branch.
2. Merge into `main`.
3. Create a Git tag:

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## 4. Run with Docker Compose

This repository provides a `docker-compose.yml` with two profiles:

- **Development (`dev`)**

  ```bash
  docker compose --profile dev up --build
  ```

  - Mounts local code (`.:/app`)
  - Enables `--reload` for fast development

- **Production (`prod`)**

  ```bash
  docker compose --profile prod up -d
  ```

  - Runs the published image from GHCR
  - Use environment variables from `.env`

## 5. Environment Variables

Create a `.env` file in the project root:

```env
APP_APP_NAME=Pentulz Backend
APP_ENVIRONMENT=production
APP_DEBUG=false
```

These values are loaded automatically by the app.

## 6. OpenAPI Documentation

Once the container is running:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## 7. Deploy the Production Image with Docker Compose

If you want to deploy the production image using Docker Compose, you can use the following configuration:

```yml
services:
  api:
    image: ghcr.io/pentulz/pentulz-backend:latest
    env_file:
      - .env
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Start the service with:

```bash
docker compose --profile prod up -d
```

> For reproducible deployments, replace :latest with a specific version tag (e.g. :v1.0.1).
