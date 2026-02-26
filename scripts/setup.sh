#!/bin/bash
#
# Setup script for ArcGIS Knowledge Integration
# This script sets up the development environment and dependencies

set -e

echo "🚀 Setting up ArcGIS Knowledge Integration environment..."

# Check for Python 3.9+
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_PYTHON="3.9"

if ! printf '%s\n' "$REQUIRED_PYTHON" "$PYTHON_VERSION" | sort -Vt. -k1,1 -k2,2 | tail -n1 == "$REQUIRED_PYTHON"; then
    echo "❌ Python $REQUIRED_PYTHON+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Found Python: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install requests
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your ArcGIS Enterprise credentials"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p demo/examples
mkdir -p samples/templates
mkdir -p automation/batch
mkdir -p automation/webhooks
mkdir -p tests

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your ArcGIS Enterprise credentials"
echo "2. Test the connection:"
echo "   python -m examples.test_connection"
echo "3. Create your first knowledge graph:"
echo "   python -m samples.facility_management"
echo ""