# Data Product Hub

**Enhanced MCP Server for dbt Project Analysis with Official dbt Integration**

A production-ready Model Context Protocol (MCP) server that provides comprehensive dbt project quality assessment for **any GitHub repository**. Now featuring **official dbt-labs MCP integration** for native dbt commands, semantic layer access, and enhanced AI capabilities. Powered by GitHub App authentication for secure, scalable access to public and private repositories.

## 🔥 What's New in v2.0

### Major Enhancements
- **🎯 Official dbt-labs MCP Integration**: Native `dbt run`, `build`, `test`, `compile` commands
- **🧠 Semantic Layer Access**: `text_to_sql` for natural language to SQL conversion
- **🔀 Git MCP Integration**: File history, blame analysis, and change context
- **⚡ Python 3.12 Support**: Enhanced performance and future-proof architecture
- **🏗️ Dual-Server Architecture**: Combine official dbt tools with GitHub orchestration
- **🔄 Backward Compatibility**: Seamless fallback to custom implementation when needed

### Migration Guide
- **Existing Users**: No action required - backward compatible with Python 3.10+
- **Enhanced Features**: Deploy with Python 3.12 for full dbt-labs integration
- **API Unchanged**: All existing MCP tools work exactly the same with enhanced capabilities

## 🚀 What is Data Product Hub?

Data Product Hub transforms **any dbt project on GitHub** into an **agent-accessible data quality platform** that:

- **🔥 NEW: Official dbt-labs MCP integration** - Native `dbt run`, `build`, `test`, `compile` commands
- **🔥 NEW: Semantic Layer access** - `text_to_sql` for natural language queries
- **🔥 NEW: Enhanced AI capabilities** - Leverages official dbt Discovery API
- **Analyzes ANY GitHub dbt repository** with AI-powered suggestions and best practices
- **Works with public and private repos** via secure GitHub App authentication
- **Supports subdirectory dbt projects** (detects dbt/, transform/, analytics/ folders)
- **Checks metadata coverage** across your entire data product portfolio
- **Maps data lineage** and dependency relationships
- **🔥 NEW: Git MCP Integration** - File history, blame, and change analysis
- **Enhanced GitHub integration** - Works with any public/private repository
- **Exposes MCP tools** for seamless AI agent integration
- **Deploys anywhere** - FastMCP Cloud (recommended), Docker, Kubernetes

## Features

### 🔧 Enhanced MCP Tools (Work with Any GitHub Repository)

#### Core Analysis Tools
- `analyze_dbt_model(model_name, repo_url)` - **Enhanced**: Now uses official dbt-labs MCP for compilation
- `analyze_dbt_model_with_ai(model_name, repo_url)` - AI-powered analysis with advanced dbt insights
- `check_metadata_coverage(repo_url)` - Project-wide metadata assessment with official dbt Discovery
- `get_project_lineage(repo_url)` - **Enhanced**: Data dependency mapping with dbt-core integration
- `assess_data_product_quality(model_name, repo_url)` - Comprehensive quality scoring
- `validate_github_repository(repo_url)` - Validate repo access and dbt structure
- `analyze_dbt_model_with_git_context(model_name, repo_url)` - **Enhanced**: dbt analysis + Git history, blame, and change context
- `get_composite_server_status()` - Server capabilities and GitHub/Git integration status

#### 🔥 NEW: Enhanced Integrations

**Official dbt-labs Integration** *(Python 3.12+)*:
- **Native dbt Commands**: `compile`, `run`, `build`, `test` via official dbt-core
- **Semantic Layer**: `text_to_sql` for natural language to SQL conversion
- **Advanced Discovery**: Full dbt manifest and metadata access
- **Future-Proof**: Automatically inherits new dbt-labs MCP features

**Git MCP Integration**:
- **File History**: `git_log` for tracking model changes over time
- **Blame Analysis**: `git_blame` for understanding code ownership
- **Change Context**: Enhanced analysis with Git commit information
- **Repository Integration**: Seamless GitHub repository analysis

### 🌐 Deployment Options

#### Production (Recommended): Dual-Server Architecture
- **Data Product Hub Server**: Enhanced orchestration with GitHub integration
- **dbt MCP Server**: Official dbt-labs tools and semantic layer
- **Single Repo, Two Entry Points**: `server.py` and `dbt_server.py`
- **Full Feature Set**: All official dbt-labs capabilities + your enhancements

#### Development: Single-Server Mode
- **Local CLI** - `dph -f ./project`
- **Hostable MCP Server** - `dph serve --mcp-host 0.0.0.0`
- **Container Deployment** - Docker + Kubernetes + Helm charts
- **Basic Feature Set**: Custom dbt implementation (Python 3.10+ compatible)

### 🔗 Agent Integration
- Compatible with Claude Code, Cursor, and any MCP-enabled AI agent
- JSON-first output for automation and CI/CD pipelines
- Structured responses for programmatic consumption

## Quick Start

### 🚀 Use the Hosted Service (Recommended)

**Ready to use immediately - no setup required!**

**1. Install the GitHub App (30 seconds):**
   - Visit: https://github.com/apps/data-product-hub/installations/new
   - Select repositories containing dbt projects
   - Grant read permissions

**2. Add to Claude Desktop:**
   ```json
   {
     "mcpServers": {
       "data-product-hub": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-fetch", "https://data-product-hub.fastmcp.app/mcp"]
       }
     }
   }
   ```

