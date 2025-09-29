"""Enhanced MCP Server for Data Product Hub with GitHub Repository Support"""

import glob
import os
from typing import Any, Dict, List, Optional

from fastmcp import Client, FastMCP

from data_product_hub.dbt import DbtModelProcessor
from data_product_hub.github_auth import get_github_auth
from data_product_hub.repo_manager import repo_manager


def find_model_files(dbt_project_path: str) -> List[str]:
    """Find all SQL model files in the dbt project"""
    return glob.glob(os.path.join(dbt_project_path, "models/**/*.sql"), recursive=True)


def find_model_file(model_name: str, model_files: List[str]) -> Optional[str]:
    """Find specific model file by name"""
    for model_file in model_files:
        if os.path.basename(model_file).replace(".sql", "") == model_name:
            return model_file
    return None


class CompositeMCPManager:
    """Manages connections to external MCP servers for composite functionality"""

    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.connected_servers: Dict[str, str] = {}

    async def add_git_client(self, git_server_url: Optional[str] = None) -> bool:
        """Add Git MCP server client"""
        try:
            if git_server_url:
                # Connect to external Git MCP server
                self.clients["git"] = Client(git_server_url)
                self.connected_servers["git"] = git_server_url
            else:
                # Use local git-mcp-server if available
                self.clients["git"] = Client("git-mcp-server")
                self.connected_servers["git"] = "local:git-mcp-server"

            # Test connection
            async with self.clients["git"]:
                await self.clients["git"].ping()

            return True
        except Exception as e:
            print(f"⚠️  Could not connect to Git MCP server: {e}")
            return False

    async def call_git_tool(self, tool_name: str, **params: Any) -> Dict[str, Any]:
        """Call a tool on the Git MCP server"""
        if "git" not in self.clients:
            return {"error": "Git MCP server not connected"}

        try:
            async with self.clients["git"]:
                result = await self.clients["git"].call_tool(tool_name, params)
                # Convert result to dict format
                if hasattr(result, "content"):
                    return {"content": result.content}
                elif hasattr(result, "__dict__"):
                    return result.__dict__
                else:
                    return {"result": str(result)}
        except Exception as e:
            return {"error": f"Git MCP call failed: {str(e)}"}

    def get_connected_servers(self) -> Dict[str, str]:
        """Get list of connected external servers"""
        return self.connected_servers.copy()


