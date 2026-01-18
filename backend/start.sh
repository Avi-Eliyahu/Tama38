#!/bin/sh
# Dynamic CORS configuration for EC2 deployment
# Detects EC2 public IP and sets CORS_ORIGINS accordingly

# Try multiple methods to get EC2 public IP
# Method 1: Use EC2_IP_ENV if passed from host (most reliable)
EC2_IP="${EC2_IP_ENV:-}"

# Method 2: Try EC2 metadata service (may not work from container)
if [ -z "$EC2_IP" ]; then
  EC2_IP=$(curl -s --max-time 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")
fi

# Method 3: If CORS_ORIGINS is already set and contains an IP, extract it
if [ -z "$EC2_IP" ] && [ -n "$CORS_ORIGINS" ]; then
  # Try to extract IP from CORS_ORIGINS if it's in format http://IP:3000
  EC2_IP=$(echo "$CORS_ORIGINS" | sed -n 's|.*http://\([0-9.]*\):3000.*|\1|p' | head -1)
fi

# Method 4: If still empty, default to localhost-only CORS
if [ -z "$EC2_IP" ]; then
  echo "EC2 IP not detected - defaulting CORS to localhost only"
fi

# Build CORS_ORIGINS dynamically - only if not already set
if [ -z "$CORS_ORIGINS" ] || [ "$CORS_ORIGINS" = "" ]; then
  if [ -n "$EC2_IP" ]; then
    # EC2 environment detected - add EC2 IP to CORS origins
    export CORS_ORIGINS="http://${EC2_IP}:3000,http://localhost:3000,http://localhost:5173"
    echo "Detected EC2 IP: ${EC2_IP}"
  else
    export CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
  fi
  echo "Setting CORS_ORIGINS: ${CORS_ORIGINS}"
else
  # Use provided CORS_ORIGINS (clean it up - remove any leading/trailing spaces or quotes)
  export CORS_ORIGINS=$(echo "$CORS_ORIGINS" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sed 's/^"//;s/"$//')
  echo "Using provided CORS_ORIGINS: ${CORS_ORIGINS}"
fi

# Start uvicorn with the configured CORS
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

