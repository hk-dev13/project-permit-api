# PowerShell script for Docker deployment to AWS App Runner
param(
    [string]$AWSRegion = "ap-southeast-2",
    [string]$ECRRepository = "permit-api",
    [string]$ImageTag = "latest"
)

Write-Host "🚀 Building and deploying Permit API to AWS App Runner via ECR" -ForegroundColor Green
Write-Host "Region: $AWSRegion" -ForegroundColor Yellow
Write-Host "Repository: $ECRRepository" -ForegroundColor Yellow

# Get AWS Account ID
try {
    $AWSAccountID = aws sts get-caller-identity --query Account --output text 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "Account: $AWSAccountID" -ForegroundColor Yellow
}
catch {
    Write-Host "❌ AWS CLI not configured or not authenticated" -ForegroundColor Red
    Write-Host "Please run: aws configure" -ForegroundColor Yellow
    exit 1
}

# Create ECR repository if it doesn't exist
Write-Host "📦 Creating ECR repository..." -ForegroundColor Cyan
$repoExists = aws ecr describe-repositories --repository-names $ECRRepository --region $AWSRegion 2>$null
if ($LASTEXITCODE -ne 0) {
    aws ecr create-repository --repository-name $ECRRepository --region $AWSRegion
}

# Get ECR login token
Write-Host "🔐 Authenticating Docker with ECR..." -ForegroundColor Cyan
$loginPassword = aws ecr get-login-password --region $AWSRegion
if ($LASTEXITCODE -eq 0) {
    echo $loginPassword | docker login --username AWS --password-stdin "$AWSAccountID.dkr.ecr.$AWSRegion.amazonaws.com"
}

# Build Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Cyan
docker build -f Dockerfile.apprunner -t "${ECRRepository}:${ImageTag}" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Tag image for ECR
$ECRURI = "$AWSAccountID.dkr.ecr.$AWSRegion.amazonaws.com/${ECRRepository}:${ImageTag}"
docker tag "${ECRRepository}:${ImageTag}" $ECRURI

# Push to ECR
Write-Host "📤 Pushing image to ECR..." -ForegroundColor Cyan
docker push $ECRURI

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image pushed successfully!" -ForegroundColor Green
    Write-Host "ECR URI: $ECRURI" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "1. Go to AWS App Runner console" -ForegroundColor White
    Write-Host "2. Choose 'Container registry' as source" -ForegroundColor White
    Write-Host "3. Use this image URI: $ECRURI" -ForegroundColor Cyan
    Write-Host "4. Configure service settings" -ForegroundColor White
} else {
    Write-Host "❌ Docker push failed" -ForegroundColor Red
    exit 1
}
