FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
	apt-get install -y curl && \
	rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

COPY alembic/ ./alembic
COPY alembic.ini .

ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=10s --timeout=5s \
	CMD curl -f http://localhost:8001/health || exit 1 

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

