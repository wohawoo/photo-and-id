FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    MALLOC_TRIM_THRESHOLD_=100000

# Install system dependencies including cmake
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Create and activate virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Set memory optimization for Python
ENV PYTHONMALLOC=malloc

# Command to run the application with memory constraints
CMD ["gunicorn", \
     "--config", "gunicorn.conf.py", \
     "--worker-class", "sync", \
     "--workers", "1", \
     "--threads", "2", \
     "--timeout", "120", \
     "--max-requests", "5", \
     "--max-requests-jitter", "2", \
     "app:app"] 