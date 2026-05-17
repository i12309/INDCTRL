FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_STATIC_ROOT=/app/staticfiles

WORKDIR /app

# common ставится как обычный Python-пакет, чтобы Django и FastAPI использовали
# один источник общих констант и утилит.
COPY common ./common
COPY services/control_web/requirements.txt ./services/control_web/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install ./common \
    && python -m pip install -r ./services/control_web/requirements.txt

COPY services/control_web ./services/control_web

RUN mkdir -p /app/staticfiles \
    && adduser --system --group appuser \
    && chown -R appuser:appuser /app/staticfiles
USER appuser

WORKDIR /app/services/control_web

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
