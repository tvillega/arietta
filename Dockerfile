FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY README.md .

COPY src/ ./src/

RUN pip install --no-cache-dir .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "arietta.app:app"]