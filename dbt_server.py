"""
dbt MCP Server Entry Point for FastMCP Cloud Deployment

This serves as the entry point for deploying the official dbt-labs/dbt-mcp server
alongside our Data Product Hub composite server. This allows us to leverage
official dbt MCP tools while maintaining our orchestration capabilities.

Usage:
- Deploy this as a separate FastMCP instance for dbt-specific operations
- Your main Data Product Hub server connects to this as an MCP client
- Provides official dbt-core functionality without custom implementation
"""

import os
import sys
from pathlib import Path


# Configure environment for dbt-core operations
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


def main() -> None:
    """Main entry point for dbt MCP server"""

    # Setup environment
    setup_dbt_environment()

    try:
        # Import and run the official dbt MCP server
        from dbt_mcp.main import main as dbt_main

        print("🚀 Starting dbt MCP Server...")
        print("   This server provides official dbt-labs MCP tools")
        print("   for dbt-core projects and integrates with Data Product Hub")

        # Delegate to official dbt MCP main function
        dbt_main()

    except ImportError as e:
        print(f"❌ Failed to import dbt-mcp: {e}")
        print("   Make sure dbt-mcp is installed: pip install git+https://github.com/dbt-labs/dbt-mcp.git")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dbt MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
