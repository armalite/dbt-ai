# dbt-ai MCP Server Testing Guide

## What's Been Added

✅ **MCP Server Mode**: New `--mcp-server` flag to start dbt-ai as an MCP server
✅ **FastMCP Integration**: Using FastMCP 2.11.3 for MCP protocol support
✅ **Four Tools Exposed**:
- `analyze_dbt_model(model_name)` - Analyze specific model
- `check_metadata_coverage()` - Check metadata across all models
- `get_project_lineage()` - Get project lineage information
- `assess_data_product_quality(model_name)` - Composite quality assessment (placeholder for future integrations)

## Testing the MCP Server

### 1. Start the MCP Server

```bash
# Activate environment and install dependencies
source .venv/bin/activate
pip install -e .

# Start MCP server (requires a dbt project path)
dbt-ai --mcp-server -f /path/to/your/dbt/project

# Example with sample dbt project
dbt-ai --mcp-server -f ./sample-dbt-project
```

### 2. Test with MCP Client

Currently, the server runs in stdio mode (standard for MCP). To test:

```bash
# Test that it starts without errors
dbt-ai --mcp-server -f ./sample-dbt-project
# Should show:
# 🚀 Starting dbt-ai MCP Server
# 📁 dbt project: ./sample-dbt-project
# 💾 Database: snowflake
# 🔧 Available tools:
#    - analyze_dbt_model(model_name)
#    - check_metadata_coverage()
#    - get_project_lineage()
#    - assess_data_product_quality(model_name)
```

## What Works Now

✅ **CLI Integration**: `--mcp-server` flag added without breaking existing functionality
✅ **FastMCP Server**: Creates MCP server with proper tool registration
✅ **Tool Definitions**: All four tools properly defined with docstrings
✅ **Existing Logic Reuse**: Uses existing `DbtModelProcessor` logic
✅ **Error Handling**: Graceful error handling in all tools

## What's Next (Future Development)

🔄 **Composite MCP Client**: Add ability to call other MCP servers
🔄 **Service Discovery**: Auto-discover other MCP servers on local network
🔄 **Real Integrations**: Connect to Monte Carlo, DataHub, Snowflake MCP servers
🔄 **Configuration**: Simple config for specifying integration endpoints

## Current Limitations

- **Stdio Mode Only**: Currently runs in stdio mode (standard for MCP)
- **No Real Integrations**: `assess_data_product_quality` shows placeholder data
- **Testing**: Need proper MCP client to test tool functionality

## Architecture

```
CLI Mode:           dbt-ai -f project → JSON output
MCP Server Mode:    dbt-ai --mcp-server -f project → MCP tools exposed

MCP Tools:
├── analyze_dbt_model(model_name) → Uses existing process_model()
├── check_metadata_coverage() → Uses existing process_dbt_models(metadata_only=True)
├── get_project_lineage() → Uses existing generate_lineage()
└── assess_data_product_quality(model_name) → Future composite tool
```

## Installation

```bash
# Install with MCP support
pip install -e .

# Verify FastMCP is installed
python -c "import fastmcp; print('FastMCP version:', fastmcp.__version__)"
```

This is Phase 1 of the composite MCP server - basic foundation that exposes dbt-ai functionality via MCP protocol!