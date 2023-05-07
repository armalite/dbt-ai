# flake8: noqa

import os

from dbt_ai.dbt import DbtModelProcessor  #
from dbt_ai.helper import find_yaml_files


def test_find_yaml_files(dbt_project):
    processor = DbtModelProcessor(dbt_project)
    yaml_files = find_yaml_files(processor.dbt_project_path)

    assert len(yaml_files) >= 1
    assert os.path.basename(yaml_files[0]) == "schema.yml"
