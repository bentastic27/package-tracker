FROM python:3.14-slim AS parent
ENV PYTHONUNBUFFERED=true
WORKDIR /app

COPY app.py .
COPY templates .
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN groupadd --gid 1000 appuser && \
  useradd --uid 1000 --gid 1000 -M appuser -s /sbin/nologin -d /app && \
  chown 1000.1000 /app


EXPOSE 8000

ENTRYPOINT ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
