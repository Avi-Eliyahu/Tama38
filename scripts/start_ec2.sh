#!/bin/bash
# EC2 Startup Script
# Gets EC2 IP from metadata service and starts docker-compose

set -e

cd ~/tama38

# Get EC2 public IP from metadata service
echo "Getting EC2 public IP..."
EC2_IP=$(curl -s --max-time 5 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")

if [ -z "$EC2_IP" ]; then
    echo "Warning: Could not detect EC2 IP from metadata service"
    echo "Using default CORS_ORIGINS (localhost only)"
    export CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
else
    echo "Detected EC2 IP: $EC2_IP"
    export CORS_ORIGINS="http://${EC2_IP}:3000,http://localhost:3000,http://localhost:5173"
    export EC2_IP_ENV="$EC2_IP"
fi

echo "CORS_ORIGINS: $CORS_ORIGINS"
echo ""

# Start docker-compose
docker-compose -f docker-compose.aws.yml up -d

echo ""
echo "Services started. Checking status..."
sleep 5
docker-compose -f docker-compose.aws.yml ps

