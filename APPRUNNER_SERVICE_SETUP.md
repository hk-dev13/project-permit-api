# AWS App Runner Service Role Configuration

## 🔐 Service Role Requirements

AWS App Runner membutuhkan IAM service role untuk mengakses ECR dan layanan AWS lainnya.

### Option 1: Auto-create Service Role (Recommended)
Saat membuat App Runner service, pilih **"Create new service role"** - AWS akan otomatis membuat role dengan permissions yang tepat.

### Option 2: Manual Service Role Creation

#### 1. Create IAM Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### 2. Attach Policy
Role name: `AppRunnerECRAccessRole`

**AWS Managed Policy:**
- `AWSAppRunnerServicePolicyForECRAccess`

**Or Custom Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:DescribeRepositories",
        "ecr:DescribeImages"
      ],
      "Resource": "arn:aws:ecr:ap-southeast-2:147845229604:repository/permit-api"
    }
  ]
}
```

## 📋 App Runner Service Configuration

### Container Configuration
```yaml
Source: Container registry
Provider: Amazon ECR
Container image URI: 147845229604.dkr.ecr.ap-southeast-2.amazonaws.com/permit-api:latest
Deployment trigger: Manual
```

### Build Configuration
```yaml
Service role: AppRunnerECRAccessRole (or auto-created)
```

### Service Configuration
```yaml
Service name: permit-api-service
Virtual CPU: 1 vCPU
Virtual memory: 2 GB
Port: 8000
Environment variables:
  FLASK_ENV: production
  FLASK_DEBUG: 0
  PORT: 8000
  API_KEYS: demo_basic_key:DemoBasic:basic,demo_premium_key:DemoPremium:premium
  MASTER_API_KEY: demo_master_key_12345
  LOG_LEVEL: INFO
```

### Auto-scaling Configuration
```yaml
Minimum size: 1
Maximum size: 3
Max concurrency: 100 per instance
```

### Health Check Configuration
```yaml
Health check path: /health
Health check interval: 20 seconds
Health check timeout: 5 seconds
Healthy threshold: 1
Unhealthy threshold: 5
```

## 🚀 Step-by-Step Creation

1. **AWS App Runner Console**: https://ap-southeast-2.console.aws.amazon.com/apprunner/home
2. **Create service** → Container registry
3. **ECR Image**: `147845229604.dkr.ecr.ap-southeast-2.amazonaws.com/permit-api:latest`
4. **Service role**: Choose "Create new service role" or select existing `AppRunnerECRAccessRole`
5. **Configure** service settings as above
6. **Review and create**

## ✅ Verification Steps

After deployment:
1. **Check service status**: Should show "Running"
2. **Test health endpoint**: `https://your-app-url.awsapprunner.com/health`
3. **Test API with key**:
   ```bash
   curl -H "Authorization: Bearer demo_basic_key" \
     "https://your-app-url.awsapprunner.com/global/emissions?limit=5"
   ```

## 🔧 Troubleshooting

**Common Issues:**
- **Service role permissions**: Ensure ECR access is granted
- **Container port**: Must match Dockerfile EXPOSE 8000
- **Health check**: Verify `/health` endpoint responds
- **Environment variables**: Check all required vars are set
