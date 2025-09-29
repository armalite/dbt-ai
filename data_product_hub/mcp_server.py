"""MCP Server for dbt-ai - Data Product Quality Hub"""

import glob
import os
from typing import Any, Dict, List, Optional

from fastmcp import Client, FastMCP

from data_product_hub.dbt import DbtModelProcessor


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
                if hasattr(result, 'content'):
                    return {"content": result.content}
                elif hasattr(result, '__dict__'):
                    return result.__dict__
                else:
                    return {"result": str(result)}
        except Exception as e:
            return {"error": f"Git MCP call failed: {str(e)}"}

    def get_connected_servers(self) -> Dict[str, str]:
        """Get list of connected external servers"""
        return self.connected_servers.copy()


def create_mcp_server(
    dbt_project_path: str, database: str = "snowflake", enable_git_integration: bool = True
) -> FastMCP:
    """Create and configure the FastMCP server with composite capabilities"""

    app = FastMCP(
        name="Data Product Hub",
        instructions=(
            "A composite MCP server that provides dbt model analysis and "
            "data product quality assessment with Git integration"
        ),
    )

    # Initialize dbt processor
    dbt_processor = DbtModelProcessor(dbt_project_path, database)

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

    def _analyze_dbt_model_impl(model_name: str) -> dict:
        """Internal implementation for dbt model analysis"""
        try:
            # Use existing dbt analysis logic
            model_files = find_model_files(dbt_project_path)
            model_file = find_model_file(model_name, model_files)

            if not model_file:
                return {
                    "model_name": model_name,
                    "error": f"Model '{model_name}' not found in project",
                    "metadata_exists": False,
                    "suggestions": "",
                    "dependencies": [],
                }

            # Process using existing logic
            result = dbt_processor.process_model(model_file, advanced=False)

            return {
                "model_name": result["model_name"],
                "dbt_analysis": result,
                "metadata_exists": result["metadata_exists"],
                "suggestions": result["suggestions"],
                "dependencies": result["refs"],
            }

        except Exception as e:
            return {
                "model_name": model_name,
                "error": str(e),
                "metadata_exists": False,
                "suggestions": f"Error analyzing model: {str(e)}",
                "dependencies": [],
            }

    @app.tool
    def analyze_dbt_model(model_name: str) -> dict:
        """Analyze a specific dbt model for quality and best practices

        Args:
            model_name: Name of the dbt model to analyze

        Returns:
            Comprehensive quality assessment including dbt analysis and metadata
        """
        return _analyze_dbt_model_impl(model_name)

    @app.tool
    def check_metadata_coverage() -> dict:
        """Check metadata coverage across all dbt models

        Returns:
            Summary of metadata coverage including missing models and statistics
        """
        try:
            # Use existing metadata checking logic
            models, missing_metadata = dbt_processor.process_dbt_models(metadata_only=True)

            return {
                "operation": "metadata_coverage_check",
                "project_path": dbt_project_path,
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
                "error": str(e),
                "total_models": 0,
                "metadata_coverage_percent": 0,
            }

    @app.tool
    def get_project_lineage() -> dict:
        """Get lineage information for all models in the dbt project

        Returns:
            Model lineage description and dependency information
        """
        try:
            # Use existing lineage logic
            models, _ = dbt_processor.process_dbt_models(metadata_only=True)
            lineage_description, graph = dbt_processor.generate_lineage(models)

            return {
                "operation": "project_lineage",
                "project_path": dbt_project_path,
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
                "error": str(e),
                "lineage_description": "",
                "total_models": 0,
                "models": [],
            }

    @app.tool
    def assess_data_product_quality(model_name: str) -> dict:
        """Comprehensive data product quality assessment (future: will aggregate multiple tools)

        Args:
            model_name: Name of the data product/model to assess

        Returns:
            Comprehensive quality assessment from multiple tools
        """
        try:
            # Start with dbt analysis
            dbt_result = _analyze_dbt_model_impl(model_name)

            # Placeholder for future integrations
            composite_assessment = {
                "model_name": model_name,
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
            return {"model_name": model_name, "error": str(e), "overall_score": 0}

    @app.tool
    def analyze_dbt_model_with_git_context(model_name: str, include_history: bool = True) -> dict:
        """Enhanced dbt model analysis with Git context from connected Git MCP server

        Args:
            model_name: Name of the dbt model to analyze
            include_history: Whether to include Git history and blame information

        Returns:
            Enhanced analysis including dbt quality assessment and Git context
        """
        # Start with basic dbt analysis
        dbt_result = _analyze_dbt_model_impl(model_name)

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
                "available_integrations": list(mcp_manager.get_connected_servers().keys()),
            },
        }

        return enhanced_result

    @app.tool
    def get_composite_server_status() -> dict:
        """Get status of connected external MCP servers and available integrations

        Returns:
            Status of all connected external servers and their capabilities
        """
        return {
            "server_name": "Data Product Hub",
            "version": "2.0-composite",
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
                "get_composite_server_status",
            ],
            "future_integrations": [
                "Monte Carlo MCP (data quality)",
                "DataHub MCP (data catalog)",
                "Snowflake MCP (performance metrics)",
            ],
        }

    return app


