import os

from dbt_ai.dbt import DbtModelProcessor  #


def test_model_has_metadata(dbt_project):
    processor = DbtModelProcessor(dbt_project)

    assert processor.model_has_metadata("model1")
    assert processor.model_has_metadata("model2")
    assert not processor.model_has_metadata("model3")


def test_suggest_dbt_model_improvements(mock_generate_response, dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    suggestions = processor.suggest_dbt_model_improvements(model_file, "model1")

    assert len(suggestions) > 0
    assert suggestions[0] == "Use ref() function instead of hardcoding table names."


def test_process_model(mock_generate_response, dbt_project):
    processor = DbtModelProcessor(dbt_project)
    model_file = os.path.join(dbt_project, "models", "model1.sql")

    result = processor.process_model(model_file)

    assert result["model_name"] == "model1"
    assert result["metadata_exists"]
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0] == "Use ref() function instead of hardcoding table names."


def test_process_dbt_models(mock_generate_response, dbt_project):
    processor = DbtModelProcessor(dbt_project)

    models = processor.process_dbt_models()

    assert len(models) == 1

    model = models[0]
    assert model["model_name"] == "model1"
    assert model["metadata_exists"]
    assert len(model["suggestions"]) == 1
    assert model["suggestions"][0] == "Use ref() function instead of hardcoding table names."
