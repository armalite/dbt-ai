FROM python:3.10-slim-buster

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev

COPY . .
