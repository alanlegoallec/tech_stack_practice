#!/bin/bash

# Path to your .env file (adjust if needed)
ENV_FILE=".env"

# Read each line of the file
while IFS='=' read -r key _; do
  # Skip empty lines and comments
  if [[ -n "$key" && "$key" != \#* ]]; then
    # Trim whitespace
    var_name=$(echo "$key" | xargs)
    # Only unset if it's a valid variable name
    if [[ "$var_name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
      echo "Unsetting $var_name"
      unset "$var_name"
    fi
  fi
done < "$ENV_FILE"
