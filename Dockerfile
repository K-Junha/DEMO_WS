# Stage 1: Frontend build
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN npm install -g pnpm@10 && pnpm install --frozen-lockfile
COPY frontend/ .
RUN pnpm build

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

COPY backend/ ./backend/
COPY config/ ./config/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

RUN pip install --no-cache-dir -e ./backend

ENV DEMO_CONFIG_PATH=/app/config/demo_data.yaml

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
