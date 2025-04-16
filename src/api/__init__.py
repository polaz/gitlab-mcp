"""API module for GitLab MCP.

This module contains the GitLab client and API exceptions.
"""

from .client import gitlab_client
from .exceptions import GitLabAPIError, GitLabAuthError

__all__ = [
    "GitLabAPIError",
    "GitLabAuthError",
    "gitlab_client",
]