def create_github_mcp_server(
    default_dbt_project_path: Optional[str] = None,
    database: str = "snowflake",
    enable_git_integration: bool = True
) -> FastMCP:
    """Create and configure the FastMCP server with GitHub repository support"""

    app = FastMCP(
        name="Data Product Hub",
        instructions=(
            "A composite MCP server that provides dbt model analysis and data product quality assessment. "
            "Supports analysis of any GitHub dbt repository with proper authentication. "
            "Tools accept either a repo_url parameter for GitHub repositories or use the default local project."
        ),
    )

    # Initialize composite MCP manager
    mcp_manager = CompositeMCPManager()

    # Try to connect to Git MCP server on startup
    git_available = False
    if enable_git_integration:
        import asyncio

        try:
            # Try to connect to Git server (this will be called during server startup)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            git_available = loop.run_until_complete(mcp_manager.add_git_client())
            loop.close()
        except Exception:
            pass  # Git integration optional

    def _get_dbt_processor(repo_url: Optional[str] = None) -> tuple[Optional[DbtModelProcessor], Optional[str], Optional[Dict]]:
        """Get dbt processor for either GitHub repo or default local project

        Returns:
            Tuple of (processor, project_path, error_info)
        """
        if repo_url:
            # Handle GitHub repository
            local_path, error = repo_manager.get_repository(repo_url)
            if error:
                return None, None, error

            # Validate it's a proper dbt project
            if local_path is not None:
                validation = repo_manager.validate_dbt_project(local_path)
                if not validation["valid"]:
                    return None, None, {
                        "error": "Invalid dbt project",
                        "message": "Repository does not contain a valid dbt project",
                        "validation": validation
                    }

                return DbtModelProcessor(local_path, database), local_path, None
            else:
                return None, None, {"error": "Failed to get repository path"}
        else:
            # Use default local project
            if not default_dbt_project_path:
                return None, None, {
                    "error": "No dbt project specified",
                    "message": "Either provide repo_url parameter or configure default dbt project path"
                }

            # We've already checked that default_dbt_project_path is not None above
            assert default_dbt_project_path is not None
            return DbtModelProcessor(default_dbt_project_path, database), default_dbt_project_path, None

    def _analyze_dbt_model_impl(model_name: str, repo_url: Optional[str] = None) -> dict:
        """Internal implementation for dbt model analysis"""
        try:
            dbt_processor, project_path, error = _get_dbt_processor(repo_url)
            if error or not dbt_processor or not project_path:
                return {
                    "model_name": model_name,
                    "repo_url": repo_url,
                    **(error or {"error": "Failed to get dbt processor"}),
                    "metadata_exists": False,
                    "suggestions": "",
                    "dependencies": [],
                }

            # Use existing dbt analysis logic
            model_files = find_model_files(project_path)
            model_file = find_model_file(model_name, model_files)

            if not model_file:
                return {
                    "model_name": model_name,
                    "repo_url": repo_url,
                    "project_path": project_path,
                    "error": f"Model '{model_name}' not found in project",
                    "metadata_exists": False,
                    "suggestions": "",
                    "dependencies": [],
                }

            # Process using existing logic
            result = dbt_processor.process_model(model_file, advanced=False)

            return {
                "model_name": result["model_name"],
                "repo_url": repo_url,
                "project_path": project_path,
                "dbt_analysis": result,
                "metadata_exists": result["metadata_exists"],
                "suggestions": result["suggestions"],
                "dependencies": result["refs"],
            }

        except Exception as e:
            return {
                "model_name": model_name,
                "repo_url": repo_url,
                "error": str(e),
                "metadata_exists": False,
                "suggestions": f"Error analyzing model: {str(e)}",
                "dependencies": [],
            }

    @app.tool
    def analyze_dbt_model(model_name: str, repo_url: Optional[str] = None) -> dict:
        """Analyze a specific dbt model for quality and best practices

        Args:
            model_name: Name of the dbt model to analyze
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Comprehensive quality assessment including dbt analysis and metadata
        """
        return _analyze_dbt_model_impl(model_name, repo_url)

    @app.tool
    def check_metadata_coverage(repo_url: Optional[str] = None) -> dict:
        """Check metadata coverage across all dbt models

        Args:
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Summary of metadata coverage including missing models and statistics
        """
        try:
            dbt_processor, project_path, error = _get_dbt_processor(repo_url)
            if error or not dbt_processor or not project_path:
                return {
                    "operation": "metadata_coverage_check",
                    "repo_url": repo_url,
                    **(error or {"error": "Failed to get dbt processor"}),
                    "total_models": 0,
                    "metadata_coverage_percent": 0,
                }

            # Use existing metadata checking logic
            models, missing_metadata = dbt_processor.process_dbt_models(metadata_only=True)

            return {
                "operation": "metadata_coverage_check",
                "repo_url": repo_url,
                "project_path": project_path,
                "database": database,
                "total_models": len(models),
                "models_with_metadata": [m["model_name"] for m in models if m["metadata_exists"]],
                "missing_metadata": missing_metadata,
                "metadata_coverage_percent": round((len(models) - len(missing_metadata)) / len(models) * 100, 1)
                if models
                else 0,
            }

        except Exception as e:
            return {
                "operation": "metadata_coverage_check",
                "repo_url": repo_url,
                "error": str(e),
                "total_models": 0,
                "metadata_coverage_percent": 0,
            }

    @app.tool
    def get_project_lineage(repo_url: Optional[str] = None) -> dict:
        """Get lineage information for all models in the dbt project

        Args:
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Model lineage description and dependency information
        """
        try:
            dbt_processor, project_path, error = _get_dbt_processor(repo_url)
            if error or not dbt_processor or not project_path:
                return {
                    "operation": "project_lineage",
                    "repo_url": repo_url,
                    **(error or {"error": "Failed to get dbt processor"}),
                    "lineage_description": "",
                    "total_models": 0,
                    "models": [],
                }

            # Use existing lineage logic
            models, _ = dbt_processor.process_dbt_models(metadata_only=True)
            lineage_description, graph = dbt_processor.generate_lineage(models)

            return {
                "operation": "project_lineage",
                "repo_url": repo_url,
                "project_path": project_path,
                "lineage_description": lineage_description,
                "total_models": len(models),
                "models": [
                    {
                        "name": model["model_name"],
                        "dependencies": model["refs"],
                        "has_metadata": model["metadata_exists"],
                    }
                    for model in models
                ],
            }

        except Exception as e:
            return {
                "operation": "project_lineage",
                "repo_url": repo_url,
                "error": str(e),
                "lineage_description": "",
                "total_models": 0,
                "models": [],
            }

    @app.tool
    def assess_data_product_quality(model_name: str, repo_url: Optional[str] = None) -> dict:
        """Comprehensive data product quality assessment

        Args:
            model_name: Name of the data product/model to assess
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Comprehensive quality assessment from multiple tools
        """
        try:
            # Start with dbt analysis
            dbt_result = _analyze_dbt_model_impl(model_name, repo_url)

            # Placeholder for future integrations
            composite_assessment = {
                "model_name": model_name,
                "repo_url": repo_url,
                "dbt_analysis": dbt_result,
                "data_quality": {"status": "not_configured", "message": "No data quality tools configured"},
                "performance": {"status": "not_configured", "message": "No performance monitoring configured"},
                "usage": {"status": "not_configured", "message": "No usage analytics configured"},
                "overall_score": None,
                "recommendations": [
                    "Configure data quality monitoring (e.g., Monte Carlo MCP server)",
                    "Set up performance monitoring (e.g., Snowflake MCP server)",
                    "Enable usage analytics (e.g., Looker MCP server)",
                ],
            }

            return composite_assessment

        except Exception as e:
            return {
                "model_name": model_name,
                "repo_url": repo_url,
                "error": str(e),
                "overall_score": 0
            }

    @app.tool
    def analyze_dbt_model_with_git_context(model_name: str, repo_url: Optional[str] = None, include_history: bool = True) -> dict:
        """Enhanced dbt model analysis with Git context from connected Git MCP server

        Args:
            model_name: Name of the dbt model to analyze
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.
            include_history: Whether to include Git history and blame information

        Returns:
            Enhanced analysis including dbt quality assessment and Git context
        """
        # Start with basic dbt analysis
        dbt_result = _analyze_dbt_model_impl(model_name, repo_url)

        # Add Git context if available and requested
        git_context = {"status": "not_available", "message": "Git integration not enabled"}

        if include_history and git_available:
            try:
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Get Git information for the model file
                model_file_path = f"models/{model_name}.sql"

                # Call Git MCP server for file history
                history_result = loop.run_until_complete(
                    mcp_manager.call_git_tool("git_log", path=model_file_path, limit=5)
                )

                # Call Git MCP server for blame information
                blame_result = loop.run_until_complete(mcp_manager.call_git_tool("git_blame", path=model_file_path))

                loop.close()

                git_context = {
                    "status": "available",
                    "file_path": model_file_path,
                    "recent_commits": history_result.get("content", [])[:5] if "error" not in history_result else [],
                    "blame_info": blame_result.get("content", {}) if "error" not in blame_result else {},
                    "connected_servers": mcp_manager.get_connected_servers(),
                }

            except Exception as e:
                git_context = {"status": "error", "message": f"Git integration failed: {str(e)}"}

        # Combine dbt analysis with Git context
        enhanced_result = {
            **dbt_result,
            "git_context": git_context,
            "analysis_type": "enhanced_with_git",
            "composite_features": {
                "git_integration": git_available,
                "github_repository_support": True,
                "available_integrations": list(mcp_manager.get_connected_servers().keys()),
            },
        }

        return enhanced_result

    @app.tool
    def validate_github_repository(repo_url: str) -> dict:
        """Validate GitHub repository access and dbt project structure

        Args:
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo')

        Returns:
            Validation results including repository access and dbt project structure
        """
        try:
            github_auth = get_github_auth()
            if not github_auth:
                return {
                    "valid": False,
                    "repo_url": repo_url,
                    "error": "GitHub authentication not configured",
                    "message": "GitHub App credentials are required for repository access"
                }

            # Validate repo access without cloning
            validation_result = github_auth.validate_repo_access(repo_url)

            return {
                "repo_url": repo_url,
                **validation_result
            }

        except Exception as e:
            return {
                "valid": False,
                "repo_url": repo_url,
                "error": "Validation failed",
                "message": f"Unexpected error: {str(e)}"
            }

    @app.tool
    def get_composite_server_status() -> dict:
        """Get status of connected external MCP servers and available integrations

        Returns:
            Status of all connected external servers and their capabilities
        """
        github_auth = get_github_auth()

        return {
            "server_name": "Data Product Hub",
            "version": "2.0-github-composite",
            "github_integration": {
                "enabled": github_auth is not None,
                "status": "configured" if github_auth else "not_configured",
                "message": "Ready for GitHub repository analysis" if github_auth else "GitHub App credentials required"
            },
            "git_integration": {
                "enabled": git_available,
                "status": "connected" if git_available else "not_available",
            },
            "connected_servers": mcp_manager.get_connected_servers(),
            "available_tools": [
                "analyze_dbt_model",
                "check_metadata_coverage",
                "get_project_lineage",
                "assess_data_product_quality",
                "analyze_dbt_model_with_git_context",
                "validate_github_repository",
                "get_composite_server_status",
            ],
            "repository_support": {
                "github_repositories": True,
                "local_projects": bool(default_dbt_project_path),
                "authentication": "GitHub App" if github_auth else "Not configured"
            },
            "future_integrations": [
                "Monte Carlo MCP (data quality)",
                "DataHub MCP (data catalog)",
                "Snowflake MCP (performance metrics)",
            ],
        }

    return app


