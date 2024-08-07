import glob
import os
import re

import networkx as nx
import yaml

from dbt_ai.ai import (
    generate_models,
    generate_prompt,
    generate_response,
    generate_response_advanced,
)
from dbt_ai.helper import find_yaml_files


class DbtModelProcessor:
    """Class containing functions to process and analyse a DBT project"""

    def __init__(self, dbt_project_path: str, database: str = "snowflake") -> None:
        self.dbt_project_path = dbt_project_path
        self.yaml_files = find_yaml_files(dbt_project_path)
        self.api_key_available = bool(os.getenv("OPENAI_API_KEY"))
        self.sources_yml_content = self.read_sources_yml(dbt_project_path)
        self.database = database
        if not self.api_key_available:
            print("Warning: OPENAI_API_KEY is not set. Suggestion features will be unavailable.")

    def read_sources_yml(self, dbt_project_path: str):
        sources_yml_path = os.path.join(dbt_project_path, "models", "sources.yml")
        try:
            with open(sources_yml_path, "r") as f:
                sources_yml_content = f.read()
        except FileNotFoundError:
            print("sources.yml not found. Proceeding with an empty sources file.")
            sources_yml_content = None
        return sources_yml_content

    def get_model_refs(self, model_file_path: str) -> list:
        with open(model_file_path, "r") as f:
            content = f.read()

        refs = re.findall(r"ref\(['\"]([\w\.]+)['\"]\)", content)

        return refs

    def suggest_dbt_model_improvements(self, file_path: str, model_name: str) -> dict:
        with open(file_path, "r") as f:
            content = f.read()
        prompt = generate_prompt(content, model_name, level="basic")
        response = generate_response(prompt)
        return response

    def suggest_dbt_model_improvements_advanced(self, file_path: str, model_name: str) -> dict:
        with open(file_path, "r") as f:
            content = f.read()
        prompt = generate_prompt(content, model_name, level="advanced")
        response = generate_response_advanced(prompt)
        return response

    def process_model(self, model_file: str, advanced: bool = False):
        model_name = os.path.basename(model_file).replace(".sql", "")

        has_metadata = self.model_has_metadata(model_name)
        if self.api_key_available:
            if advanced:
                raw_suggestion = self.suggest_dbt_model_improvements_advanced(model_file, model_name)
            else:
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

    def process_dbt_models(self, advanced: bool = False):
        model_files = glob.glob(os.path.join(self.dbt_project_path, "models/**/*.sql"), recursive=True)
        models = [self.process_model(model_file, advanced) for model_file in model_files]
        missing_metadata = []

        # Check for models without metadata
        for model in models:
            if not model["metadata_exists"]:
                missing_metadata.append(model["model_name"])

        return models, missing_metadata

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

    def generate_lineage_description(self, gph: nx.DiGraph) -> str:
        nodes = list(nx.topological_sort(gph))

        description = ""  # "The following DBT models are used:\n\n"
        for node in nodes:
            parents = list(gph.predecessors(node))
            if parents:
                parent_names = ", ".join(parents)
                description += f"{node} depends on {parent_names}\n"
            else:
                description += f"{node} is a root node\n"

        return description

    def generate_lineage(self, dbt_models: list[dict]):
        gph = self.generate_lineage_graph(dbt_models)
        description = self.generate_lineage_description(gph)
        return description, gph

    def create_dbt_models(self, prompt: str) -> None:
        print("Attempting to create dbt models based on prompt")
        sources_yml = self.sources_yml_content if self.sources_yml_content else ""
        response = generate_models(prompt, sources_yml)

        model_delimiter = "===\n\n"
        response_lines = response[0].split(model_delimiter)

        for _i, model_str in enumerate(response_lines):
            if not model_str.strip():
                continue

            model_lines = model_str.strip().split("\n")
            model_name = model_lines[0].split(":")[-1].strip()
            model_content = "\n".join(model_lines[1:])
            model_content = model_content.replace("===", "")

            model_path = os.path.join(self.dbt_project_path, "models", f"{model_name}.sql")
            with open(model_path, "w") as f:
                f.write(model_content.strip())
            print(f"Created model file: {model_path}")
