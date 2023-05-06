# DBT AI

This application helps you improve your dbt models by providing suggestions using the OpenAI GPT-3.5 model.

## Installation

To install the application, run the following command:

NOTE: PIP MODULE IS NOT YET AVAILABLE

```bash
pip install dbt-ai
```

## Usage
 1. Set up your OpenAI API key as an environment variable:
```bash
    export OPENAI_API_KEY="your_openai_api_key"
```

 2. Run the application within the root directory of your dbt project:
```bash
    dbt-ai
```

The application will process all dbt model files in your project and generate an HTML report with suggestions for each model. The report will be saved as suggestions_report.html in the current directory.

## Generated Report
This shows an example of a report generated from a DBT project containing 3 models
![](images/example_report.png?raw=true)



## Contributing
We welcome contributions to the project! Please feel free to open issues or submit pull requests with your improvements and suggestions.

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started and develop in this repo.
