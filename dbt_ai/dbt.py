import glob
import os

import yaml

from dbt_ai.ai import generate_response
from dbt_ai.helper import find_yaml_files, format_suggestions


class DbtModelProcessor:
    """Class containing functions to process and analyse a DBT project"""

    def __init__(self, dbt_project_path):
        self.dbt_project_path = dbt_project_path
        self.yaml_files = find_yaml_files(dbt_project_path)
        self.api_key_available = bool(os.getenv("OPENAI_API_KEY"))
        if not self.api_key_available:
            print("Warning: OPENAI_API_KEY is not set. Suggestion features will be unavailable.")

    def suggest_dbt_model_improvements(self, file_path, model_name) -> list:
        with open(file_path, "r") as f:
            content = f.read()
        prompt = f"Given the following dbt model {model_name}:\n\n{content}\n\nPlease provide suggestions on how to improve this model in terms of syntax, code structure and dbt best practices such as using ref instead of hardcoding table names:"
        response = generate_response(prompt)
        return response

    def model_has_metadata(self, model_name) -> bool:
        for yaml_file in self.yaml_files:
            with open(yaml_file, "r") as f:
                try:
                    yaml_content = yaml.safe_load(f)

                    if yaml_content:
                        for item in yaml_content.get("models", []):
                            if isinstance(item, dict) and item.get("name") == model_name:
                                return True
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML file {yaml_file}: {e}")

        return False

    def process_model(self, model_file) -> dict:
        model_name = os.path.basename(model_file).replace(".sql", "")

        has_metadata = self.model_has_metadata(model_name)
        if self.api_key_available:
            raw_suggestions = self.suggest_dbt_model_improvements(model_file, model_name)
            formatted_suggestions = format_suggestions(raw_suggestions)
        else:
            formatted_suggestions = []

        return {
            "model_name": model_name,
            "metadata_exists": has_metadata,
            "suggestions": [formatted_suggestions],
        }

    def process_dbt_models(self) -> list:
        model_files = glob.glob(os.path.join(self.dbt_project_path, "models/**/*.sql"), recursive=True)
        models = [self.process_model(model_file) for model_file in model_files]

        return models
