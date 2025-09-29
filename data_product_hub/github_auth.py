"""GitHub App authentication for Data Product Hub MCP Server"""

import base64
import json
import os
import time
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import jwt
import requests


class GitHubAppAuth:
    """Handles GitHub App authentication and repository access"""

    def __init__(self):
        """Initialize GitHub App authentication from environment variables"""
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.private_key_base64 = os.getenv("GITHUB_APP_PRIVATE_KEY_BASE64")
        self.base_url = "https://api.github.com"

        if not self.app_id or not self.private_key_base64:
            raise ValueError(
                "Missing GitHub App credentials. Set GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY_BASE64 "
                "environment variables."
            )

        # Decode the base64-encoded private key
        try:
            # We've already checked that private_key_base64 is not None above
            assert self.private_key_base64 is not None
            self.private_key = base64.b64decode(self.private_key_base64).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Invalid GITHUB_APP_PRIVATE_KEY_BASE64: {e}") from e

    def _generate_jwt_token(self) -> str:
        """Generate a JWT token for GitHub App authentication"""
        now = int(time.time())
        # We've already checked that app_id is not None in __init__
        assert self.app_id is not None
        payload = {
            'iat': now - 60,  # issued at (60 seconds in the past to account for clock skew)
            'exp': now + 600,  # expires in 10 minutes
            'iss': int(self.app_id)  # issuer is the GitHub App ID
        }

        return jwt.encode(payload, self.private_key, algorithm='RS256')

    def _get_installation_id(self, owner: str, repo: str) -> Optional[int]:
        """Get the installation ID for a specific repository"""
        jwt_token = self._generate_jwt_token()

        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'DataProductHub/1.0'
        }

        # Get installations for this app
        response = requests.get(f"{self.base_url}/app/installations", headers=headers)

        if response.status_code != 200:
            print(f"Failed to get installations: {response.status_code} {response.text}")
            return None

        installations = response.json()

        # Find installation that has access to this repo
        for installation in installations:
            installation_id = installation['id']

            # Get repositories for this installation
            install_token = self._get_installation_token(installation_id)
            if not install_token:
                continue

            repo_headers = {
                'Authorization': f'token {install_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'DataProductHub/1.0'
            }

            repo_response = requests.get(
                f"{self.base_url}/installation/repositories",
                headers=repo_headers
            )

            if repo_response.status_code == 200:
                repositories = repo_response.json().get('repositories', [])
                for repository in repositories:
                    if repository['owner']['login'] == owner and repository['name'] == repo:
                        return installation_id

        return None

    def _get_installation_token(self, installation_id: int) -> Optional[str]:
        """Get an installation access token for a specific installation"""
        jwt_token = self._generate_jwt_token()

        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'DataProductHub/1.0'
        }

        response = requests.post(
            f"{self.base_url}/app/installations/{installation_id}/access_tokens",
            headers=headers
        )

        if response.status_code == 201:
            return response.json()['token']
        else:
            print(f"Failed to get installation token: {response.status_code} {response.text}")
            return None

    def parse_github_url(self, repo_url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name

        Args:
            repo_url: GitHub repository URL (various formats supported)

        Returns:
            Tuple of (owner, repo_name)

        Raises:
            ValueError: If URL is not a valid GitHub repository URL
        """
        # Handle different URL formats
        repo_url = repo_url.strip().rstrip('/')

        # Remove .git suffix if present
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]

        # Parse URL
        if repo_url.startswith('https://github.com/'):
            path = repo_url.replace('https://github.com/', '')
        elif repo_url.startswith('github.com/'):
            path = repo_url.replace('github.com/', '')
        elif '/' in repo_url and not repo_url.startswith('http'):
            # Assume it's in format "owner/repo"
            path = repo_url
        else:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

        parts = path.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid GitHub repository path: {path}")

        owner, repo = parts
        if not owner or not repo:
            raise ValueError(f"Invalid GitHub repository path: {path}")

        return owner, repo

    def get_repo_access_token(self, repo_url: str) -> Optional[str]:
        """Get an access token for a specific repository

        Args:
            repo_url: GitHub repository URL

        Returns:
            Access token if the app is installed on the repo, None otherwise
        """
        try:
            owner, repo = self.parse_github_url(repo_url)
            installation_id = self._get_installation_id(owner, repo)

            if installation_id:
                return self._get_installation_token(installation_id)
            else:
                print(f"GitHub App not installed on {owner}/{repo}")
                return None

        except Exception as e:
            print(f"Error getting repo access token: {e}")
            return None

    def validate_repo_access(self, repo_url: str) -> Dict[str, Any]:
        """Validate that the app has access to a repository and it's a valid dbt project

        Args:
            repo_url: GitHub repository URL

        Returns:
            Dictionary with validation results
        """
        try:
            owner, repo = self.parse_github_url(repo_url)
            token = self.get_repo_access_token(repo_url)

            if not token:
                return {
                    "valid": False,
                    "error": f"GitHub App not installed on {owner}/{repo}. "
                           f"Please install the Data Product Hub app on this repository.",
                    "install_url": f"https://github.com/apps/data-product-hub/installations/new"
                }

            # Check if repository exists and we can access it
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'DataProductHub/1.0'
            }

            repo_response = requests.get(f"{self.base_url}/repos/{owner}/{repo}", headers=headers)

            if repo_response.status_code != 200:
                return {
                    "valid": False,
                    "error": f"Cannot access repository {owner}/{repo}. Status: {repo_response.status_code}"
                }

            repo_info = repo_response.json()

            # Check for dbt_project.yml to confirm it's a dbt project
            dbt_project_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/dbt_project.yml",
                headers=headers
            )

            has_dbt_project = dbt_project_response.status_code == 200

            # Check for models directory
            models_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/models",
                headers=headers
            )

            has_models_dir = models_response.status_code == 200

            return {
                "valid": True,
                "owner": owner,
                "repo": repo,
                "repo_info": {
                    "name": repo_info["name"],
                    "full_name": repo_info["full_name"],
                    "description": repo_info.get("description"),
                    "private": repo_info["private"],
                    "default_branch": repo_info["default_branch"]
                },
                "dbt_project": {
                    "has_dbt_project_yml": has_dbt_project,
                    "has_models_directory": has_models_dir,
                    "is_valid_dbt_project": has_dbt_project and has_models_dir
                },
                "access_token": token
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Error validating repository access: {str(e)}"
            }


# Singleton instance for use across the MCP server
github_auth = None

def get_github_auth() -> Optional[GitHubAppAuth]:
    """Get the GitHub authentication instance (singleton)"""
    global github_auth

    if github_auth is None:
        try:
            github_auth = GitHubAppAuth()
        except ValueError as e:
            print(f"GitHub App authentication not configured: {e}")
            return None

    return github_auth