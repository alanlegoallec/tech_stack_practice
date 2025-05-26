#!/bin/bash
set -euo pipefail

###############################################################################
# 🔁 RDS Instance Recreation Script
#
# Usage:
#   ./create-rds.sh <aws_profile> <db_instance_identifier>
#
# Example:
#   ./create-rds.sh deployer-full-stack-practice numbers-db
###############################################################################

PROFILE="${1:-default}"
DB_INSTANCE_ID="$2"
REGION="us-east-1"

# Customize RDS configuration
DB_INSTANCE_CLASS="db.t3.micro"
ENGINE="postgres"
USERNAME="postgres"
PASSWORD="changeme123"  # 🔐 In production, replace with secret manager retrieval
ALLOCATED_STORAGE=20

# 🧨 Delete existing instance if it exists
echo "🔍 Checking if RDS instance '$DB_INSTANCE_ID' exists..."
if aws rds describe-db-instances --db-instance-identifier "$DB_INSTANCE_ID" --region "$REGION" --profile "$PROFILE" &>/dev/null; then
  echo "💣 Deleting existing RDS instance '$DB_INSTANCE_ID'..."
  aws rds delete-db-instance \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --skip-final-snapshot \
    --region "$REGION" \
    --profile "$PROFILE"

  echo "⏳ Waiting for deletion to complete..."
  aws rds wait db-instance-deleted \
    --db-instance-identifier "$DB_INSTANCE_ID" \
    --region "$REGION" \
    --profile "$PROFILE"
else
  echo "✅ No existing RDS instance to delete."
fi

# 🚀 Create new RDS instance
echo "🌱 Creating new RDS instance '$DB_INSTANCE_ID'..."
aws rds create-db-instance \
  --db-instance-identifier "$DB_INSTANCE_ID" \
  --db-instance-class "$DB_INSTANCE_CLASS" \
  --engine "$ENGINE" \
  --master-username "$USERNAME" \
  --master-user-password "$PASSWORD" \
  --allocated-storage "$ALLOCATED_STORAGE" \
  --publicly-accessible \
  --region "$REGION" \
  --profile "$PROFILE"

echo "⏳ Waiting for RDS instance to become available..."
aws rds wait db-instance-available \
  --db-instance-identifier "$DB_INSTANCE_ID" \
  --region "$REGION" \
  --profile "$PROFILE"

echo "✅ RDS instance '$DB_INSTANCE_ID' created and available."
