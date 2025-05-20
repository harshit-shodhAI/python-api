#!/bin/bash

# Use PORT environment variable if provided by Cloud Run, otherwise default to 8080
PORT=${PORT:-8080}

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
