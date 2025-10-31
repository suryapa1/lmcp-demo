# Minimal SQLite MCP Server using GenAI Toolbox
FROM debian:bookworm-slim

# Install minimal dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Download GenAI Toolbox binary
RUN curl -L -o /usr/local/bin/toolbox \
    "https://storage.googleapis.com/genai-toolbox/v0.18.0/linux/amd64/toolbox" \
    && chmod +x /usr/local/bin/toolbox

# Set working directory
WORKDIR /app

# Copy application files
COPY init-db.sql /app/
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8080

# Set environment defaults
ENV SQLITE_DATABASE=/app/data/sample.db
ENV PORT=8080

# Start the server
CMD ["/app/start.sh"]
