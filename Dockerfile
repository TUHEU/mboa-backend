FROM cgr.dev/chainguard/python:latest-dev AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN python -m venv /venv && /venv/bin/pip install --disable-pip-version-check -r requirements.txt

FROM cgr.dev/chainguard/python:latest AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /venv /venv
COPY app ./app

EXPOSE 8000

ENTRYPOINT ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]