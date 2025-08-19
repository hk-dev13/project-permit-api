# Production Deployment Checklist for AWS App Runner

## 🚀 Pre-Deployment Checklist

### Code Preparation
- ✅ All tests passing (`pytest tests/`)
- ✅ Security implementation tested (`python test_security.py`)
- ✅ Production environment variables configured
- ✅ Production API keys generated and secured
- ✅ CORS origins configured for production domain
- ✅ Logging configuration optimized for production
- ✅ Sample data disabled or minimized for production
- ✅ Debug mode disabled (`FLASK_DEBUG=0`)

### Files Required in Repository
- ✅ `apprunner.yaml` - App Runner build/runtime configuration
- ✅ `requirements.txt` - All dependencies with locked versions  
- ✅ `run_server.py` - Production startup script
- ✅ `wsgi.py` - WSGI entry point for Gunicorn
- ✅ `.env.production` - Production environment template
- ✅ `AWS_DEPLOYMENT_GUIDE.md` - Deployment documentation

### Security Checklist
- ✅ Production API keys generated (not demo keys)
- ✅ Master API key is cryptographically secure
- ✅ Environment variables contain no hardcoded secrets
- ✅ CORS configured for specific domains (not *)
- ✅ Rate limiting enabled and tested
- ✅ Input validation implemented
- ✅ Error messages don't expose sensitive information

## 📋 Deployment Steps

### 1. AWS Account Setup
- ✅ AWS account with App Runner permissions
- ✅ IAM user/role with necessary permissions:
  - `AWSAppRunnerServicePolicyForECRAccess`
  - `AWSAppRunnerServicePolicy` 
- ✅ GitHub account connected to AWS (if using GitHub source)

### 2. Repository Preparation  
- ✅ Code pushed to `main` branch
- ✅ Repository is public or AWS has access to private repo
- ✅ All deployment files committed and pushed

### 3. AWS App Runner Configuration

**Service Settings:**
```
Service name: permit-api-prod
Source: GitHub repository
Repository: your-username/project-permit-api  
Branch: main
Build configuration: Use configuration file (apprunner.yaml)
```

**Compute Configuration:**
```
CPU: 1 vCPU
Memory: 2 GB  
Environment variables: (see below)
```

**Auto Scaling:**
```
Minimum size: 1 instance
Maximum size: 3 instances  
Max concurrency: 100 requests per instance
```

**Environment Variables (REQUIRED):**
```
FLASK_ENV=production
FLASK_DEBUG=0
PORT=8000
API_KEYS=your_prod_basic:ProductionBasic:basic,your_prod_premium:ProductionPremium:premium
MASTER_API_KEY=your_secure_master_key_here
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
PYTHONPATH=/opt/app
PYTHONUNBUFFERED=1
```

### 4. Health Check Configuration
```
Health check path: /health
Interval: 20 seconds
Timeout: 5 seconds
Healthy threshold: 1
Unhealthy threshold: 5
```

### 5. Custom Domain (Optional)
- ✅ Domain name purchased and managed in Route 53 (or external DNS)
- ✅ SSL certificate will be auto-provisioned
- ✅ DNS validation completed

## ✅ Post-Deployment Verification

### Immediate Tests (within 5 minutes)
```bash
# Replace with your actual App Runner URL
export API_URL="https://abc123.us-east-1.awsapprunner.com"

# 1. Health check
curl -f "$API_URL/health"

# 2. Public endpoint  
curl -f "$API_URL/"

# 3. Protected endpoint without key (should return 401)
curl "$API_URL/global/emissions"

# 4. Protected endpoint with production API key
curl -H "Authorization: Bearer your_prod_basic_key" \
  "$API_URL/global/emissions?limit=5"

# 5. Admin endpoint (premium key required)
curl -H "Authorization: Bearer your_prod_premium_key" \
  "$API_URL/admin/stats"
```

