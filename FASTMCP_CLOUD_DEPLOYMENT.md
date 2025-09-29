# FastMCP Cloud Deployment Guide

Deploy Data Product Hub MCP Server to FastMCP Cloud with one click!

## Quick Deployment

### 1. Push to GitHub
Ensure your repository is pushed to GitHub (public or private).

### 2. Deploy to FastMCP Cloud
1. Visit [fastmcp.cloud](https://fastmcp.cloud)
2. Sign in with your GitHub account
3. Create a new project
4. Select this repository
5. Configure the entry point:
   - **File**: `server.py`
   - **Object**: `app`
   - **Entry Point**: `server.py:app`

### 3. Configure Environment Variables
In the FastMCP Cloud project settings, add these environment variables:

```bash
# Required: dbt project path (relative to repo root)
DBT_PROJECT_PATH=./sample_dbt_project

# Optional: Database type
DATABASE=snowflake

# Optional: Enable Git integration
ENABLE_GIT_INTEGRATION=true

# Optional: OpenAI API key (for AI features)
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. Deploy!
FastMCP Cloud will automatically:
- ✅ Install dependencies from `requirements-cloud.txt`
- ✅ Build your Data Product Hub MCP server
- ✅ Deploy to a unique URL
- ✅ Provide MCP endpoint for agents

## Available Tools

Your deployed Data Product Hub server will expose these MCP tools:

### Core dbt Analysis
- `analyze_dbt_model(model_name)` - Analyze specific dbt model
- `check_metadata_coverage()` - Check metadata across all models
- `get_project_lineage()` - Get model dependencies and relationships
- `assess_data_product_quality(model_name)` - Comprehensive quality assessment

### Enhanced Composite Features
- `analyze_dbt_model_with_git_context(model_name)` - Enhanced analysis with Git history
- `get_composite_server_status()` - Server capabilities and connected integrations

## Connecting AI Agents

Once deployed, connect your AI agents using the FastMCP Cloud URL:

```bash
# Example connection URL (FastMCP Cloud will provide the actual URL)
https://your-project-id.fastmcp.cloud
```

### Claude Desktop Integration
Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "data-product-hub": {
      "transport": "http",
      "url": "https://your-project-id.fastmcp.cloud"
    }
  }
}
```

### Custom Agent Integration
```python
from fastmcp import Client

# Connect to your deployed server
client = Client("https://your-project-id.fastmcp.cloud")

async with client:
    # Check metadata coverage
    result = await client.call_tool("check_metadata_coverage")
    print(result)

    # Analyze specific model
    analysis = await client.call_tool("analyze_dbt_model", {"model_name": "customers"})
    print(analysis)
```

## Advanced Configuration

### Custom dbt Project
To use your own dbt project instead of the sample:

1. **Option A**: Replace `sample_dbt_project/` in your repo
2. **Option B**: Set `DBT_PROJECT_PATH` environment variable to your project path

### Database Configuration
Set the `DATABASE` environment variable:
- `snowflake` (default)
- `postgres`
- `redshift`
- `bigquery`

### Git Integration
The server attempts to connect to Git MCP servers for enhanced analysis:
- Set `ENABLE_GIT_INTEGRATION=false` to disable
- Gracefully degrades if Git server unavailable

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `requirements-cloud.txt`
2. **dbt Project Not Found**: Check `DBT_PROJECT_PATH` environment variable
3. **OpenAI Errors**: Add `OPENAI_API_KEY` environment variable for AI features

### Testing Locally
Before deploying, test the entry point:

```bash
# Test the server.py entry point
python -c "import server; print('✅ Server loads successfully')"

# Test with fastmcp CLI
pip install fastmcp
fastmcp inspect server.py:app
```

## Benefits of FastMCP Cloud Deployment

✅ **Zero Infrastructure**: No servers to manage
✅ **Auto-scaling**: Handles traffic automatically
✅ **Free Beta**: No cost during beta period
✅ **HTTPS Endpoints**: Secure agent connections
✅ **Auto-deployment**: Deploys on every push to main
✅ **Preview Deployments**: Test changes in PRs

## Migration from Self-Hosted

If you were using the self-hosted version:

```bash
# Old: Self-hosted
dph serve -f ./project --mcp-host 0.0.0.0

# New: FastMCP Cloud
# Just deploy and use the provided URL!
```

All the same tools and functionality, but hosted and managed for you! 🚀