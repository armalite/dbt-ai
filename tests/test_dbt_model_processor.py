# flake8: noqa

import os
from unittest.mock import mock_open, patch, call
from unittest import mock
from dbt_ai.dbt import DbtModelProcessor  #


def test_suggest_dbt_model_improvements(mock_generate_response, dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    suggestions = processor.suggest_dbt_model_improvements(model_file, "model1")

    assert len(suggestions) > 0
    assert suggestions[0] == "Use ref() function instead of hardcoding table names."


def test_process_model(mock_generate_response, mock_generate_response_advanced, dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    result = processor.process_model(model_file, advanced=False)

    assert result["model_name"] == "model1"
    assert result["metadata_exists"]
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0] == "Use ref() function instead of hardcoding table names."


def test_process_dbt_models(mock_generate_response, mock_generate_response_advanced, dbt_project):
    processor = DbtModelProcessor(dbt_project)

    models, missing_metadata = processor.process_dbt_models(advanced=False)

    assert len(models) == 1

    model = models[0]
    assert model["model_name"] == "model1"
    assert model["metadata_exists"]
    assert model["suggestions"][0] == "Use ref() function instead of hardcoding table names."


def test_suggest_dbt_model_improvements_advanced(mock_generate_response, mock_generate_response_advanced, dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    suggestions = processor.suggest_dbt_model_improvements_advanced(model_file, "model1")

    assert len(suggestions) > 0
    assert suggestions[0] == "Use ref() function instead of hardcoding table names (advanced)."


def test_process_model_advanced(mock_generate_response, mock_generate_response_advanced, dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    result = processor.process_model(model_file, advanced=True)

    assert result["model_name"] == "model1"
    assert result["metadata_exists"]
    assert result["suggestions"][0] == "Use ref() function instead of hardcoding table names (advanced)."


def test_process_dbt_models_advanced(mock_generate_response, mock_generate_response_advanced, dbt_project):
    processor = DbtModelProcessor(dbt_project)

    models, missing_metadata = processor.process_dbt_models(advanced=True)

    assert len(models) == 1

    model = models[0]
    assert model["model_name"] == "model1"
    assert model["metadata_exists"]
    assert model["suggestions"][0] == "Use ref() function instead of hardcoding table names (advanced)."


def test_model_has_metadata(dbt_project):
    processor = DbtModelProcessor(dbt_project)

    assert processor.model_has_metadata("model1")
    assert processor.model_has_metadata("model2")
    assert not processor.model_has_metadata("model3")


def test_create_dbt_models(dbt_project, mock_generate_models):
    processor = DbtModelProcessor(dbt_project)

    prompt = "prompt for creating dbt models"
    processor.create_dbt_models(prompt)

    assert mock_generate_models.called_once_with(prompt, mock.ANY)
