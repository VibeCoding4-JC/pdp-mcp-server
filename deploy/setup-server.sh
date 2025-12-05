#!/bin/bash
# =============================================================================
# PDP MCP Server - Initial Server Setup Script
# =============================================================================
# Run this script on a fresh server to set up the PDP MCP Server
# Usage: sudo bash setup-server.sh
# =============================================================================

set -e

# Configuration
DEPLOY_PATH="/opt/pdp-mcp-server"
SERVICE_USER="www-data"
REPO_URL="${1:-https://github.com/your-username/pdp-mcp-server.git}"

echo "=================================================="
echo "PDP MCP Server - Initial Setup"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget

# Create deployment directory
echo "📁 Creating deployment directory..."
mkdir -p "$DEPLOY_PATH"
chown "$SERVICE_USER:$SERVICE_USER" "$DEPLOY_PATH"

# Clone repository (if REPO_URL provided)
if [ -n "$REPO_URL" ] && [ "$REPO_URL" != "https://github.com/your-username/pdp-mcp-server.git" ]; then
    echo "📥 Cloning repository..."
    cd "$DEPLOY_PATH"
    git clone "$REPO_URL" .
else
    echo "⚠️  Skipping git clone. Please manually copy files to $DEPLOY_PATH"
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
cd "$DEPLOY_PATH"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Create .env file template
echo "🔧 Creating .env template..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=pdp-knowledge

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Server Configuration
MCP_SERVER_NAME=UU PDP Assistant
LOG_LEVEL=INFO
EOF
    chmod 600 .env
    echo "⚠️  Please edit .env file with your API keys!"
fi

# Install systemd service
echo "🔧 Installing systemd service..."
cp deploy/pdp-mcp-server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pdp-mcp-server

# Set permissions
echo "🔒 Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$DEPLOY_PATH"
chmod -R 755 "$DEPLOY_PATH"
chmod 600 "$DEPLOY_PATH/.env"

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   sudo nano $DEPLOY_PATH/.env"
echo ""
echo "2. Ingest data to Pinecone:"
echo "   cd $DEPLOY_PATH"
echo "   source venv/bin/activate"
echo "   python scripts/ingest_data.py"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start pdp-mcp-server"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status pdp-mcp-server"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u pdp-mcp-server -f"
echo ""
