"""Enhanced MCP Server for Data Product Hub with GitHub Repository Support"""

import glob
import os
from typing import Any, Dict, List, Optional

from fastmcp import Client, FastMCP

from data_product_hub.api_keys import get_api_key_source, get_openai_api_key
from data_product_hub.dbt_client import DbtClientInterface, create_dbt_client
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
            return {"error": f"Git MCP call failed: {e!s}"}

    def get_connected_servers(self) -> Dict[str, str]:
        """Get list of connected external servers"""
        return self.connected_servers.copy()


def create_github_mcp_server(
    default_dbt_project_path: Optional[str] = None, database: str = "snowflake", enable_git_integration: bool = True
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

    # Initialize dbt client (auto-detects implementation based on Python version)
    dbt_client = create_dbt_client(database=database)

    # Try to connect to Git MCP server on startup
    git_available = False
    if enable_git_integration:
        pass

        # Git integration will be initialized lazily when needed
        # This avoids event loop issues during server startup

    async def _get_dbt_client_and_path(
        repo_url: Optional[str] = None,
    ) -> tuple[Optional[DbtClientInterface], Optional[str], Optional[Dict]]:
        """Get dbt client and project path for either GitHub repo or default local project

        Returns:
            Tuple of (dbt_client, project_path, error_info)
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
                    return (
                        None,
                        None,
                        {
                            "error": "Invalid dbt project",
                            "message": "Repository does not contain a valid dbt project",
                            "validation": validation,
                        },
                    )

                # Use the discovered dbt project path
                dbt_subpath = validation.get("dbt_project_subpath", ".")
                if dbt_subpath and dbt_subpath != ".":
                    dbt_project_path = os.path.join(local_path, dbt_subpath)
                else:
                    dbt_project_path = local_path

                return dbt_client, dbt_project_path, None
            else:
                return None, None, {"error": "Failed to get repository path"}
        else:
            # Use default local project
            if not default_dbt_project_path:
                return (
                    None,
                    None,
                    {
                        "error": "No dbt project specified",
                        "message": "Either provide repo_url parameter or configure default dbt project path",
                    },
                )

            # We've already checked that default_dbt_project_path is not None above
            assert default_dbt_project_path is not None
            return dbt_client, default_dbt_project_path, None

    async def _analyze_dbt_model_impl(model_name: str, repo_url: Optional[str] = None) -> dict:
        """Internal implementation for dbt model analysis"""
        try:
            dbt_client_instance, project_path, error = await _get_dbt_client_and_path(repo_url)
            if error or not dbt_client_instance or not project_path:
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

            # Get model info using abstracted client
            model_info = await dbt_client_instance.get_model_info(model_name, project_path)

            return {
                "model_name": model_name,
                "repo_url": repo_url,
                "project_path": project_path,
                "dbt_analysis": model_info,
                "metadata_exists": "description" in model_info and bool(model_info.get("description")),
                "suggestions": model_info.get("suggestions", ""),
                "dependencies": model_info.get("dependencies", []),
            }

        except Exception as e:
            return {
                "model_name": model_name,
                "repo_url": repo_url,
                "error": str(e),
                "metadata_exists": False,
                "suggestions": f"Error analyzing model: {e!s}",
                "dependencies": [],
            }

    @app.tool
    async def analyze_dbt_model(model_name: str, repo_url: Optional[str] = None) -> dict:
        """Analyze a specific dbt model for quality and best practices

        Args:
            model_name: Name of the dbt model to analyze
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Comprehensive quality assessment including dbt analysis and metadata
        """
        return await _analyze_dbt_model_impl(model_name, repo_url)

    @app.tool
    async def analyze_dbt_model_with_ai(model_name: str, repo_url: Optional[str] = None) -> dict:
        """Analyze a specific dbt model with AI-powered suggestions (requires OpenAI API key)

        Args:
            model_name: Name of the dbt model to analyze
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Enhanced dbt analysis with AI-powered suggestions and recommendations
        """
        # Get basic analysis first
        basic_analysis = await _analyze_dbt_model_impl(model_name, repo_url)

        # Check for OpenAI API access
        api_key = get_openai_api_key(repo_url)
        if not api_key:
            # Return basic analysis with note about missing API key
            return {
                **basic_analysis,
                "ai_analysis": {
                    "status": "unavailable",
                    "message": "OpenAI API key not found. Add OPENAI_API_KEY to your repository's environment secrets.",
                    "setup_instructions": [
                        "1. Go to Repository Settings → Environments",
                        "2. Create or select an environment (e.g., 'production')",
                        "3. Add OPENAI_API_KEY as an Environment Secret",
                        "4. Set the value to your OpenAI API key (sk-proj-...)",
                    ],
                },
                "api_key_source": get_api_key_source(repo_url),
            }

        # Perform AI-enhanced analysis
        try:
            dbt_client_instance, project_path, error = await _get_dbt_client_and_path(repo_url)
            if error or not dbt_client_instance or not project_path:
                return {**basic_analysis, "ai_analysis": {"status": "error", "message": "Could not access dbt project"}}

            # Get model info with AI analysis
            model_info = await dbt_client_instance.get_model_info(model_name, project_path)

            if not model_info:
                return {
                    **basic_analysis,
                    "ai_analysis": {"status": "error", "message": f"Model '{model_name}' not found"},
                }

            # AI analysis is handled by the client implementation
            ai_result = model_info

            return {
                **basic_analysis,
                "ai_analysis": {
                    "status": "success",
                    "advanced_suggestions": ai_result.get("suggestions", ""),
                    "ai_recommendations": ai_result.get("ai_recommendations", []),
                    "quality_score": ai_result.get("quality_score"),
                },
                "api_key_source": get_api_key_source(repo_url),
            }

        except Exception as e:
            return {
                **basic_analysis,
                "ai_analysis": {"status": "error", "message": f"AI analysis failed: {e!s}"},
                "api_key_source": get_api_key_source(repo_url),
            }

    @app.tool
    async def check_metadata_coverage(repo_url: Optional[str] = None) -> dict:
        """Check metadata coverage across all dbt models

        Args:
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Summary of metadata coverage including missing models and statistics
        """
        try:
            dbt_client_instance, project_path, error = await _get_dbt_client_and_path(repo_url)
            if error or not dbt_client_instance or not project_path:
                return {
                    "operation": "metadata_coverage_check",
                    "repo_url": repo_url,
                    **(error or {"error": "Failed to get dbt client"}),
                    "total_models": 0,
                    "metadata_coverage_percent": 0,
                }

            # Check metadata coverage using abstracted client
            coverage = await dbt_client_instance.check_metadata_coverage(project_path)

            return {
                "operation": "metadata_coverage_check",
                "repo_url": repo_url,
                "project_path": project_path,
                "database": database,
                **coverage,
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
    async def get_project_lineage(repo_url: Optional[str] = None) -> dict:
        """Get lineage information for all models in the dbt project

        Args:
            repo_url: GitHub repository URL (e.g., 'https://github.com/org/repo').
                     If not provided, uses the default configured dbt project.

        Returns:
            Model lineage description and dependency information
        """
        try:
            dbt_client_instance, project_path, error = await _get_dbt_client_and_path(repo_url)
            if error or not dbt_client_instance or not project_path:
                return {
                    "operation": "project_lineage",
                    "repo_url": repo_url,
                    **(error or {"error": "Failed to get dbt client"}),
                    "lineage_description": "",
                    "total_models": 0,
                    "models": [],
                }

            # Get lineage using abstracted client
            lineage = await dbt_client_instance.get_lineage(project_path)

            return {
                "operation": "project_lineage",
                "repo_url": repo_url,
                "project_path": project_path,
                **lineage,
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
            return {"model_name": model_name, "repo_url": repo_url, "error": str(e), "overall_score": 0}

    @app.tool
    async def analyze_dbt_model_with_git_context(
        model_name: str, repo_url: Optional[str] = None, include_history: bool = True
    ) -> dict:
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
        dbt_result = await _analyze_dbt_model_impl(model_name, repo_url)

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
                git_context = {"status": "error", "message": f"Git integration failed: {e!s}"}

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
                    "message": "GitHub App credentials are required for repository access",
                }

            # Validate repo access without cloning
            validation_result = github_auth.validate_repo_access(repo_url)

            # Remove sensitive access token from response
            result = {"repo_url": repo_url, **validation_result}
            # Don't expose access tokens in responses
            if "access_token" in result:
                del result["access_token"]
            return result

        except Exception as e:
            return {
                "valid": False,
                "repo_url": repo_url,
                "error": "Validation failed",
                "message": f"Unexpected error: {e!s}",
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
                "message": "Ready for GitHub repository analysis" if github_auth else "GitHub App credentials required",
            },
            "git_integration": {
                "enabled": git_available,
                "status": "connected" if git_available else "not_available",
            },
            "connected_servers": mcp_manager.get_connected_servers(),
            "available_tools": [
                "analyze_dbt_model",
                "analyze_dbt_model_with_ai",
                "check_metadata_coverage",
                "get_project_lineage",
                "assess_data_product_quality",
                "analyze_dbt_model_with_git_context",
                "validate_github_repository",
                "get_composite_server_status",
            ],
            "ai_features": {
                "local_openai_key": bool(os.getenv("OPENAI_API_KEY")),
                "supports_user_api_keys": True,
                "api_key_sources": ["local_environment", "github_environment_secrets"],
            },
            "repository_support": {
                "github_repositories": True,
                "local_projects": bool(default_dbt_project_path),
                "authentication": "GitHub App" if github_auth else "Not configured",
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


async def run_github_mcp_server(default_dbt_project_path: Optional[str] = None, database: str = "snowflake") -> None:
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
