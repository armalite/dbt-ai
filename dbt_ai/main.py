import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob
from helper import find_yaml_files, generate_response
from dbt import DbtModelProcessor
from report import generate_html_report

def main():
    parser = argparse.ArgumentParser(description="Generate improvement suggestions and check metadata coverage for dbt models")
    parser.add_argument("dbt_project_path", help="Path to the dbt project directory")
    args = parser.parse_args()

    processor = DbtModelProcessor(args.dbt_project_path)
    models = processor.process_dbt_models()

    output_path = os.path.join(args.dbt_project_path, "dbt_model_suggestions.html")
    generate_html_report(models, output_path)

    print(f"Generated improvement suggestions report at: {output_path}")

    models_without_metadata = [model["name"] for model in models if not model["metadata_exists"]]

    if models_without_metadata:
        print("\nThe following models are missing metadata:")
        for model_name in models_without_metadata:
            print(f"  - {model_name}")
    else:
        print("\nAll models have associated metadata.")

if __name__ == "__main__":
    main()



