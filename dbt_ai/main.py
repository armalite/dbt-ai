import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob


def main():
    parser = argparse.ArgumentParser(description="Generate improvement suggestions for dbt models")
    parser.add_argument("dbt_project_path", help="Path to the dbt project directory")
    args = parser.parse_args()

    model_files = glob.glob(os.path.join(args.dbt_project_path, "models/**/*.sql"), recursive=True)
    models = []

    for model_file in model_files:
        model_name = os.path.basename(model_file).replace(".sql", "")
        suggestions = suggest_dbt_model_improvements(model_file, model_name)
        models.append({"name": model_name, "suggestions": suggestions})

    output_path = os.path.join(args.dbt_project_path, "dbt_model_suggestions.html")
    generate_html_report(models, output_path)

    print(f"Generated improvement suggestions report at: {output_path}")

if __name__ == "__main__":
    main()
