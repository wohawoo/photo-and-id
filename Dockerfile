FROM continuumio/miniconda3:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CONDA_AUTO_UPDATE_CONDA=false \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create conda environment
RUN conda create -n face_env python=3.9 -y
SHELL ["conda", "run", "-n", "face_env", "/bin/bash", "-c"]

# Install dependencies using conda
RUN conda install -c conda-forge dlib=19.24.2 -y && \
    conda install -c conda-forge face_recognition=1.3.0 -y && \
    conda install -c conda-forge flask=2.3.3 flask-cors=4.0.0 gunicorn=21.2.0 -y && \
    conda install -c conda-forge opencv=4.8.0 -y

# Copy application code
COPY . .

# Set memory optimization for Python
ENV PYTHONMALLOC=malloc \
    MALLOC_TRIM_THRESHOLD_=100000

# Command to run the application with memory constraints
CMD ["conda", "run", "--no-capture-output", "-n", "face_env", \
     "gunicorn", \
     "--config", "gunicorn.conf.py", \
     "--worker-class", "sync", \
     "--workers", "1", \
     "--threads", "2", \
     "--timeout", "120", \
     "--max-requests", "5", \
     "--max-requests-jitter", "2", \
     "app:app"] 