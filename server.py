"""FastMCP Cloud entry point for Data Product Hub MCP Server"""
import os
from data_product_hub.mcp_server import create_mcp_server

# Configuration from environment variables
DBT_PROJECT_PATH = os.getenv("DBT_PROJECT_PATH", "./sample_dbt_project")
DATABASE = os.getenv("DATABASE", "snowflake")
ENABLE_GIT_INTEGRATION = os.getenv("ENABLE_GIT_INTEGRATION", "true").lower() == "true"

# Create the MCP server instance for FastMCP Cloud
app = create_mcp_server(
    dbt_project_path=DBT_PROJECT_PATH,
    database=DATABASE,
    enable_git_integration=ENABLE_GIT_INTEGRATION
)

# FastMCP Cloud will automatically serve this app instance