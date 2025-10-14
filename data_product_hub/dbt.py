# flake8: noqa

import glob
import json
import os
import re
import subprocess
from typing import Callable, Dict, List, Optional, Union

import networkx as nx
import plotly.graph_objects as go
import yaml

from data_product_hub.ai import generate_dalle_image, generate_models, generate_response, generate_response_advanced
from data_product_hub.helper import find_yaml_files
from data_product_hub.config import Config


class DbtModelProcessor:
    """Class containing functions to process and analyse a DBT project"""

    def __init__(self, dbt_project_path: str, database: str = "snowflake") -> None:
        self.dbt_project_path = dbt_project_path
        self.yaml_files = find_yaml_files(dbt_project_path)
        self.api_key_available = Config.is_api_available()
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

    def suggest_dbt_model_improvements(self, file_path: str, model_name: str) -> str:
        with open(file_path, "r") as f:
            content = f.read()
        prompt = f"""Given the following dbt model {model_name}:\n\n{content}\n\nPlease provide suggestions on how to improve this model in terms of syntax, code structure and dbt best practices \
            such as using ref instead of hardcoding table names. The suggestion should be specific to db models written in the {self.database} database system: \
            """
        response = generate_response(prompt)
        return response

    def suggest_dbt_model_improvements_advanced(self, file_path: str, model_name: str) -> str:
        with open(file_path, "r") as f:
            content = f.read()
        prompt = f"""Given the following dbt model {model_name}:\n\n{content}\n\n \
            Please provide advanced suggestions on how to improve this model.
            The suggestion should be specific to dbt models written in the {self.database} database system 
            If there are no advanced recommendations to provide, then do not provide anything. If you are lacking context required to provide any advanced
            recommendations then don't provide anything. Example of an advanced recommendation include suggesting Snowflake partitioning keys when you see table names 
            being used that are very likely to be large tables e.g. invoice or journal line tables. Note that is just one example.
                """
        response = generate_response_advanced(prompt)
        return response

    def process_model(self, model_file: str, advanced: bool = False, metadata_only: bool = False):
        model_name = os.path.basename(model_file).replace(".sql", "")

        has_metadata = self.model_has_metadata(model_name)

        if metadata_only:
            # Skip AI suggestions and refs when only checking metadata
            raw_suggestion = ""
            refs = []
        else:
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

    def process_dbt_models(self, advanced: bool = False, metadata_only: bool = False):
        model_files = glob.glob(os.path.join(self.dbt_project_path, "models/**/*.sql"), recursive=True)
        models = [self.process_model(model_file, advanced, metadata_only) for model_file in model_files]
        missing_metadata = []

        # Check for models without metadata
        for model in models:
            if not model["metadata_exists"]:
                missing_metadata.append(model["model_name"])

        return models, missing_metadata

    def model_has_metadata(self, model_name: str) -> bool:
        for yaml_file in self.yaml_files:
            # Skip if not a file (extra safety check)
            if not os.path.isfile(yaml_file):
                continue

            try:
                with open(yaml_file, "r") as f:
                    yaml_content = yaml.safe_load(f)

                    if yaml_content:
                        for item in yaml_content.get("models", []):
                            if isinstance(item, dict) and item.get("name") == model_name:
                                return True
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {yaml_file}: {e}")
            except (OSError, IOError) as e:
                print(f"Error reading file {yaml_file}: {e}")

        return False

    def generate_lineage_graph(self, models):
        # Create a directed graph
        gph = nx.DiGraph()

        # Add nodes for each model
        for model in models:
            gph.add_node(model["model_name"], metadata_exists=model["metadata_exists"])

        # Add edges based on ref() calls
        for model in models:
            refs = model["refs"]
            for ref in refs:
                gph.add_edge(ref, model["model_name"])

        return gph

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

    def generate_image(self, description: str) -> None:
        image_binary = generate_dalle_image(description)
        image_path = f"{self.dbt_project_path}/lineage.png"
        print(f"Saving generated lineage image in {image_path}")
        # Write image to file
        with open(image_path, "wb") as f:
            f.write(image_binary)

    def plot_directed_graph(self, gph: nx.DiGraph):
        pos = nx.spring_layout(gph, seed=42)

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode="markers+text",
            textposition="top center",
            hoverinfo="text",
            marker=dict(color="rgb(71, 122, 193)", size=10, line=dict(width=2, color="rgb(0, 0, 0)")),
            name="Nodes",
        )

        missing_metadata_color = "rgb(255, 0, 0)"

        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=2, color="#888"),
            hoverinfo="none",
            mode="lines",
            name="Edges",
        )

        for node in gph.nodes():
            x, y = pos[node]
            node_trace["x"] += tuple([x])
            node_trace["y"] += tuple([y])
            node_trace["text"] += tuple([node])

            # set marker color and/or text label based on whether the model has metadata or not
            if "metadata_exists" in gph.nodes[node] and not gph.nodes[node]["metadata_exists"]:
                node_trace["marker"]["color"] = missing_metadata_color
                node_trace["text"] += tuple(["MISSING METADATA"])
            else:
                node_trace["marker"]["color"] = "rgb(71, 122, 193)"

        for edge in gph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace["x"] += tuple([x0, x1, None])
            edge_trace["y"] += tuple([y0, y1, None])

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="Directed Graph of DBT Models",
            title_x=0.5,
            title_font_size=24,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.2, 1.2]),
        )

        fig.show()

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

    def get_or_generate_manifest(self, project_path: str) -> Optional[Dict]:
        """Get or generate dbt manifest.json for advanced analysis

        Uses dbt parse (fast, no DB connection) or dbt ls (fallback) to generate manifest.
        These commands work without database connections unlike dbt compile.
        """
        manifest_path = os.path.join(project_path, "target", "manifest.json")

        # Try to load existing manifest
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Check if dbt_project.yml exists
        dbt_project_file = os.path.join(project_path, "dbt_project.yml")
        if not os.path.exists(dbt_project_file):
            print(f"⚠️  No dbt_project.yml found at {dbt_project_file}")
            return None

        # Check if dbt is available
        try:
            dbt_check = subprocess.run(["dbt", "--version"], capture_output=True, text=True, timeout=10)
            if dbt_check.returncode != 0:
                print(f"❌ dbt not available or not working: {dbt_check.stderr}")
                return None
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"❌ dbt command not found: {e}")
            return None

        # Try to generate manifest using dbt parse (works without database connection)
        try:
            print(f"🔍 Attempting dbt parse in {project_path}")
            result = subprocess.run(
                ["dbt", "parse", "--project-dir", project_path], capture_output=True, text=True, timeout=60
            )
            print(f"📄 dbt parse exit code: {result.returncode}")
            if result.stderr:
                print(f"⚠️  dbt parse stderr: {result.stderr}")

            if result.returncode == 0 and os.path.exists(manifest_path):
                print(f"✅ Manifest generated at {manifest_path}")
                with open(manifest_path, "r") as f:
                    return json.load(f)
            # If dbt parse fails, try dbt ls as fallback (also works without DB connection)
            elif result.returncode != 0:
                print(f"🔄 dbt parse failed, trying dbt ls fallback")
                result = subprocess.run(
                    ["dbt", "ls", "--project-dir", project_path], capture_output=True, text=True, timeout=60
                )
                print(f"📄 dbt ls exit code: {result.returncode}")
                if result.stderr:
                    print(f"⚠️  dbt ls stderr: {result.stderr}")

                if result.returncode == 0 and os.path.exists(manifest_path):
                    print(f"✅ Manifest generated via dbt ls at {manifest_path}")
                    with open(manifest_path, "r") as f:
                        return json.load(f)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"❌ Exception during manifest generation: {e}")
            pass

        return None

    def _fallback_dbt_analysis_without_cli(self, project_path: str) -> Dict:
        """Fallback analysis using direct file parsing when dbt CLI unavailable"""
        try:
            # Use existing YAML-based analysis as fallback
            models, missing_metadata = self.process_dbt_models(metadata_only=True)

            # Convert to manifest-like structure for consistency
            models_dict: Dict[str, Dict] = {}
            fallback_data = {
                "models": models_dict,
                "total_models": len(models),
                "missing_metadata": missing_metadata,
                "metadata_coverage_percent": round((len(models) - len(missing_metadata)) / len(models) * 100, 1)
                if models
                else 0,
                "fallback_method": "yaml_based_analysis",
            }

            # Convert models to expected format
            for model in models:
                model_name = model.get("model_name", "")
                if isinstance(model_name, str) and model_name:
                    models_dict[model_name] = {
                        "columns": [],  # Limited info without manifest
                        "tests": [],  # Limited info without manifest
                        "has_metadata": model.get("metadata_exists", False),
                        "dependencies": model.get("refs", []),
                    }

            return fallback_data

        except Exception as e:
            return {"error": f"Both manifest generation and fallback analysis failed: {e}", "fallback_method": "failed"}

    def analyze_column_metadata_coverage(self, project_path: str) -> Dict:
        """Analyze column-level metadata coverage using manifest"""
        manifest = self.get_or_generate_manifest(project_path)
        if not manifest:
            # Check what specifically failed
            dbt_project_file = os.path.join(project_path, "dbt_project.yml")
            diagnostics = {
                "dbt_project_exists": os.path.exists(dbt_project_file),
                "project_path": project_path,
            }

            # Check if dbt is available
            try:
                dbt_check = subprocess.run(["dbt", "--version"], capture_output=True, text=True, timeout=10)
                diagnostics["dbt_available"] = dbt_check.returncode == 0
                if dbt_check.returncode != 0:
                    diagnostics["dbt_error"] = dbt_check.stderr
            except (subprocess.SubprocessError, FileNotFoundError):
                diagnostics["dbt_available"] = False
                diagnostics["dbt_error"] = "dbt command not found"

            # Try fallback analysis using existing YAML-based methods
            print("🔄 Attempting fallback analysis without dbt CLI")
            fallback_result = self._fallback_dbt_analysis_without_cli(project_path)

            if "error" not in fallback_result:
                return {
                    "error": "Manifest generation failed, using fallback analysis",
                    "fallback_used": True,
                    "diagnostics": diagnostics,
                    "total_columns": 0,  # Limited without manifest
                    "documented_columns": 0,  # Limited without manifest
                    "coverage_percentage": 0,  # Limited without manifest
                    "undocumented_by_model": {},
                    "fallback_data": fallback_result,
                }
            else:
                return {
                    "error": "Could not load or generate dbt manifest",
                    "fallback_used": True,
                    "diagnostics": diagnostics,
                }

        total_columns = 0
        documented_columns = 0
        undocumented_by_model = {}

        models = manifest.get("nodes", {})
        for node_id, node in models.items():
            if node.get("resource_type") == "model":
                model_name = node.get("name", "")
                columns = node.get("columns", {})

                model_undocumented = []
                for col_name, col_info in columns.items():
                    total_columns += 1
                    description = col_info.get("description", "").strip()
                    if description:
                        documented_columns += 1
                    else:
                        model_undocumented.append(col_name)

                if model_undocumented:
                    undocumented_by_model[model_name] = model_undocumented

        coverage_percentage = round((documented_columns / total_columns * 100) if total_columns > 0 else 0, 1)

        return {
            "total_columns": total_columns,
            "documented_columns": documented_columns,
            "coverage_percentage": coverage_percentage,
            "undocumented_by_model": undocumented_by_model,
        }

    def analyze_test_coverage(self, project_path: str) -> Dict:
        """Analyze test coverage for models and columns using manifest"""
        manifest = self.get_or_generate_manifest(project_path)
        if not manifest:
            # Check what specifically failed
            dbt_project_file = os.path.join(project_path, "dbt_project.yml")
            diagnostics = {
                "dbt_project_exists": os.path.exists(dbt_project_file),
                "project_path": project_path,
            }

            # Check if dbt is available
            try:
                dbt_check = subprocess.run(["dbt", "--version"], capture_output=True, text=True, timeout=10)
                diagnostics["dbt_available"] = dbt_check.returncode == 0
                if dbt_check.returncode != 0:
                    diagnostics["dbt_error"] = dbt_check.stderr
            except (subprocess.SubprocessError, FileNotFoundError):
                diagnostics["dbt_available"] = False
                diagnostics["dbt_error"] = "dbt command not found"

            # Try fallback analysis using existing YAML-based methods
            print("🔄 Attempting fallback analysis without dbt CLI")
            fallback_result = self._fallback_dbt_analysis_without_cli(project_path)

            if "error" not in fallback_result:
                return {
                    "error": "Manifest generation failed, using fallback analysis",
                    "fallback_used": True,
                    "diagnostics": diagnostics,
                    "models": fallback_result.get("models", {}),
                    "untested_models": list(fallback_result.get("missing_metadata", [])),  # Approximate
                    "model_coverage_percentage": fallback_result.get("metadata_coverage_percent", 0),
                    "column_coverage_percentage": 0,  # Limited without manifest
                    "fallback_data": fallback_result,
                }
            else:
                return {
                    "error": "Could not load or generate dbt manifest",
                    "fallback_used": True,
                    "diagnostics": diagnostics,
                }

        models = {}
        tests = {}

        # Collect models
        nodes = manifest.get("nodes", {})
        for node_id, node in nodes.items():
            if node.get("resource_type") == "model":
                model_name = node.get("name", "")
                models[model_name] = {"columns": list(node.get("columns", {}).keys()), "tests": []}

        # Collect tests and map them to models
        for node_id, node in nodes.items():
            if node.get("resource_type") == "test":
                test_name = node.get("name", "")
                depends_on = node.get("depends_on", {}).get("nodes", [])

                # Find which model this test applies to
                for dep in depends_on:
                    if dep.startswith("model."):
                        model_name = dep.split(".")[-1]
                        if model_name in models:
                            test_info = {
                                "name": test_name,
                                "test_type": self._classify_test_type(node.get("raw_code", "")),
                                "column": self._extract_test_column(node),
                            }
                            models[model_name]["tests"].append(test_info)

        # Calculate coverage stats
        total_models = len(models)
        tested_models = len([m for m in models.values() if m["tests"]])
        untested_models = [name for name, info in models.items() if not info["tests"]]

        # Calculate column test coverage
        total_columns = sum(len(model["columns"]) for model in models.values())
        tested_columns = 0
        for model_info in models.values():
            tested_cols = set()
            for test in model_info["tests"]:
                if test["column"]:
                    tested_cols.add(test["column"])
            tested_columns += len(tested_cols)

        return {
            "total_models": total_models,
            "tested_models": tested_models,
            "untested_models": untested_models,
            "model_coverage_percentage": round((tested_models / total_models * 100) if total_models > 0 else 0, 1),
            "total_columns": total_columns,
            "tested_columns": tested_columns,
            "column_coverage_percentage": round((tested_columns / total_columns * 100) if total_columns > 0 else 0, 1),
            "models": models,
        }

    def _classify_test_type(self, raw_code: str) -> str:
        """Classify test type based on raw SQL code"""
        code_lower = raw_code.lower()
        if "not_null" in code_lower:
            return "not_null"
        elif "unique" in code_lower:
            return "unique"
        elif "relationships" in code_lower or "foreign" in code_lower:
            return "relationships"
        elif "accepted_values" in code_lower:
            return "accepted_values"
        else:
            return "custom"

    def _extract_test_column(self, test_node: Dict) -> Optional[str]:
        """Extract column name from test node"""
        # Check if test has column_name metadata
        if "column_name" in test_node:
            return test_node["column_name"]

        # Try to extract from test metadata
        test_metadata = test_node.get("test_metadata", {})
        if "kwargs" in test_metadata:
            column_name = test_metadata["kwargs"].get("column_name")
            if column_name:
                return column_name

        return None

    def get_model_tests_detailed(self, model_name: str, project_path: str) -> Dict:
        """Get detailed test information for a specific model"""
        coverage_data = self.analyze_test_coverage(project_path)

        if "error" in coverage_data:
            return coverage_data

        models = coverage_data.get("models", {})
        if model_name not in models:
            return {"error": f"Model '{model_name}' not found in project"}

        model_info = models[model_name]

        # Calculate test coverage score for this model
        total_columns = len(model_info["columns"])
        tested_columns = len(set(test["column"] for test in model_info["tests"] if test["column"]))
        has_model_tests = any(not test["column"] for test in model_info["tests"])

        coverage_score = 0.0
        if total_columns > 0:
            column_score = tested_columns / total_columns * 0.8  # 80% weight for column tests
            model_score = 0.2 if has_model_tests else 0  # 20% weight for model-level tests
            coverage_score = round(column_score + model_score, 2)

        return {
            "model_name": model_name,
            "tests": model_info["tests"],
            "total_columns": total_columns,
            "tested_columns": tested_columns,
            "has_model_tests": has_model_tests,
            "test_coverage_score": coverage_score,
            "recommendations": self.generate_test_recommendations(model_info),
        }

    def generate_test_recommendations(self, model_info: Dict) -> List[str]:
        """Generate test recommendations for a model"""
        recommendations = []

        tested_columns = set(test["column"] for test in model_info["tests"] if test["column"])
        untested_columns = set(model_info["columns"]) - tested_columns

        if untested_columns:
            recommendations.append(f"Consider adding tests for columns: {', '.join(sorted(untested_columns))}")

        # Check for common test patterns
        test_types = set(test["test_type"] for test in model_info["tests"])
        if "not_null" not in test_types:
            recommendations.append("Consider adding not_null tests for key columns")
        if "unique" not in test_types:
            recommendations.append("Consider adding unique tests for identifier columns")

        return recommendations