**3. Start analyzing (any GitHub repository):**
   ```
   "Analyze the customer_summary model with Git history in https://github.com/company/dbt-project"
   "Check metadata coverage for github.com/myorg/data-warehouse"
   "Run dbt tests and compile models in github.com/startup/analytics"
   "Show me who last changed the user_events model and why"
   ```

**That's it!** 🎉 No deployment required. GitHub App handles authentication automatically.

### 🔑 Enable AI Features (Optional)

For AI-powered suggestions and advanced analysis:

1. **Go to Repository Settings → Environments**
2. **Create environment:** `production`, `prod`, `data-analysis`, `main`, or `staging`
3. **Add Environment Secret:** `OPENAI_API_KEY` = `sk-proj-...`
4. **Use enhanced tools:**
   ```
   "Get AI-powered suggestions for the user_events model"
   "Convert to SQL: 'Show revenue by customer for last 30 days'"
   ```

### 🖥️ Local Development (Optional)

For local development and testing:

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

## Why Choose Data Product Hub?

### 🚀 Hosted Service (Zero Setup)
- **Instant access** - Works immediately with any GitHub repository
- **Always up-to-date** - Latest dbt-labs MCP integration and features
- **Fully managed** - No deployment, maintenance, or scaling concerns
- **Enhanced security** - GitHub App authentication with environment secrets
- **Free tier available** - Get started without commitment

### 🏢 Enterprise Options

For organizations with specific requirements:

#### Option 1: Hosted Service + Private GitHub App
- Use our hosted MCP server with your own GitHub App
- Full control over repository access and permissions
- [📖 Custom GitHub App Setup Guide](./GITHUB_APP_SETUP.md)

#### Option 2: Self-Hosted Deployment
- Deploy in your own infrastructure for maximum control
- Perfect for air-gapped environments or strict compliance
- [📖 Enterprise Self-Hosting Guide](./ENTERPRISE.md)

---

## Support & Community

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/data-product-hub/issues)
- **Discussions**: [GitHub Discussions](https://github.com/data-product-hub/discussions)
- **Enterprise Support**: Contact us for dedicated support

### Roadmap
- ✅ **Q3 2025**: Official dbt-labs MCP integration with Python 3.12
- 🔄 **Q4 2025**: Monte Carlo data quality integration
- 🔄 **Q1 2026**: DataHub lineage integration
- 🔄 **Q2 2026**: Snowflake performance insights

## Technical Details

### Supported Databases
- Snowflake (default)
- PostgreSQL
- Amazon Redshift
- Google BigQuery

### Python Requirements
- **Hosted Service**: No requirements - runs Python 3.12 with latest features
- **Local CLI**: Python 3.10+ (Python 3.12+ recommended for full feature set)

### Enterprise Configuration
For self-hosted deployments, see [Enterprise Guide](./ENTERPRISE.md) for detailed configuration options.

## How It Works

### Simple Integration
```
Your AI Agent (Claude, Cursor, etc.)
            ↓
    Data Product Hub MCP Server
            ↓
  📊 Analyzes any GitHub dbt repository
  🤖 Enhanced with official dbt-labs tools
  🔍 Provides comprehensive quality insights
```

### Behind the Scenes (Hosted Service)
- **GitHub App Authentication** - Secure repository access
- **Official dbt-labs Integration** - Native dbt commands and semantic layer
- **Composite MCP Architecture** - Combines multiple data tools in one endpoint
- **Intelligent Fallbacks** - Works with any dbt project structure

### Architecture Benefits
- **Single MCP Endpoint** - No complex setup for users
- **Enhanced Capabilities** - Official dbt tools + GitHub integration + AI insights
- **Future-Proof** - Automatically inherits new dbt-labs and tool updates
- **Scalable** - Handles repositories of any size

## Use Cases

### 🚀 **AI-First Data Development**
- **"Analyze this dbt model and suggest improvements"**
- **"Check if our data warehouse has good documentation"**
- **"What's the lineage for this customer table?"**
- **"Convert this question to SQL: show revenue by month"**

### 👥 **Team Collaboration**
- **Code reviews** - AI agents understand dbt context
- **Onboarding** - New team members get instant project insights
- **Documentation** - Automated coverage monitoring
- **Best practices** - Consistent standards across projects

### 🏢 **Enterprise Data Governance**
- **Quality monitoring** across all dbt repositories
- **Compliance checks** for documentation standards
- **Impact analysis** before making changes
- **Cross-project insights** and dependencies

---

## Getting Started

Ready to transform your dbt development with AI?

1. **[Install GitHub App](https://github.com/apps/data-product-hub/installations/new)** (30 seconds)
2. **[Add to Claude Desktop](https://data-product-hub.fastmcp.app/docs/setup)**
3. **Start analyzing** any dbt repository with natural language

**Questions?** Check our [documentation](https://data-product-hub.fastmcp.app/docs) or [open an issue](https://github.com/data-product-hub/issues).

---

## Contributing & Support

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/data-product-hub/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/data-product-hub/discussions)
- **🏢 Enterprise Support**: Contact us for dedicated support
- **🤝 Contributing**: [Contributing Guide](CONTRIBUTING.md)

## License

[MIT License](LICENSE) - Built with ❤️ for the data community

---

**Data Product Hub** - Transforming dbt projects into agent-accessible data quality platforms. 🚀