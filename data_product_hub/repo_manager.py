"""Repository management for Data Product Hub MCP Server"""

import hashlib
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .github_auth import get_github_auth


class RepositoryManager:
    """Manages repository cloning, caching, and cleanup for dbt project analysis"""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize repository manager with cache directory

        Args:
            cache_dir: Directory to cache repositories (defaults to system temp)
        """
        if cache_dir is None:
            cache_dir = os.path.join(tempfile.gettempdir(), "data_product_hub_repos")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache settings
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.max_cache_size = 100  # Maximum number of cached repos

    def _get_repo_cache_path(self, repo_url: str) -> Path:
        """Get the cache path for a repository

        Args:
            repo_url: GitHub repository URL

        Returns:
            Path to the cached repository directory
        """
        # Create a hash of the repo URL for the cache directory name
        repo_hash = hashlib.md5(repo_url.encode()).hexdigest()

        github_auth = get_github_auth()
        if github_auth:
            try:
                owner, repo = github_auth.parse_github_url(repo_url)
                safe_name = f"{owner}_{repo}_{repo_hash[:8]}"
            except:
                safe_name = f"repo_{repo_hash[:8]}"
        else:
            safe_name = f"repo_{repo_hash[:8]}"

        return self.cache_dir / safe_name

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cached repository is still valid (not expired)

        Args:
            cache_path: Path to cached repository

        Returns:
            True if cache is valid, False if expired or doesn't exist
        """
        if not cache_path.exists():
            return False

        cache_time_file = cache_path / ".cache_timestamp"
        if not cache_time_file.exists():
            return False

        try:
            with open(cache_time_file, 'r') as f:
                cache_timestamp = float(f.read().strip())

            return (time.time() - cache_timestamp) < self.cache_ttl
        except:
            return False

    def _update_cache_timestamp(self, cache_path: Path) -> None:
        """Update the cache timestamp for a repository

        Args:
            cache_path: Path to cached repository
        """
        cache_time_file = cache_path / ".cache_timestamp"
        with open(cache_time_file, 'w') as f:
            f.write(str(time.time()))

    def _cleanup_old_caches(self) -> None:
        """Remove old cached repositories to prevent disk space issues"""
        if not self.cache_dir.exists():
            return

        # Get all cache directories with their timestamps
        cache_dirs = []
        for item in self.cache_dir.iterdir():
            if item.is_dir():
                cache_time_file = item / ".cache_timestamp"
                if cache_time_file.exists():
                    try:
                        with open(cache_time_file, 'r') as f:
                            timestamp = float(f.read().strip())
                        cache_dirs.append((item, timestamp))
                    except:
                        # Remove corrupted cache
                        shutil.rmtree(item, ignore_errors=True)

        # Sort by timestamp (oldest first)
        cache_dirs.sort(key=lambda x: x[1])

        # Remove oldest caches if we exceed max cache size
        while len(cache_dirs) > self.max_cache_size:
            old_cache, _ = cache_dirs.pop(0)
            shutil.rmtree(old_cache, ignore_errors=True)

    def _clone_repository(self, repo_url: str, target_path: Path, access_token: Optional[str] = None) -> bool:
        """Clone a repository to the target path

        Args:
            repo_url: GitHub repository URL
            target_path: Path where to clone the repository
            access_token: GitHub access token for authentication

        Returns:
            True if clone was successful, False otherwise
        """
        try:
            # Prepare clone URL with authentication if token is provided
            if access_token:
                # Insert token into URL for private repos
                if repo_url.startswith('https://github.com/'):
                    auth_url = repo_url.replace('https://github.com/', f'https://x-access-token:{access_token}@github.com/')
                else:
                    auth_url = f'https://x-access-token:{access_token}@github.com/{repo_url}'
            else:
                # For public repos, use the original URL
                if not repo_url.startswith('https://'):
                    auth_url = f'https://github.com/{repo_url}'
                else:
                    auth_url = repo_url

            # Ensure target directory doesn't exist
            if target_path.exists():
                shutil.rmtree(target_path)

            # Clone repository with depth=1 for faster cloning
            result = subprocess.run([
                'git', 'clone', '--depth', '1', auth_url, str(target_path)
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                self._update_cache_timestamp(target_path)
                return True
            else:
                print(f"Git clone failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"Git clone timed out for {repo_url}")
            return False
        except Exception as e:
            print(f"Error cloning repository {repo_url}: {e}")
            return False

    def get_repository(self, repo_url: str) -> Tuple[Optional[str], Optional[Dict]]:
        """Get a repository (from cache or by cloning)

        Args:
            repo_url: GitHub repository URL

        Returns:
            Tuple of (local_path, error_info)
            - local_path: Path to the local repository directory, None if failed
            - error_info: Error information if failed, None if successful
        """
        try:
            # Validate GitHub URL and get access token
            github_auth = get_github_auth()
            if not github_auth:
                return None, {
                    "error": "GitHub authentication not configured",
                    "message": "GitHub App credentials are required for repository access"
                }

            validation_result = github_auth.validate_repo_access(repo_url)
            if not validation_result["valid"]:
                return None, validation_result

            if not validation_result["dbt_project"]["is_valid_dbt_project"]:
                return None, {
                    "error": "Not a valid dbt project",
                    "message": "Repository must contain dbt_project.yml and models/ directory",
                    "dbt_validation": validation_result["dbt_project"]
                }

            access_token = validation_result["access_token"]

            # Check cache
            cache_path = self._get_repo_cache_path(repo_url)

            if self._is_cache_valid(cache_path):
                return str(cache_path), None

            # Clean up old caches before adding new one
            self._cleanup_old_caches()

            # Clone repository
            if self._clone_repository(repo_url, cache_path, access_token):
                return str(cache_path), None
            else:
                return None, {
                    "error": "Failed to clone repository",
                    "message": f"Could not clone {repo_url}. Check repository URL and permissions."
                }

        except Exception as e:
            return None, {
                "error": "Repository access failed",
                "message": f"Unexpected error: {str(e)}"
            }

    def validate_dbt_project(self, local_path: str) -> Dict[str, Any]:
        """Validate that a local directory contains a valid dbt project

        Args:
            local_path: Path to the local repository directory

        Returns:
            Dictionary with validation results
        """
        try:
            repo_path = Path(local_path)

            # Check for dbt_project.yml
            dbt_project_file = repo_path / "dbt_project.yml"
            has_dbt_project = dbt_project_file.exists()

            # Check for models directory
            models_dir = repo_path / "models"
            has_models_dir = models_dir.exists() and models_dir.is_dir()

            # Count SQL files in models directory
            sql_files = []
            if has_models_dir:
                sql_files = list(models_dir.rglob("*.sql"))

            return {
                "valid": has_dbt_project and has_models_dir and len(sql_files) > 0,
                "has_dbt_project_yml": has_dbt_project,
                "has_models_directory": has_models_dir,
                "sql_model_count": len(sql_files),
                "models_path": str(models_dir) if has_models_dir else None,
                "dbt_project_path": str(dbt_project_file) if has_dbt_project else None,
                "repo_path": str(repo_path)
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Error validating dbt project: {str(e)}"
            }

    def cleanup_cache(self, max_age_hours: int = 24) -> int:
        """Clean up cached repositories older than specified age

        Args:
            max_age_hours: Maximum age in hours for cached repositories

        Returns:
            Number of repositories cleaned up
        """
        if not self.cache_dir.exists():
            return 0

        cleanup_count = 0
        cutoff_time = time.time() - (max_age_hours * 3600)

        for item in self.cache_dir.iterdir():
            if item.is_dir():
                cache_time_file = item / ".cache_timestamp"
                if cache_time_file.exists():
                    try:
                        with open(cache_time_file, 'r') as f:
                            timestamp = float(f.read().strip())

                        if timestamp < cutoff_time:
                            shutil.rmtree(item, ignore_errors=True)
                            cleanup_count += 1
                    except:
                        # Remove corrupted cache
                        shutil.rmtree(item, ignore_errors=True)
                        cleanup_count += 1

        return cleanup_count


# Singleton instance for use across the MCP server
repo_manager = RepositoryManager()