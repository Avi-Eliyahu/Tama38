#!/bin/bash

# AWS Deployment Script for TAMA38
# Usage: ./scripts/deploy_aws.sh <EC2_PUBLIC_IP> [ec2-user|ubuntu]

set -e

EC2_PUBLIC_IP=${1:-""}
EC2_USER=${2:-"ec2-user"}  # Use "ubuntu" for Ubuntu AMI, "ec2-user" for Amazon Linux

if [ -z "$EC2_PUBLIC_IP" ]; then
    echo "Usage: $0 <EC2_PUBLIC_IP> [ec2-user|ubuntu]"
    echo "Example: $0 54.123.45.67 ec2-user"
    exit 1
fi

echo "=========================================="
echo "Deploying TAMA38 to EC2"
echo "=========================================="
echo "EC2 Public IP: $EC2_PUBLIC_IP"
echo "EC2 User: $EC2_USER"
echo ""

# Export VITE_API_URL for docker-compose
export VITE_API_URL="http://${EC2_PUBLIC_IP}:8000"
export CORS_ORIGINS="http://${EC2_PUBLIC_IP}:3000"

echo "Environment variables:"
echo "  VITE_API_URL=$VITE_API_URL"
echo "  CORS_ORIGINS=$CORS_ORIGINS"
echo ""

# Check if SSH key exists
SSH_KEY="${HOME}/.ssh/tama38-keypair.pem"
if [ ! -f "$SSH_KEY" ]; then
    echo "Warning: SSH key not found at $SSH_KEY"
    echo "Please ensure your SSH key is accessible"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    SSH_KEY_OPTION=""
else
    SSH_KEY_OPTION="-i $SSH_KEY"
    chmod 400 "$SSH_KEY" 2>/dev/null || true
fi

# Copy files to EC2
echo "Step 1: Copying files to EC2..."
scp $SSH_KEY_OPTION -r \
    docker-compose.aws.yml \
    backend/ \
    frontend/ \
    scripts/ \
    ${EC2_USER}@${EC2_PUBLIC_IP}:/home/${EC2_USER}/tama38/ || {
    echo "Error: Failed to copy files. Check SSH connection and key permissions."
    exit 1
}

echo "Files copied successfully!"
echo ""

# SSH into EC2 and deploy
echo "Step 2: Deploying on EC2..."
ssh $SSH_KEY_OPTION ${EC2_USER}@${EC2_PUBLIC_IP} << ENDSSH
set -e

cd ~/tama38

# Get EC2 public IP (in case Elastic IP is used)
EC2_IP=\$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "${EC2_PUBLIC_IP}")

# Export environment variables
export VITE_API_URL="http://\${EC2_IP}:8000"
export CORS_ORIGINS="http://\${EC2_IP}:3000"

echo "Deploying with:"
echo "  VITE_API_URL=\$VITE_API_URL"
echo "  CORS_ORIGINS=\$CORS_ORIGINS"
echo ""

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.aws.yml down || true

# Build and start containers
echo "Building and starting containers..."
docker-compose -f docker-compose.aws.yml up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 15

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head || echo "Warning: Migrations may have failed, check logs"

# Show status
echo ""
echo "Container status:"
docker-compose -f docker-compose.aws.yml ps

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Deployment finished successfully!"
    echo "=========================================="
    echo ""
    echo "Access the application:"
    echo "  Frontend: http://${EC2_PUBLIC_IP}:3000"
    echo "  Backend API: http://${EC2_PUBLIC_IP}:8000"
    echo "  API Docs: http://${EC2_PUBLIC_IP}:8000/docs"
    echo ""
    echo "Next steps:"
    echo "  1. Create admin user:"
    echo "     ssh $SSH_KEY_OPTION ${EC2_USER}@${EC2_PUBLIC_IP}"
    echo "     cd ~/tama38"
    echo "     docker-compose -f docker-compose.aws.yml exec backend python scripts/create_admin.py"
    echo ""
else
    echo ""
    echo "Error: Deployment failed. Check the output above for details."
    exit 1
fi

