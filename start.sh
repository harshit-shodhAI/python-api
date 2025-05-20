#!/bin/bash

# Use PORT environment variable if provided by Cloud Run, otherwise default to 8080
PORT=${PORT:-8080}

# Log environment information for debugging
echo "Starting server with PORT=$PORT"
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Run the minimal server that has no dependencies
# This will ensure the container starts and listens on the required port
exec python -m app.minimal_server
