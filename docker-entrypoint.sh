#!/bin/sh
set -eu

export PROMETHEUS_MULTIPROC_DIR=/tmp/cloudops-prometheus

mkdir -p "$PROMETHEUS_MULTIPROC_DIR"

# Remove metrics files left by previous application runs.
find "$PROMETHEUS_MULTIPROC_DIR" -maxdepth 1 -type f -name '*.db' -delete

exec gunicorn \
    --config /app/gunicorn.conf.py \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --access-logfile - \
    --error-logfile - \
    kbass_monitoring.app:app
