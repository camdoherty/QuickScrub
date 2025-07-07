# Stage 1: Build the frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the backend
FROM python:3.10-slim AS backend-builder
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY pyproject.toml ./
RUN pip install --no-cache-dir --prefix="/install" .
COPY QuickScrub ./QuickScrub

# Stage 3: Final image
FROM python:3.10-slim
WORKDIR /app
COPY --from=backend-builder /install /usr/local
COPY --from=backend-builder /app/QuickScrub ./QuickScrub
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["uvicorn", "QuickScrub.main:app", "--host", "0.0.0.0", "--port", "8000"]
