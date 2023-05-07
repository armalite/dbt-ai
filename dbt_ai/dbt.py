import glob
import os
import re
import yaml

from dbt_ai.ai import generate_response
from dbt_ai.helper import find_yaml_files


class DbtModelProcessor:
    """Class containing functions to process and analyse a DBT project"""

    def __init__(self, dbt_project_path) -> None:
        self.dbt_project_path = dbt_project_path
        self.yaml_files = find_yaml_files(dbt_project_path)
        self.api_key_available = bool(os.getenv("OPENAI_API_KEY"))
        if not self.api_key_available:
            print("Warning: OPENAI_API_KEY is not set. Suggestion features will be unavailable.")

    def get_model_refs(model_file_path: str) -> list:
        with open(model_file_path, "r") as f:
            content = f.read()

        refs = re.findall(r"ref\(['\"]([\w\.]+)['\"]\)", content)

        return refs
    
    def suggest_dbt_model_improvements(self, file_path: str, model_name: str) -> list:
        with open(file_path, "r") as f:
            content = f.read()
        prompt = f"Given the following dbt model {model_name}:\n\n{content}\n\nPlease provide suggestions on how to improve this model in terms of syntax, code structure and dbt best practices such as using ref instead of hardcoding table names:"
        response = generate_response(prompt)
        return response

    def model_has_metadata(self, model_name: str) -> bool:
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

    def process_model(self, model_file: str) -> dict:
        model_name = os.path.basename(model_file).replace(".sql", "")

        has_metadata = self.model_has_metadata(model_name)
        if self.api_key_available:
            raw_suggestion = self.suggest_dbt_model_improvements(model_file, model_name)
        else:
            raw_suggestion = ""

        refs = self.get_model_refs(model_file)
        
        return {
            "model_name": model_name,
            "metadata_exists": has_metadata,
            "suggestions": raw_suggestion,
            "refs": refs,
        }

    def process_dbt_models(self):  # flake8: noqa
        model_files = glob.glob(os.path.join(self.dbt_project_path, "models/**/*.sql"), recursive=True)
        models = [self.process_model(model_file) for model_file in model_files]
        missing_metadata = []

        # Check for models without metadata
        for model in models:
            if not model["metadata_exists"]:
                missing_metadata.append(model["model_name"])

        return models, missing_metadata
