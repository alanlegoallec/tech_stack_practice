#!/bin/bash
set -euo pipefail

PROFILE="${1:-default}"
APP_DIR="$2"
ENV_NAME="$3"

cd "$APP_DIR"

echo "🔍 Checking if EB environment '$ENV_NAME' exists..."

# 👇 Use --profile only if not in GitHub Actions and a profile is set
EB_PROFILE_FLAG=""
if [[ "$PROFILE" != "default" && -z "${GITHUB_ACTIONS:-}" ]]; then
  EB_PROFILE_FLAG="--profile $PROFILE"
fi

if ! eb status "$ENV_NAME" $EB_PROFILE_FLAG &>/dev/null; then
  echo "🚧 Environment '$ENV_NAME' not found. Initializing and creating..."

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

  echo "🌱 Creating new EB environment '$ENV_NAME'..."
  eb create "$ENV_NAME" --cfg backend-with-sg $EB_PROFILE_FLAG || {
    echo "❌ eb create failed. Aborting."
    exit 1
  }

  eb use "$ENV_NAME" $EB_PROFILE_FLAG
else
  echo "✅ Environment '$ENV_NAME' already exists."
  eb use "$ENV_NAME" $EB_PROFILE_FLAG
fi

echo "🚀 Deploying to '$ENV_NAME'..."
eb deploy $EB_PROFILE_FLAG
