import os
import tempfile
import pytest
from dbt_ai.dbt import DbtModelProcessor  # 
from dbt_ai.helper import find_yaml_files
from unittest.mock import MagicMock
from tests.fixtures import dbt_project


def test_find_yaml_files(dbt_project):
    processor = DbtModelProcessor(dbt_project)
    yaml_files = find_yaml_files(processor.dbt_project_path)

    assert len(yaml_files) == 1
    assert os.path.basename(yaml_files[0]) == "schema.yml"