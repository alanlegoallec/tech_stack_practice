#!/bin/bash
set -euo pipefail

PROFILE="${1:-default}"
APP_DIR="$2"
ENV_NAME="$3"

APP_NAME="full-stack-practice-backend"
REGION="us-east-1"
PLATFORM="Docker"

cd "$APP_DIR"

echo "🔍 Checking if EB environment '$ENV_NAME' exists..."

# Determine profile arguments
EB_PROFILE_FLAG=""
AWS_CLI_PROFILE_ARGS=""
if [[ "$PROFILE" != "default" && -z "${GITHUB_ACTIONS:-}" ]]; then
  EB_PROFILE_FLAG="--profile $PROFILE"
  AWS_CLI_PROFILE_ARGS="--profile $PROFILE"
fi

# 💣 Always wipe local EB config to avoid drift
echo "🧹 Removing old .elasticbeanstalk config..."
rm -rf .elasticbeanstalk

# ⚙️ Reinitialize EB CLI config
echo "⚙️ Running eb init..."
eb init "$APP_NAME" \
  --platform "$PLATFORM" \
  --region "$REGION" \
  $EB_PROFILE_FLAG \
  --quiet

# 🌱 Create env if it doesn't exist
if ! aws elasticbeanstalk describe-environments \
  --region "$REGION" \
  --environment-names "$ENV_NAME" \
  $AWS_CLI_PROFILE_ARGS \
  | grep -q '"Status":'; then

  echo "🌱 Creating EB environment '$ENV_NAME' using saved config 'backend-with-sg'..."
  eb create "$ENV_NAME" --cfg backend-with-sg $EB_PROFILE_FLAG || {
    echo "❌ eb create failed. Aborting."
    exit 1
  }
else
  echo "✅ Environment '$ENV_NAME' already exists."
fi

# 📌 Set default environment
eb use "$ENV_NAME" $EB_PROFILE_FLAG

# 🚀 Deploy
echo "🚀 Deploying to '$ENV_NAME'..."
eb deploy --staged $EB_PROFILE_FLAG
