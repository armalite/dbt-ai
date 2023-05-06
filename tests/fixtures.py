
import os
import tempfile
import pytest
from dbt_ai.dbt import DbtModelProcessor  # 
from dbt_ai.helper import find_yaml_files
from unittest.mock import MagicMock


sample_sql_content = "SELECT * FROM table1;"

# Sample data for testing
sample_yaml_content = """
models:
  - name: model1
    description: Example model 1
  - name: model2
    description: Example model 2
"""


@pytest.fixture
def dbt_project(tmp_path):
    models_path = tmp_path / "models"
    models_path.mkdir()

    yaml_file = tmp_path / "schema.yml"
    yaml_file.write_text(sample_yaml_content)

    sql_file = models_path / "model1.sql"
    sql_file.write_text(sample_sql_content)

    return tmp_path