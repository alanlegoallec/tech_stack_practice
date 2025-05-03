#!/bin/bash
set -e

# List of extensions to install
extensions=(
    ms-python.python
    ms-toolsai.jupyter
    ms-vscode.cpptools
)

# Check if VS Code is already installed; if not, install it
if ! command -v code &> /dev/null; then
    echo "[INFO] Installing VS Code..."
    apt-get update
    apt-get install -y wget gpg apt-transport-https

    # Add Microsoft's GPG key and repository for VS Code
    wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | gpg --dearmor > /usr/share/keyrings/microsoft-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list

    apt-get update
    apt-get install -y code
fi

# Create a temporary user data directory to avoid running VS Code as root
USER_DATA_DIR=$(mktemp -d)

echo "[INFO] VS Code already installed."

# Install each extension using the --no-sandbox flag and the created user data directory
for extension in "${extensions[@]}"; do
    echo "[INFO] Installing extension: $extension"
    code --no-sandbox --user-data-dir=$USER_DATA_DIR --install-extension $extension
done

echo "[INFO] All extensions installed successfully."
