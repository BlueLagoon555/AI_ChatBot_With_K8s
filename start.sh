#!/usr/bin/env bash
set -euo pipefail

# Start the whole stack (build and run in background)
DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if .env file exists
if [ ! -f "$DIR/.env" ]; then
	echo "Error: .env file not found in $DIR"
	echo "Please create .env file with required configuration."
	echo "You can copy from .env.example and update the values."
	exit 1
fi

echo "Starting KubenAI stack from $DIR"
docker compose -f "$DIR/docker-compose.yml" up -d --build
echo "Started. Use 'docker compose ps' to see running services."
echo "Access UI at http://localhost:8501"
