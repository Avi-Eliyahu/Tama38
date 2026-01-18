# CLOUD.md - EC2 Deployment Runbook for Cursor AI

This runbook is executed from your local machine with Cursor AI. It assumes the user creates the EC2 instance and provides the EC2 public IP, SSH user, and PEM key path. The Cursor AI agent then runs the deployment commands locally (using SSH/SCP into EC2).

## What the user must provide to the agent
- EC2 public IPv4 address
- SSH user (Amazon Linux: `ec2-user`, Ubuntu: `ubuntu`)
- Absolute path to the PEM key file on the local machine
- EC2 OS type (Amazon Linux 2/2023 or Ubuntu 22.04)

## Local machine prerequisites (before running any steps)
- Git installed
- SSH + SCP available in PATH
- PowerShell (Windows) or Bash (Mac/Linux)
- Access to the repository on the local machine

Optional but recommended:
- Docker Desktop (for local validation)

## EC2 instance prerequisites (user does this in AWS Console)
1. Launch an EC2 instance:
   - Amazon Linux 2023 or Ubuntu 22.04 (x86_64)
   - Instance type: `t2.micro` or `t3.micro`
2. Create and download a key pair (.pem)
3. Configure Security Group inbound rules:
   - SSH: TCP 22 from your IP
   - Frontend: TCP 3000 from 0.0.0.0/0
   - Backend: TCP 8000 from 0.0.0.0/0
4. Note the public IPv4 address
5. (Optional) Allocate and associate an Elastic IP for a stable address

## Step-by-step deployment (Cursor AI runs these from local machine)

### 1) Clone and prepare repo
```
git clone https://github.com/Avi-Eliyahu/Tama38.git
cd Tama38
```
If you already have the repo, pull latest changes for your working branch.

### 2) (Optional) Configure environment overrides
```
cp .env.example .env
```
Edit `.env` to set production secrets:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- Optional: `CORS_ORIGINS` and `VITE_API_URL`

### 3) Bootstrap EC2 (one-time)
Copy the setup script to EC2 and run it.

Mac/Linux:
```
chmod +x scripts/setup_ec2.sh
scp -i /path/to/key.pem scripts/setup_ec2.sh ec2-user@EC2_PUBLIC_IP:/home/ec2-user/setup_ec2.sh
ssh -i /path/to/key.pem ec2-user@EC2_PUBLIC_IP "chmod +x ~/setup_ec2.sh && ~/setup_ec2.sh"
```

Windows PowerShell:
```
scp -i C:\path\to\key.pem scripts\setup_ec2.sh ec2-user@EC2_PUBLIC_IP:/home/ec2-user/setup_ec2.sh
ssh -i C:\path\to\key.pem ec2-user@EC2_PUBLIC_IP "chmod +x ~/setup_ec2.sh && ~/setup_ec2.sh"
```

Note: After setup, the EC2 user may need to log out and log back in for Docker group permissions.

### 4) Configure local EC2 settings (recommended)
Windows PowerShell:
```
.\scripts\setup_ec2_config.ps1
```
This creates `.ec2-config.json` (gitignored) with:
- EC2PublicIP
- EC2User
- SSHKey

### 5) Initial full deployment (recommended on first deploy)

Option A: PowerShell full deploy
```
.\scripts\deploy_aws.ps1 -EC2PublicIP "EC2_PUBLIC_IP" -EC2User "ec2-user"
```

Option B: Bash full deploy
```
chmod +x scripts/deploy_aws.sh
./scripts/deploy_aws.sh EC2_PUBLIC_IP ec2-user
```

### 6) Incremental deployments (after initial setup)
Windows PowerShell:
```
.\scripts\deploy_to_ec2.ps1 -Auto
```
Use `-Files` or `-FullDeploy` as needed.

### 7) Initialize database and create admin user (required on first deploy)

After the initial deployment, you need to:
1. Create the database (if it doesn't exist)
2. Run database migrations
3. Create the admin user

Windows PowerShell:
```powershell
# Create database (ignore error if it already exists)
ssh -i C:\path\to\key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml exec -T database psql -U postgres -c 'CREATE DATABASE tama38_hebrew_sample;' 2>&1 || echo 'Database may already exist'"

# Run migrations
ssh -i C:\path\to\key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head"

# Create admin user
ssh -i C:\path\to\key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml exec -T backend python scripts/create_admin.py"
```

Mac/Linux:
```bash
# Create database (ignore error if it already exists)
ssh -i /path/to/key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml exec -T database psql -U postgres -c 'CREATE DATABASE tama38_hebrew_sample;' 2>&1 || echo 'Database may already exist'"

# Run migrations
ssh -i /path/to/key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml exec -T backend alembic upgrade head"

# Create admin user
ssh -i /path/to/key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml exec -T backend python scripts/create_admin.py"
```

**Default Admin Credentials:**
- Email: `admin@tama38.local`
- Password: `Admin123!@#`
- Role: `SUPER_ADMIN`

Note: The `create_admin.py` script is idempotent - it won't create a duplicate if admin already exists.

## Post-deploy verification (run from local)
```
curl http://EC2_PUBLIC_IP:8000/health
```
Expected: `{"status":"healthy"}`

Access in browser:
- Frontend: `http://EC2_PUBLIC_IP:3000`
- Backend docs: `http://EC2_PUBLIC_IP:8000/docs`

**Login with admin credentials:**
- Email: `admin@tama38.local`
- Password: `Admin123!@#`

## Troubleshooting quick checks
- SSH connectivity:
```
ssh -i /path/to/key.pem ec2-user@EC2_PUBLIC_IP
```
- Container status:
```
ssh -i /path/to/key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml ps"
```
- Logs:
```
ssh -i /path/to/key.pem ec2-user@EC2_PUBLIC_IP "cd ~/tama38 && docker-compose -f docker-compose.aws.yml logs --tail=100"
```

## Notes for the Cursor AI agent
- Always run commands locally and use SSH/SCP for EC2 actions.
- Request the EC2 public IP, SSH user, and PEM path from the user.
- Use `deploy_aws.*` for initial full deploy, then `deploy_to_ec2.ps1 -Auto` for incremental changes.