### Extended Tests (within 30 minutes)
- ✅ All major endpoints responding correctly
- ✅ Rate limiting working (test with multiple rapid requests)
- ✅ CORS headers present for your domain
- ✅ Error handling working (test invalid API keys)
- ✅ Performance acceptable (< 2 second response times)
- ✅ Memory usage stable (check App Runner metrics)

### Monitoring Setup
- ✅ CloudWatch logs accessible
- ✅ CloudWatch metrics showing data
- ✅ Alarms configured for:
  - High error rate (> 5%)
  - High response time (> 5 seconds)  
  - High memory usage (> 80%)
  - Low health check success rate (< 90%)

## 🔧 Production Configuration

### Environment Variables Explanation
```bash
# Core Flask settings
FLASK_ENV=production          # Enables production optimizations
FLASK_DEBUG=0                # Disables debug mode and error traces
PORT=8000                    # App Runner default port

# Security
API_KEYS=key1:name1:tier1,key2:name2:tier2  # Production API keys
MASTER_API_KEY=secure_key    # Administrative access key  
CORS_ORIGINS=https://yourdomain.com         # Restrict CORS

# Logging
LOG_LEVEL=INFO               # Production logging level
LOG_FILE=/opt/app/logs/app.log             # Log file path

# Performance  
PYTHONUNBUFFERED=1           # Immediate stdout/stderr output
PYTHONPATH=/opt/app          # Python module resolution
```

### Resource Sizing Guide
```
Development:  0.25 vCPU, 0.5 GB RAM  (~$5/month)
Staging:      0.5 vCPU,  1 GB RAM    (~$12/month)  
Production:   1 vCPU,    2 GB RAM    (~$25/month)
High-traffic: 2 vCPU,    4 GB RAM    (~$50/month)
```

### Auto-Scaling Configuration
```
Light traffic:     Min 1, Max 2, Concurrency 80
Medium traffic:    Min 1, Max 3, Concurrency 100  
Heavy traffic:     Min 2, Max 5, Concurrency 120
```

## 🚨 Troubleshooting Guide

### Build Failures
1. **Python version issues**: Ensure Python 3.11 compatibility
2. **Dependency conflicts**: Check `requirements.txt` for version mismatches
3. **Missing files**: Verify all required files are committed to Git
4. **Build timeout**: Reduce dependencies or optimize build process

### Runtime Failures  
1. **Port binding**: Ensure app binds to `0.0.0.0:$PORT`
2. **Health check failures**: Verify `/health` endpoint returns 200
3. **Memory issues**: Monitor memory usage in CloudWatch
4. **Import errors**: Check `PYTHONPATH` and module structure

### Performance Issues
1. **Slow responses**: Check database connections and API timeouts
2. **High memory usage**: Review caching configuration
3. **Rate limiting**: Verify rate limits are appropriate for traffic
4. **Cold starts**: Consider keeping minimum instances > 0

## 📞 Support & Monitoring

### Key Metrics to Monitor
- **Request volume**: Requests per minute/hour
- **Response time**: 95th percentile response time
- **Error rate**: 4xx and 5xx error percentage  
- **Memory usage**: Average and peak memory utilization
- **CPU usage**: Average CPU utilization
- **Health check success rate**: Percentage of successful health checks

### Alerting Thresholds
- **Error rate > 5%**: Critical alert
- **Response time > 5 seconds**: Warning alert
- **Memory usage > 80%**: Warning alert
- **Health check success < 90%**: Critical alert

### Log Analysis
```bash
# View recent logs
aws logs tail /aws/apprunner/permit-api-prod --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/apprunner/permit-api-prod \
  --filter-pattern "ERROR"

# Monitor API key usage
aws logs filter-log-events \
  --log-group-name /aws/apprunner/permit-api-prod \
  --filter-pattern "API key"
```

---

## 🎉 Success!

Once all checklist items are complete, your Environmental Data Verification API is live in production on AWS App Runner!

**Next Steps:**
1. Update your documentation with the production URL
2. Notify your users about the new production API
3. Monitor the service for the first 24 hours
4. Set up regular backups if using databases
5. Plan for the next deployment cycle
