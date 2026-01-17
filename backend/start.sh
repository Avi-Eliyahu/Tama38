#!/bin/sh
# Dynamic CORS configuration for EC2 deployment
# Detects EC2 public IP and sets CORS_ORIGINS accordingly

# Try to get EC2 public IP from metadata service
EC2_IP=$(curl -s --max-time 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")

# Build CORS_ORIGINS dynamically
if [ -n "$EC2_IP" ]; then
  # EC2 environment detected - add EC2 IP to CORS origins
  export CORS_ORIGINS="http://${EC2_IP}:3000,http://localhost:3000,http://localhost:5173"
else
  # Not on EC2 or metadata service unavailable - use localhost defaults
  # Allow override via environment variable
  export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:3000,http://localhost:5173}"
fi

# Start uvicorn with the configured CORS
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

