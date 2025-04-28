#!/bin/bash

# List of extensions to install
extensions=(
    ms-python.python
    ms-toolsai.jupyter
    ms-vscode.cpptools
)

# Install each extension
for extension in "${extensions[@]}"; do
    code --install-extension $extension
done
