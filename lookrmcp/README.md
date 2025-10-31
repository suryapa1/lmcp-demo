# SQLite MCP Server

A minimal, production-ready MCP (Model Context Protocol) server for SQLite databases using Google's GenAI Toolbox.

## 🎯 Features

- **Prebuilt SQLite Tools**: Auto-configured with `--prebuilt sqlite`
- **Minimal Dependencies**: Single GenAI Toolbox binary (~90MB image)
- **Sample Database**: Pre-populated with users, products, and orders
- **Persistent Storage**: Volume-mounted SQLite database
- **MCP Protocol**: Standard Model Context Protocol for AI tool integration
- **Production Ready**: Works with Claude Desktop, Cline, and other MCP clients

## 📦 What's Included

### Available MCP Tools

1. **execute_sql** - Execute SQL queries
2. **list_tables** - List all database tables

### Sample Database Schema

- **users** - Sample user accounts (4 records)
- **products** - Product catalog (8 records)
- **orders** - Order history (6 records)

## 🚀 Quick Start

### Local Development

```bash
# Build the Docker image
docker build -t sqlite-mcp:latest .

# Run with persistent storage
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  --name sqlite-mcp \
  sqlite-mcp:latest

# Verify server started successfully
docker logs sqlite-mcp

# Expected output:
# ✓ "Initialized 1 sources."
# ✓ "Initialized 2 tools."
# ✓ "Server ready to serve!"
```

### Stop and Cleanup

```bash
docker stop sqlite-mcp
docker rm sqlite-mcp
```

### Verification

Since this is an MCP protocol server (not HTTP REST API), verify status through logs:

```bash
# Check if server is running
docker ps | grep sqlite-mcp

# View detailed logs
docker logs sqlite-mcp

# Follow logs in real-time
docker logs -f sqlite-mcp
```

## 📊 Database Access

### Query the Database Directly

```bash
# List all tables
sqlite3 data/sample.db "SELECT name FROM sqlite_master WHERE type='table';"

# Query users
sqlite3 data/sample.db "SELECT * FROM users;"

# Query products
sqlite3 data/sample.db "SELECT name, price, category FROM products;"

# Query orders with user info
sqlite3 data/sample.db "
SELECT u.name, p.name, o.quantity, o.total_price, o.status 
FROM orders o 
JOIN users u ON o.user_id = u.id 
JOIN products p ON o.product_id = p.id;
"
```

## 🏗️ Architecture

```
┌────────────────────────────────────┐
│  Docker Container                  │
│                                    │
│  ┌─────────────────────────────┐   │
│  │ GenAI Toolbox v0.18.0       │   │
│  │ toolbox --prebuilt sqlite   │   │
│  │ --port 8080                 │   │
│  └─────────────────────────────┘   │
│                                    │
│  /app/data/sample.db               │
│  (Persistent SQLite DB)            │
└────────────────────────────────────┘
         ↓
    Volume Mount
         ↓
┌────────────────────────────────────┐
│  ./data/sample.db                  │
│  (Host Machine)                    │
└────────────────────────────────────┘
```

## 📝 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SQLITE_DATABASE` | `/app/data/sample.db` | Path to SQLite database file |
| `PORT` | `8080` | Server port |

SQLite MCP Server - Starting
📝 Initializing SQLite database...
✓ Database created with sample data

Configuration:
  Database: /app/data/sample.db
  Port: 8080
------------------------------------------------------------
Starting GenAI Toolbox (SQLite MCP Server)...
Health endpoint: http://0.0.0.0:8080/health
INFO "Using prebuilt tool configuration for sqlite"
INFO "Initialized 1 sources."
INFO "Initialized 2 tools."
INFO "Server ready to serve!"
```
## 🧪 Testing

### Test Server Startup

```bash
# Build and run
docker build -t sqlite-mcp:latest .
docker run -d -p 8080:8080 -v $(pwd)/data:/app/data --name sqlite-mcp-test sqlite-mcp:latest

# Wait for startup
sleep 3

