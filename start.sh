#!/bin/bash

# Use PORT environment variable if provided by Cloud Run, otherwise default to 8080
PORT=${PORT:-8080}

# Log environment information for debugging
echo "Starting server with PORT=$PORT"
echo "Current directory: $(pwd)"

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
  echo "WARNING: OPENAI_API_KEY environment variable is not set."
  echo "The application will run with limited functionality."
fi

# Start the main application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
