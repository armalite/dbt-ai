# flake8: noqa

import json
import os
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
import pytest

from data_product_hub.main import main, output_json, output_text_metadata_only, output_text_full_analysis


class TestOutputFunctions:
    def test_output_json(self, capsys):
        """Test JSON output formatting"""
        test_data = {"operation": "test", "total_models": 3, "models": [{"name": "test_model", "has_metadata": True}]}

        output_json(test_data)

        captured = capsys.readouterr()
        parsed_output = json.loads(captured.out)
        assert parsed_output == test_data

    def test_output_text_metadata_only_with_missing(self, capsys):
        """Test text output when models are missing metadata"""
        models = [{"model_name": "model1", "metadata_exists": True}, {"model_name": "model2", "metadata_exists": False}]
        missing_metadata = ["model2"]

        output_text_metadata_only(models, missing_metadata)

        captured = capsys.readouterr()
        assert "The following models are missing metadata:" in captured.out
        assert "- model2" in captured.out
        assert "Metadata check complete. 2 models analyzed." in captured.out

    def test_output_text_metadata_only_all_present(self, capsys):
        """Test text output when all models have metadata"""
        models = [{"model_name": "model1", "metadata_exists": True}, {"model_name": "model2", "metadata_exists": True}]
        missing_metadata = []

        output_text_metadata_only(models, missing_metadata)

        captured = capsys.readouterr()
        assert "All models have associated metadata." in captured.out
        assert "Metadata check complete. 2 models analyzed." in captured.out

    @patch("data_product_hub.main.generate_html_report")
    def test_output_text_full_analysis(self, mock_html_report, capsys):
        """Test full analysis text output"""
        models = [{"model_name": "test_model", "metadata_exists": True}]
        missing_metadata = []
        lineage_description = "test_model is a root node"
        output_path = "/test/path.html"
        advanced = True

        output_text_full_analysis(models, missing_metadata, lineage_description, output_path, advanced)

        captured = capsys.readouterr()
        assert "Lineage description:" in captured.out
        assert "test_model is a root node" in captured.out
        assert "Generated advanced improvement suggestions report at: /test/path.html" in captured.out
        mock_html_report.assert_called_once_with(models, output_path, missing_metadata)


