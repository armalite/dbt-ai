# DBT AI

An application that allows AI powered [DBT](https://www.getdbt.com/) development and recommendations for your [DBT](https://www.getdbt.com/) models.

## 🚀 What's New in v0.4.0

- **Agent-First Design**: JSON output is now the default format for seamless integration with AI coding agents
- **Structured Output**: Machine-parseable JSON responses that work with any agent or automation tool
- **Fast Metadata Checks**: New `--metadata-only` flag for quick metadata coverage analysis without AI processing
- **Modern OpenAI API**: Upgraded to the latest OpenAI API (v1.x) with support for GPT-4o and GPT-4o-mini
- **Enhanced Prompts**: Completely rewritten prompts with better structure and clearer guidelines
- **Smart Model Selection**: Automatically uses GPT-4o for advanced suggestions and GPT-4o-mini for basic ones
- **Better Error Handling**: Improved error handling and fallback mechanisms
- **Configuration Options**: Environment variables for customizing AI models and settings
- **Maintained Compatibility**: All existing CLI commands work exactly the same

## Features
 - **Agent-Ready Output**: Structured JSON output by default for seamless automation and agent integration
 - **AI-Powered Analysis**: Scans all dbt models and generates recommendations for each model
   - Basic recommendations for quick improvements (default: GPT-4o-mini)
   - Advanced recommendations for complex optimizations (GPT-4o)
 - **Fast Metadata Checking**: Instantly verify which models are missing documentation
 - **Model Creation**: Generate new dbt models from natural language prompts
 - **Lineage Analysis**: Understand model dependencies and data flow
 - **Multi-Database Support**: Works with Snowflake, PostgreSQL, Redshift, and BigQuery
 - **Human-Readable Reports**: Optional HTML reports for visual analysis

## Installation
First time installation:
```bash
pip install dbt-ai
```

To upgrade to the latest version:
```bash
pip install dbt-ai --upgrade
```

To install a specific version:
```bash
pip install dbt-ai==<version>
```
Replace `<version>` with your desired version e.g. `0.2.0`. You can view available versions in the [Releases](https://github.com/armalite/dbt-ai/releases) section of this repo or on our [Pypi page](https://pypi.org/project/dbt-ai/).
WARNING: This is an early phase application that may still contain bugs

## Prerequisites
 - In order to benefit from AI features, you need your own OpenAI API Key with the initial version of this application
    - Once you sign up to [OpenAI](https://openai.com/product) you can create an API key. 
    - Trial version gives you a certain amount of credits allowing you to make many API calls
    - Usage beyond the trial credits require billing details. [API usage pricing](https://openai.com/pricing) provides more info
 - Ideally you already have dbt project to test this out on
 - Python 3.10 or greater is required


## Usage
Setting up your API key is needed for all the AI features
 - Set up your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

## Configuration

dbt-ai now supports environment variables for customizing AI model selection and behavior:

### AI Model Configuration
```bash
# Basic suggestions model (default: gpt-4o-mini)
export DBT_AI_BASIC_MODEL="gpt-4o-mini"

# Advanced suggestions model (default: gpt-4o)  
export DBT_AI_ADVANCED_MODEL="gpt-4o"

# Fallback model for compatibility (default: gpt-3.5-turbo)
export DBT_AI_FALLBACK_MODEL="gpt-3.5-turbo"
```

### API Settings
```bash
# Maximum tokens per API call (default: 4000)
export DBT_AI_MAX_TOKENS="4000"

# Temperature for AI responses (default: 0.1)
export DBT_AI_TEMPERATURE="0.1"
```

### Recommended Model Selection

- **For cost-conscious users**: Use `gpt-3.5-turbo` for both basic and advanced
- **For best quality**: Use `gpt-4o-mini` for basic and `gpt-4o` for advanced (default)
- **For organizations**: Consider `gpt-4` models for production use

### Quick Start

#### Basic Analysis (JSON Output)
Get structured analysis perfect for agents and automation:
```bash
dbt-ai -f path/to/dbt/project
```

Example with current directory:
```bash
dbt-ai -f .
```

This outputs machine-parseable JSON with model analysis, suggestions, and metadata coverage.

#### Fast Metadata Check
Quick metadata coverage check without AI processing:
```bash
dbt-ai -f . --metadata-only
```

#### Human-Readable Reports
Generate visual HTML reports for manual review:
```bash
dbt-ai -f . --output text
```

### Advanced Usage

#### Output Formats
```bash
# JSON output (default) - perfect for agents
dbt-ai -f . --output json

# Text output - generates HTML report for humans
dbt-ai -f . --output text
```

#### Database Configuration
Specify your database type for optimized suggestions:
```bash
dbt-ai -f . -d snowflake    # Default
dbt-ai -f . -d postgres     # PostgreSQL
dbt-ai -f . -d redshift     # Amazon Redshift
dbt-ai -f . -d bigquery     # Google BigQuery
```

#### Advanced AI Recommendations
Request more sophisticated optimization suggestions:
```bash
dbt-ai -f . -a              # Short form
dbt-ai -f . --advanced-rec  # Long form
```

#### Combined Examples
```bash
# Advanced PostgreSQL analysis with JSON output
dbt-ai -f . -d postgres -a

# Quick metadata check only
dbt-ai -f . --metadata-only

# Full analysis with HTML report
dbt-ai -f . --output text -a
```

### Create DBT Models from prompt (AI)
This feature lets you specify a prompt, which creates AI generated DBT model files in the `models/` directory of the specified dbt project. The AI model has access to your `sources.yml` file, if you wish to refer to any sources in your prompt. Being specific will provide better results.
 1. Run the application with the --create-models flag to specify the prompt you wish to use to create your DBT models
 ```bash
dbt-ai -f path/to/dbt/project --create-models 'your prompt goes here'
 ```

Here is an example:
```bash
dbt-ai -f . --create-models 'Write me a model that uses all the sources available in sources.yml and joins them together using the id column'
```

## Output Formats

### JSON Output (Default)
Perfect for AI agents, automation tools, and programmatic analysis:

```json
{
  "operation": "full_analysis",
  "project_path": "./sample-dbt-project",
  "total_models": 3,
  "models": [
    {
      "name": "customer_summary",
      "has_metadata": true,
      "suggestions": "Consider adding data freshness tests...",
      "dependencies": ["raw_customers", "raw_orders"]
    }
  ],
  "metadata_coverage_percent": 66.7,
  "lineage_description": "customer_summary depends on raw_customers, raw_orders..."
}
```

### HTML Report
Visual reports for human analysis when using `--output text`:

### 🌐 [**View Live Demo Report**](https://armalite.github.io/dbt-ai/sample-report.html)

The HTML report includes:
- 🤖 **AI-powered improvement suggestions** for each dbt model
- 📋 **Metadata coverage analysis** showing which models need documentation
- 🎨 **Professional styling** with responsive design
- 🔗 **Model lineage information** and dependencies

*The demo above shows the actual output generated from the sample dbt project included in this repository.*

## Agent Integration

dbt-ai is designed to work seamlessly with AI coding agents like Claude Code, Cursor, and GitHub Copilot. The JSON output format allows agents to:

- **Analyze dbt projects** programmatically without human intervention
- **Identify optimization opportunities** across multiple models
- **Check metadata coverage** for documentation completeness
- **Understand model lineage** for impact analysis
- **Generate improvement suggestions** based on current best practices

### Example Agent Workflow
```bash
# Agent runs analysis
dbt-ai -f ./dbt-project --output json > analysis.json

# Agent parses results to identify issues
cat analysis.json | jq '.models[] | select(.has_metadata == false) | .name'

# Agent can then take corrective actions based on structured data
```

## Changelog

### v0.4.0 (Latest)
- **Agent-first design**: JSON output is now the default format
- **Fast metadata checks**: New `--metadata-only` flag for quick coverage analysis
- **Structured output**: Machine-parseable JSON for seamless automation
- **Agent integration**: Designed for seamless use with AI coding agents
- **Bug fixes**: Resolved directory handling issues in YAML file discovery
- **Enhanced error handling**: Better safety checks for file processing

### v0.3.0
- **Major upgrade**: Modernized OpenAI API integration (v1.x)
- **Enhanced AI prompts**: Completely rewritten prompts with better structure and context
- **Smart model selection**: GPT-4o for advanced suggestions, GPT-4o-mini for basic ones
- **Structured responses**: JSON-based output parsing with Pydantic validation
- **Configuration options**: Environment variables for model and API customization
- **Improved error handling**: Better fallbacks and error messages
- **Backward compatibility**: All existing commands work unchanged
- **Fixed tests**: All test suite now passes correctly

### v0.2.x (Previous)
- Basic OpenAI integration with GPT-3.5-turbo
- Simple prompt-based suggestions
- Basic and advanced recommendation modes
- HTML report generation
- Metadata checking functionality

## Contributing
We welcome contributions to the project! Please feel free to open issues or submit pull requests with your improvements and suggestions.

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started and develop in this repo.
