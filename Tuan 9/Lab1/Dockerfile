# ─── stage 1: builder ───
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml ./
COPY src ./src
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN pip install --no-cache-dir ".[postgres,server]"

# ─── stage 2: runtime ───
FROM python:3.12-slim
WORKDIR /app
RUN groupadd -r app && useradd -r -g app -d /app app
COPY --from=builder --chown=app:app /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1
USER app
EXPOSE 5000

# Tao bang (neu chua co) roi chay gunicorn
CMD ["sh", "-c", "flask --app product_api.factory:create_app init-db && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - 'product_api.factory:create_app()'"]
