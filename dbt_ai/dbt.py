# flake8: noqa
import glob
import os
import re
import yaml
from typing import List
import networkx as nx

from dbt_ai.ai import generate_review, classify_model
from dbt_ai.helper import find_yaml_files


class DbtModelProcessor:
    def __init__(self, dbt_project_path: str, database: str = "snowflake") -> None:
        self.dbt_project_path = dbt_project_path
        self.yaml_files = find_yaml_files(dbt_project_path)
        self.api_key_available = bool(os.getenv("OPENAI_API_KEY"))
        self.database = database

    def read_model_file(self, model_path: str) -> str:
        with open(model_path, "r") as f:
            return f.read()

    def model_has_metadata(self, model_name: str) -> bool:
        for yaml_file in self.yaml_files:
            with open(yaml_file, "r") as f:
                try:
                    yaml_content = yaml.safe_load(f)
                    for item in yaml_content.get("models", []):
                        if isinstance(item, dict) and item.get("name") == model_name:
                            return True
                except yaml.YAMLError as e:
                    print(f"Error parsing YAML file {yaml_file}: {e}")
        return False

    def get_model_refs(self, content: str) -> List[str]:
        return re.findall(r"ref\(['\"]([\w\.]+)['\"]\)", content)

    def process_model(
        self, model_path: str, level: str = "basic", provider: str = "openai", model: str = "gpt-4"
    ) -> dict:
        model_name = os.path.basename(model_path).replace(".sql", "")
        sql = self.read_model_file(model_path)
        has_metadata = self.model_has_metadata(model_name)
        refs = self.get_model_refs(sql)

        if self.api_key_available:
            try:
                classification = classify_model(sql, model_name)
                review = generate_review(
                    model_content=sql,
                    model_name=model_name,
                    level=level,
                    provider=provider,
                    model=model,
                    classification=classification,  # ✅ New argument
                )
            except Exception as e:
                print(f"Failed to review model {model_name}: {e}")
                classification = {}
                review = {}
        else:
            classification = {}
            review = {}

        return {
            "model_name": model_name,
            "metadata_exists": has_metadata,
            "review": review,
            "refs": refs,
            "classification": classification,  # ✅ Add this too
        }

    def process_dbt_models(self, level: str = "basic") -> tuple[list[dict], list[str]]:
        model_files = glob.glob(os.path.join(self.dbt_project_path, "models/**/*.sql"), recursive=True)
        results = [self.process_model(path, level) for path in model_files]
        missing_metadata = [r["model_name"] for r in results if not r["metadata_exists"]]
        return results, missing_metadata

    def generate_lineage_graph(self, models):
        g = nx.DiGraph()
        for model in models:
            g.add_node(model["model_name"], metadata_exists=model["metadata_exists"])
            for ref in model["refs"]:
                g.add_edge(ref, model["model_name"])
        return g

    def generate_lineage_description(self, gph: nx.DiGraph) -> str:
        lines = []
        for node in nx.topological_sort(gph):
            parents = list(gph.predecessors(node))
            if parents:
                lines.append(f"{node} depends on {', '.join(parents)}")
            else:
                lines.append(f"{node} is a root node")
        return "\n".join(lines)
