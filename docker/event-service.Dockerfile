FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Общий пакет ставится отдельным шагом, чтобы оба FastAPI-сервиса использовали
# одинаковые настройки, ответы и служебные функции.
COPY common ./common
COPY services/event_service/requirements.txt ./services/event_service/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install ./common \
    && python -m pip install -r ./services/event_service/requirements.txt

COPY services/event_service ./services/event_service

RUN adduser --system --group appuser
USER appuser

WORKDIR /app/services/event_service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
