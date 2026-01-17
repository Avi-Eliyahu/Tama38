# Basic AWS Migration Plan - TAMA38 System
## Option A: Single EC2 Instance Deployment

**Purpose:** Deploy TAMA38 system on AWS for remote testing by 2 market people  
**Duration:** Few weeks (temporary testing environment)  
**Cost:** $0/month (Free Tier) or ~$8-15/month after free tier  
**Architecture:** Single EC2 instance running all services via Docker Compose  
**Branch:** All AWS deployment changes are on `develop-avraham-eliyahu` branch (not merged to main)

---

## Table of Contents

1. [AWS Introduction & Preparation](#1-aws-introduction--preparation)
2. [AWS Account Setup](#2-aws-account-setup)
3. [Prerequisites & Requirements](#3-prerequisites--requirements)
4. [Code Changes Required](#4-code-changes-required)
5. [AWS EC2 Instance Setup](#5-aws-ec2-instance-setup)
6. [Deployment Steps](#6-deployment-steps)
7. [Cursor AI Integration](#7-cursor-ai-integration)
8. [Accessing the System](#8-accessing-the-system)
9. [Troubleshooting](#9-troubleshooting)
10. [Cost Monitoring](#10-cost-monitoring)
11. [Cleanup & Shutdown](#11-cleanup--shutdown)

---

## 1. AWS Introduction & Preparation

### What is AWS?

Amazon Web Services (AWS) is a cloud computing platform that provides on-demand computing resources. For this deployment, we'll use:

- **EC2 (Elastic Compute Cloud)**: Virtual servers in the cloud
- **Security Groups**: Firewall rules for network access
- **Elastic IP**: Static public IP address (optional but recommended)

### Why Single EC2 Instance?

- **Simplest**: One server runs everything (database, backend, frontend)
- **Cost-effective**: Free tier eligible for 12 months
- **Fast setup**: Deploy in ~30 minutes
- **Easy debugging**: All services in one place
- **Perfect for testing**: Handles 2 users easily

### AWS Free Tier Benefits

- **750 hours/month** of t2.micro EC2 instance (enough for 24/7 operation)
- **30 GB** of EBS storage
- **15 GB** of data transfer out
- **Valid for 12 months** from account creation

### Estimated Costs

| Item | Free Tier | After Free Tier |
|------|-----------|-----------------|
| EC2 t2.micro | $0 (750 hrs/month) | ~$8-15/month |
| EBS Storage (20GB) | $0 (30GB free) | ~$2/month |
| Data Transfer | $0 (15GB free) | ~$1-2/month |
| **Total** | **$0/month** | **~$10-20/month** |

---

## 2. AWS Account Setup

### Step 1: Create AWS Account

1. Go to [https://aws.amazon.com](https://aws.amazon.com)
2. Click **"Create an AWS Account"**
3. Follow the registration process:
   - Enter email address
   - Choose account name
   - Provide payment information (credit card required, but won't be charged if you stay within free tier)
   - Verify phone number
   - Choose support plan: **"Basic Plan"** (free)

### Step 2: Access AWS Console

1. Go to [https://console.aws.amazon.com](https://console.aws.amazon.com)
2. Sign in with your credentials
3. You'll see the AWS Management Console dashboard

### Step 3: Select AWS Region

**Important:** Choose a region close to your users to reduce latency.

1. Click the region dropdown (top right, e.g., "N. Virginia")
2. Recommended regions:
   - **Europe**: `eu-central-1` (Frankfurt) - Good for Israel/Europe
   - **US East**: `us-east-1` (N. Virginia) - Cheapest, most services
   - **US West**: `us-west-2` (Oregon) - Good alternative

**Note:** Once you choose a region, all resources will be created there. You can change it later, but it's easier to stick with one.

### Step 4: Enable Free Tier Monitoring

1. Go to **Billing Dashboard**: [https://console.aws.amazon.com/billing](https://console.aws.amazon.com/billing)
2. Click **"Preferences"** in the left menu
3. Enable **"Receive Free Tier Usage Alerts"**
4. Set up billing alerts (optional but recommended):
   - Go to **"Budgets"** → **"Create budget"**
   - Choose **"Cost budget"**
   - Set limit: **$5/month** (to catch any unexpected charges)
   - Add email notification

---

## 3. Prerequisites & Requirements

### What You Need

1. **AWS Account** (created in Step 2)
2. **Local Machine Requirements**:
   - Git installed
   - SSH client (built into Windows 10/11, Mac, Linux)
   - AWS CLI (optional but recommended for Cursor AI)
   - Text editor (VS Code/Cursor)

### AWS CLI Installation (For Cursor AI Integration)

**Windows:**
```powershell
# Download and install AWS CLI
# https://aws.amazon.com/cli/
# Or use winget:
winget install Amazon.AWSCLI
```

**Mac:**
```bash
brew install awscli
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Verify Installation:**
```bash
aws --version
# Should show: aws-cli/2.x.x
```

---

## 4. Code Changes Required

### 4.1 Create AWS-Specific Docker Compose File

Create `docker-compose.aws.yml` in the project root:

```yaml
version: '3.8'

services:
  database:
    image: postgres:15-alpine
    container_name: tama38_database
    environment:
      POSTGRES_DB: tama38_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: tama38_backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@database:5432/tama38_hebrew_sample
      - SECRET_KEY=${SECRET_KEY:-dev-secret-key-change-in-production}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-jwt-secret-change-in-production}
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=INFO
      - CORS_ORIGINS=${CORS_ORIGINS:-http://EC2_PUBLIC_IP:3000}
    volumes:
      - backend_logs:/app/logs
      - backend_storage:/app/storage
    depends_on:
      database:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=${VITE_API_URL:-http://EC2_PUBLIC_IP:8000}
    container_name: tama38_frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=${VITE_API_URL:-http://EC2_PUBLIC_IP:8000}
      - NODE_ENV=production
    depends_on:
      - backend
    command: npm run dev -- --host 0.0.0.0
    restart: unless-stopped

volumes:
  postgres_data:
  backend_logs:
  backend_storage:
```

**Key Changes:**
- Removed volume mounts for code (not needed for production)
- Added `restart: unless-stopped` for auto-recovery
- Changed environment to `production`
- Added `VITE_API_URL` as build arg for frontend
- Updated CORS_ORIGINS to use EC2 IP

### 4.2 Update Frontend Dockerfile

Modify `frontend/Dockerfile` to accept build argument:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Accept build argument for API URL
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### 4.3 Update Backend CORS Configuration

The backend already reads `CORS_ORIGINS` from environment variables. We'll set it during deployment.

### 4.4 Create Deployment Script

Create `scripts/deploy_aws.sh`:

```bash
#!/bin/bash

# AWS Deployment Script for TAMA38
# Usage: ./scripts/deploy_aws.sh <EC2_PUBLIC_IP>

set -e

EC2_PUBLIC_IP=${1:-""}
EC2_USER=${2:-"ec2-user"}  # Use "ubuntu" for Ubuntu AMI, "ec2-user" for Amazon Linux

if [ -z "$EC2_PUBLIC_IP" ]; then
    echo "Usage: $0 <EC2_PUBLIC_IP> [ec2-user|ubuntu]"
    exit 1
fi

echo "Deploying to EC2 instance: $EC2_PUBLIC_IP"

# Export VITE_API_URL for docker-compose
export VITE_API_URL="http://${EC2_PUBLIC_IP}:8000"
export CORS_ORIGINS="http://${EC2_PUBLIC_IP}:3000"

# Copy files to EC2
echo "Copying files to EC2..."
scp -r \
    docker-compose.aws.yml \
    backend/ \
    frontend/ \
    scripts/ \
    ${EC2_USER}@${EC2_PUBLIC_IP}:/home/${EC2_USER}/tama38/

# SSH into EC2 and deploy
echo "Deploying on EC2..."
ssh ${EC2_USER}@${EC2_PUBLIC_IP} << 'ENDSSH'
cd ~/tama38

# Export environment variables
export VITE_API_URL="http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
export CORS_ORIGINS="http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"

# Stop existing containers
docker-compose -f docker-compose.aws.yml down || true

# Build and start containers
docker-compose -f docker-compose.aws.yml up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Run database migrations
docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head || echo "Migrations may have failed, check logs"

# Show status
docker-compose -f docker-compose.aws.yml ps

echo "Deployment complete!"
ENDSSH

echo "Deployment finished. Access the application at:"
echo "Frontend: http://${EC2_PUBLIC_IP}:3000"
echo "Backend API: http://${EC2_PUBLIC_IP}:8000"
echo "API Docs: http://${EC2_PUBLIC_IP}:8000/docs"
```

**For Windows PowerShell, create `scripts/deploy_aws.ps1`:**

```powershell
# AWS Deployment Script for TAMA38 (PowerShell)
# Usage: .\scripts\deploy_aws.ps1 <EC2_PUBLIC_IP> [ec2-user|ubuntu]

param(
    [Parameter(Mandatory=$true)]
    [string]$EC2PublicIP,
    
    [Parameter(Mandatory=$false)]
    [string]$EC2User = "ec2-user"
)

$ErrorActionPreference = "Stop"

Write-Host "Deploying to EC2 instance: $EC2PublicIP"

# Set environment variables
$env:VITE_API_URL = "http://${EC2PublicIP}:8000"
$env:CORS_ORIGINS = "http://${EC2PublicIP}:3000"

# Copy files to EC2 (requires SSH key setup)
Write-Host "Copying files to EC2..."
scp -r docker-compose.aws.yml backend/ frontend/ scripts/ ${EC2User}@${EC2PublicIP}:/home/${EC2User}/tama38/

# Deploy on EC2
Write-Host "Deploying on EC2..."
ssh ${EC2User}@${EC2PublicIP} @"
cd ~/tama38
export VITE_API_URL='http://`$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000'
export CORS_ORIGINS='http://`$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000'
docker-compose -f docker-compose.aws.yml down
docker-compose -f docker-compose.aws.yml up -d --build
sleep 10
docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head
docker-compose -f docker-compose.aws.yml ps
"@

Write-Host "Deployment complete!"
Write-Host "Frontend: http://${EC2PublicIP}:3000"
Write-Host "Backend API: http://${EC2PublicIP}:8000"
Write-Host "API Docs: http://${EC2PublicIP}:8000/docs"
```

### 4.5 Create Setup Script for EC2

Create `scripts/setup_ec2.sh` (to be run once on EC2):

```bash
#!/bin/bash

# EC2 Initial Setup Script
# Run this once on a fresh EC2 instance

set -e

echo "Setting up EC2 instance for TAMA38 deployment..."

# Update system
sudo yum update -y || sudo apt-get update -y

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    # Amazon Linux 2
    if [ -f /etc/os-release ] && grep -q "Amazon Linux" /etc/os-release; then
        sudo yum install -y docker
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    # Ubuntu
    elif [ -f /etc/os-release ] && grep -q "Ubuntu" /etc/os-release; then
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    fi
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install curl (if not present)
sudo yum install -y curl || sudo apt-get install -y curl || true

# Create application directory
mkdir -p ~/tama38
cd ~/tama38

echo "EC2 setup complete!"
echo "Next steps:"
echo "1. Copy your application files to ~/tama38"
echo "2. Run: docker-compose -f docker-compose.aws.yml up -d"
```

---

## 5. AWS EC2 Instance Setup

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console**
   - Navigate to: [https://console.aws.amazon.com/ec2](https://console.aws.amazon.com/ec2)
   - Click **"Launch Instance"**

2. **Name Your Instance**
   - Name: `tama38-test-server`

3. **Choose AMI (Amazon Machine Image)**
   - Select: **Amazon Linux 2023 AMI** (free tier eligible)
   - Architecture: **64-bit (x86)**
   - **Alternative:** Ubuntu Server 22.04 LTS (also free tier eligible)

4. **Choose Instance Type**
   - Select: **t2.micro** (free tier eligible)
   - **Note:** If t2.micro is not available, choose **t3.micro** (may incur small charges)

5. **Create Key Pair** (IMPORTANT - Save this!)
   - Click **"Create new key pair"**
   - Name: `tama38-keypair`
   - Key pair type: **RSA**
   - Private key file format: **.pem** (for Linux/Mac) or **.ppk** (for Windows PuTTY)
   - Click **"Create key pair"**
   - **SAVE THE DOWNLOADED FILE** - You'll need it to SSH into the server!

6. **Network Settings**
   - Click **"Edit"** to configure:
   - **Allow SSH traffic from:** Select **"My IP"** (for security) or **"Anywhere-IPv4"** (0.0.0.0/0) for easier access
   - Click **"Add security group rule"**:
     - **Type:** Custom TCP
     - **Port:** 3000
     - **Source:** 0.0.0.0/0 (Anywhere-IPv4)
     - **Description:** Frontend access
   - Click **"Add security group rule"** again:
     - **Type:** Custom TCP
     - **Port:** 8000
     - **Source:** 0.0.0.0/0 (Anywhere-IPv4)
     - **Description:** Backend API access

7. **Configure Storage**
   - Keep default: **8 GB gp3** (free tier includes 30 GB)
   - **Note:** You can increase to 20 GB if needed (still within free tier)

8. **Review and Launch**
   - Review all settings
   - Click **"Launch Instance"**

9. **Wait for Instance to Start**
   - Click **"View all instances"**
   - Wait for **Instance State** to show **"Running"** (green)
   - Wait for **Status Checks** to show **"2/2 checks passed"** (takes 1-2 minutes)

### Step 2: Get Public IP Address

1. In EC2 Console, select your instance
2. Find **"Public IPv4 address"** in the details panel
3. **Copy this IP** - You'll need it for:
   - Accessing the application
   - Deployment scripts
   - Cursor AI configuration

**Example:** `54.123.45.67`

### Step 3: (Optional) Allocate Elastic IP

Elastic IP gives you a static IP that doesn't change when you restart the instance.

1. In EC2 Console, click **"Elastic IPs"** (left sidebar)
2. Click **"Allocate Elastic IP address"**
3. Click **"Allocate"**
4. Select the Elastic IP, click **"Actions"** → **"Associate Elastic IP address"**
5. Select your instance, click **"Associate"**

**Note:** Elastic IPs are free when attached to a running instance. If you stop/terminate the instance, you may incur charges if you don't release the IP.

### Step 4: Connect to EC2 Instance

**Windows (PowerShell):**

```powershell
# Navigate to folder containing your .pem key file
cd C:\path\to\your\keys

# Set permissions (if needed)
# Note: In PowerShell, use $env:USERNAME instead of %username%
icacls .\tama38-keypair.pem /inheritance:r
icacls .\tama38-keypair.pem /grant:r "$env:USERNAME`:R"

# Connect (replace with your public IP)
ssh -i .\tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP

# For Ubuntu AMI, use:
ssh -i .\tama38-keypair.pem ubuntu@YOUR_PUBLIC_IP
```

**Mac/Linux:**

```bash
# Set permissions
chmod 400 tama38-keypair.pem

# Connect
ssh -i tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP

# For Ubuntu AMI:
ssh -i tama38-keypair.pem ubuntu@YOUR_PUBLIC_IP
```

**First Connection:**
- You'll see a security warning - type **"yes"** to continue
- You should now be connected to your EC2 instance!

### Step 5: Initial EC2 Setup

Once connected to EC2, run the setup script:

**Option A: Copy via SCP (Recommended - Works with private repos)**

From your local machine (before SSH into EC2):
```bash
# Copy setup script to EC2
scp -i tama38-keypair.pem scripts/setup_ec2.sh ec2-user@YOUR_PUBLIC_IP:/home/ec2-user/setup_ec2.sh
```

Then SSH into EC2 and run:
```bash
ssh -i tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP
chmod +x setup_ec2.sh
./setup_ec2.sh
```

**Option B: Clone Repository (Alternative)**

If you prefer to clone the entire repository:
```bash
# SSH into EC2 first
ssh -i tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP

# Install git if not present
sudo yum install -y git  # For Amazon Linux
# OR
sudo apt-get install -y git  # For Ubuntu

# Clone repository using HTTPS (works with public repos, no SSH keys needed)
git clone https://github.com/Avi-Eliyahu/Tama38.git
cd Tama38
git checkout develop-avraham-eliyahu

# Run setup script
chmod +x scripts/setup_ec2.sh
./scripts/setup_ec2.sh
```

**Note:** If the repository is private, you'll need to either:
- Use HTTPS with a Personal Access Token: `git clone https://YOUR_TOKEN@github.com/Avi-Eliyahu/Tama38.git`
- Or set up SSH keys on EC2 for GitHub (more complex)

**Option C: Manual Copy (If repository is private and SCP not available)**

If you can't use SCP, you can manually create the file on EC2:
```bash
ssh -i tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP
nano setup_ec2.sh
# Copy and paste the contents of scripts/setup_ec2.sh from your local machine
chmod +x setup_ec2.sh
./setup_ec2.sh
```

# After setup, logout and login again for Docker group to take effect
exit
```

Then reconnect:
```bash
ssh -i tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP
```

Verify Docker is installed:
```bash
docker --version
docker-compose --version
```

---

## 6. Deployment Steps

### Step 1: Prepare Local Environment

1. **Clone/Update Repository**
   ```bash
   # Clone repository using HTTPS (works with public repos, no SSH keys needed)
   git clone https://github.com/Avi-Eliyahu/Tama38.git
   cd Tama38
   git checkout develop-avraham-eliyahu
   git pull origin develop-avraham-eliyahu
   
   # If repository is private, use HTTPS with token:
   # git clone https://YOUR_GITHUB_TOKEN@github.com/Avi-Eliyahu/Tama38.git
   ```

2. **Create AWS Docker Compose File**
   - Copy `docker-compose.aws.yml` (from section 4.1) to project root

3. **Update Frontend Dockerfile**
   - Update `frontend/Dockerfile` (from section 4.2)

### Step 2: Deploy to EC2

**Option A: Using Deployment Script (Recommended)**

**Windows PowerShell:**
```powershell
# Set your EC2 public IP
$EC2_IP = "54.123.45.67"  # Replace with your actual IP

# Run deployment script
.\scripts\deploy_aws.ps1 -EC2PublicIP $EC2_IP -EC2User "ec2-user"
```

**Mac/Linux:**
```bash
# Set your EC2 public IP
export EC2_IP="54.123.45.67"  # Replace with your actual IP

# Make script executable
chmod +x scripts/deploy_aws.sh

# Run deployment script
./scripts/deploy_aws.sh $EC2_IP ec2-user
```

**Option B: Manual Deployment**

1. **Copy Files to EC2**
   ```bash
   # From your local machine
   scp -i tama38-keypair.pem -r \
       docker-compose.aws.yml \
       backend/ \
       frontend/ \
       scripts/ \
       ec2-user@YOUR_PUBLIC_IP:/home/ec2-user/tama38/
   ```

2. **SSH into EC2**
   ```bash
   ssh -i tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP
   ```

3. **Deploy on EC2**
   ```bash
   cd ~/tama38
   
   # Get public IP (if not using Elastic IP)
   export EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
   export VITE_API_URL="http://${EC2_PUBLIC_IP}:8000"
   export CORS_ORIGINS="http://${EC2_PUBLIC_IP}:3000"
   
   # Build and start containers
   # Note: Use docker-compose (v1) or ensure buildx is installed for docker compose (v2)
   docker-compose -f docker-compose.aws.yml up -d --build
   
   # Alternative if using docker compose (v2) without buildx:
   # DOCKER_BUILDKIT=0 docker compose -f docker-compose.aws.yml up -d --build
   
   # Wait for services to start
   sleep 15
   
   # Run database migrations
   docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head
   
   # Check status
   docker-compose -f docker-compose.aws.yml ps
   ```

### Step 3: Create Admin User

```bash
# SSH into EC2
ssh -i tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP

# Create admin user
cd ~/tama38
docker-compose -f docker-compose.aws.yml exec backend python scripts/create_admin.py
```

### Step 4: Automated Deployment Setup (Optional but Recommended)

For faster development cycles, set up automated deployment that detects changes and deploys only affected services.

**Setup EC2 Configuration:**

```powershell
# Run the setup script
.\scripts\setup_ec2_config.ps1
```

This will create `.ec2-config.json` with your EC2 connection details. This file is automatically ignored by git for security.

**Automated Deployment Options:**

1. **Auto-detect changed files from git:**
   ```powershell
   .\scripts\deploy_to_ec2.ps1 -Auto
   ```
   This detects files changed in the last commit and deploys only those.

2. **Deploy specific files:**
   ```powershell
   .\scripts\deploy_to_ec2.ps1 -Files "backend/app/api/v1/auth.py", "frontend/src/pages/Login.tsx"
   ```

3. **Full deployment:**
   ```powershell
   .\scripts\deploy_to_ec2.ps1 -FullDeploy
   ```

**Smart Service Restart:**

The script automatically determines which services need restarting:
- Backend changes → Only backend container restarts
- Frontend changes → Only frontend container restarts  
- Docker config changes → Full restart with rebuild

**Cursor AI Auto-Deployment:**

When working on EC2-related fixes, Cursor AI will automatically deploy changes after commits. See `.cursor/rules/ec2_auto_deploy.cursorrules` for details.

**Example Workflow:**

```powershell
# 1. Fix a bug in auth.py
# 2. Commit the change
git commit -m "fix: resolve login authentication issue"

# 3. Auto-deploy (or let Cursor AI do it automatically)
.\scripts\deploy_to_ec2.ps1 -Auto

# Output:
# ✓ Found 1 file(s) to deploy:
#   - backend/app/api/v1/auth.py
# ✓ Files copied successfully!
# ✓ Restarting backend...
# ✓ Deployment completed successfully!
```

### Step 5: Verify Deployment

1. **Check Container Status**
   ```bash
   docker-compose -f docker-compose.aws.yml ps
   ```
   All services should show "Up" status.

2. **Check Logs**
   ```bash
   # All services
   docker-compose -f docker-compose.aws.yml logs
   
   # Specific service
   docker-compose -f docker-compose.aws.yml logs backend
   docker-compose -f docker-compose.aws.yml logs frontend
   ```

3. **Test Endpoints**
   - Backend Health: `http://YOUR_PUBLIC_IP:8000/health`
   - API Docs: `http://YOUR_PUBLIC_IP:8000/docs`
   - Frontend: `http://YOUR_PUBLIC_IP:3000`

---

## 7. Cursor AI Integration

### 7.1 AWS Credentials Setup for Cursor AI

Cursor AI needs AWS credentials to interact with AWS services. Here's how to set it up:

#### Step 1: Create IAM User for Cursor AI

1. **Go to IAM Console**
   - Navigate to: [https://console.aws.amazon.com/iam](https://console.aws.amazon.com/iam)

2. **Create New User**
   - Click **"Users"** → **"Create user"**
   - User name: `cursor-ai-user`
   - Click **"Next"**

3. **Attach Policies**
   - Select: **"AmazonEC2FullAccess"** (for EC2 management)
   - **Optional:** Add **"AmazonSSMFullAccess"** (for Systems Manager)
   - Click **"Next"** → **"Create user"**

4. **Create Access Keys**
   - Click on the user: `cursor-ai-user`
   - Go to **"Security credentials"** tab
   - Click **"Create access key"**
   - Use case: **"Command Line Interface (CLI)"**
   - Click **"Next"** → **"Create access key"**
   - **IMPORTANT:** Copy both:
     - **Access key ID**
     - **Secret access key**
   - **Save these securely** - You won't be able to see the secret key again!

#### Step 2: Configure AWS CLI

On your local machine (where Cursor runs):

**Windows PowerShell:**
```powershell
aws configure
```

**Mac/Linux:**
```bash
aws configure
```

**Enter the following when prompted:**
```
AWS Access Key ID: [Paste your Access Key ID]
AWS Secret Access Key: [Paste your Secret Access Key]
Default region name: [Your region, e.g., eu-central-1]
Default output format: json
```

**Verify Configuration:**
```bash
aws sts get-caller-identity
```

You should see your IAM user details.

#### Step 3: Configure SSH Key for Cursor AI

Cursor AI needs SSH access to EC2 for debugging and deployment.

1. **Store SSH Key Securely**
   - Place your `.pem` key file in a secure location
   - **Windows:** `C:\Users\YourUsername\.ssh\tama38-keypair.pem`
   - **Mac/Linux:** `~/.ssh/tama38-keypair.pem`

2. **Set Permissions (Mac/Linux)**
   ```bash
   chmod 400 ~/.ssh/tama38-keypair.pem
   ```

3. **Create SSH Config** (Optional but recommended)

   **Windows:** `C:\Users\YourUsername\.ssh\config`
   **Mac/Linux:** `~/.ssh/config`

   ```
   Host tama38-aws
       HostName YOUR_PUBLIC_IP
       User ec2-user
       IdentityFile ~/.ssh/tama38-keypair.pem
       StrictHostKeyChecking no
   ```

   Then you can connect with:
   ```bash
   ssh tama38-aws
   ```

### 7.2 Cursor AI Commands for AWS Management

Cursor AI can now use these commands to manage AWS:

#### Check EC2 Instance Status
```bash
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' --output table
```

#### Get All EC2 Instances
```bash
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' --output table
```

#### Start EC2 Instance
```bash
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

#### Stop EC2 Instance
```bash
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

#### SSH into EC2
```bash
ssh -i ~/.ssh/tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP
```

#### View EC2 Logs via SSH
```bash
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs --tail=100 backend"
```

#### Deploy via Cursor AI

Cursor AI can run the deployment script:
```bash
# Windows PowerShell
.\scripts\deploy_aws.ps1 -EC2PublicIP "YOUR_PUBLIC_IP" -EC2User "ec2-user"

# Mac/Linux
./scripts/deploy_aws.sh YOUR_PUBLIC_IP ec2-user
```

### 7.3 What Cursor AI Needs from You

To enable Cursor AI to work with AWS, provide:

1. **AWS Credentials** (already configured via `aws configure`)
2. **EC2 Instance ID** (found in EC2 Console)
3. **EC2 Public IP** (found in EC2 Console)
4. **SSH Key Path** (location of your .pem file)
5. **EC2 User** (`ec2-user` for Amazon Linux, `ubuntu` for Ubuntu)

**Example Information to Provide:**
```
EC2 Instance ID: i-0123456789abcdef0
EC2 Public IP: 54.123.45.67
SSH Key Path: C:\Users\YourName\.ssh\tama38-keypair.pem
EC2 User: ec2-user
AWS Region: eu-central-1
```

### 7.4 Cursor AI Debugging Workflow

When debugging issues, Cursor AI can:

1. **Check EC2 Status**
   ```bash
   aws ec2 describe-instances --instance-ids YOUR_INSTANCE_ID
   ```

2. **SSH and Check Logs**
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs --tail=50"
   ```

3. **Restart Services**
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml restart"
   ```

4. **Redeploy**
   ```bash
   ./scripts/deploy_aws.sh YOUR_PUBLIC_IP ec2-user
   ```

---

## 8. Accessing the System

### For Market People (End Users)

1. **Frontend Application**
   - URL: `http://YOUR_PUBLIC_IP:3000`
   - Example: `http://54.123.45.67:3000`
   - Open in any web browser

2. **Login**
   - Use the admin credentials created in Step 6.3
   - Or create test users through the admin interface

3. **Backend API Documentation**
   - URL: `http://YOUR_PUBLIC_IP:8000/docs`
   - Swagger UI for API testing

### Security Notes

- **No HTTPS:** This is HTTP only (as requested)
- **Public Access:** Anyone with the IP can access (as requested)
- **No Authentication on Ports:** Ports 3000 and 8000 are open to the internet
- **For Production:** You would add HTTPS, domain name, and proper security

---

## 9. Troubleshooting

### Common Issues and Solutions

#### Issue 1: Cannot SSH into EC2

**Symptoms:** Connection timeout or "Permission denied"

**Solutions:**
1. Check Security Group allows SSH (port 22) from your IP
2. Verify you're using the correct key file
3. Check instance is running: `aws ec2 describe-instances --instance-ids YOUR_INSTANCE_ID`
4. Try connecting from a different network (your IP might have changed)

#### Issue 2: Cannot Access Frontend/Backend

**Symptoms:** Browser shows "Connection refused" or timeout

**Solutions:**
1. Check Security Group allows ports 3000 and 8000 from 0.0.0.0/0
2. Verify containers are running:
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml ps"
   ```
3. Check logs for errors:
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs"
   ```
4. Verify public IP hasn't changed (if not using Elastic IP)

#### Issue 3: Frontend Cannot Connect to Backend

**Symptoms:** Frontend loads but API calls fail

**Solutions:**
1. Check `VITE_API_URL` is set correctly:
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml exec frontend env | grep VITE_API_URL"
   ```
2. Verify backend is accessible: `http://YOUR_PUBLIC_IP:8000/health`
3. Check CORS settings in backend logs
4. Rebuild frontend with correct API URL:
   ```bash
   ssh tama38-aws "cd ~/tama38 && export VITE_API_URL=http://YOUR_PUBLIC_IP:8000 && docker-compose -f docker-compose.aws.yml up -d --build frontend"
   ```

#### Issue 4: Database Connection Errors

**Symptoms:** Backend logs show "could not connect to database"

**Solutions:**
1. Check database container is running:
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml ps database"
   ```
2. Check database logs:
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs database"
   ```
3. Restart database:
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml restart database"
   ```

#### Issue 5: Out of Memory

**Symptoms:** Containers keep restarting, "OOM" errors

**Solutions:**
1. t2.micro has 1GB RAM - may be tight for all services
2. Upgrade to t3.small (2GB RAM) - costs ~$15/month
3. Or optimize: reduce Docker memory limits, use lighter images

#### Issue 6: Git Clone Permission Denied (Publickey)

**Symptoms:** `git clone git@github.com:...` fails with "Permission denied (publickey)"

**Solutions:**
1. **Use HTTPS instead** (recommended for public repos):
   ```bash
   git clone https://github.com/Avi-Eliyahu/Tama38.git
   ```
2. If repository is private, use HTTPS with token:
   ```bash
   git clone https://YOUR_GITHUB_TOKEN@github.com/Avi-Eliyahu/Tama38.git
   ```
3. Or set up SSH keys on EC2 (more complex):
   ```bash
   ssh-keygen -t ed25519 -C "ec2-user@ec2"
   cat ~/.ssh/id_ed25519.pub
   # Add this public key to your GitHub account
   ```

#### Issue 7: Docker Compose Build Requires Buildx

**Symptoms:** `compose build requires buildx 0.17 or later` error when running `docker-compose up --build`

**Solutions:**

**Option A: Install Docker Buildx (Recommended)**
```bash
# Install buildx plugin
mkdir -p ~/.docker/cli-plugins

# Map architecture (uname -m to GitHub format)
ARCH=$(uname -m)
case "$ARCH" in
    x86_64) BUILDX_ARCH="amd64" ;;
    aarch64|arm64) BUILDX_ARCH="arm64" ;;
    *) BUILDX_ARCH="amd64" ;;  # Default fallback
esac

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
TAG=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest | grep -m1 '"tag_name"' | cut -d'"' -f4)
if [ -z "$TAG" ]; then TAG="v0.30.1"; fi

BUILDX_URL="https://github.com/docker/buildx/releases/download/${TAG}/buildx-${TAG}.${OS}-${BUILDX_ARCH}"

curl -L "$BUILDX_URL" -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx

# Verify installation
docker buildx version

# Create and use buildx builder
docker buildx create --use --name builder
docker buildx inspect --bootstrap
```

**Option B: Use Docker Compose v1 (docker-compose with hyphen)**
```bash
# Use docker-compose (v1) instead of docker compose (v2)
docker-compose -f docker-compose.aws.yml up -d --build
```

**Option C: Disable BuildKit (Workaround)**
```bash
# Disable BuildKit to use legacy builder
DOCKER_BUILDKIT=0 docker compose -f docker-compose.aws.yml up -d --build
```

**Note:** The setup script (`setup_ec2.sh`) now installs buildx automatically.

#### Issue 8: Instance Stopped Unexpectedly

**Solutions:**
1. Check AWS Console for reason
2. Check billing - may have exceeded free tier
3. Restart instance:
   ```bash
   aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID
   ```

### Useful Debugging Commands

```bash
# Check all container status
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml ps"

# View all logs
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs --tail=100"

# View specific service logs
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs backend --tail=50"

# Check system resources
ssh tama38-aws "free -h && df -h"

# Check Docker disk usage
ssh tama38-aws "docker system df"

# Restart all services
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml restart"

# Rebuild and restart
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml up -d --build"
```

---

## 10. Cost Monitoring

### Free Tier Limits

- **EC2:** 750 hours/month of t2.micro
- **EBS Storage:** 30 GB
- **Data Transfer Out:** 15 GB/month

### Monitor Usage

1. **AWS Cost Explorer**
   - Go to: [https://console.aws.amazon.com/cost-management/home](https://console.aws.amazon.com/cost-management/home)
   - View current month costs

2. **Billing Dashboard**
   - Go to: [https://console.aws.amazon.com/billing](https://console.aws.amazon.com/billing)
   - Set up billing alerts (recommended: $5/month threshold)

3. **EC2 Usage**
   - Check running hours in EC2 Console
   - Stop instance when not in use to save free tier hours

### Cost Optimization Tips

1. **Stop Instance When Not Testing**
   ```bash
   aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID
   ```
   - Saves free tier hours
   - Data persists (EBS storage)
   - Start when needed:
   ```bash
   aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID
   ```
   - **Note:** Public IP may change unless using Elastic IP

2. **Use Elastic IP** (if you stop/start frequently)
   - Prevents IP changes
   - Free when attached to running instance

3. **Monitor Data Transfer**
   - 15 GB/month free
   - Each user visit uses ~1-5 MB
   - 2 users testing = ~100-500 MB/day max
   - Should be well within limits

---

## 11. Cleanup & Shutdown

### When Testing is Complete

#### Step 1: Stop Instance (Saves Money)

```bash
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID
```

**Or via Console:**
1. Go to EC2 Console
2. Select instance
3. Click **"Instance state"** → **"Stop instance"**

#### Step 2: Release Elastic IP (If Used)

```bash
aws ec2 release-address --allocation-id eipalloc-12345678
```

**Or via Console:**
1. Go to EC2 → Elastic IPs
2. Select IP
3. Click **"Actions"** → **"Release Elastic IP address"**

#### Step 3: Terminate Instance (Permanent Deletion)

**WARNING:** This permanently deletes the instance and all data!

```bash
aws ec2 terminate-instances --instance-ids YOUR_INSTANCE_ID
```

**Or via Console:**
1. Go to EC2 Console
2. Select instance
3. Click **"Instance state"** → **"Terminate instance"**
4. Confirm termination

#### Step 4: Clean Up IAM User (Optional)

If you created IAM user for Cursor AI:

1. Go to IAM Console
2. Select user: `cursor-ai-user`
3. Click **"Delete user"**
4. Confirm deletion

#### Step 5: Remove Local Files (Optional)

```bash
# Remove SSH key (if you want)
rm ~/.ssh/tama38-keypair.pem

# Remove AWS credentials (if you want)
# Edit ~/.aws/credentials and remove [default] section
```

---

## Summary Checklist

### Before Deployment
- [ ] AWS account created
- [ ] AWS region selected
- [ ] AWS CLI installed and configured
- [ ] IAM user created for Cursor AI
- [ ] SSH key pair created and saved securely

### EC2 Setup
- [ ] EC2 instance launched (t2.micro)
- [ ] Security groups configured (ports 22, 3000, 8000)
- [ ] Public IP noted
- [ ] Elastic IP allocated (optional)
- [ ] SSH connection tested
- [ ] Docker and Docker Compose installed on EC2

### Code Changes
- [ ] `docker-compose.aws.yml` created
- [ ] `frontend/Dockerfile` updated
- [ ] Deployment scripts created
- [ ] Setup script created

### Deployment
- [ ] Files copied to EC2
- [ ] Containers built and started
- [ ] Database migrations run
- [ ] Admin user created
- [ ] Frontend accessible at `http://YOUR_IP:3000`
- [ ] Backend accessible at `http://YOUR_IP:8000`

### Cursor AI Integration
- [ ] AWS credentials configured
- [ ] SSH config created
- [ ] Cursor AI can SSH to EC2
- [ ] Cursor AI can run deployment scripts

### Testing
- [ ] Market people can access frontend
- [ ] Login works
- [ ] All features tested
- [ ] No errors in logs

---

## Quick Reference

### Important URLs
- **AWS Console:** [https://console.aws.amazon.com](https://console.aws.amazon.com)
- **EC2 Console:** [https://console.aws.amazon.com/ec2](https://console.aws.amazon.com/ec2)
- **IAM Console:** [https://console.aws.amazon.com/iam](https://console.aws.amazon.com/iam)
- **Billing Dashboard:** [https://console.aws.amazon.com/billing](https://console.aws.amazon.com/billing)

### Key Commands
```bash
# Connect to EC2
ssh -i ~/.ssh/tama38-keypair.pem ec2-user@YOUR_PUBLIC_IP

# Deploy
./scripts/deploy_aws.sh YOUR_PUBLIC_IP ec2-user

# Check status
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml ps"

# View logs
ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs"

# Stop instance
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID

# Start instance
aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID
```

---

## Support & Next Steps

### If You Need Help

1. **Check Logs First**
   ```bash
   ssh tama38-aws "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs"
   ```

2. **AWS Documentation**
   - EC2: [https://docs.aws.amazon.com/ec2](https://docs.aws.amazon.com/ec2)
   - Docker on EC2: [https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html)

3. **Ask Cursor AI**
   - Provide error messages
   - Share relevant logs
   - Describe what you were trying to do

### Future Enhancements (Not in Scope)

- HTTPS/SSL certificates
- Custom domain name
- Load balancing
- Auto-scaling
- Database backups
- Monitoring and alerting
- CI/CD pipeline

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-06  
**Author:** Cursor AI Assistant  
**Status:** Ready for Implementation

