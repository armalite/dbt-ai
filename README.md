# Data Product Hub

**Composite MCP Server for Data Product Quality Assessment and AI Agent Integration**

A production-ready Model Context Protocol (MCP) server that provides comprehensive data product quality assessment by integrating dbt analysis with Git context and other data tools. Purpose-built for AI agents and modern data workflows.

## 🚀 What is Data Product Hub?

Data Product Hub transforms your dbt project into an **agent-accessible data quality platform** that:

- **Analyzes dbt models** with AI-powered suggestions and best practices
- **Checks metadata coverage** across your entire data product portfolio
- **Maps data lineage** and dependency relationships
- **Integrates with Git** for enhanced context and change analysis
- **Exposes MCP tools** for seamless AI agent integration
- **Deploys anywhere** - local CLI, Docker, Kubernetes, or FastMCP Cloud

## Features

### 🔧 Core MCP Tools
- `analyze_dbt_model(model_name)` - AI-powered dbt model analysis
- `check_metadata_coverage()` - Project-wide metadata assessment
- `get_project_lineage()` - Data dependency mapping
- `assess_data_product_quality(model_name)` - Comprehensive quality scoring

### 🆕 Enhanced Composite Tools
- `analyze_dbt_model_with_git_context(model_name)` - dbt analysis + Git history
- `get_composite_server_status()` - Server capabilities and integrations

### 🌐 Deployment Flexibility
- **Local CLI** - `data-product-hub -f ./project`
- **Hostable MCP Server** - `data-product-hub serve --mcp-host 0.0.0.0`
- **Container Deployment** - Docker + Kubernetes + Helm charts
- **FastMCP Cloud** - One-click cloud deployment

### 🔗 Agent Integration
- Compatible with Claude Code, Cursor, and any MCP-enabled AI agent
- JSON-first output for automation and CI/CD pipelines
- Structured responses for programmatic consumption

## Quick Start

### Installation

```bash
pip install data-product-hub
```

### Basic Usage

```bash
# CLI analysis (backwards compatible)
data-product-hub -f ./my-dbt-project --metadata-only

# Start hostable MCP server
data-product-hub serve -f ./my-dbt-project --mcp-host 0.0.0.0

# Start local MCP server for stdio connections
data-product-hub --mcp-server -f ./my-dbt-project
```

### Agent Integration

```python
from fastmcp import Client

# Connect to your MCP server
client = Client("mcp+sse://localhost:8080")

async with client:
    # Check metadata coverage
    coverage = await client.call_tool("check_metadata_coverage")

    # Analyze specific model with Git context
    analysis = await client.call_tool(
        "analyze_dbt_model_with_git_context",
        {"model_name": "customer_summary"}
    )
```

## Deployment Options

### 1. FastMCP Cloud (Recommended for Getting Started)

Deploy to FastMCP Cloud with one click:

1. Visit [fastmcp.cloud](https://fastmcp.cloud)
2. Connect your GitHub repository
3. Entry point: `server.py:app`
4. Set environment variables:
   ```bash
   DBT_PROJECT_PATH=./sample_dbt_project
   DATABASE=snowflake
   OPENAI_API_KEY=your-key
   ```

[📖 Full FastMCP Cloud Guide](./FASTMCP_CLOUD_DEPLOYMENT.md)

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

### Environment Variables

```bash
# Database configuration
DATABASE=snowflake  # snowflake, postgres, redshift, bigquery

# Git integration
ENABLE_GIT_INTEGRATION=true

# OpenAI API (optional - for AI features)
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

# New command (identical functionality)
data-product-hub -f ./project --metadata-only
```

All CLI functionality is **100% backwards compatible**.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT License](LICENSE)

---

**Data Product Hub** - Transforming dbt projects into agent-accessible data quality platforms. 🚀