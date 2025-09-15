#!/usr/bin/env bash
# Build script for Render Free Tier

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
# Only run if DATABASE_URL is set
if [ ! -z "$DATABASE_URL" ]; then
    alembic upgrade head
fi

echo "Build complete!"