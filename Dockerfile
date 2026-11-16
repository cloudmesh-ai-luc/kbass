FROM python:3.14-slim

WORKDIR /app

COPY requirements.lock ./
COPY pyproject.toml ./

RUN pip install --no-cache-dir -r requirements.lock

COPY src/ ./src/

RUN pip install --no-cache-dir --no-deps .

EXPOSE 8000

COPY gunicorn.conf.py docker-entrypoint.sh ./

RUN chmod +x /app/docker-entrypoint.sh

CMD ["/app/docker-entrypoint.sh"]