async def run_mcp_server(dbt_project_path: str, database: str = "snowflake") -> None:
    """Start the MCP server in stdio mode"""
    print("🚀 Starting dbt-ai MCP Server (stdio mode)")
    print(f"📁 dbt project: {dbt_project_path}")
    print(f"💾 Database: {database}")
    print("🔧 Available tools:")
    print("   - analyze_dbt_model(model_name)")
    print("   - check_metadata_coverage()")
    print("   - get_project_lineage()")
    print("   - assess_data_product_quality(model_name)")
    print("   🆕 analyze_dbt_model_with_git_context(model_name)")
    print("   🆕 get_composite_server_status()")
    print()

    app = create_mcp_server(dbt_project_path, database)

    # Start FastMCP server in stdio mode (standard for MCP)
    await app.run_stdio_async()


async def run_mcp_server_hostable(
    dbt_project_path: str, database: str = "snowflake", host: str = "localhost", port: int = 8080
) -> None:
    """Start the MCP server in hostable mode (SSE transport)"""
    print("🚀 Starting dbt-ai MCP Server (hostable mode)")
    print(f"📁 dbt project: {dbt_project_path}")
    print(f"💾 Database: {database}")
    print(f"🌐 Host: {host}:{port}")
    print("🔧 Available tools:")
    print("   - analyze_dbt_model(model_name)")
    print("   - check_metadata_coverage()")
    print("   - get_project_lineage()")
    print("   - assess_data_product_quality(model_name)")
    print("   🆕 analyze_dbt_model_with_git_context(model_name)")
    print("   🆕 get_composite_server_status()")
    print()
    print(f"🔗 MCP clients can connect to: mcp+sse://{host}:{port}")
    print()

    app = create_mcp_server(dbt_project_path, database)

    # Start FastMCP server in SSE mode (hostable)
    await app.run_sse_async(host=host, port=port)


def start_mcp_server(dbt_project_path: str, database: str = "snowflake", _port: int = 8080) -> None:
    """Start the MCP server in stdio mode (sync wrapper)"""
    import asyncio

    try:
        asyncio.run(run_mcp_server(dbt_project_path, database))
    except KeyboardInterrupt:
        print("\n👋 dbt-ai MCP Server stopped")
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        raise


def start_mcp_server_hostable(
    dbt_project_path: str, database: str = "snowflake", host: str = "localhost", port: int = 8080
) -> None:
    """Start the MCP server in hostable mode (sync wrapper)"""
    import asyncio

    try:
        asyncio.run(run_mcp_server_hostable(dbt_project_path, database, host, port))
    except KeyboardInterrupt:
        print("\n👋 dbt-ai MCP Server stopped")
    except Exception as e:
        print(f"❌ Error starting hostable MCP server: {e}")
        raise
