#!/bin/bash
# $APP_PORT comes from docker-compose backend environment
# $VIRTUAL_ENV is uploaded by dockerfile into docker envs
set -e
source $VIRTUAL_ENV/bin/activate
cd /backend/api


if [ -z "$GUNICORN_WORKERS" ]; then
    CPU_CORES=$(nproc 2>/dev/null || echo 1)  # Fallback to 1 if nproc fails
    GUNICORN_WORKERS=$((2 * CPU_CORES + 1))
fi

# Set log level based on environment (default to 'info' for production, 'debug' for development)
LOG_LEVEL="${LOG_LEVEL:-info}"

# Start Gunicorn with Uvicorn workers
# Notes:
# - Uses uvicorn.workers.UvicornWorker for async FastAPI compatibility
# - Binds to 0.0.0.0 to accept external connections
# - Alternative worker classes (e.g., gevent) can be used by setting --worker-class
exec gunicorn app:app \
    --workers "$GUNICORN_WORKERS" \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:"$APP_PORT"