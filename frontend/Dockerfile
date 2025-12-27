# Multi-stage Dockerfile for Next.js 16 (Node 20)
# 1) deps: install dependencies with npm ci
# 2) builder: copy sources and build
# 3) runner: run "next start" with built assets

FROM node:20-bookworm-slim AS deps
WORKDIR /app
ENV NODE_ENV=production
# Prefer npm as package-lock.json exists
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

FROM node:20-bookworm-slim AS builder
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Build the Next.js app
RUN npm run build

FROM node:20-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# Copy only what we need to run the app
COPY --from=builder /app/package.json ./package.json
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
# If you use custom server files or next.config.ts during runtime, copy them too
# COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000
CMD ["npm", "run", "start"]
