FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Make the startup script executable
RUN chmod +x /app/start.sh

# Use the startup script as the entrypoint
CMD ["/app/start.sh"]
