#!/bin/bash

set -e

echo "============================================================"
echo "Looker MCP Server - Starting"
echo "============================================================"

echo "Configuration:"
echo "  Looker Base URL: ${LOOKER_BASE_URL}"
echo "  Looker Client ID: ${LOOKER_CLIENT_ID}"
echo "  Port: ${PORT}"
echo "------------------------------------------------------------"

# Validate required environment variables
if [ -z "$LOOKER_BASE_URL" ]; then
    echo "❌ ERROR: LOOKER_BASE_URL environment variable is required"
    exit 1
fi

if [ -z "$LOOKER_CLIENT_ID" ]; then
    echo "❌ ERROR: LOOKER_CLIENT_ID environment variable is required"
    exit 1
fi

if [ -z "$LOOKER_CLIENT_SECRET" ]; then
    echo "❌ ERROR: LOOKER_CLIENT_SECRET environment variable is required"
    exit 1
fi

echo "✓ Looker configuration validated"

# Start GenAI Toolbox with prebuilt Looker tools
echo "Starting GenAI Toolbox (Looker MCP Server)..."
echo "MCP Protocol Mode: HTTP + UI"
echo "Looker Integration: Basic Looker API"
echo "============================================================"

exec toolbox --prebuilt looker --address 0.0.0.0 --port "${PORT}" --ui
