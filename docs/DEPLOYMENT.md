# Deployment Guide

## 1. Overview

This project uses **GitHub Actions** and **GitHub Container Registry (GHCR)** for deployment.  
Images are built automatically and pushed to `ghcr.io/pentulz/pentulz-backend`.

---

## 2. Workflows

- **CI (all branches/PRs)**  
  Runs tests and linting on every push and pull request.  
  Ensures the code is correct before merging.

- **CD Production (tags)**  
  When a Git tag is created (e.g. `v1.0.0`), a production image is pushed:
  - `ghcr.io/pentulz/pentulz-backend:v1.0.0`
  - `ghcr.io/pentulz/pentulz-backend:latest`

---

## 3. How to Release

1. Make sure all tests/lint checks pass on your branch.
2. Merge into `main`.
3. Create a Git tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
