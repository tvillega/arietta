FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .

COPY src/ ./src/

RUN pip install --no-cache-dir .

ENV PORT=5050

CMD exec gunicorn --bind 0.0.0.0:${PORT} arietta.app:app