# Check logs for success
docker logs sqlite-mcp-test
```

Expected output:
```
SQLite MCP Server - Starting
📝 Initializing SQLite database...
✓ Database created with sample data

Configuration:
  Database: /app/data/sample.db
  Port: 8080
------------------------------------------------------------
Starting GenAI Toolbox (SQLite MCP Server)...
MCP Protocol Mode: stdio/SSE
Note: No HTTP REST endpoints - use MCP protocol for communication
INFO "Using prebuilt tool configuration for sqlite"
INFO "Initialized 1 sources."
INFO "Initialized 2 tools."
INFO "Server ready to serve!"
```

### Verify Database Contents

```bash
# List all tables
sqlite3 data/sample.db ".tables"

# Count records
sqlite3 data/sample.db "SELECT 'users:', COUNT(*) FROM users UNION ALL SELECT 'products:', COUNT(*) FROM products UNION ALL SELECT 'orders:', COUNT(*) FROM orders;"
```
============================================================
SQLite MCP Server - Starting
============================================================
📝 Initializing SQLite database...
✓ Database created with sample data

Configuration:
  Database: /app/data/sample.db
  Port: 8080
------------------------------------------------------------
Starting GenAI Toolbox (SQLite MCP Server)...
Health endpoint: http://0.0.0.0:8080/health
============================================================
INFO "Using prebuilt tool configuration for sqlite"
INFO "Initialized 1 sources."
INFO "Initialized 2 tools."
INFO "Server ready to serve!"
```

## 🌐 Cloud Run Deployment

### Prerequisites

```bash
# Set your GCP project
export PROJECT_ID=llmgenai-448101
export REGION=us-central1

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Build and Deploy

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/${PROJECT_ID}/sqlite-mcp

# Deploy to Cloud Run
gcloud run deploy sqlite-mcp \
  --image gcr.io/${PROJECT_ID}/sqlite-mcp \
  --platform managed \
  --region ${REGION} \
  --port 8080 \
  --allow-unauthenticated
```

⚠️ **Note**: SQLite data on Cloud Run is ephemeral and resets on container restart. For production, consider using Cloud SQL instead.

## � Customization

### Using Your Own Database

Replace the `init-db.sql` file with your schema:

```sql
-- init-db.sql
CREATE TABLE your_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

INSERT INTO your_table (name) VALUES ('Example');
```

Then rebuild:

```bash
docker build -t sqlite-mcp:latest .
```

### Empty Database

To start with an empty database, simply remove the volume mount:

```bash
docker run -d -p 8080:8080 --name sqlite-mcp sqlite-mcp:latest
```

## 📚 MCP Integration

### Use with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/path/to/your/data:/app/data",
        "sqlite-mcp:latest"
      ]
    }
  }
}
```

### Use with Cline (VSCode)

Configure in Cline settings:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "sqlite-mcp:latest"]
    }
  }
}
```

## 🛠️ Development

### File Structure

```
lookrmcp/
├── Dockerfile           # Container definition
├── start.sh             # Startup script
├── init-db.sql          # Sample database schema
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── data/                # SQLite database (gitignored)
    └── sample.db
```

### Build Options

```bash
# Build with custom tag
docker build -t my-sqlite-mcp:v1.0 .

# Build without cache
docker build --no-cache -t sqlite-mcp:latest .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t sqlite-mcp:latest .
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker logs sqlite-mcp

# Run interactively for debugging
docker run -it --rm sqlite-mcp:latest /bin/bash
```

### Database permission errors

```bash
# Ensure data directory has correct permissions
chmod -R 755 data/
```

### Health check fails

```bash
# Check if port 8080 is already in use
lsof -i :8080

# Use different port
docker run -d -p 9090:8080 --name sqlite-mcp sqlite-mcp:latest
```

## 📖 Resources

- [GenAI Toolbox Documentation](https://googleapis.github.io/genai-toolbox/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [SQLite Documentation](https://sqlite.org/docs.html)

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

---

**Built with** ❤️ **using Google GenAI Toolbox v0.18.0**
