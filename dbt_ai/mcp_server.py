"""MCP Server for dbt-ai - Data Product Quality Hub"""

import glob
import os
from typing import Dict, List, Optional, Any

from fastmcp import FastMCP

from dbt_ai.dbt import DbtModelProcessor


def find_model_files(dbt_project_path: str) -> List[str]:
    """Find all SQL model files in the dbt project"""
    return glob.glob(os.path.join(dbt_project_path, "models/**/*.sql"), recursive=True)


def find_model_file(model_name: str, model_files: List[str]) -> Optional[str]:
    """Find specific model file by name"""
    for model_file in model_files:
        if os.path.basename(model_file).replace(".sql", "") == model_name:
            return model_file
    return None


def create_mcp_server(dbt_project_path: str, database: str = "snowflake") -> FastMCP:
    """Create and configure the FastMCP server"""

    app = FastMCP(
        name="dbt-ai Data Product Quality Hub",
        instructions="A composite MCP server that provides dbt model analysis and data product quality assessment"
    )

    # Initialize dbt processor
    dbt_processor = DbtModelProcessor(dbt_project_path, database)

    @app.tool
    def analyze_dbt_model(model_name: str) -> dict:
        """Analyze a specific dbt model for quality and best practices

        Args:
            model_name: Name of the dbt model to analyze

        Returns:
            Comprehensive quality assessment including dbt analysis and metadata
        """
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
                    "dependencies": []
                }

            # Process using existing logic
            result = dbt_processor.process_model(model_file, advanced=False)

            return {
                "model_name": result["model_name"],
                "dbt_analysis": result,
                "metadata_exists": result["metadata_exists"],
                "suggestions": result["suggestions"],
                "dependencies": result["refs"]
            }

        except Exception as e:
            return {
                "model_name": model_name,
                "error": str(e),
                "metadata_exists": False,
                "suggestions": f"Error analyzing model: {str(e)}",
                "dependencies": []
            }

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
                "metadata_coverage_percent": round(
                    (len(models) - len(missing_metadata)) / len(models) * 100, 1
                ) if models else 0
            }

        except Exception as e:
            return {
                "operation": "metadata_coverage_check",
                "error": str(e),
                "total_models": 0,
                "metadata_coverage_percent": 0
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
                        "has_metadata": model["metadata_exists"]
                    }
                    for model in models
                ]
            }

        except Exception as e:
            return {
                "operation": "project_lineage",
                "error": str(e),
                "lineage_description": "",
                "total_models": 0,
                "models": []
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
            dbt_result = analyze_dbt_model(model_name)

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
                    "Enable usage analytics (e.g., Looker MCP server)"
                ]
            }

            return composite_assessment

        except Exception as e:
            return {
                "model_name": model_name,
                "error": str(e),
                "overall_score": 0
            }

    return app


async def run_mcp_server(dbt_project_path: str, database: str = "snowflake"):
    """Start the MCP server"""
    print(f"🚀 Starting dbt-ai MCP Server")
    print(f"📁 dbt project: {dbt_project_path}")
    print(f"💾 Database: {database}")
    print("🔧 Available tools:")
    print("   - analyze_dbt_model(model_name)")
    print("   - check_metadata_coverage()")
    print("   - get_project_lineage()")
    print("   - assess_data_product_quality(model_name)")
    print()

    app = create_mcp_server(dbt_project_path, database)

    # Start FastMCP server in stdio mode (standard for MCP)
    await app.run_stdio_async()


def start_mcp_server(dbt_project_path: str, database: str = "snowflake", port: int = 8080):
    """Start the MCP server (sync wrapper)"""
    import asyncio

    try:
        asyncio.run(run_mcp_server(dbt_project_path, database))
    except KeyboardInterrupt:
        print("\n👋 dbt-ai MCP Server stopped")
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        raise