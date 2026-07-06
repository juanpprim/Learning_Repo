# Multi-stage build for the React frontend (Tier C).
# Stage 1 compiles the Vite bundle; stage 2 is just nginx serving static files.

# ---------- stage 1: build ----------
FROM node:22-alpine AS builder

WORKDIR /app
# package files first so `npm ci` is cached across code-only changes.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# VITE_API_URL is baked into the bundle at BUILD time (Vite env semantics).
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ---------- stage 2: serve ----------
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
