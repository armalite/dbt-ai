import argparse
import json
import os

from data_product_hub.dbt import DbtModelProcessor
from data_product_hub.report import generate_html_report


def output_json(data: dict) -> None:
    """Output structured JSON to stdout for agent consumption"""
    print(json.dumps(data, indent=2))


def output_text_metadata_only(models: list, missing_metadata: list) -> None:
    """Output metadata-only results in text format"""
    if missing_metadata:
        print("The following models are missing metadata:")
        for model_name in missing_metadata:
            print(f"  - {model_name}")
    else:
        print("All models have associated metadata.")

    print(f"\nMetadata check complete. {len(models)} models analyzed.")


def output_text_full_analysis(
    models: list, missing_metadata: list, lineage_description: str, output_path: str, advanced: bool
) -> None:
    """Output full analysis results in text format"""
    print(f"Lineage description:\n {lineage_description}")

    generate_html_report(models, output_path, missing_metadata)
    advancedprint = "advanced " if advanced else ""
    print(f"Generated {advancedprint}improvement suggestions report at: {output_path}")

    models_without_metadata = [model["model_name"] for model in models if not model["metadata_exists"]]

    if models_without_metadata:
        print("\nThe following models are missing metadata:")
        for model_name in models_without_metadata:
            print(f"  - {model_name}")
    else:
        print("\nAll models have associated metadata.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate improvement suggestions and check metadata coverage for dbt models"
    )
    parser.add_argument("-f", "--dbt-project-path", help="Path to the dbt project directory")
    parser.add_argument(
        "--create-models",
        help="Create dbt models using the provided prompt",
        default=None,
    )
    parser.add_argument(
        "-a",
        "--advanced-rec",
        action="store_true",
        help="Generate only advanced recommendations for dbt models",
    )
    parser.add_argument(
        "-d",
        "--database",
        help="Specify the type of database system the dbt project is built on",
        choices=["snowflake", "postgres", "redshift", "bigquery"],
        default="snowflake",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Check only metadata coverage without generating AI suggestions",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="json",
        help="Output format: json (default) or text for human-readable output",
    )
    parser.add_argument(
        "--mcp-server",
        action="store_true",
        help="Start MCP server mode for AI agent integration (stdio transport)",
    )
    parser.add_argument(
        "--mcp-port",
        type=int,
        default=8080,
        help="Port for MCP server (default: 8080)",
    )
    parser.add_argument(
        "serve",
        nargs="?",
        const=True,
        help="Start hostable MCP server mode (network accessible)",
    )
    parser.add_argument(
        "--mcp-host",
        default="localhost",
        help="Host for hostable MCP server (default: localhost)",
    )
    args = parser.parse_args()

    # Handle MCP server modes
    if args.mcp_server or args.serve:
        if not args.dbt_project_path:
            print("❌ Error: --dbt-project-path is required for MCP server mode")
            return

        try:
            if args.serve:
                # Hostable MCP server mode
                from data_product_hub.mcp_server import start_mcp_server_hostable

                start_mcp_server_hostable(args.dbt_project_path, args.database, args.mcp_host, args.mcp_port)
            else:
                # Traditional stdio MCP server mode
                from data_product_hub.mcp_server import start_mcp_server

                start_mcp_server(args.dbt_project_path, args.database, args.mcp_port)
        except ImportError:
            print("❌ Error: FastMCP not installed. Run: pip install fastmcp")
            return
        return

    if not args.create_models:
        processor = DbtModelProcessor(args.dbt_project_path, args.database)

        if args.metadata_only:
            # Metadata-only mode: skip AI suggestions
            models, missing_metadata = processor.process_dbt_models(advanced=False, metadata_only=True)

            if args.output == "json":
                # JSON output for agents
                result = {
                    "operation": "metadata_check",
                    "project_path": args.dbt_project_path,
                    "total_models": len(models),
                    "missing_metadata": [model["model_name"] for model in models if not model["metadata_exists"]],
                    "models_with_metadata": [model["model_name"] for model in models if model["metadata_exists"]],
                    "metadata_coverage_percent": round((len(models) - len(missing_metadata)) / len(models) * 100, 1)
                    if models
                    else 0,
                }
                output_json(result)
            else:
                # Text output for humans
                output_text_metadata_only(models, missing_metadata)
        else:
            # Normal mode: full processing with AI suggestions
            models, missing_metadata = processor.process_dbt_models(advanced=args.advanced_rec)

            if args.output == "json":
                # JSON output for agents
                lineage_description, graph = processor.generate_lineage(models)

                result = {
                    "operation": "full_analysis",
                    "project_path": args.dbt_project_path,
                    "advanced_mode": args.advanced_rec,
                    "database": args.database,
                    "total_models": len(models),
                    "models": [
                        {
                            "name": model["model_name"],
                            "has_metadata": model["metadata_exists"],
                            "suggestions": model["suggestions"],
                            "dependencies": model["refs"],
                        }
                        for model in models
                    ],
                    "missing_metadata": missing_metadata,
                    "metadata_coverage_percent": round((len(models) - len(missing_metadata)) / len(models) * 100, 1)
                    if models
                    else 0,
                    "lineage_description": lineage_description,
                }
                output_json(result)
            else:
                # Text output for humans
                output_path = os.path.join(args.dbt_project_path, "dbt_model_suggestions.html")
                lineage_description, graph = processor.generate_lineage(models)
                output_text_full_analysis(models, missing_metadata, lineage_description, output_path, args.advanced_rec)
    else:
        processor = DbtModelProcessor(args.dbt_project_path, args.database)
        prompt = args.create_models
        processor.create_dbt_models(prompt)


if __name__ == "__main__":
    main()
