# 05. Environment and Secrets

Guidelines for configuration and external dependencies.

## 1. Secrets Management
- Use a `.env` file for API keys (e.g., `GOOGLE_API_KEY`).
- Load env variables at the very beginning of the entry point.
- NEVER commit `.env` files to version control.

## 2. Infrastructure
- Prefer using the `Makefile` for common tasks (build, run, clean).
- Ensure new tools are added to `pyproject.toml` via Poetry.

## 3. Docker
- Maintain the `Dockerfile` and `docker-compose.yml` updated if global dependencies change (e.g., FFmpeg version).
