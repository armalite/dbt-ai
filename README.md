# DBT AI

An application that allows AI powered [DBT](https://www.getdbt.com/) development and recommendations for your [DBT](https://www.getdbt.com/) models.

## 🚀 What's New in v0.3.0

- **Modern OpenAI API**: Upgraded to the latest OpenAI API (v1.x) with support for GPT-4o and GPT-4o-mini
- **Enhanced Prompts**: Completely rewritten prompts with better structure and clearer guidelines
- **Structured Responses**: AI responses now use structured JSON format for more reliable parsing
- **Smart Model Selection**: Automatically uses GPT-4o for advanced suggestions and GPT-4o-mini for basic ones
- **Better Error Handling**: Improved error handling and fallback mechanisms
- **Configuration Options**: Environment variables for customizing AI models and settings
- **Maintained Compatibility**: All existing CLI commands work exactly the same

## Features
 - Scans all dbt models and generates a report containing recommendations for each model
   - By default only basic recommendations are provided
   - Ability to request for more advanced recommendations
 - Create DBT models by using AI prompts
 - Lists dbt models that are missing associated metadata e.g. in a `schema.yml` file or equivalent
 - DBT model lineage description is listed in the terminal (more features coming soon)

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

### Generate Recommendations (AI)
This feature will generate the recommendation report and also inform you about any models missing metadata

#### Basic Usage
The default setting is to provide basic recommendations
  1. Run the application passing in the path to your dbt project:
```bash
dbt-ai -f path/to/dbt/project
```

For example, if you are already inside your dbt project directory, you can run:
```bash
dbt-ai -f .
```

#### Available Settings

   - *Database:* specify which database system your dbt models are written for. Default: `snowflake`
      - `-d` / `--database`
      - Available values: `snowflake`, `postgres`, `redshift`, `bigquery`
      - Usage example: 
      ```bash
      dbt ai -f . -d snowflake
      ```
   - *Advanced Recommendations:* Request for advanced recommendations. Default: No setting defaults to basic recommendations
      - `-a` / `--advanced-rec`
      - Available values: Only flag required
      - Usage example: 
      ```bash
      dbt ai -f . -a 
      ```
      Or
      ```bash
      dbt ai -f . --advanced-req
      ```

Please allow some time for the AI model to process your dbt models. The application will process all dbt model files in your project and generate an HTML report with suggestions for each model. The report will be saved as dbt_model_suggestions.html within the dbt project directory. Upon generation of the report, it will be opened in a new browser tab.

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

## Generated Report
This shows an example of a report generated from a DBT project containing 3 models
![](images/generated_report_1.png?raw=true)

## Changelog

### v0.3.0 (Latest)
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
