"""Tests for API key management functionality"""

import os
import unittest
from unittest.mock import MagicMock, patch

from data_product_hub.api_keys import get_api_key_source, get_openai_api_key, has_openai_access


class TestApiKeys(unittest.TestCase):
    """Test API key management with backwards compatibility"""

    def setUp(self):
        """Set up test environment"""
        # Clear environment variables
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    def tearDown(self):
        """Clean up test environment"""
        # Clear environment variables
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    def test_local_environment_variable_priority(self):
        """Test that local environment variable takes priority"""
        # Set local environment variable
        os.environ["OPENAI_API_KEY"] = "sk-local-test-key"

        # Should return local key even with repo_url provided
        result = get_openai_api_key("https://github.com/test/repo")
        self.assertEqual(result, "sk-local-test-key")

        # Check source
        source = get_api_key_source("https://github.com/test/repo")
        self.assertEqual(source, "local_environment")

        # Check access
        self.assertTrue(has_openai_access("https://github.com/test/repo"))

    @patch("data_product_hub.api_keys.get_github_auth")
    def test_github_environment_secret_fallback(self, mock_get_github_auth: MagicMock) -> None:
        """Test GitHub environment secret fallback when no local key"""
        # Mock GitHub auth
        mock_auth = MagicMock()
        mock_auth.get_openai_api_key.return_value = "sk-github-env-key"
        mock_get_github_auth.return_value = mock_auth

        # No local environment variable
        result = get_openai_api_key("https://github.com/test/repo")
        self.assertEqual(result, "sk-github-env-key")

        # Check that GitHub auth was called
        mock_auth.get_openai_api_key.assert_called_once_with("https://github.com/test/repo")

        # Check source
        source = get_api_key_source("https://github.com/test/repo")
        self.assertEqual(source, "github_environment_secret")

    @patch("data_product_hub.api_keys.get_github_auth")
    def test_no_api_key_available(self, mock_get_github_auth: MagicMock) -> None:
        """Test when no API key is available"""
        # Mock GitHub auth returning None
        mock_auth = MagicMock()
        mock_auth.get_openai_api_key.return_value = None
        mock_get_github_auth.return_value = mock_auth

        # No local environment variable, no GitHub key
        result = get_openai_api_key("https://github.com/test/repo")
        self.assertIsNone(result)

        # Check access
        self.assertFalse(has_openai_access("https://github.com/test/repo"))

        # Check source
        source = get_api_key_source("https://github.com/test/repo")
        self.assertEqual(source, "not_available")

    def test_no_repo_url_provided(self):
        """Test behavior when no repo_url is provided"""
        # Only local environment should work
        result = get_openai_api_key()
        self.assertIsNone(result)

        # With local environment variable
        os.environ["OPENAI_API_KEY"] = "sk-local-only"
        result = get_openai_api_key()
        self.assertEqual(result, "sk-local-only")

    @patch("data_product_hub.api_keys.get_github_auth")
    def test_github_auth_not_configured(self, mock_get_github_auth: MagicMock) -> None:
        """Test when GitHub auth is not configured"""
        # Mock no GitHub auth available
        mock_get_github_auth.return_value = None

        # Should fall back gracefully
        result = get_openai_api_key("https://github.com/test/repo")
        self.assertIsNone(result)

        source = get_api_key_source("https://github.com/test/repo")
        self.assertEqual(source, "not_available")

    def test_backwards_compatibility(self):
        """Test that CLI usage (local env var only) still works"""
        # This is how the original CLI worked
        os.environ["OPENAI_API_KEY"] = "sk-cli-compatible"

        # Should work without repo_url (CLI usage)
        result = get_openai_api_key()
        self.assertEqual(result, "sk-cli-compatible")

        # Should also work with repo_url (MCP usage with local override)
        result = get_openai_api_key("https://github.com/test/repo")
        self.assertEqual(result, "sk-cli-compatible")

        self.assertTrue(has_openai_access())
        self.assertTrue(has_openai_access("https://github.com/test/repo"))


if __name__ == "__main__":
    unittest.main()
