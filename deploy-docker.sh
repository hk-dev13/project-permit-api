#!/bin/bash
# Docker deployment script for AWS App Runner

# Configuration
AWS_REGION="ap-southeast-2"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
ECR_REPOSITORY="permit-api"
IMAGE_TAG="latest"

echo "🚀 Building and deploying Permit API to AWS App Runner via ECR"
echo "Region: $AWS_REGION"
echo "Account: $AWS_ACCOUNT_ID"
echo "Repository: $ECR_REPOSITORY"

# Check if AWS CLI is configured
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "❌ AWS CLI not configured or not authenticated"
    echo "Please run: aws configure"
    exit 1
fi

# Create ECR repository if it doesn't exist
echo "📦 Creating ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION >/dev/null 2>&1 || \
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# Get ECR login token
echo "🔐 Authenticating Docker with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.apprunner -t $ECR_REPOSITORY:$IMAGE_TAG .

# Tag image for ECR
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG"
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI

# Push to ECR
echo "📤 Pushing image to ECR..."
docker push $ECR_URI

echo "✅ Docker image pushed successfully!"
echo "ECR URI: $ECR_URI"
echo ""
echo "Next steps:"
echo "1. Go to AWS App Runner console"
echo "2. Choose 'Container registry' as source"
echo "3. Use this image URI: $ECR_URI"
echo "4. Configure service settings"
