# Secure AWS Credentials Setup

## 🔐 Secure Method to Configure AWS CLI

### Option 1: Environment Variables (Recommended)
Create a `.env` file with your credentials:

```powershell
# Create .env file
echo 'AWS_ACCESS_KEY_ID=your_new_access_key_here' > .env.aws
echo 'AWS_SECRET_ACCESS_KEY=your_new_secret_key_here' >> .env.aws
echo 'AWS_DEFAULT_REGION=ap-southeast-2' >> .env.aws
```

Then load them:
```powershell
# Load environment variables
Get-Content .env.aws | ForEach {
    $parts = $_.Split('=')
    [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], "User")
}
```

### Option 2: Manual Config File Edit
Edit AWS config files directly:

**Windows locations:**
- `%USERPROFILE%\.aws\credentials`
- `%USERPROFILE%\.aws\config`

**Credentials file content:**
```ini
[default]
aws_access_key_id = YOUR_NEW_ACCESS_KEY
aws_secret_access_key = YOUR_NEW_SECRET_KEY
```

**Config file content:**
```ini
[default]
region = ap-southeast-2
output = json
```

### Option 3: Use AWS CLI with input redirection
```powershell
# Create temporary input file
@'
YOUR_NEW_ACCESS_KEY
YOUR_NEW_SECRET_KEY
ap-southeast-2
json
'@ | .\.venv\Scripts\python.exe -m awscli configure
```

## 🎯 Next Steps After Setup

1. **Test credentials:**
   ```powershell
   .\.venv\Scripts\python.exe -m awscli sts get-caller-identity
   ```

2. **Test App Runner access:**
   ```powershell
   .\.venv\Scripts\python.exe -m awscli apprunner list-services --region ap-southeast-2
   ```

3. **Continue with App Runner service creation**

## 🚨 Security Best Practices

1. **Never paste credentials** in chat/terminal logs
2. **Use temporary credentials** when possible
3. **Rotate keys regularly**
4. **Delete unused access keys** immediately
5. **Use least privilege policies**

## 🔄 For GitHub Actions

Make sure to update GitHub Secrets with the new credentials:
- Repository Settings → Secrets and Variables → Actions
- Update `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
