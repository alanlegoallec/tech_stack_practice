#!/bin/sh
set -e

PROFILE="devops-full-stack-practice"

if [ -z "$1" ]; then
  echo "❌ Usage: $0 <environment-name>"
  echo "Example: $0 full-stack-practice-backend-env"
  exit 1
fi

ENV_NAME="$1"

echo "🔍 Finding EC2 instance for environment: $ENV_NAME"

INSTANCE_ID=$(aws elasticbeanstalk describe-environment-resources \
  --environment-name "$ENV_NAME" \
  --query "EnvironmentResources.Instances[0].Id" \
  --output text \
  --profile "$PROFILE")

if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" = "None" ]; then
  echo "❌ No running EC2 instance found for $ENV_NAME"
  exit 1
fi

echo "✅ Found instance: $INSTANCE_ID"
echo "🚀 Starting SSM session..."
aws ssm start-session --target "$INSTANCE_ID" --profile "$PROFILE"
