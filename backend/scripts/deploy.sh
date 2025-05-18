#!/bin/bash
set -euo pipefail

PROFILE="$1"
APP_DIR="$2"
ENV_NAME="$3"

cd "$APP_DIR"

echo "🔍 Checking if EB environment '$ENV_NAME' exists..."

if ! eb status "$ENV_NAME" --profile "$PROFILE" &>/dev/null; then
  echo "🚧 Environment '$ENV_NAME' not found. Initializing and creating..."

  # SAFEGUARD: Remove default key reference from config if it exists
  CONFIG_FILE=".elasticbeanstalk/config.yml"
  if [[ -f "$CONFIG_FILE" ]]; then
    echo "🩹 Removing stale default_ec2_keyname..."
    sed -i.bak '/default_ec2_keyname/d' "$CONFIG_FILE"
  fi

  # SAFE: Non-interactive init with explicit null key
  eb init \
    --profile "$PROFILE" \
    --platform "Docker" \
    --region "us-east-1" \
    --keyname "" || {
      echo "❌ eb init failed. Aborting."
      exit 1
  }

  # CRITICAL: Do NOT pass unsupported flags here
eb create "$ENV_NAME" --cfg backend-with-sg --profile "$PROFILE"

  # Set environment as default for the current git branch
  eb use "$ENV_NAME" --profile "$PROFILE"
else
  echo "✅ Environment '$ENV_NAME' already exists."
  eb use "$ENV_NAME" --profile "$PROFILE"
fi

echo "🚀 Deploying to '$ENV_NAME'..."
eb deploy --profile "$PROFILE"
