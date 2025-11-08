#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Stopping KubenAI stack from $DIR"
docker compose -f "$DIR/docker-compose.yml" down
echo "Stopped."
