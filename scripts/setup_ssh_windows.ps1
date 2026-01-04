# Windows SSH Setup Script for GitHub
# Run this script to configure SSH authentication

Write-Host "=== Windows SSH Setup for GitHub ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if SSH keys exist
if (-not (Test-Path $env:USERPROFILE\.ssh\id_ed25519)) {
    Write-Host "Generating new SSH key..." -ForegroundColor Yellow
    
    # Generate SSH key without passphrase
    ssh-keygen -t ed25519 -C "$(git config user.email)" -f $env:USERPROFILE\.ssh\id_ed25519 -N '""' -q
    
    Write-Host "✓ SSH key generated" -ForegroundColor Green
} else {
    Write-Host "✓ SSH key already exists" -ForegroundColor Green
}

# Step 2: Display public key
Write-Host "`n=== YOUR SSH PUBLIC KEY ===" -ForegroundColor Cyan
$publicKey = Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
Write-Host $publicKey -ForegroundColor White

# Copy to clipboard
$publicKey | Set-Clipboard
Write-Host "`n✓ Public key copied to clipboard!" -ForegroundColor Green

# Step 3: Try to start SSH agent service
Write-Host "`n=== Configuring SSH Agent ===" -ForegroundColor Cyan

$service = Get-Service ssh-agent -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "SSH Agent service found: $($service.Status)" -ForegroundColor Yellow
    
    if ($service.Status -eq 'Stopped') {
        Write-Host "Attempting to start SSH agent service..." -ForegroundColor Yellow
        Write-Host "Note: This may require Administrator privileges" -ForegroundColor Yellow
        
        try {
            Start-Service ssh-agent -ErrorAction Stop
            Set-Service -Name ssh-agent -StartupType Automatic -ErrorAction SilentlyContinue
            Write-Host "✓ SSH Agent service started" -ForegroundColor Green
            
            # Add key to agent
            ssh-add $env:USERPROFILE\.ssh\id_ed25519
            Write-Host "✓ SSH key added to agent" -ForegroundColor Green
            
            # Verify
            $keys = ssh-add -l 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Agent has keys loaded" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "⚠ Could not start SSH agent service (may need Admin)" -ForegroundColor Yellow
            Write-Host "  Git for Windows can use SSH keys directly without agent" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "✓ SSH Agent service is running" -ForegroundColor Green
        ssh-add $env:USERPROFILE\.ssh\id_ed25519 2>&1 | Out-Null
    }
}
else {
    Write-Host "⚠ SSH Agent service not found" -ForegroundColor Yellow
    Write-Host "  Git for Windows can use SSH keys directly" -ForegroundColor Yellow
}

# Step 4: Instructions
Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://github.com/settings/keys" -ForegroundColor White
Write-Host "2. Click 'New SSH key'" -ForegroundColor White
Write-Host "3. Title: 'TAMA38 Development - Windows'" -ForegroundColor White
Write-Host "4. Paste your public key (already in clipboard)" -ForegroundColor White
Write-Host "5. Click 'Add SSH key'" -ForegroundColor White
Write-Host ""
Write-Host "Then test connection:" -ForegroundColor Yellow
Write-Host "  ssh -T git@github.com" -ForegroundColor Cyan
Write-Host ""

# Step 5: Show public key again for reference
Write-Host "=== Your Public Key (for reference) ===" -ForegroundColor Cyan
Write-Host $publicKey -ForegroundColor White
Write-Host ""
