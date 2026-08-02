#!/bin/sh
set -e

# Run database migrations
cd "$(dirname "$0")" || exit 1
alembic upgrade head

# Start the application (Render injects $PORT; default to 8000 for local/dev)
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
