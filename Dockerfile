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
COPY apps/backend/requirements.docker.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY apps/backend ./backend

# Copy frontend build
COPY --from=frontend-builder /app/frontend/build ./frontend/build
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci --production
WORKDIR /app

# Create nginx config
RUN echo 'server { \
    listen 8080; \
    location /api { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
    location / { \
        proxy_pass http://127.0.0.1:3000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/sites-available/default

# Create supervisor config  
RUN printf '[supervisord]\n\
nodaemon=true\n\
\n\
[program:backend]\n\
command=python -m uvicorn main:app --host 127.0.0.1 --port 8000\n\
directory=/app/backend\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:frontend]\n\
command=node build\n\
environment=PORT="3000",HOST="127.0.0.1"\n\
directory=/app/frontend\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:nginx]\n\
command=nginx -g "daemon off;"\n\
autostart=true\n\
autorestart=true\n' > /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8080
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
