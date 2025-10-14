# GitHub Copilot Instructions for Data Product Hub

## Project Overview
This repository contains **Data Product Hub**, a Python CLI application that provides AI-powered assistance for dbt (data build tool) development. The tool offers:

- **AI-powered recommendations** for dbt model improvements (basic and advanced)
- **Model analysis** including metadata validation and lineage visualization
- **Code generation** for creating new dbt models from prompts
- **HTML report generation** for presenting suggestions and analysis

## Key Architecture Components

### Core Modules
- `data_product_hub/main.py` - CLI entry point and argument parsing
- `data_product_hub/dbt.py` - `DbtModelProcessor` class with core dbt project analysis logic
- `data_product_hub/ai.py` - OpenAI integration for generating recommendations and models
- `data_product_hub/report.py` - HTML report generation using Jinja2 templates
- `data_product_hub/helper.py` - Utility functions for YAML processing and formatting

### Key Classes
- `DbtModelProcessor` - Main processor class for analyzing dbt projects
  - Handles model file parsing, metadata validation, lineage generation
  - Supports multiple database types (Snowflake, PostgreSQL, Redshift, BigQuery)
  - Provides both basic and advanced AI recommendations

## Development Environment

### Setup Requirements
- Python >= 3.10 (specified in pyproject.toml)
- Node.js (for pyright type checking)
- make (for development tasks)

### Development Workflow
```bash
make install    # Set up venv, install dependencies, git hooks
make check      # Run linting and type checking
make test       # Run pytest test suite
make lint       # Format code and run linters
```

### Build System
- Uses setuptools with pyproject.toml configuration
- Pre-commit hooks for code quality (black, ruff, pyright)
- Automated formatting with black (120 char line length)
- Type checking with pyright

## Code Style and Conventions

### Python Style
- **Line length**: 120 characters (configured in pyproject.toml)
- **Formatter**: Black with default settings
- **Linter**: Ruff with comprehensive rule set including:
  - pyflakes (F), pycodestyle (E,W), type annotations (ANN)
  - pep8-naming (N), bugbear (B), isort (I)
- **Type hints**: Required for all functions (except self/cls and dunder methods)

### File Patterns
- All Python files include `# flake8: noqa` header in main modules
- Import organization: standard library → third party → local imports  
- Class docstrings use simple format: `"""Brief description"""`
- CLI argument parsing uses argparse with comprehensive help text

### Error Handling
- Graceful degradation when OpenAI API key unavailable
- Warning messages for missing dependencies/configuration
- Comprehensive file path validation and existence checks

## Testing Practices

### Test Structure
- Tests located in `tests/` directory
- Uses pytest framework with fixtures in `conftest.py`
- Test files follow pattern `test_*.py`
- Fixtures defined in separate `fixtures.py` file

### Testing Guidelines
- Test both success and error scenarios
- Mock external dependencies (OpenAI API, file system operations)
- Validate edge cases (missing files, invalid YAML, etc.)
- Use descriptive test function names

## AI/ML Specific Considerations

### OpenAI Integration
- Uses OpenAI ChatCompletion API with gpt-3.5-turbo model
- Two distinct prompt strategies:
  - **Basic recommendations**: For new dbt/SQL engineers
  - **Advanced recommendations**: For experienced data engineers
- Temperature settings: 0.1 for basic, 0 for advanced (consistent outputs)
- Max tokens: 1024 for generated responses

### Prompt Engineering Patterns
- Detailed system prompts with specific rules and constraints
- Context-aware suggestions based on model content analysis
- Formatting specifications for consistent output structure
- Example-driven prompts for advanced recommendations

### AI Safety Considerations
- API key validation and graceful degradation
- Rate limiting considerations for batch model processing
- Error handling for API timeouts and failures
- No sensitive data in prompts (model content only)

## Database Support
The application supports multiple dbt database adapters:
- **Snowflake** (default)
- **PostgreSQL** 
- **Redshift**
- **BigQuery**

Database-specific considerations should be included in AI recommendations.

## File Processing Patterns

### dbt Project Structure
- Processes `.sql` files recursively in dbt project directories
- Validates associated `.yml`/`.yaml` metadata files
- Extracts model references using regex: `{{\s*ref\([\'"](.+?)[\'"]\)\s*}}`
- Generates lineage graphs using NetworkX

### Template System
- Uses Jinja2 for HTML report generation
- Templates located in `data_product_hub/templates/`
- Markdown filter support for rich content formatting
- Automatic browser opening for generated reports

## Common Code Patterns

### CLI Argument Handling
```python
parser = argparse.ArgumentParser(description="Brief description")
parser.add_argument("-f", "--dbt-project-path", help="Path description")
parser.add_argument("-a", "--advanced-rec", action="store_true", help="Flag description")
```

### File Path Operations
```python
# Use os.path.join for cross-platform compatibility
file_path = os.path.join(dbt_project_path, "**/*.sql")
# Use glob with recursive=True for pattern matching
sql_files = glob.glob(file_path, recursive=True)
```

### AI Response Processing
```python
# Standard OpenAI call pattern
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1024,
    temperature=0.1
)
return response.choices[0].message["content"].strip()
```

## Contributing Guidelines
- Follow existing code patterns and style
- Add tests for new functionality
- Update documentation for API changes
- Use meaningful commit messages
- Ensure all checks pass before submitting PRs

## Performance Considerations
- Batch process multiple models efficiently
- Use appropriate timeouts for AI API calls
- Consider file size limits for model content
- Implement progress indicators for long-running operations