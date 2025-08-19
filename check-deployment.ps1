# Check GitHub Actions and AWS deployment status

Write-Host "🔍 Deployment Status Checker" -ForegroundColor Green
Write-Host ""

# GitHub Actions URL
$REPO_URL = "https://github.com/hk-dev13/project-permit-api"
$ACTIONS_URL = "$REPO_URL/actions"

Write-Host "📋 Quick Links:" -ForegroundColor Yellow
Write-Host "GitHub Actions: $ACTIONS_URL" -ForegroundColor Cyan
Write-Host "AWS App Runner:  https://ap-southeast-2.console.aws.amazon.com/apprunner/home" -ForegroundColor Cyan
Write-Host "AWS ECR:        https://ap-southeast-2.console.aws.amazon.com/ecr/repositories" -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is working (with new credentials)
Write-Host "🔐 Testing AWS Access..." -ForegroundColor Yellow
try {
    $AccountOutput = .\.venv\Scripts\python.exe -m awscli sts get-caller-identity 2>$null
    if ($LASTEXITCODE -eq 0) {
        $AccountInfo = $AccountOutput | ConvertFrom-Json
        Write-Host "✅ AWS Account: $($AccountInfo.Account)" -ForegroundColor Green
        Write-Host "✅ User: $($AccountInfo.Arn)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Local AWS credentials not configured (that's OK - using GitHub Actions)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️  Local AWS CLI test failed (that's OK - using GitHub Actions)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Next Steps After GitHub Actions Completes:" -ForegroundColor Green
Write-Host "1. Check Actions tab for ECR image URI" -ForegroundColor White
Write-Host "2. Go to AWS App Runner Console" -ForegroundColor White
Write-Host "3. Create Service → Container Registry" -ForegroundColor White
Write-Host "4. Use ECR image URI from Actions output" -ForegroundColor White
Write-Host "5. Set port: 8000" -ForegroundColor White
Write-Host ""

# Open browser to actions page
Write-Host "Opening GitHub Actions page..." -ForegroundColor Cyan
Start-Process $ACTIONS_URL

Write-Host "✨ Ready for deployment!" -ForegroundColor Green
