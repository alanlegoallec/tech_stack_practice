#!/bin/bash
set -e

echo "✅ Ensuring SSM Agent is installed and running..."

# Install SSM agent if not installed
if ! command -v amazon-ssm-agent &> /dev/null; then
    yum install -y amazon-ssm-agent
fi

systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Add ec2-user to docker group (already done)
usermod -aG docker ec2-user

# Also add ssm-user to docker group if it exists
if id "ssm-user" &>/dev/null; then
    usermod -aG docker ssm-user
    echo "✅ Added ssm-user to docker group"
fi

echo "✅ SSM Agent and user permissions setup complete."
