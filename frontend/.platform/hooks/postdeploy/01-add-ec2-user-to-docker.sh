#!/bin/bash
set -e

# Add ec2-user to docker group if not already
if ! id -nG ec2-user | grep -qw docker; then
    usermod -aG docker ec2-user
    echo "Added ec2-user to docker group"
else
    echo "ec2-user already in docker group"
fi
