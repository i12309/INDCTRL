FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Сначала устанавливаем зависимости: так Docker сможет переиспользовать слой,
# если меняется только код сервиса.
COPY common ./common
COPY services/auth_service/requirements.txt ./services/auth_service/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install ./common \
    && python -m pip install -r ./services/auth_service/requirements.txt

COPY services/auth_service ./services/auth_service

# Сервис не должен работать от root-пользователя в production-контейнере.
RUN adduser --system --group appuser
USER appuser

WORKDIR /app/services/auth_service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
