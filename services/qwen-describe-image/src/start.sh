#!/bin/bash
set -euo pipefail

echo "RunPod Serverless worker starting..."

# Optional small delay for cold start sequencing
if [ -n "${STARTUP_DELAY:-}" ]; then
  echo "Delaying startup for ${STARTUP_DELAY}s"
  sleep "$STARTUP_DELAY"
fi

exec python -u rp_handler.py
