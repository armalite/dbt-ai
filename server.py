"""FastMCP Cloud entry point for Data Product Hub MCP Server with GitHub Support"""
import os

from data_product_hub.mcp_server_github import create_github_mcp_server

# Configuration from environment variables
DEFAULT_DBT_PROJECT_PATH = os.getenv("DEFAULT_DBT_PROJECT_PATH", None)  # Optional fallback
DATABASE = os.getenv("DATABASE", "snowflake")
ENABLE_GIT_INTEGRATION = os.getenv("ENABLE_GIT_INTEGRATION", "true").lower() == "true"

# GitHub App authentication (required for GitHub repository support)
# Set these in your FastMCP Cloud environment:
# GITHUB_APP_ID = "your_github_app_id"
# GITHUB_APP_PRIVATE_KEY_BASE64 = "base64_encoded_private_key"

# Create the GitHub-enabled MCP server instance for FastMCP Cloud
app = create_github_mcp_server(
    default_dbt_project_path=DEFAULT_DBT_PROJECT_PATH, database=DATABASE, enable_git_integration=ENABLE_GIT_INTEGRATION
)

# FastMCP Cloud will automatically serve this app instance
