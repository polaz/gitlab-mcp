"""GitLab MCP - A Model Context Protocol server for interacting with GitLab API."""

__version__ = "0.2.0"

# Re-export key components for easier imports
from .api.exceptions import GitLabAPIError, GitLabAuthError
from .api.rest_client import gitlab_rest_client

__all__ = [
    "GitLabAPIError",
    "GitLabAuthError",
    "gitlab_rest_client",
]
