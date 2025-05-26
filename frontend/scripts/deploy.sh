#!/bin/bash
set -euo pipefail

###############################################################################
# 📝 Shared Deploy Script
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
PROFILE="${1:-default}"      # AWS profile name
APP_DIR="$2"                 # Directory path to the app (e.g., backend or frontend)
ENV_NAME="$3"                # Elastic Beanstalk environment name
APP_NAME="$4"                # Elastic Beanstalk application name
CONFIG_NAME="${5:-}"         # Optional: saved config name for `eb create`

# AWS settings
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

# 🧹 Clean old EB CLI config to avoid drift
echo "🧹 Removing old .elasticbeanstalk config..."
rm -rf .elasticbeanstalk

# ⚙️ Initialize EB CLI non-interactively
echo "⚙️ Running eb init..."
eb init "$APP_NAME" \
  --platform "$PLATFORM" \
  --region "$REGION" \
  $EB_PROFILE_FLAG \
  --quiet

# 🌱 Create environment if it does not exist
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

# 🚀 Deploy application
echo "🚀 Deploying to '$ENV_NAME'..."
eb deploy $EB_PROFILE_FLAG
