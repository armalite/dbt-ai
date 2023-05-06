import os
import tempfile
import pytest
from dbt_ai.dbt import DbtModelProcessor  # 
from unittest.mock import MagicMock
from tests.fixtures import dbt_project



def test_model_has_metadata(dbt_project):
    processor = DbtModelProcessor(dbt_project)

    assert processor.model_has_metadata("model1")
    assert processor.model_has_metadata("model2")
    assert not processor.model_has_metadata("model3")

def test_suggest_dbt_model_improvements(dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    # Mock the generate_response method to return a fixed suggestion
    processor.generate_response = MagicMock(return_value="Use ref() function instead of hardcoding table names.")

    suggestions = processor.suggest_dbt_model_improvements(model_file, "model1")

    assert len(suggestions) == 1
    assert suggestions[0] == "Use ref() function instead of hardcoding table names."

def test_process_model(dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    # Mock the generate_response method to return a fixed suggestion
    processor.generate_response = MagicMock(return_value="Use ref() function instead of hardcoding table names.")

    result = processor.process_model(model_file)

    assert result["name"] == "model1"
    assert result["has_metadata"]
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0] == "Use ref() function instead of hardcoding table names."


def test_process_dbt_models(dbt_project):
    processor = DbtModelProcessor(dbt_project)

    # Mock the generate_response method to return a fixed suggestion
    processor.generate_response = MagicMock(return_value="Use ref() function instead of hardcoding table names.")

    models = processor.process_dbt_models()

    assert len(models) == 1

    model = models[0]
    assert model["name"] == "model1"
    assert model["has_metadata"]
    assert len(model["suggestions"]) == 1
    assert model["suggestions"][0] == "Use ref() function instead of hardcoding table names."
