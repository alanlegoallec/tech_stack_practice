#!/bin/sh
set -e

PROFILE="devops-full-stack-practice"

ENV_NAMES=("full-stack-practice-backend-env" "full-stack-practice-frontend-env")

echo "👉 Select environment to connect via SSM:"
i=1
for ENV in "${ENV_NAMES[@]}"; do
    echo "$i) $ENV"
    i=$((i+1))
done

read -p "Enter choice [1-${#ENV_NAMES[@]}]: " CHOICE

INDEX=$((CHOICE - 1))

if [ "$INDEX" -lt 0 ] || [ "$INDEX" -ge "${#ENV_NAMES[@]}" ]; then
    echo "❌ Invalid choice"
    exit 1
fi

ENV_NAME="${ENV_NAMES[$INDEX]}"

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
