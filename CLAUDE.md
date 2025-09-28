# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
make install    # Create venv, install dependencies, setup git hooks
source .venv/bin/activate  # Activate virtual environment
```

### Code Quality and Testing
```bash
make check      # Run linting and type checking
make lint       # Format code with black and run ruff linter
make pyright    # Run pyright type checker
make test       # Run pytest test suite
```

### Building and Publishing
```bash
make dist       # Build Python distribution packages
make publish    # Publish to PyPI (requires credentials)
```

### Individual Test Commands
```bash
pytest                    # Run all tests
pytest tests/test_*.py    # Run specific test file
pytest -v                 # Verbose test output
```

## Architecture Overview

### Core Components
- **CLI Entry Point**: `dbt_ai/main.py` - Command-line interface with argparse
- **Model Processor**: `dbt_ai/dbt.py` - `DbtModelProcessor` class handles dbt project analysis
- **AI Integration**: `dbt_ai/ai.py` - OpenAI API integration for generating recommendations and models
- **Report Generation**: `dbt_ai/report.py` - HTML report generation with Jinja2 templates
- **Configuration**: `dbt_ai/config.py` - Environment variable configuration management
- **Utilities**: `dbt_ai/helper.py` - YAML processing and utility functions

### Key Classes
- `DbtModelProcessor` - Main analysis class that:
  - Parses dbt SQL model files and metadata YAML files
  - Validates model metadata coverage
  - Generates lineage graphs using NetworkX
  - Supports multiple database types (Snowflake, PostgreSQL, Redshift, BigQuery)
  - Provides both basic and advanced AI recommendations

### AI Model Configuration
The application uses environment variables for AI model selection:
- `DBT_AI_BASIC_MODEL` - Model for basic recommendations (default: gpt-4o-mini)
- `DBT_AI_ADVANCED_MODEL` - Model for advanced recommendations (default: gpt-4o)
- `DBT_AI_FALLBACK_MODEL` - Fallback model (default: gpt-3.5-turbo)
- `DBT_AI_MAX_TOKENS` - Maximum tokens per API call (default: 4000)
- `DBT_AI_TEMPERATURE` - AI response temperature (default: 0.1)

## Code Style Guidelines

### Python Standards
- **Line length**: 120 characters (configured in pyproject.toml)
- **Formatter**: Black with 120 char line length
- **Linter**: Ruff with comprehensive rules (pyflakes, pycodestyle, type annotations, etc.)
- **Type hints**: Required for all functions except self/cls and dunder methods
- **Import order**: Standard library → third party → local imports

### File Processing Patterns
- Use `glob.glob(pattern, recursive=True)` for finding SQL files
- Extract model references with regex: `{{\s*ref\([\'"](.+?)[\'"]\)\s*}}`
- Use `os.path.join()` for cross-platform file paths
- Validate file existence before processing

### Testing Requirements
- All tests in `tests/` directory using pytest
- Mock external dependencies (OpenAI API, file system)
- Test both success and error scenarios
- Use descriptive test function names

## Database Support
The application supports multiple dbt database adapters with specific configurations:
- **Snowflake** (default)
- **PostgreSQL**
- **Redshift**
- **BigQuery**

Database type affects AI recommendations and SQL syntax validation.

## Important Notes
- Requires OpenAI API key for AI features (`OPENAI_API_KEY` environment variable)
- Python >= 3.10 required (specified in pyproject.toml)
- Uses Pydantic for structured AI response validation
- HTML reports generated using Jinja2 templates
- Pre-commit hooks enforce code quality on push