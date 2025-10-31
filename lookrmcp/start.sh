#!/bin/bash

set -e

echo "============================================================"
echo "SQLite MCP Server - Starting"
echo "============================================================"

# Create data directory if it doesn't exist
mkdir -p "$(dirname "$SQLITE_DATABASE")"

# Initialize SQLite database if it doesn't exist
if [ ! -f "$SQLITE_DATABASE" ]; then
    echo "📝 Initializing SQLite database..."
    sqlite3 "$SQLITE_DATABASE" < /app/init-db.sql
    echo "✓ Database created with sample data"
else
    echo "✓ Using existing database"
fi

echo ""
echo "Configuration:"
echo "  Database: ${SQLITE_DATABASE}"
echo "  Port: ${PORT}"
echo "------------------------------------------------------------"

# Start GenAI Toolbox with prebuilt SQLite tools
echo "Starting GenAI Toolbox (SQLite MCP Server)..."
echo "MCP Protocol Mode: stdio/SSE"
echo "Note: No HTTP REST endpoints - use MCP protocol for communication"
echo "============================================================"

exec toolbox --prebuilt sqlite --address 0.0.0.0 --port "${PORT}" --ui
