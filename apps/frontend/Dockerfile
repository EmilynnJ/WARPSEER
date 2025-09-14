# Frontend Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
COPY apps/frontend/package.json ./apps/frontend/package.json
RUN corepack enable && corepack prepare pnpm@9.0.0 --activate
RUN pnpm install -w --ignore-scripts
COPY apps/frontend /app/apps/frontend
RUN pnpm --filter @soulseer/frontend build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/apps/frontend/.svelte-kit /app/.svelte-kit
EXPOSE 4173
CMD ["node", ".svelte-kit/output/server/index.js"]