class TestMainFunction:
    @patch("data_product_hub.main.DbtModelProcessor")
    def test_main_metadata_only_json_output(self, mock_processor_class, capsys):
        """Test main function with --metadata-only flag and JSON output"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_dbt_models.return_value = (
            [{"model_name": "model1", "metadata_exists": True}, {"model_name": "model2", "metadata_exists": False}],
            ["model2"],
        )

        # Mock sys.argv
        test_args = ["data-product-hub", "-f", "/test/path", "--metadata-only", "--output", "json"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify processor was called correctly
        mock_processor_class.assert_called_once_with("/test/path", "snowflake")
        mock_processor.process_dbt_models.assert_called_once_with(advanced=False, metadata_only=True)

        # Verify JSON output
        captured = capsys.readouterr()
        output_data = json.loads(captured.out)
        assert output_data["operation"] == "metadata_check"
        assert output_data["total_models"] == 2
        assert output_data["missing_metadata"] == ["model2"]
        assert output_data["metadata_coverage_percent"] == 50.0

    @patch("data_product_hub.main.DbtModelProcessor")
    def test_main_metadata_only_text_output(self, mock_processor_class, capsys):
        """Test main function with --metadata-only flag and text output"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_dbt_models.return_value = (
            [{"model_name": "model1", "metadata_exists": False}],
            ["model1"],
        )

        # Mock sys.argv
        test_args = ["data-product-hub", "-f", "/test/path", "--metadata-only", "--output", "text"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify text output
        captured = capsys.readouterr()
        assert "The following models are missing metadata:" in captured.out
        assert "- model1" in captured.out

    @patch("data_product_hub.main.DbtModelProcessor")
    def test_main_full_analysis_json_output(self, mock_processor_class, capsys):
        """Test main function with full analysis and JSON output"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_dbt_models.return_value = (
            [
                {
                    "model_name": "model1",
                    "metadata_exists": True,
                    "suggestions": "Use better naming",
                    "refs": ["raw_table"],
                }
            ],
            [],
        )
        mock_processor.generate_lineage.return_value = ("model1 depends on raw_table", MagicMock())

        # Mock sys.argv
        test_args = ["data-product-hub", "-f", "/test/path", "--output", "json"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify JSON output
        captured = capsys.readouterr()
        output_data = json.loads(captured.out)
        assert output_data["operation"] == "full_analysis"
        assert output_data["total_models"] == 1
        assert len(output_data["models"]) == 1
        assert output_data["models"][0]["name"] == "model1"
        assert output_data["models"][0]["suggestions"] == "Use better naming"
        assert output_data["lineage_description"] == "model1 depends on raw_table"

    @patch("data_product_hub.main.DbtModelProcessor")
    @patch("data_product_hub.main.generate_html_report")
    def test_main_full_analysis_text_output(self, mock_html_report, mock_processor_class, capsys):
        """Test main function with full analysis and text output"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_dbt_models.return_value = ([{"model_name": "model1", "metadata_exists": True}], [])
        mock_processor.generate_lineage.return_value = ("model1 is a root node", MagicMock())

        # Mock sys.argv
        test_args = ["data-product-hub", "-f", "/test/path", "--output", "text"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify HTML report was generated
        mock_html_report.assert_called_once()
        captured = capsys.readouterr()
        assert "Generated improvement suggestions report at:" in captured.out

    @patch("data_product_hub.main.DbtModelProcessor")
    def test_main_advanced_recommendations(self, mock_processor_class, capsys):
        """Test main function with advanced recommendations flag"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_dbt_models.return_value = ([], [])
        mock_processor.generate_lineage.return_value = ("", MagicMock())

        # Mock sys.argv
        test_args = ["data-product-hub", "-f", "/test/path", "--advanced-rec"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify advanced flag was passed
        mock_processor.process_dbt_models.assert_called_once_with(advanced=True)

    @patch("data_product_hub.main.DbtModelProcessor")
    def test_main_database_selection(self, mock_processor_class):
        """Test main function with database selection"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_dbt_models.return_value = ([], [])
        mock_processor.generate_lineage.return_value = ("", MagicMock())

        # Mock sys.argv
        test_args = ["data-product-hub", "-f", "/test/path", "-d", "postgres"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify database was passed correctly
        mock_processor_class.assert_called_once_with("/test/path", "postgres")

    @patch("data_product_hub.main.DbtModelProcessor")
    def test_main_create_models(self, mock_processor_class):
        """Test main function with create models functionality"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor

        # Mock sys.argv
        test_args = ["data-product-hub", "-f", "/test/path", "--create-models", "Create a customer model"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify create_dbt_models was called
        mock_processor.create_dbt_models.assert_called_once_with("Create a customer model")

    @patch("data_product_hub.main.DbtModelProcessor")
    def test_main_default_output_is_json(self, mock_processor_class, capsys):
        """Test that JSON is the default output format"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_dbt_models.return_value = (
            [{"model_name": "test", "metadata_exists": True, "suggestions": "test suggestion", "refs": ["ref1"]}],
            [],
        )
        mock_processor.generate_lineage.return_value = ("test lineage", MagicMock())

        # Mock sys.argv (no --output flag specified)
        test_args = ["data-product-hub", "-f", "/test/path"]
        with patch.object(sys, "argv", test_args):
            main()

        # Verify JSON output is produced
        captured = capsys.readouterr()
        # Should be valid JSON
        output_data = json.loads(captured.out)
        assert "operation" in output_data
        assert output_data["operation"] == "full_analysis"
