# Data Product Hub

> NOTE: This project is still under construction and in a state of flux. It is being tested internally so setup instructions below may not work as intended.

**Universal MCP Server for dbt Project Analysis - Works with Any GitHub Repository**

A production-ready Model Context Protocol (MCP) server that provides comprehensive dbt project quality assessment for **any GitHub repository**. Powered by GitHub App authentication for secure, scalable access to public and private repositories. Purpose-built for AI agents and modern data workflows.

## 🚀 What is Data Product Hub?

Data Product Hub transforms **any dbt project on GitHub** into an **agent-accessible data quality platform** that:

- **Analyzes ANY GitHub dbt repository** with AI-powered suggestions and best practices
- **Works with public and private repos** via secure GitHub App authentication
- **Supports subdirectory dbt projects** (detects dbt/, transform/, analytics/ folders)
- **Checks metadata coverage** across your entire data product portfolio
- **Maps data lineage** and dependency relationships
- **Integrates with Git** for enhanced context and change analysis
- **Exposes MCP tools** for seamless AI agent integration
- **Deploys anywhere** - FastMCP Cloud (recommended), Docker, Kubernetes

## Features

### 🔧 Universal MCP Tools (Work with Any GitHub Repository)
- `analyze_dbt_model(model_name, repo_url)` - Basic dbt model analysis
- `analyze_dbt_model_with_ai(model_name, repo_url)` - **NEW**: AI-powered analysis with user's OpenAI key
- `check_metadata_coverage(repo_url)` - Project-wide metadata assessment
- `get_project_lineage(repo_url)` - Data dependency mapping
- `assess_data_product_quality(model_name, repo_url)` - Comprehensive quality scoring
- `validate_github_repository(repo_url)` - Validate repo access and dbt structure
- `analyze_dbt_model_with_git_context(model_name, repo_url)` - dbt analysis + Git history
- `get_composite_server_status()` - Server capabilities and GitHub integration status

### 🌐 Deployment Flexibility
- **Local CLI** - `dph -f ./project`
- **Hostable MCP Server** - `dph serve --mcp-host 0.0.0.0`
- **Container Deployment** - Docker + Kubernetes + Helm charts
- **FastMCP Cloud** - One-click cloud deployment

### 🔗 Agent Integration
- Compatible with Claude Code, Cursor, and any MCP-enabled AI agent
- JSON-first output for automation and CI/CD pipelines
- Structured responses for programmatic consumption

## Quick Start

### 🎯 GitHub Repository Analysis (Recommended)

**1. Install the GitHub App on your dbt repositories:**
   - Visit: https://github.com/apps/data-product-hub/installations/new
   - Select repositories containing dbt projects
   - Grant read permissions

**2. (Optional) Enable AI features by adding your OpenAI API key:**
   - Go to Repository Settings → Environments
   - Create or use any of these environment names: `production`, `prod`, `data-analysis`, `main`, or `staging`
   - Add `OPENAI_API_KEY` as an **Environment Secret**
   - Set the value to your OpenAI API key (`sk-proj-...`)
   - This enables the `analyze_dbt_model_with_ai` tool
   - **Note:** All other tools work without an API key - only AI-powered analysis requires it

**3. Use via Claude Desktop:**
   ```json
   // Add to ~/.claude_desktop_config.json
   {
     "mcpServers": {
       "data-product-hub": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-fetch", "https://data-product-hub.fastmcp.app/mcp"]
       }
     }
   }
   ```

**4. Ask Claude to analyze any dbt repository:**
   ```
   "Analyze the customer_metrics model in https://github.com/company/analytics-dbt"
   "Get AI-powered suggestions for the user_events model in github.com/company/dbt-models"
   "Check metadata coverage for github.com/myorg/data-warehouse"
   "Get project lineage for github.com/startup/dbt-models"
   ```

### 🖥️ Local CLI Usage (Backwards Compatible)

```bash
# Install package
pip install data-product-hub

# CLI analysis
dph -f ./my-dbt-project --metadata-only

# Start local MCP server
dph --mcp-server -f ./my-dbt-project
```

### 🔌 Programmatic Integration

