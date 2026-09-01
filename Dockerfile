# Backend image — FastAPI + Tesseract OCR
FROM python:3.11-slim

# System deps: Tesseract binary for OCR, gcc for psycopg2 wheels if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY backend ./backend

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
