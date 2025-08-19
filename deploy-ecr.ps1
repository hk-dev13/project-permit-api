# PowerShell script for ECR deployment (Windows)
param(
    [string]$AWSRegion = "ap-southeast-2",
    [string]$ECRRepository = "permit-api",
    [string]$ImageTag = "latest"
)

Write-Host "🔐 AWS CLI ECR Deployment Script" -ForegroundColor Green
Write-Host "Region: $AWSRegion" -ForegroundColor Yellow

# Use AWS CLI from venv
$AWS_CMD = ".\.venv\Scripts\python.exe -m awscli"

# Test AWS credentials
Write-Host "🔍 Testing AWS credentials..." -ForegroundColor Cyan
try {
    $AccountOutput = & cmd /c "$AWS_CMD sts get-caller-identity 2>nul"
    if ($LASTEXITCODE -eq 0) {
        $AccountInfo = $AccountOutput | ConvertFrom-Json
        $AWSAccountID = $AccountInfo.Account
        Write-Host "✅ AWS Account: $AWSAccountID" -ForegroundColor Green
    } else {
        throw "AWS credentials test failed"
    }
}
catch {
    Write-Host "❌ AWS CLI not configured or credentials invalid" -ForegroundColor Red
    Write-Host "Please run: .\.venv\Scripts\python.exe -m awscli configure" -ForegroundColor Yellow
    Write-Host "Make sure to use fresh AWS Access Keys!" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is available
Write-Host "🐳 Checking Docker..." -ForegroundColor Cyan
try {
    docker --version | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is available" -ForegroundColor Green
    } else {
        throw "Docker not found"
    }
}
catch {
    Write-Host "❌ Docker not installed" -ForegroundColor Red
    Write-Host "Please install Docker Desktop or use GitHub Actions deployment" -ForegroundColor Yellow
    Write-Host "GitHub Actions URL: https://github.com/hk-dev13/project-permit-api/actions" -ForegroundColor Cyan
    exit 1
}

# Create ECR repository if needed
Write-Host "📦 Setting up ECR repository..." -ForegroundColor Cyan
$RepoCheck = & cmd /c "$AWS_CMD ecr describe-repositories --repository-names $ECRRepository --region $AWSRegion 2>nul"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating ECR repository: $ECRRepository" -ForegroundColor Yellow
    & cmd /c "$AWS_CMD ecr create-repository --repository-name $ECRRepository --region $AWSRegion"
}

# Login to ECR
Write-Host "🔐 Logging into ECR..." -ForegroundColor Cyan
$LoginPassword = & cmd /c "$AWS_CMD ecr get-login-password --region $AWSRegion"
if ($LASTEXITCODE -eq 0) {
    echo $LoginPassword | docker login --username AWS --password-stdin "$AWSAccountID.dkr.ecr.$AWSRegion.amazonaws.com"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ ECR login successful" -ForegroundColor Green
    } else {
        Write-Host "❌ ECR login failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Failed to get ECR login token" -ForegroundColor Red
    exit 1
}

# Build Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Cyan
docker build -f Dockerfile.apprunner -t "${ECRRepository}:${ImageTag}" .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Tag and push image
$ECRURI = "$AWSAccountID.dkr.ecr.$AWSRegion.amazonaws.com/${ECRRepository}:${ImageTag}"
Write-Host "🏷️ Tagging image: $ECRURI" -ForegroundColor Cyan
docker tag "${ECRRepository}:${ImageTag}" $ECRURI

Write-Host "📤 Pushing to ECR..." -ForegroundColor Cyan
docker push $ECRURI

if ($LASTEXITCODE -eq 0) {
    Write-Host "" -ForegroundColor Green
    Write-Host "🎉 SUCCESS! Docker image pushed to ECR" -ForegroundColor Green
    Write-Host "" -ForegroundColor Green
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Go to AWS App Runner Console" -ForegroundColor White
    Write-Host "2. Create Service → Container Registry" -ForegroundColor White
    Write-Host "3. Use this ECR Image URI:" -ForegroundColor White
    Write-Host "   $ECRURI" -ForegroundColor Cyan
    Write-Host "4. Set Port: 8000" -ForegroundColor White
    Write-Host "5. Add Environment Variables:" -ForegroundColor White
    Write-Host "   FLASK_ENV=production" -ForegroundColor Gray
    Write-Host "   FLASK_DEBUG=0" -ForegroundColor Gray
    Write-Host "   PORT=8000" -ForegroundColor Gray
    Write-Host "" -ForegroundColor Green
    Write-Host "🌐 App Runner Console:" -ForegroundColor Yellow  
    Write-Host "   https://ap-southeast-2.console.aws.amazon.com/apprunner/home" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to push image to ECR" -ForegroundColor Red
    exit 1
}
