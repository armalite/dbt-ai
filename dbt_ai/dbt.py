import yaml
import openai
import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob
from dbt_ai.helper import find_yaml_files, generate_response


class DbtModelProcessor:
    """Class containing functions to process and analyse a DBT project"""


    def __init__(self, dbt_project_path):
        self.dbt_project_path = dbt_project_path
        self.yaml_files = find_yaml_files(dbt_project_path)


    def suggest_dbt_model_improvements(self, file_path, model_name):
        with open(file_path, "r") as f:
            content = f.read()
        prompt = f"Given the following dbt model {model_name}:\n\n{content}\n\nPlease provide suggestions on how to improve this model in terms of syntax, code structure and dbt best practices such as using ref instead of hardcoding table names:"
        response = generate_response(prompt)
        return response


    def model_has_metadata(self, model_name):
        for yaml_file in self.yaml_files:
            with open(yaml_file, "r") as f:
                try:
                    yaml_content = yaml.safe_load(f)

                    if yaml_content:
                        for item in yaml_content.get("models", []):
                            if item.get("name") == model_name:
                                return True
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML file {yaml_file}: {e}")

        return False


    def process_model(self, model_file):
        model_name = os.path.basename(model_file).replace(".sql", "")

        has_metadata = self.model_has_metadata(model_name)
        suggestions = self.suggest_dbt_model_improvements(model_file, model_name)

        return {
            "name": model_name,
            "has_metadata": has_metadata,
            "suggestions": suggestions,
        }


    def process_dbt_models(self):
        model_files = glob.glob(os.path.join(self.dbt_project_path, "models/**/*.sql"), recursive=True)
        models = [self.process_model(model_file) for model_file in model_files]

        return models

