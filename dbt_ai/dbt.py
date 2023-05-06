
import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob


def suggest_dbt_model_improvements(file_path, model_name):
    with open(file_path, "r") as f:
        content = f.read()

    prompt = f"Given the following dbt model {model_name}:\n\n{content}\n\nPlease provide suggestions on how to improve this model in terms of syntax, code structure and dbt best practices such as using ref instead of hardcoding table names:"
    response = generate_response(prompt)
    return response


def model_has_metadata(model_name, yaml_files):
    for yaml_file in yaml_files:
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
    

def process_model(model_file, yaml_files):
    model_name = os.path.basename(model_file).replace(".sql", "")

    has_metadata = model_has_metadata(model_name, yaml_files)
    suggestions = suggest_dbt_model_improvements(model_file, model_name)

    return {
        "name": model_name,
        "has_metadata": has_metadata,
        "suggestions": suggestions,
    }


def process_dbt_models(dbt_project_path):
    model_files = glob.glob(os.path.join(dbt_project_path, "models/**/*.sql"), recursive=True)
    yaml_files = find_yaml_files(dbt_project_path)

    models = [process_model(model_file, yaml_files) for model_file in model_files]

    return models



