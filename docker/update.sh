#!/bin/bash
# Update AI Commerce OS on a production server

set -e

cd "$(dirname "$0")"

git pull

docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

docker image prune -f

echo "Update complete. Check logs with: docker-compose -f docker-compose.prod.yml logs -f"
