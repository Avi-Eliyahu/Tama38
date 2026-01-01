# How to Add SSH Key to GitHub - Step by Step

## Your SSH Public Key

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILwsEw1QyfqjeCRVVvYgM0ZgpSs1a+xvvWMe9Ekp/bGJ avraham.eliyahu@example.com
```

**This key is already copied to your clipboard!**

---

## Step-by-Step Instructions

### Step 1: Go to GitHub SSH Settings

1. Open your web browser
2. Go to: **https://github.com/settings/keys**
3. Make sure you're logged into your GitHub account

### Step 2: Add New SSH Key

1. Click the green button: **"New SSH key"** (top right)
2. You'll see a form with:
   - **Title** (required)
   - **Key** (required)
   - **Key type** (auto-detected)

### Step 3: Fill in the Form

**Title field:**
```
TAMA38 Development - Windows
```
(or any name you prefer)

**Key field:**
- Paste your public key (already in clipboard)
- Make sure you paste the ENTIRE key:
  ```
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILwsEw1QyfqjeCRVVvYgM0ZgpSs1a+xvvWMe9Ekp/bGJ avraham.eliyahu@example.com
  ```
- It should be ONE line
- Starts with `ssh-ed25519`
- Ends with your email

**Key type:**
- Should auto-detect as "Authentication Key"
- If not, select "Authentication Key"

### Step 4: Save the Key

1. Click **"Add SSH key"** button
2. GitHub may ask for your password (2FA if enabled)
3. After confirmation, you'll see your key listed

### Step 5: Verify It's Added

You should see:
- ✅ Your key listed on the page
- ✅ Title: "TAMA38 Development - Windows"
- ✅ Key type: "Authentication Key"
- ✅ Last used: "Never" (will update after first use)

---

## Test the Connection

After adding the key, go back to PowerShell and test:

```powershell
ssh -T git@github.com
```

**Expected Success Message:**
```
Hi YOUR_USERNAME! You've successfully authenticated, but GitHub does not provide shell access.
```

If you see this, SSH is working! ✅

---

## Troubleshooting

### Still Getting "Permission denied"?

**Wait a moment**: GitHub may need 10-30 seconds to sync the key.

**Check**:
1. Did you copy the ENTIRE key? (all three parts)
2. Is there any extra spaces or line breaks?
3. Did you click "Add SSH key" button?
4. Did GitHub ask for password confirmation?

**Verify key format**:
- Must start with: `ssh-ed25519`
- Must contain: Long base64 string
- Must end with: Your email
- Must be: ONE continuous line (no breaks)

**Try again**:
```powershell
# Wait 30 seconds, then:
ssh -T git@github.com
```

### Wrong GitHub Account?

Make sure you added the key to the correct GitHub account!

---

## Quick Checklist

- [ ] Logged into GitHub
- [ ] Went to https://github.com/settings/keys
- [ ] Clicked "New SSH key"
- [ ] Entered title
- [ ] Pasted ENTIRE public key (one line)
- [ ] Clicked "Add SSH key"
- [ ] Confirmed with password/2FA
- [ ] Key appears in list
- [ ] Tested connection: `ssh -T git@github.com`

---

## Alternative: Use HTTPS Instead

If SSH continues to cause issues, you can use HTTPS with Personal Access Token:

1. **Generate PAT**: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select `repo` scope
   - Copy token (save it!)

2. **Use HTTPS URL**:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/tama38.git
   ```

3. **When pushing**: Use PAT as password

---

**After adding the key, test the connection!**

