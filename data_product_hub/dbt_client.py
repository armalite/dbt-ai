"""
dbt Client Abstraction Layer

This module provides a unified interface for dbt operations that can switch between:
1. Custom dbt implementation (current, Python 3.10 compatible)
2. Official dbt MCP client (future, requires Python 3.12)

This abstraction allows seamless migration when upgrading to Python 3.12.
"""

import glob
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DbtClientInterface(ABC):
    """Abstract interface for dbt operations"""

    @abstractmethod
    async def get_model_info(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Get detailed information about a dbt model"""
        pass

    @abstractmethod
    async def get_project_models(self, project_path: str) -> List[Dict[str, Any]]:
        """Get all models in the dbt project"""
        pass

    @abstractmethod
    async def get_model_lineage(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Get lineage information for a model"""
        pass

    @abstractmethod
    async def check_metadata_coverage(self, project_path: str) -> Dict[str, Any]:
        """Check metadata coverage across the project"""
        pass

    @abstractmethod
    async def validate_dbt_project(self, project_path: str) -> Dict[str, Any]:
        """Validate that the project is a valid dbt project"""
        pass

    @abstractmethod
    async def compile_model(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Compile a dbt model to SQL"""
        pass

    @abstractmethod
    async def get_lineage(self, project_path: str) -> Dict[str, Any]:
        """Get project lineage information"""
        pass


class CustomDbtClient(DbtClientInterface):
    """Custom dbt implementation using our existing DbtModelProcessor"""

    def __init__(self, database: str = "snowflake"):
        self.database = database

    def _get_processor(self, project_path: str):
        """Get a DbtModelProcessor instance for the project"""
        from .dbt import DbtModelProcessor

        return DbtModelProcessor(dbt_project_path=project_path, database=self.database)

    async def get_model_info(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Get detailed information about a dbt model"""
        try:
            processor = self._get_processor(project_path)

            # Find the model file
            model_files = glob.glob(os.path.join(project_path, "models", "**", "*.sql"), recursive=True)
            model_file = None
            for file in model_files:
                if os.path.basename(file).replace(".sql", "") == model_name:
                    model_file = file
                    break

            if not model_file:
                return {"error": f"Model {model_name} not found"}

            # Process the model
            result = processor.process_model(model_file, advanced=False, metadata_only=True)
            result["source"] = "custom_implementation"
            return result
        except Exception as e:
            return {"error": f"Error getting model info: {e!s}"}

    async def get_project_models(self, project_path: str) -> List[Dict[str, Any]]:
        """Get all models in the dbt project"""
        try:
            processor = self._get_processor(project_path)
            models, _ = processor.process_dbt_models(metadata_only=True)

            return [
                {
                    "name": model["model_name"],
                    "description": model.get("description", ""),
                    "path": model.get("file_path", ""),
                    "source": "custom_implementation",
                }
                for model in models
            ]
        except Exception as e:
            return [{"error": f"Error listing models: {e!s}"}]

    async def get_model_lineage(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Get lineage information for a model"""
        try:
            processor = self._get_processor(project_path)
            models, _ = processor.process_dbt_models(metadata_only=True)
            lineage_description, graph = processor.generate_lineage(models)

            # Find this model's dependencies
            model_deps = []
            for model in models:
                if model["model_name"] == model_name:
                    model_deps = model.get("refs", [])
                    break

            return {
                "model": model_name,
                "dependencies": model_deps,
                "lineage_description": lineage_description,
                "source": "custom_implementation",
            }
        except Exception as e:
            return {"error": f"Error getting lineage: {e!s}"}

    async def check_metadata_coverage(self, project_path: str) -> Dict[str, Any]:
        """Check metadata coverage across the project"""
        try:
            processor = self._get_processor(project_path)
            models, missing_metadata = processor.process_dbt_models(metadata_only=True)

            return {
                "total_models": len(models),
                "models_with_metadata": [m["model_name"] for m in models if m["metadata_exists"]],
                "missing_metadata": missing_metadata,
                "metadata_coverage_percent": round((len(models) - len(missing_metadata)) / len(models) * 100, 1)
                if models
                else 0,
                "source": "custom_implementation",
            }
        except Exception as e:
            return {"error": f"Error checking coverage: {e!s}"}

    async def validate_dbt_project(self, project_path: str) -> Dict[str, Any]:
        """Validate that the project is a valid dbt project"""
        try:
            # Check for dbt_project.yml
            dbt_project_file = os.path.join(project_path, "dbt_project.yml")
            if not os.path.exists(dbt_project_file):
                return {"valid": False, "error": "dbt_project.yml not found", "source": "custom_implementation"}

            processor = self._get_processor(project_path)
            models, _ = processor.process_dbt_models(metadata_only=True)

            return {
                "valid": True,
                "dbt_project_path": project_path,
                "models_found": len(models),
                "source": "custom_implementation",
            }
        except Exception as e:
            return {"valid": False, "error": f"Invalid dbt project: {e!s}", "source": "custom_implementation"}

    async def compile_model(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Compile a dbt model to SQL"""
        try:
            # Find the model file and read SQL
            model_files = glob.glob(os.path.join(project_path, "models", "**", "*.sql"), recursive=True)
            model_file = None
            for file in model_files:
                if os.path.basename(file).replace(".sql", "") == model_name:
                    model_file = file
                    break

            if not model_file:
                return {"error": f"Model {model_name} not found"}

            with open(model_file, "r") as f:
                sql = f.read()

            return {"model": model_name, "compiled_sql": sql, "source": "custom_implementation"}
        except Exception as e:
            return {"error": f"Error compiling model: {e!s}"}

    async def get_lineage(self, project_path: str) -> Dict[str, Any]:
        """Get project lineage information"""
        try:
            processor = self._get_processor(project_path)
            models, _ = processor.process_dbt_models(metadata_only=True)
            lineage_description, graph = processor.generate_lineage(models)

            return {
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
                "source": "custom_implementation",
            }
        except Exception as e:
            return {"error": f"Error getting lineage: {e!s}"}


class OfficialDbtMcpClient(DbtClientInterface):
    """Official dbt MCP client implementation (requires Python 3.12)"""

    def __init__(self, mcp_server_url: str = "http://localhost:8000"):
        self.mcp_server_url = mcp_server_url
        self._client = None

    async def _get_client(self):
        """Get or create MCP client connection"""
        if self._client is None:
            try:
                from fastmcp import Client

                self._client = Client(self.mcp_server_url)
            except ImportError:
                raise ImportError("fastmcp client not available for dbt MCP connection")
        return self._client

    async def get_model_info(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Get detailed information about a dbt model using official MCP"""
        try:
            client = await self._get_client()
            async with client:
                result = await client.call_tool("get_model", {"name": model_name, "project_path": project_path})
                if isinstance(result, dict):
                    result["source"] = "official_dbt_mcp"
                    return result
                else:
                    return {"error": "Unexpected result format from dbt MCP"}
        except Exception as e:
            return {"error": f"dbt MCP error: {e!s}"}

    async def get_project_models(self, project_path: str) -> List[Dict[str, Any]]:
        """Get all models using official dbt MCP"""
        try:
            client = await self._get_client()
            async with client:
                result = await client.call_tool("list_models", {"project_path": project_path})
                # Add source to each model
                if isinstance(result, list):
                    for model in result:
                        if isinstance(model, dict):
                            model["source"] = "official_dbt_mcp"
                    return result
                else:
                    return [{"error": "Unexpected result format from dbt MCP"}]
        except Exception as e:
            return [{"error": f"dbt MCP error: {e!s}"}]

    async def get_model_lineage(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Get lineage using official dbt MCP"""
        try:
            client = await self._get_client()
            async with client:
                result = await client.call_tool("get_lineage", {"model": model_name, "project_path": project_path})
                if isinstance(result, dict):
                    result["source"] = "official_dbt_mcp"
                    return result
                else:
                    return {"error": "Unexpected result format from dbt MCP"}
        except Exception as e:
            return {"error": f"dbt MCP error: {e!s}"}

    async def check_metadata_coverage(self, project_path: str) -> Dict[str, Any]:
        """Check metadata coverage using official dbt MCP"""
        try:
            client = await self._get_client()
            async with client:
                result = await client.call_tool("check_coverage", {"project_path": project_path})
                if isinstance(result, dict):
                    result["source"] = "official_dbt_mcp"
                    return result
                else:
                    return {"error": "Unexpected result format from dbt MCP"}
        except Exception as e:
            return {"error": f"dbt MCP error: {e!s}"}

    async def validate_dbt_project(self, project_path: str) -> Dict[str, Any]:
        """Validate project using official dbt MCP"""
        try:
            client = await self._get_client()
            async with client:
                result = await client.call_tool("validate_project", {"project_path": project_path})
                if isinstance(result, dict):
                    result["source"] = "official_dbt_mcp"
                    return result
                else:
                    return {"error": "Unexpected result format from dbt MCP"}
        except Exception as e:
            return {"error": f"dbt MCP error: {e!s}"}

    async def compile_model(self, model_name: str, project_path: str) -> Dict[str, Any]:
        """Compile model using official dbt MCP"""
        try:
            client = await self._get_client()
            async with client:
                result = await client.call_tool("compile", {"models": [model_name], "project_path": project_path})
                if isinstance(result, dict):
                    result["source"] = "official_dbt_mcp"
                    return result
                else:
                    return {"error": "Unexpected result format from dbt MCP"}
        except Exception as e:
            return {"error": f"dbt MCP error: {e!s}"}

    async def get_lineage(self, project_path: str) -> Dict[str, Any]:
        """Get project lineage using official dbt MCP"""
        try:
            client = await self._get_client()
            async with client:
                result = await client.call_tool("get_project_lineage", {"project_path": project_path})
                if isinstance(result, dict):
                    result["source"] = "official_dbt_mcp"
                    return result
                else:
                    return {"error": "Unexpected result format from dbt MCP"}
        except Exception as e:
            return {"error": f"dbt MCP error: {e!s}"}


def create_dbt_client(
    use_official_mcp: Optional[bool] = None, mcp_server_url: Optional[str] = None, database: str = "snowflake"
) -> DbtClientInterface:
    """
    Factory function to create the appropriate dbt client

    Args:
        use_official_mcp: If True, use official dbt MCP. If False, use custom implementation.
                         If None, auto-detect based on Python version and availability.
        mcp_server_url: URL for official dbt MCP server
        database: Database type for custom implementation

    Returns:
        Configured dbt client instance
    """

    # Auto-detect if not specified
    if use_official_mcp is None:
        # Check if we're on Python 3.12+ and dbt-mcp is available
        python_version = sys.version_info
        if python_version >= (3, 12):
            try:
                import dbt_mcp

                use_official_mcp = True
            except ImportError:
                use_official_mcp = False
        else:
            use_official_mcp = False

    if use_official_mcp:
        server_url = mcp_server_url or os.getenv("DBT_MCP_SERVER_URL", "http://localhost:8000")
        print(f"🔗 Using official dbt MCP client: {server_url}")
        return OfficialDbtMcpClient(server_url)
    else:
        print(f"🛠️ Using custom dbt implementation (database: {database})")
        return CustomDbtClient(database)


# Convenience function for backwards compatibility
def get_dbt_client(**kwargs) -> DbtClientInterface:
    """Get a dbt client instance with sensible defaults"""
    return create_dbt_client(**kwargs)
