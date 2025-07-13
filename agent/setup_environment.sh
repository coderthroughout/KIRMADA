#!/bin/bash
# Setup script for Aztec Protocol development environment

echo "=== Setting up Aztec Protocol Development Environment ==="

# Check if python3-venv is installed
if ! dpkg -l | grep -q python3-venv; then
    echo "Installing python3-venv..."
    sudo apt update
    sudo apt install -y python3-venv python3-pip
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv aztec_env

# Activate virtual environment
echo "Activating virtual environment..."
source aztec_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install torch transformers datasets peft accelerate numpy requests ipfshttpclient

echo "=== Environment Setup Complete ==="
echo ""
echo "To activate the environment in the future, run:"
echo "source aztec_env/bin/activate"
echo ""
echo "To test the ZK proof system, run:"
echo "python test_zk_proofs.py" 