# DBT AI

This application provides AI generated recommendations on how to improve your dbt models.

## Features
 - Scans all dbt models and generates a report containing recommendations for each model
 - Lists dbt models that are missing associated metadata e.g. in a `schema.yml` file or equivalent

## Installation
You can install the application here
```bash
pip install dbt-ai==0.0.10a0
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
 1. Set up your OpenAI API key as an environment variable:
```bash
    export OPENAI_API_KEY="your_openai_api_key"
```

 2. Run the application passing in the path to your dbt project:
```bash
    dbt-ai path/to/dbt/project
```

Please allow some time for the AI model to process your dbt models. The application will process all dbt model files in your project and generate an HTML report with suggestions for each model. The report will be saved as dbt_model_suggestions.html within the dbt project directory. Upon generation of the report, it will be opened in a new browser tab.

## Generated Report
This shows an example of a report generated from a DBT project containing 3 models
![](images/generated_report_1.png?raw=true)


## Contributing
We welcome contributions to the project! Please feel free to open issues or submit pull requests with your improvements and suggestions.

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started and develop in this repo.
