FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
	apt-get install -y gcc curl && \
	rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /app ./app

COPY alembic/ ./alembic
COPY alembic.ini .

ENV PYTHONUNBUFFERED=1

EXPOSE 8002

HEALTHCHECK --interval=10s --timeout=5s \
	CMD curl -f http://localhost:${APP_PORT}/health || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT}"]
