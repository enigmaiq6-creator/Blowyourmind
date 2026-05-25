FROM python:3.13-slim

# 1) Instala ffmpeg + dependencias mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2) Configura Poetry
ENV POETRY_VERSION=1.8.3
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

# 3) Copia archivos de Poetry primero (mejor cache)
COPY pyproject.toml poetry.lock* /app/

# 4) Instala dependencias (sin crear venv)
RUN poetry install --no-root

# 5) Copia el código
COPY app /app/app

# 6) Comando por defecto
CMD ["poetry", "run", "app"]
