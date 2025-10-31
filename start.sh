#!/bin/bash

# Start script for Looker MCP Server
# This script runs the FastMCP server with uvicorn

set -e

echo "=================================="
echo "Looker MCP Server Starting..."
echo "=================================="

# Verify toolbox is available
if ! command -v toolbox &> /dev/null; then
    echo "ERROR: toolbox binary not found in PATH"
    exit 1
fi

echo "✓ Google GenAI Toolbox binary found"

# Check if required environment variables are set
if [ -z "$LOOKER_BASE_URL" ] || [ -z "$LOOKER_CLIENT_ID" ] || [ -z "$LOOKER_CLIENT_SECRET" ]; then
    echo ""
    echo "WARNING: Missing required Looker environment variables!"
    echo "Please ensure the following are set:"
    echo "  - LOOKER_BASE_URL"
    echo "  - LOOKER_CLIENT_ID"
    echo "  - LOOKER_CLIENT_SECRET"
    echo ""
    echo "You can pass them via docker run:"
    echo "  docker run -e LOOKER_BASE_URL=... -e LOOKER_CLIENT_ID=... \\"
    echo "             -e LOOKER_CLIENT_SECRET=... -p 8080:8080 looker-mcp"
    echo ""
fi

# Display configuration (masked)
echo ""
echo "Configuration:"
echo "  Base URL: ${LOOKER_BASE_URL:-NOT_SET}"
echo "  Client ID: ${LOOKER_CLIENT_ID:+***}"
echo "  Client Secret: ${LOOKER_CLIENT_SECRET:+***}"
echo "  Verify SSL: ${LOOKER_VERIFY_SSL:-true}"
echo "  API Version: ${LOOKER_API_VERSION:-4.0}"
echo "  Port: ${PORT:-8080}"
echo ""
echo "=================================="

# Start the FastMCP server
exec python server.py
