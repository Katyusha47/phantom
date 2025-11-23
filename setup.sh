#!/bin/bash
# Installation and Setup Script for ParrotOS
# Run this script to set up the Recon Suite

echo "=========================================="
echo "RECON SUITE - Installation Script"
echo "=========================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "[WARNING] This script is designed for Linux systems"
fi

# Navigate to project directory
echo "[1/4] Navigating to project directory..."
cd "$(dirname "$0")"

# Install Python dependencies
echo ""
echo "[2/4] Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Dependencies installed"
else
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

# Make scripts executable
echo ""
echo "[3/4] Making scripts executable..."
chmod +x recon_suite.py
chmod +x modules/*.py

echo "[SUCCESS] Scripts are now executable"

# Create output directory
echo ""
echo "[4/4] Creating output directories..."
mkdir -p output
mkdir -p wordlists

echo "[SUCCESS] Directory structure created"

echo ""
echo "=========================================="
echo "INSTALLATION COMPLETE"
echo "=========================================="
echo ""
echo "USAGE:"
echo "  Run the multi-tool interface:"
echo "    python3 recon_suite.py"
echo ""
echo "  Or use individual modules:"
echo "    python3 modules/port_scanner.py -t <target>"
echo ""
echo "LEGAL NOTICE:"
echo "  Only use on authorized systems"
echo "  Unauthorized testing is illegal"
echo ""
echo "Ready to start. Run: python3 recon_suite.py"
echo ""
