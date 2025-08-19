# AWS App Runner Deployment Guide

## 🚀 Quick Deployment Steps

### Prerequisites
- AWS Account with appropriate permissions
- GitHub repository with your code
- AWS CLI installed (optional, for advanced configuration)

### Step 1: Prepare Your Repository

Ensure these files are in your repository root:
- ✅ `apprunner.yaml` - App Runner configuration
- ✅ `requirements.txt` - Python dependencies  
- ✅ `run_server.py` - Application startup script
- ✅ `wsgi.py` - WSGI entry point
- ✅ `.env.production` - Production environment template

### Step 2: Deploy via AWS Console

1. **Open AWS App Runner Console**
   - Go to: https://console.aws.amazon.com/apprunner/
   - Click "Create an App Runner service"

2. **Configure Source**
   - Source: "Source code repository"
   - Repository type: GitHub
   - Connect to your GitHub account
   - Select repository: `your-username/project-permit-api`  
   - Branch: `main`
   - Deployment trigger: "Automatic" (deploys on push)

3. **Configure Build**
   - Configuration file: "Use configuration file" 
   - Configuration file: `apprunner.yaml`

4. **Configure Service**
   - Service name: `permit-api-prod`
   - Virtual CPU: `1 vCPU` 
   - Virtual memory: `2 GB`
   - Environment variables (click "Add environment variable"):

   **Required Variables:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0  
   API_KEYS=your_prod_basic_key:ProductionBasic:basic,your_prod_premium_key:ProductionPremium:premium
   MASTER_API_KEY=your_secure_master_key_here
   LOG_LEVEL=INFO
   CORS_ORIGINS=*
   ```

5. **Configure Auto Scaling** 
   - Minimum size: 1
   - Maximum size: 3
   - Max concurrency: 100 per instance

6. **Configure Health Check**
   - Health check path: `/health`
   - Health check interval: 20 seconds
   - Health check timeout: 5 seconds
   - Healthy threshold: 1
   - Unhealthy threshold: 5

7. **Configure Security (Optional)**
   - Create VPC connector if needed for database access
   - Configure IAM roles if accessing other AWS services

8. **Review and Create**
   - Review all settings
   - Click "Create & deploy"

### Step 3: Monitor Deployment

1. **Check Build Status**
   - Monitor the "Activity" tab in App Runner console
   - Build typically takes 3-5 minutes

2. **Test Your API**
   - Once deployed, you'll get a URL like: `https://abc123.us-east-1.awsapprunner.com`
   - Test health: `curl https://your-url.awsapprunner.com/health`
   - Test with API key: 
   ```bash
   curl -H "Authorization: Bearer your_prod_basic_key" \
     "https://your-url.awsapprunner.com/global/emissions?limit=5"
   ```

## 🔧 Advanced Configuration

### Custom Domain Setup

1. **In App Runner Console:**
   - Go to your service → "Custom domains" tab  
   - Click "Link domain"
   - Enter your domain (e.g., `api.yourcompany.com`)
   - Follow DNS validation steps

2. **DNS Configuration:**
   - Add CNAME record pointing to App Runner URL
   - Certificate will be auto-provisioned via AWS Certificate Manager

### Environment-Specific Configurations

**Staging Environment:**
```
Service name: permit-api-staging
Environment: FLASK_ENV=staging
Resources: 0.5 vCPU, 1 GB RAM
Auto-scaling: Min 1, Max 2
```

**Production Environment:**  
```
Service name: permit-api-prod
Environment: FLASK_ENV=production  
Resources: 1 vCPU, 2 GB RAM
Auto-scaling: Min 1, Max 5
```

### Monitoring & Logging

**CloudWatch Integration:**
- App Runner automatically sends logs to CloudWatch
- Metrics available: CPU, Memory, Request count, Response time
- Set up alarms for high error rates or resource usage

**Custom Monitoring:**
```python
# Add to your Flask app
import boto3
cloudwatch = boto3.client('cloudwatch')

# Custom metrics
cloudwatch.put_metric_data(
    Namespace='PermitAPI',
    MetricData=[{
        'MetricName': 'APIRequests',
        'Value': 1,
        'Unit': 'Count'
    }]
)
```

## 🔒 Security Best Practices

### Environment Variables
- **Never commit production keys to Git**
- Use AWS Systems Manager Parameter Store for sensitive values
- Rotate API keys regularly

### Network Security
- Use VPC connector for database connections
- Configure WAF if needed for additional protection
- Enable AWS Shield for DDoS protection

### Access Control
```python
# Update CORS for production
CORS_ORIGINS=https://yourapp.com,https://api.yourcompany.com
```

## 📊 Cost Optimization

### Right-Sizing Resources
- **Development**: 0.25 vCPU, 0.5 GB RAM (~$5/month)
- **Production**: 1 vCPU, 2 GB RAM (~$25/month)
- **Enterprise**: 2 vCPU, 4 GB RAM (~$50/month)

### Auto-Scaling Configuration
```yaml
# Optimize for cost
Min instances: 0 (for dev/staging)
Max instances: 3 (for production)
Max concurrency: 80 (balance latency vs cost)
```

## 🚨 Troubleshooting

### Common Issues

**Build Failures:**
- Check `requirements.txt` for version conflicts
- Verify Python 3.11 compatibility
- Check build logs in App Runner console

**Health Check Failures:**  
- Ensure `/health` endpoint returns 200 status
- Check if app is binding to `0.0.0.0:PORT`
- Verify PORT environment variable is used

**API Key Issues:**
- Check environment variables are set correctly
- Test with demo keys first
- Verify API key format in requests

### Debug Commands

```bash
# Local testing
python run_server.py

# Test API endpoints
curl -H "Authorization: Bearer demo_key_basic_2025" \
  "http://localhost:5000/global/emissions?limit=1"

# Check logs
aws logs tail /aws/apprunner/permit-api-prod --follow
```

## 📝 Post-Deployment Checklist

- ✅ Health check returning 200
- ✅ API key authentication working  
- ✅ Rate limiting active
- ✅ CORS configured correctly
- ✅ Monitoring enabled
- ✅ Custom domain configured (if needed)
- ✅ SSL certificate active
- ✅ Production API keys rotated
- ✅ Documentation updated with new URL

## 🎯 Next Steps

1. **Set up monitoring dashboards**
2. **Configure automated backups** (if using databases)
3. **Implement CI/CD pipeline** with GitHub Actions
4. **Set up staging environment** 
5. **Configure alerts** for errors and performance issues

---

**Your API will be available at:** `https://[unique-id].us-east-1.awsapprunner.com`

**Documentation:** Update your API documentation with the production URL and new authentication requirements.
