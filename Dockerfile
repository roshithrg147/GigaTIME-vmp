FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# System deps: OpenSlide for WSI reading, build tools for SimpleITK
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    openslide-tools \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Default: Cloud Run HTTP mode via app.py
# Override CMD to `python main.py` for local MCP stdio mode
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
