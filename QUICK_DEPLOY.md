# AWS App Runner Deployment via GitHub Actions

## Quick Solution for GitHub Connection Issues

Since AWS App Runner GitHub connection is experiencing loading issues, we can use **GitHub Actions + ECR deployment** as an alternative.

### Step 1: Setup AWS Credentials in GitHub

1. **Get AWS Access Keys:**
   ```bash
   # In AWS Console → IAM → Users → Your User → Security Credentials
   # Create Access Key for CLI/SDK usage
   ```

2. **Add GitHub Secrets:**
   - Go to: `https://github.com/hk-dev13/project-permit-api/settings/secrets/actions`
   - Add these secrets:
     - `AWS_ACCESS_KEY_ID`: Your AWS Access Key
     - `AWS_SECRET_ACCESS_KEY`: Your AWS Secret Key

### Step 2: Run GitHub Action

1. **Go to GitHub Actions:**
   - URL: `https://github.com/hk-dev13/project-permit-api/actions`
   - Click on "Deploy to AWS App Runner" workflow
   - Click "Run workflow" → "Run workflow"

2. **The action will:**
   - Build Docker image using `Dockerfile.apprunner`
   - Push to Amazon ECR
   - Provide image URI for App Runner

### Step 3: Create App Runner Service with ECR

After GitHub Action completes:

1. **In AWS App Runner Console:**
   - Create service
   - Source: **"Container registry"**
   - Provider: **Amazon ECR**
   - Container image URI: *(from GitHub Action output)*
   - Port: `8000`

2. **Service Configuration:**
   ```yaml
   Service name: permit-api-service
   CPU: 1 vCPU
   Memory: 2 GB
   Port: 8000
   Environment variables:
     FLASK_ENV: production
     FLASK_DEBUG: 0
     PORT: 8000
   ```

### Alternative: Manual ECR Push (Local Deployment)

### Prerequisites
1. **Install Docker Desktop** (if not installed)
2. **AWS CLI Setup:**
   ```powershell
   # AWS CLI already installed via pip in venv
   .\.venv\Scripts\python.exe -m awscli configure
   ```

### Manual Deployment Steps
```powershell
# Run the automated deployment script
.\deploy-ecr.ps1

# Or manual steps:
# 1. Test AWS credentials
.\.venv\Scripts\python.exe -m awscli sts get-caller-identity

# 2. Create ECR repository
.\.venv\Scripts\python.exe -m awscli ecr create-repository --repository-name permit-api --region ap-southeast-2

# 3. Get ECR login
$AWS_ACCOUNT_ID = (.\.venv\Scripts\python.exe -m awscli sts get-caller-identity --query Account --output text)
$LOGIN_PASSWORD = (.\.venv\Scripts\python.exe -m awscli ecr get-login-password --region ap-southeast-2)
echo $LOGIN_PASSWORD | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com"

# 4. Build and push
docker build -f Dockerfile.apprunner -t permit-api .
docker tag permit-api "$AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com/permit-api:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.ap-southeast-2.amazonaws.com/permit-api:latest"
```

## Next Steps

1. **Setup GitHub Secrets** (AWS credentials)
2. **Run GitHub Action** to build and push Docker image
3. **Create App Runner service** using ECR image URI
4. **Test deployment** once service is running

This approach bypasses the GitHub connection loading issue completely!
