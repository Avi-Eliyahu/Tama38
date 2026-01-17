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

# Install Docker Buildx (required for Docker Compose v2 builds)
if ! docker buildx version &> /dev/null; then
    echo "Installing Docker Buildx..."
    mkdir -p ~/.docker/cli-plugins
    
    # Map architecture names (uname -m to GitHub release format)
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)
            BUILDX_ARCH="amd64"
            ;;
        aarch64|arm64)
            BUILDX_ARCH="arm64"
            ;;
        *)
            echo "Warning: Unknown architecture $ARCH, trying amd64"
            BUILDX_ARCH="amd64"
            ;;
    esac
    
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    TAG=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep -m1 '"tag_name"' | cut -d'"' -f4)
    if [ -z "$TAG" ]; then
        echo "Warning: Failed to detect buildx latest tag, defaulting to v0.30.1"
        TAG="v0.30.1"
    fi

    BUILDX_URL="https://github.com/docker/buildx/releases/download/${TAG}/buildx-${TAG}.${OS}-${BUILDX_ARCH}"
    
    echo "Downloading buildx from: $BUILDX_URL"
    curl -L "$BUILDX_URL" -o ~/.docker/cli-plugins/docker-buildx
    
    if [ $? -eq 0 ] && [ -f ~/.docker/cli-plugins/docker-buildx ]; then
        chmod +x ~/.docker/cli-plugins/docker-buildx
        docker buildx version
        echo "Docker Buildx installed successfully"
    else
        echo "Warning: Failed to download buildx. You may need to install it manually."
        echo "Alternative: Use 'docker-compose' (v1) instead of 'docker compose' (v2)"
    fi
else
    echo "Docker Buildx is already installed"
    docker buildx version
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