```python
from fastmcp import Client

# Connect to the universal MCP server
client = Client("https://data-product-hub.fastmcp.app/mcp")

async with client:
    # Basic analysis of any GitHub repository
    analysis = await client.call_tool(
        "analyze_dbt_model",
        {
            "model_name": "customer_summary",
            "repo_url": "https://github.com/company/analytics-dbt"
        }
    )

    # AI-powered analysis (requires OpenAI API key in environment secrets)
    ai_analysis = await client.call_tool(
        "analyze_dbt_model_with_ai",
        {
            "model_name": "customer_summary",
            "repo_url": "https://github.com/company/analytics-dbt"
        }
    )

    # Check metadata coverage across any project
    coverage = await client.call_tool(
        "check_metadata_coverage",
        {"repo_url": "github.com/myorg/data-warehouse"}
    )
```

## Deployment Options

### 1. Use the Hosted Service (Recommended)

**Ready to use immediately:**
- MCP Server: `https://data-product-hub.fastmcp.app/mcp`
- GitHub App: https://github.com/apps/data-product-hub/installations/new

**Quick Setup:**
1. Install the GitHub App on your dbt repositories
2. Add the MCP server to Claude Desktop configuration
3. Start analyzing any dbt repository via Claude

### 2. Deploy Your Own Instance

For organizations wanting their own instance:

**Prerequisites:**
- Fork this repository
- Create your own GitHub App with read permissions
- Get GitHub App ID and base64-encoded private key

**Deployment:**
1. Deploy to FastMCP Cloud with entry point: `server.py`
2. Set your GitHub App credentials as environment variables
3. Share your GitHub App installation URL with users

[📖 Complete Deployment Guide](./GITHUB_APP_SETUP.md)

### 2. Docker Deployment

```bash
# Using Docker Compose
docker-compose up

# Custom container
docker run -p 8080:8080 \
  -v ./my-dbt-project:/dbt-project \
  data-product-hub:latest
```

### 3. Kubernetes Deployment

```bash
# Deploy with Helm
helm install data-product-hub ./charts/data-product-hub \
  --set persistence.hostPath="/path/to/dbt-project" \
  --set dbtAi.database="snowflake"
```

[📖 Full Kubernetes Guide](./charts/data-product-hub/README.md)

## Configuration

The Data Product Hub MCP server is **ready to use** - no configuration required for end users! Just install the GitHub App and start analyzing.

### For Local CLI Usage Only

```bash
# Database configuration (local CLI only)
DATABASE=snowflake  # snowflake, postgres, redshift, bigquery

# OpenAI API (optional - for AI features in local CLI)
OPENAI_API_KEY=your-openai-api-key
DBT_AI_BASIC_MODEL=gpt-4o-mini
DBT_AI_ADVANCED_MODEL=gpt-4o
```

### Supported Databases
- Snowflake (default)
- PostgreSQL
- Amazon Redshift
- Google BigQuery

## Architecture

Data Product Hub implements a **composite MCP architecture**:

```
Your Data Product Hub Server
├── Core dbt Analysis
├── Git Integration (via Git MCP server)
├── Future: Monte Carlo Integration
├── Future: DataHub Integration
└── Future: Snowflake Performance Integration
```

This allows AI agents to get comprehensive data product insights from a single MCP endpoint.

## Use Cases

### For Data Teams
- **Automated quality checks** in CI/CD pipelines
- **Documentation coverage** monitoring
- **Lineage analysis** for impact assessment
- **Agent-driven data workflows**

### for AI Agents
- **Data product understanding** before making changes
- **Quality assessment** as part of automated reviews
- **Context-aware suggestions** with Git history
- **Comprehensive data product insights**

### For Platform Teams
- **Centralized data quality hub**
- **Production-ready MCP server** deployment
- **Multi-tool integration** platform
- **Kubernetes-native** scaling

## Migrating from dbt-ai

If you're upgrading from the legacy `dbt-ai` package:

```bash
# Old command
dbt-ai -f ./project --metadata-only

# New command (identical functionality) - use the short dph command!
dph -f ./project --metadata-only
```

All CLI functionality is **100% backwards compatible**.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT License](LICENSE)

---

**Data Product Hub** - Transforming dbt projects into agent-accessible data quality platforms. 🚀