# Backwards compatibility - keep original function for local projects
def create_mcp_server(
    dbt_project_path: str, database: str = "snowflake", enable_git_integration: bool = True
) -> FastMCP:
    """Create MCP server with GitHub support (backwards compatible)"""
    return create_github_mcp_server(dbt_project_path, database, enable_git_integration)


async def run_github_mcp_server(
    default_dbt_project_path: Optional[str] = None, database: str = "snowflake"
) -> None:
    """Start the GitHub-enabled MCP server in stdio mode"""
    print("🚀 Starting Data Product Hub MCP Server with GitHub Support (stdio mode)")
    print(f"📁 Default dbt project: {default_dbt_project_path or 'None (GitHub repos only)'}")
    print(f"💾 Database: {database}")
    print("🔧 Available tools:")
    print("   - analyze_dbt_model(model_name, repo_url=None)")
    print("   - check_metadata_coverage(repo_url=None)")
    print("   - get_project_lineage(repo_url=None)")
    print("   - assess_data_product_quality(model_name, repo_url=None)")
    print("   - analyze_dbt_model_with_git_context(model_name, repo_url=None)")
    print("   - validate_github_repository(repo_url)")
    print("   - get_composite_server_status()")
    print()
    print("🔗 GitHub Repository Support:")
    github_auth = get_github_auth()
    if github_auth:
        print("   ✅ GitHub App authentication configured")
        print("   📋 Users can analyze any dbt repo by providing repo_url parameter")
    else:
        print("   ❌ GitHub App authentication not configured")
        print("   💡 Set GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY_BASE64 environment variables")
    print()

    app = create_github_mcp_server(default_dbt_project_path, database)

    # Start FastMCP server in stdio mode (standard for MCP)
    await app.run_stdio_async()