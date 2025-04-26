# filepath: c:\Users\aditp\Desktop\python\gitlab-mcp-main\src\api\__init__.py
"""API module for GitLab MCP.

This module contains the GitLab API client and exceptions.
"""

from .exceptions import (
    BranchCreationError,
    BranchDeleteError,
    BranchListError,
    BranchProtectionError,
    DefaultBranchError,
    GitLabAPIError,
    GitLabAuthError,
    GitLabBranchError,
    MergedBranchesDeleteError,
)
from .rest_client import gitlab_rest_client

__all__ = [
    # Base exceptions
    "GitLabAPIError",
    "GitLabAuthError",
    # Branch exceptions
    "BranchCreationError",
    "BranchDeleteError",
    "BranchListError",
    "BranchProtectionError",
    "DefaultBranchError",
    "GitLabBranchError",
    "MergedBranchesDeleteError",
    # Clients
    "gitlab_rest_client",
]
