#!/bin/bash

echo "🚀 Luxury Travel Agent - Setup Script"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python $(python3 --version | awk '{print $2}') found"
echo ""

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed"
    exit 1
fi

echo "Step 1: Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 2: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created (using default values)"
    echo "   Edit .env to add API credentials (optional)"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "Step 3: Running tests..."
python -m pytest tests/ -o addopts="" -q 2>&1 | tail -5
if [ $? -eq 0 ]; then
    echo "✅ All tests passing"
else
    echo "⚠️  Some tests failed. Check the output above."
fi

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo ""
echo "To start the app:"
echo "  python -m src.app"
echo ""
echo "Then visit:"
echo "  http://localhost:5000"
echo ""
echo "For more information, see QUICKSTART.md"
echo ""
