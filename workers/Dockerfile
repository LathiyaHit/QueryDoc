FROM python:3.11-slim AS runner
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1
CMD ["celery", "-A", "main.celery_app", "worker", "--loglevel=info", "--queues=memory,analytics"]
