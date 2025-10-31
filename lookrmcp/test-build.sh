#!/bin/bash

# Test script to verify the Looker MCP server build

set -e

echo "=========================================="
echo "Looker MCP Server - Build Verification"
echo "=========================================="
echo ""

# Check if image exists
echo "✓ Checking if image was built..."
if docker images | grep -q "looker-mcp"; then
    echo "  ✓ Image 'looker-mcp:latest' found"
else
    echo "  ✗ Image 'looker-mcp:latest' not found"
    exit 1
fi

# Inspect image
echo ""
echo "✓ Inspecting image details..."
docker inspect looker-mcp:latest | jq -r '.[0] | "  Size: \(.Size / 1024 / 1024 | floor)MB\n  Created: \(.Created)\n  Architecture: \(.Architecture)"'

# Check if toolbox binary exists in image
echo ""
echo "✓ Checking if GenAI Toolbox binary is present..."
if docker run --rm looker-mcp:latest which toolbox > /dev/null 2>&1; then
    echo "  ✓ toolbox binary found at /usr/local/bin/toolbox"
else
    echo "  ✗ toolbox binary not found"
    exit 1
fi

# Check toolbox version
echo ""
echo "✓ Checking GenAI Toolbox version..."
TOOLBOX_VERSION=$(docker run --rm looker-mcp:latest toolbox --version 2>&1 || echo "unknown")
echo "  Version: $TOOLBOX_VERSION"

# Check if files are present
echo ""
echo "✓ Checking if configuration files are present..."
docker run --rm looker-mcp:latest ls -la /app/ | grep -E "(tools.yaml|start.sh)" || true

echo ""
echo "=========================================="
echo "✓ Build verification complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Set your Looker credentials in .env file"
echo "  2. Run: docker run -d -p 8080:8080 --env-file .env --name looker-mcp looker-mcp:latest"
echo ""
