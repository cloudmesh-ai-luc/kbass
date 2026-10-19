FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "kbass_monitoring.app"]
