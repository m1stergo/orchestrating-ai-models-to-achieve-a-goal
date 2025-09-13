#!/usr/bin/env bash
set -euo pipefail
echo "RunPod Serverless worker starting..."
if [ -n "${STARTUP_DELAY:-}" ]; then sleep "$STARTUP_DELAY"; fi

# importante: asegurate que /app esté en PYTHONPATH (lo ponemos en el Dockerfile)
exec python -m app.rp_handler
