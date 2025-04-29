#!/bin/bash

# Enable swap
swapon /swapfile

# Clear any existing temporary files
rm -rf /dev/shm/face_verification/*

# Start gunicorn with the specified config
exec gunicorn --config gunicorn.conf.py app:app 