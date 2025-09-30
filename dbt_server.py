"""
dbt MCP Server Entry Point for FastMCP Cloud Deployment

This serves as the entry point for deploying the official dbt-labs/dbt-mcp server
alongside our Data Product Hub composite server. This allows us to leverage
official dbt MCP tools while maintaining our orchestration capabilities.

FastMCP expects to find a server object with a standard name (mcp, server, or app).
Since dbt-mcp creates its server asynchronously, we create it at module level
following their official pattern.
"""

import asyncio
import os
import sys
from pathlib import Path


def setup_dbt_environment() -> None:
    """Configure environment variables for dbt-core operations"""

    # Set default dbt profiles directory if not specified
    if not os.getenv("DBT_PROFILES_DIR"):
        os.environ["DBT_PROFILES_DIR"] = str(Path.home() / ".dbt")

    # Ensure we're using dbt-core (not cloud) by default
    if not os.getenv("DBT_CORE_MODE"):
        os.environ["DBT_CORE_MODE"] = "true"

    # Set reasonable defaults for MCP server operation
    if not os.getenv("DBT_MCP_LOG_LEVEL"):
        os.environ["DBT_MCP_LOG_LEVEL"] = "INFO"


# Setup environment before importing dbt_mcp
setup_dbt_environment()

try:
    from dbt_mcp.config.config import load_config
    from dbt_mcp.mcp.server import create_dbt_mcp

    # Create the server object that FastMCP expects to find
    # This follows the same pattern as dbt_mcp.main but exposes the server object
    config = load_config()
    mcp = asyncio.run(create_dbt_mcp(config))

except ImportError as e:
    print(f"❌ Failed to import dbt-mcp: {e}")
    print("   dbt-mcp is not available in this environment")
    print("   This server cannot function without dbt-mcp")
    print("   Please ensure dbt-mcp is installed: pip install git+https://github.com/dbt-labs/dbt-mcp.git")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error creating dbt MCP server: {e}")
    sys.exit(1)
