import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob

def generate_response(prompt):
    response = openai.Completion.create(
        engine="GPT-3.5",  
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

def suggest_dbt_model_improvements(file_path, model_name):
    with open(file_path, "r") as f:
        content = f.read()

    prompt = f"Given the following dbt model {model_name}:\n\n{content}\n\nPlease provide suggestions on how to improve this model in terms of syntax, code structure and dbt best practices such as using ref instead of hardcoding table names:"
    response = generate_response(prompt)
    return response

def generate_html_report(models, output_path):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report_template.html")

    rendered_report = template.render(models=models)
    with open(output_path, "w") as f:
        f.write(rendered_report)

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
