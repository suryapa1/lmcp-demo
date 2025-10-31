"""
FastMCP-based Looker MCP Server
Uses Google GenAI Toolbox prebuilt Looker configuration
"""
import os
import sys
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(
    name="Looker MCP Server",
    version="1.0.0",
    description="FastMCP server providing Looker data access via Google GenAI Toolbox"
)

# Get Looker configuration from environment variables
LOOKER_CONFIG = {
    "LOOKER_BASE_URL": os.getenv("LOOKER_BASE_URL", ""),
    "LOOKER_CLIENT_ID": os.getenv("LOOKER_CLIENT_ID", ""),
    "LOOKER_CLIENT_SECRET": os.getenv("LOOKER_CLIENT_SECRET", ""),
    "LOOKER_VERIFY_SSL": os.getenv("LOOKER_VERIFY_SSL", "true"),
    "LOOKER_API_VERSION": os.getenv("LOOKER_API_VERSION", "4.0"),
}

def validate_credentials():
    """Validate that all required Looker credentials are provided."""
    missing = []
    for key in ["LOOKER_BASE_URL", "LOOKER_CLIENT_ID", "LOOKER_CLIENT_SECRET"]:
        if not LOOKER_CONFIG[key]:
            missing.append(key)
    
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        print("\nPlease set these environment variables either:", file=sys.stderr)
        print("  1. In a .env file in the same directory", file=sys.stderr)
        print("  2. Or pass them via docker run:", file=sys.stderr)
        print(f"     docker run -e LOOKER_BASE_URL=... -e LOOKER_CLIENT_ID=... -e LOOKER_CLIENT_SECRET=... -p 8080:8080 looker-mcp", file=sys.stderr)
        return False
    return True

@mcp.custom_route("/health", methods=["GET"])
async def health_endpoint(request: Request) -> JSONResponse:
    """
    Health check endpoint (short path) for Cloud Run and monitoring.
    Returns HTTP 200 with server status.
    """
    is_configured = validate_credentials()
    
    health_status = {
        "status": "ok" if is_configured else "error",
        "toolbox": "Looker",
        "version": "1.0.0",
        "configured": is_configured,
        "message": "Looker MCP Toolbox - 15 prebuilt tools available" if is_configured else "Missing Looker credentials"
    }
    
    return JSONResponse(health_status)

@mcp.custom_route("/service/health", methods=["GET"])
async def service_health_check(request: Request) -> JSONResponse:
    """
    Health check endpoint (service path) for monitoring and load balancing.
    Returns HTTP 200 with server status.
    """
    is_configured = validate_credentials()
    
    health_status = {
        "status": "ok" if is_configured else "error",
        "toolbox": "Looker",
        "version": "1.0.0",
        "configured": is_configured,
        "message": "Looker MCP Toolbox - 15 prebuilt tools available" if is_configured else "Missing Looker credentials"
    }
    
    return JSONResponse(health_status)

@mcp.custom_route("/config", methods=["GET"])
async def config_check(request: Request) -> JSONResponse:
    """
    Configuration check endpoint (without exposing secrets).
    Returns masked configuration details.
    """
    config_status = {
        "looker_base_url": LOOKER_CONFIG["LOOKER_BASE_URL"] if LOOKER_CONFIG["LOOKER_BASE_URL"] else "NOT_SET",
        "looker_client_id": "***" if LOOKER_CONFIG["LOOKER_CLIENT_ID"] else "NOT_SET",
        "looker_client_secret": "***" if LOOKER_CONFIG["LOOKER_CLIENT_SECRET"] else "NOT_SET",
        "looker_verify_ssl": LOOKER_CONFIG["LOOKER_VERIFY_SSL"],
        "looker_api_version": LOOKER_CONFIG["LOOKER_API_VERSION"],
    }
    return JSONResponse(config_status)

@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> PlainTextResponse:
    """Root endpoint with server information."""
    is_configured = validate_credentials()
    return PlainTextResponse(
        "Looker MCP Server\n"
        "================\n\n"
        "Endpoints:\n"
        "  GET /              - This information page\n"
        "  GET /service/health - Health check endpoint\n"
        "  GET /config        - Configuration status (masked)\n"
        "  POST /mcp/         - MCP protocol endpoint\n\n"
        f"Status: {'Ready' if is_configured else 'Not Configured - Set environment variables'}\n\n"
        "Prebuilt Looker Tools (via Google GenAI Toolbox v0.14.0):\n"
        "  - get_models, get_explores, get_dimensions, get_measures\n"
        "  - get_filters, get_parameters, query, query_sql, query_url\n"
        "  - get_looks, run_look, make_look\n\n"
        "Note: All tools are provided by the Google GenAI Toolbox --prebuilt looker\n"
    )

if __name__ == "__main__":
    import uvicorn
    
    # Validate credentials on startup
    print("=" * 60)
    print("Looker MCP Server - Starting")
    print("=" * 60)
    print(f"Looker Base URL: {LOOKER_CONFIG['LOOKER_BASE_URL']}")
    print(f"Verify SSL: {LOOKER_CONFIG['LOOKER_VERIFY_SSL']}")
    print(f"API Version: {LOOKER_CONFIG['LOOKER_API_VERSION']}")
    print("-" * 60)
    
    if validate_credentials():
        print("✓ Looker credentials configured")
        print("✓ Google GenAI Toolbox will provide 15 prebuilt Looker tools")
    else:
        print("✗ WARNING: Looker credentials not configured")
        print("  Server will start but tools will not function")
    
    print("=" * 60)
    
    # Get port from environment or default to 8080
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Start the server
    print(f"\nStarting FastMCP server on {host}:{port}")
    print(f"Health check: http://{host}:{port}/service/health")
    print(f"MCP endpoint: http://{host}:{port}/mcp/")
    print(f"Info page: http://{host}:{port}/")
    
    uvicorn.run(
        mcp.get_asgi_app(),
        host=host,
        port=port,
        log_level="info"
    )
