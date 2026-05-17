FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_STATIC_ROOT=/app/staticfiles

WORKDIR /app

COPY service/requirements.txt ./service/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r ./service/requirements.txt

COPY service ./service

RUN mkdir -p /app/staticfiles \
    && adduser --system --group appuser \
    && chown -R appuser:appuser /app/staticfiles
USER appuser

WORKDIR /app/service

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
