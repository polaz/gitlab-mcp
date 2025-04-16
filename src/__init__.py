"""GitLab MCP - A Model Context Protocol server for interacting with GitLab API."""

__version__ = "0.2.0"

# Re-export key components for easier imports
from .api.client import gitlab_client
from .api.exceptions import GitLabAPIError, GitLabAuthError

__all__ = [
    "GitLabAPIError",
    "GitLabAuthError",
    "gitlab_client",
]
