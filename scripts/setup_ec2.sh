#!/bin/bash

# EC2 Initial Setup Script
# Run this once on a fresh EC2 instance

set -e

echo "Setting up EC2 instance for TAMA38 deployment..."

# Update system
if command -v yum &> /dev/null; then
    echo "Detected Amazon Linux / CentOS"
    sudo yum update -y
    INSTALL_CMD="yum install -y"
elif command -v apt-get &> /dev/null; then
    echo "Detected Ubuntu / Debian"
    sudo apt-get update -y
    INSTALL_CMD="apt-get install -y"
else
    echo "Unknown Linux distribution"
    exit 1
fi

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    if command -v yum &> /dev/null; then
        # Amazon Linux 2
        sudo yum install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    elif command -v apt-get &> /dev/null; then
        # Ubuntu
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    fi
    echo "Docker installed successfully"
else
    echo "Docker is already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully"
else
    echo "Docker Compose is already installed"
fi

# Install curl (if not present)
if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    sudo $INSTALL_CMD curl
fi

# Create application directory
mkdir -p ~/tama38
cd ~/tama38

echo ""
echo "=========================================="
echo "EC2 setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy your application files to ~/tama38"
echo "2. Set environment variables:"
echo "   export VITE_API_URL=http://\$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "   export CORS_ORIGINS=http://\$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "3. Run: docker-compose -f docker-compose.aws.yml up -d"
echo ""
echo "Note: You may need to logout and login again for Docker group permissions to take effect."
echo ""

