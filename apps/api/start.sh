#!/bin/sh
set -e

# Run database migrations
cd "$(dirname "$0")" || exit 1
alembic upgrade head

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000
