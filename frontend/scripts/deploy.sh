#!/bin/bash
set -euo pipefail

PROFILE="${1:-default}"
APP_DIR="$2"
ENV_NAME="$3"

cd "$APP_DIR"

echo "🔍 Checking if EB environment '$ENV_NAME' exists..."

# Use --profile only if not running inside GitHub Actions
EB_PROFILE_FLAG=""
if [[ "$PROFILE" != "default" && -z "${GITHUB_ACTIONS:-}" ]]; then
  EB_PROFILE_FLAG="--profile $PROFILE"
fi

# Always run eb init to make sure CLI is correctly configured
echo "⚙️ Running eb init to configure local directory..."
CONFIG_FILE=".elasticbeanstalk/config.yml"
if [[ -f "$CONFIG_FILE" ]]; then
  echo "🩹 Removing stale default_ec2_keyname..."
  sed -i.bak '/default_ec2_keyname/d' "$CONFIG_FILE"
fi

eb init \
  $EB_PROFILE_FLAG \
  --platform "Docker" \
  --region "us-east-1" \
  --keyname "" || {
    echo "❌ eb init failed. Aborting."
    exit 1
}

if ! eb status "$ENV_NAME" $EB_PROFILE_FLAG &>/dev/null; then
  echo "🌱 Creating new EB environment '$ENV_NAME'..."
  eb create "$ENV_NAME" $EB_PROFILE_FLAG
  eb use "$ENV_NAME" $EB_PROFILE_FLAG
else
  echo "✅ Environment '$ENV_NAME' already exists."
  eb use "$ENV_NAME" $EB_PROFILE_FLAG
fi

echo "🚀 Deploying to '$ENV_NAME'..."
eb deploy $EB_PROFILE_FLAG
