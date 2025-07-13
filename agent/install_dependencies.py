#!/usr/bin/env python3
"""
Install Python dependencies for Aztec Protocol agent
"""

import subprocess
import sys
import os

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def main():
    """Install required dependencies"""
    print("=== Installing Aztec Protocol Dependencies ===")
    
    # Check if we're in a virtual environment
    if not check_virtual_environment():
        print("⚠️  Warning: Not in a virtual environment!")
        print("This may cause permission issues. Consider running:")
        print("python3 -m venv aztec_env")
        print("source aztec_env/bin/activate")
        print("Then run this script again.")
        print()
        
        # Ask user if they want to continue
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting. Please set up a virtual environment first.")
            return 1
    
    # Required packages
    packages = [
        "torch",
        "transformers",
        "datasets",
        "peft",
        "accelerate",
        "numpy",
        "requests",
        "ipfshttpclient"
    ]
    
    print("Installing Python packages...")
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nInstallation Summary: {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("✅ All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Test the ZK proof system: python test_zk_proofs.py")
        print("2. Run the agent: python aztec-agent.py")
        return 0
    else:
        print("⚠️  Some packages failed to install. You may need to install them manually.")
        print("\nTry running the setup script instead:")
        print("chmod +x setup_environment.sh")
        print("./setup_environment.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 