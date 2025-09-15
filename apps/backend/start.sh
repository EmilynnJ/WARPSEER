#!/usr/bin/env bash
# Start script for production

# Use PORT from environment or default to 8000
PORT=${PORT:-8000}

echo "Starting FastAPI server on port $PORT..."
uvicorn src.soulseer.main:app --host 0.0.0.0 --port $PORT