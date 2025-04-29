FROM python:3.9-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV PYTHONPATH=/app
ENV PORT=8080
ENV MALLOC_TRIM_THRESHOLD_=100000
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV PYTHONDONTWRITEBYTECODE=1

# Create and set up swap space
RUN dd if=/dev/zero of=/swapfile bs=1M count=1024 && \
    chmod 600 /swapfile && \
    mkswap /swapfile && \
    echo "/swapfile swap swap defaults 0 0" >> /etc/fstab

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories with appropriate permissions
RUN mkdir -p /root/.deepface/weights && \
    chmod -R 777 /root/.deepface && \
    mkdir -p /dev/shm/face_verification && \
    chmod -R 777 /dev/shm/face_verification

# Expose the port the app runs on
EXPOSE 8080

# Start script to enable swap and run the application
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Command to run the application
CMD ["/start.sh"] 