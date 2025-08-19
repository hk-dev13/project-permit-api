# App Runner Minimal Configuration (Bypass Auto-scaling Issue)

## 🚀 Quick Service Creation

### Skip Auto-scaling Configuration
1. **Cancel** the auto-scaling dialog
2. Use **default scaling settings**:
   - Min instances: 1
   - Max instances: 25
   - Concurrency: 100

### Required Configuration Only
```yaml
Service name: permit-api-service
ECR Image URI: 147845229604.dkr.ecr.ap-southeast-2.amazonaws.com/permit-api:latest
Port: 8000
CPU: 1 vCPU
Memory: 2 GB

Environment Variables:
  FLASK_ENV: production
  PORT: 8000
  API_KEYS: demo_basic_key:DemoBasic:basic
  MASTER_API_KEY: demo_master_key_12345
```

### Health Check (Optional)
```yaml
Path: /health
Interval: 20s
Timeout: 5s
```

## 🔧 Troubleshooting Account Issues

### Check AWS Account
1. **Billing Console**: Ensure payment method is active
2. **Region**: Switch to `us-east-1` if `ap-southeast-2` has issues
3. **Account Status**: Check if account is fully activated

### Alternative Regions for App Runner
- **US East (N. Virginia)**: `us-east-1`
- **US West (Oregon)**: `us-west-2` 
- **Europe (Ireland)**: `eu-west-1`
- **Asia Pacific (Tokyo)**: `ap-northeast-1`

### Command Line Check
```powershell
# Check if App Runner is available in your region
.\.venv\Scripts\python.exe -m awscli apprunner list-services --region ap-southeast-2

# If error, try different region
.\.venv\Scripts\python.exe -m awscli apprunner list-services --region us-east-1
```
