"""API Key management for Data Product Hub MCP Server

Handles OpenAI API key retrieval with backwards compatibility:
1. Local environment variables (CLI usage)
2. GitHub Environment Secrets (MCP server usage)
"""

import os
from typing import Optional

from .github_auth import get_github_auth


def get_openai_api_key(repo_url: Optional[str] = None) -> Optional[str]:
    """Get OpenAI API key with fallback strategy

    Priority:
    1. Local environment variable (backwards compatibility for CLI)
    2. GitHub Environment Secrets (secure MCP server usage)

    Args:
        repo_url: Optional GitHub repository URL for environment secret lookup

    Returns:
        OpenAI API key if available, None otherwise
    """
    # 1. Check local environment variable first (CLI backwards compatibility)
    local_key = os.getenv("OPENAI_API_KEY")
    if local_key:
        return local_key

    # 2. If repo_url provided, try GitHub Environment Secrets
    if repo_url:
        github_auth = get_github_auth()
        if github_auth:
            repo_key = github_auth.get_openai_api_key(repo_url)
            if repo_key:
                return repo_key

    return None


def has_openai_access(repo_url: Optional[str] = None) -> bool:
    """Check if OpenAI API access is available

    Args:
        repo_url: Optional GitHub repository URL

    Returns:
        True if OpenAI API key is available, False otherwise
    """
    return get_openai_api_key(repo_url) is not None


def get_api_key_source(repo_url: Optional[str] = None) -> str:
    """Get the source of the API key for debugging/logging

    Args:
        repo_url: Optional GitHub repository URL

    Returns:
        String describing the API key source
    """
    if os.getenv("OPENAI_API_KEY"):
        return "local_environment"

    if repo_url:
        github_auth = get_github_auth()
        if github_auth:
            repo_key = github_auth.get_openai_api_key(repo_url)
            if repo_key:
                return "github_environment_secret"

    return "not_available"
