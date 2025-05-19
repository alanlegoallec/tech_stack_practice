#!/usr/bin/env bash

set -e

ASG_NAME="awseb-e-xkid3npgm7-stack-AWSEBAutoScalingGroup-VxAfTLURzU03"
PROFILE="devops-full-stack-practice"
SSH_PUBLIC_KEY="$HOME/.ssh/id_rsa.pub"
SSH_PRIVATE_KEY="$HOME/.ssh/id_rsa"
SSH_USER="ec2-user"

# Ensure private key permissions are safe
chmod 600 "$SSH_PRIVATE_KEY"

echo "🔍 Fetching EC2 instances in Auto Scaling Group: $ASG_NAME"

INSTANCE_IDS=($(aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names "$ASG_NAME" \
  --query "AutoScalingGroups[0].Instances[*].InstanceId" \
  --output text \
  --profile "$PROFILE"))

if [ ${#INSTANCE_IDS[@]} -eq 0 ]; then
  echo "❌ No instances found in ASG $ASG_NAME"
  exit 1
fi

echo "✅ Found instances:"
i=1
INSTANCE_ID_LIST=()
PUBLIC_IP_LIST=()

for INSTANCE_ID in "${INSTANCE_IDS[@]}"; do
  PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
    --query "Reservations[0].Instances[0].PublicIpAddress" \
    --output text \
    --profile "$PROFILE")
  echo "$i) $INSTANCE_ID ($PUBLIC_IP)"
  INSTANCE_ID_LIST+=("$INSTANCE_ID")
  PUBLIC_IP_LIST+=("$PUBLIC_IP")
  i=$((i+1))
done

echo ""
read -p "👉 Select instance number to connect to: " CHOICE

INDEX=$((CHOICE-1))
INSTANCE_ID="${INSTANCE_ID_LIST[$INDEX]}"
PUBLIC_IP="${PUBLIC_IP_LIST[$INDEX]}"

if [ -z "$INSTANCE_ID" ] || [ -z "$PUBLIC_IP" ]; then
  echo "❌ Invalid choice"
  exit 1
fi

echo "🚀 Sending SSH public key to instance $INSTANCE_ID ($PUBLIC_IP)..."

AVAIL_ZONE=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
  --query "Reservations[0].Instances[0].Placement.AvailabilityZone" \
  --output text \
  --profile "$PROFILE")

aws ec2-instance-connect send-ssh-public-key \
  --instance-id "$INSTANCE_ID" \
  --availability-zone "$AVAIL_ZONE" \
  --instance-os-user "$SSH_USER" \
  --ssh-public-key "file://$SSH_PUBLIC_KEY" \
  --profile "$PROFILE" > /dev/null

echo "✅ Connecting via SSH..."
ssh -i "$SSH_PRIVATE_KEY" "$SSH_USER@$PUBLIC_IP"
