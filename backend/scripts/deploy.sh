#!/bin/bash
set -euo pipefail
export AWS_PAGER=""

###############################################################################
# 📝 Shared Deploy Script (ZIP-based, Git-free safe)
#
# This script is IDENTICAL in both backend/scripts/ and frontend/scripts/.
# If you modify it in one location, you MUST copy it to the other to stay in sync.
#
# Usage:
#   ./scripts/deploy.sh <aws_profile> <app_dir> <env_name> <app_name> [config_name]
#
# Example (Backend):
#   ./scripts/deploy.sh deployer-full-stack-practice backend full-stack-practice-backend-env backend backend-with-sg
#
# Example (Frontend):
#   ./scripts/deploy.sh deployer-full-stack-practice frontend full-stack-practice-frontend-env frontend
###############################################################################

# Input arguments
PROFILE="${1:-default}"
APP_DIR="$2"
ENV_NAME="$3"
APP_NAME="$4"
CONFIG_NAME="${5:-}"

REGION="us-east-1"
PLATFORM="Docker"

cd "$APP_DIR"

echo "🔍 Checking if EB environment '$ENV_NAME' exists..."

# Determine CLI profile flags
EB_PROFILE_FLAG=""
AWS_CLI_PROFILE_ARGS=""
if [[ "$PROFILE" != "default" && -z "${GITHUB_ACTIONS:-}" ]]; then
  EB_PROFILE_FLAG="--profile $PROFILE"
  AWS_CLI_PROFILE_ARGS="--profile $PROFILE"
fi

# ⚙️ Ensure EB CLI is initialized
if [[ ! -d .elasticbeanstalk ]]; then
  echo "⚙️ Running eb init..."
  eb init "$APP_NAME" \
    --platform "$PLATFORM" \
    --region "$REGION" \
    $EB_PROFILE_FLAG \
    --quiet
else
  echo "🔄 Reusing existing .elasticbeanstalk config."
fi

# 🌱 Create environment if needed
if ! aws elasticbeanstalk describe-environments \
  --region "$REGION" \
  --environment-names "$ENV_NAME" \
  $AWS_CLI_PROFILE_ARGS \
  | grep -q '"Status":'; then

  echo "🌱 Creating EB environment '$ENV_NAME'..."
  if [[ -n "$CONFIG_NAME" ]]; then
    eb create "$ENV_NAME" --cfg "$CONFIG_NAME" $EB_PROFILE_FLAG
  else
    eb create "$ENV_NAME" $EB_PROFILE_FLAG
  fi
else
  echo "✅ Environment '$ENV_NAME' already exists."
fi

# 📌 Set the current environment
eb use "$ENV_NAME" $EB_PROFILE_FLAG

# 📦 Manually create version archive to guarantee .ebextensions is included
VERSION_LABEL="v$(date +%Y%m%d_%H%M%S)"
ZIP_FILE="app-$VERSION_LABEL.zip"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text $AWS_CLI_PROFILE_ARGS)
S3_BUCKET="elasticbeanstalk-$REGION-$ACCOUNT_ID"
S3_KEY="$APP_NAME/$ZIP_FILE"

echo "📦 Packaging source bundle: $ZIP_FILE"
zip -r "$ZIP_FILE" . -x '*.git*' '*.DS_Store*' '.elasticbeanstalk/*' > /dev/null

echo "☁️ Uploading ZIP to S3: s3://$S3_BUCKET/$S3_KEY"
aws s3 cp "$ZIP_FILE" "s3://$S3_BUCKET/$S3_KEY" $AWS_CLI_PROFILE_ARGS

echo "📝 Registering application version '$VERSION_LABEL'..."
aws elasticbeanstalk create-application-version \
  --application-name "$APP_NAME" \
  --version-label "$VERSION_LABEL" \
  --source-bundle S3Bucket="$S3_BUCKET",S3Key="$S3_KEY" \
  --region "$REGION" \
  $AWS_CLI_PROFILE_ARGS

echo "🚀 Deploying version '$VERSION_LABEL'..."
eb deploy --version "$VERSION_LABEL" $EB_PROFILE_FLAG

# 🧹 Cleanup
rm -f "$ZIP_FILE"
echo "✅ Deployment complete."
