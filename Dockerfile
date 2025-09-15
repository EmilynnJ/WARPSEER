# Multi-stage build for Koyeb
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY apps/frontend/package*.json ./
RUN npm ci
COPY apps/frontend ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install Node.js, Nginx, and supervisor
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY apps/backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY apps/backend ./backend

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build ./frontend/build
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci --production
WORKDIR /app

# Nginx config
RUN echo 'server { \
    listen 8080; \
    location /api { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
    } \
    location / { \
        proxy_pass http://127.0.0.1:3000; \
    } \
}' > /etc/nginx/sites-available/default

# Supervisor config
RUN echo '[supervisord] \
nodaemon=true \
[program:backend] \
command=python -m uvicorn main:app --host 127.0.0.1 --port 8000 \
directory=/app/backend \
[program:frontend] \
command=node build \
environment=PORT="3000" \
directory=/app/frontend \
[program:nginx] \
command=nginx -g "daemon off;"' > /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
