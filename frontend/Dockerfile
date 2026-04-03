# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# VITE_BACKEND_URL is baked into the JS bundle at build time.
# Pass it as a build arg: docker build --build-arg VITE_BACKEND_URL=https://api.example.com
ARG VITE_BACKEND_URL=http://localhost:8000
ENV VITE_BACKEND_URL=${VITE_BACKEND_URL}

RUN npm run build

# ── Stage 2: serve ────────────────────────────────────────────────────────────
FROM nginx:stable-alpine

# Remove default nginx page
RUN rm /etc/nginx/conf.d/default.conf

# Custom nginx config: serve SPA, proxy /api/v1 to backend
COPY nginx.conf /etc/nginx/conf.d/app.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
