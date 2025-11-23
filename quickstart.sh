#!/bin/bash
# Quick Start Guide for ParrotOS
# Run these commands to get started with the port scanner

echo "🦜 Network Reconnaissance Suite - Quick Start for ParrotOS"
echo "=========================================================="
echo ""

# Navigate to project
echo "📁 Navigating to project directory..."
cd /mnt/f/literally-cook/test/recon_suite

# Make the script executable
echo "🔧 Making port scanner executable..."
chmod +x port_scanner.py

echo ""
echo "✅ Setup complete! Here are some safe commands to try:"
echo ""
echo "1️⃣  Scan yourself (always safe!):"
echo "   python3 port_scanner.py -t 127.0.0.1 -v"
echo ""
echo "2️⃣  Quick scan of common ports:"
echo "   python3 port_scanner.py -t 127.0.0.1"
echo ""
echo "3️⃣  Scan your router (usually safe):"
echo "   python3 port_scanner.py -t 192.168.1.1"
echo ""
echo "4️⃣  Save results to file:"
echo "   python3 port_scanner.py -t 127.0.0.1 -o my_scan.json"
echo ""
echo "5️⃣  Get help and see all options:"
echo "   python3 port_scanner.py --help"
echo ""
echo "⚠️  REMEMBER: Only scan systems you own or have permission to test!"
echo ""
echo "📚 Read LEARNING.md for detailed explanations of how everything works"
echo "🚀 Ready to hack (legally)! Have fun twin!"
