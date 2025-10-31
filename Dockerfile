# Multi-stage Dockerfile for FastMCP Looker MCP Server
FROM python:3.11-slim as toolbox-download

# Install curl for downloading toolbox binary
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Download Google GenAI Toolbox v0.14.0
# Detect architecture and download appropriate binary
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        TOOLBOX_ARCH="linux/amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        TOOLBOX_ARCH="linux/arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    echo "Downloading toolbox for $TOOLBOX_ARCH" && \
    curl -L -o /tmp/toolbox https://storage.googleapis.com/genai-toolbox/v0.14.0/$TOOLBOX_ARCH/toolbox && \
    chmod +x /tmp/toolbox

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy toolbox binary from download stage
COPY --from=toolbox-download /tmp/toolbox /usr/local/bin/toolbox

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Expose port 8080
EXPOSE 8080

# Set environment variables with defaults
ENV LOOKER_BASE_URL="" \
    LOOKER_CLIENT_ID="" \
    LOOKER_CLIENT_SECRET="" \
    LOOKER_VERIFY_SSL="true" \
    LOOKER_API_VERSION="4.0" \
    PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/service/health || exit 1

# Run the application
CMD ["./start.sh"]
