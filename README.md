# DBT AI

This application provides AI generated recommendations on how to improve your [DBT](https://www.getdbt.com/) models.

## Features
 - Scans all dbt models and generates a report containing recommendations for each model
 - Lists dbt models that are missing associated metadata e.g. in a `schema.yml` file or equivalent
 - Use AI to generate DBT models for you based on a prompt
 - DBT model lineage description is listed in the terminal (more features coming soon)

## Installation
You can install the application here
```bash
pip install dbt-ai==0.1.1a0
```

WARNING: This is an early phase application that may still contain bugs

## Prerequisites
 - In order to benefit from AI recommendations, you need your own OpenAI API Key with the initial version of this application
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

### Generate Recommendations (AI)
This feature will generate the recommendation report and also inform you about any models missing metadata
  1. Run the application passing in the path to your dbt project:
```bash
    dbt-ai -f path/to/dbt/project
```

For example, if you are already inside your dbt project directory, you can run:
```bash
   dbt-ai -f .
```

Please allow some time for the AI model to process your dbt models. The application will process all dbt model files in your project and generate an HTML report with suggestions for each model. The report will be saved as dbt_model_suggestions.html within the dbt project directory. Upon generation of the report, it will be opened in a new browser tab.

### Create DBT Models from prompt (AI)
This feature lets you specify a prompt, which creates AI generated DBT model files for your in the `models/` directory of your specified dbt project. You can assume that the AI model has access to your `sources.yml` file, if you wish to refer to any sources in your prompt. Being specific will provide better results.
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

## Contributing
We welcome contributions to the project! Please feel free to open issues or submit pull requests with your improvements and suggestions.

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started and develop in this repo.
