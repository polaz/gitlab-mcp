# filepath: c:\Users\aditp\Desktop\python\gitlab-mcp-main\src\api\exceptions\__init__.py
"""Exceptions module for GitLab MCP API.

This module contains all exception classes used throughout the GitLab MCP API.
"""

from .base import GitLabAPIError, GitLabAuthError
from .branch import (
    BranchCreationError,
    BranchDeleteError,
    BranchListError,
    BranchProtectionError,
    DefaultBranchError,
    GitLabBranchError,
    MergedBranchesDeleteError,
)
from .file import (
    FileBlameError,
    FileContentError,
    FileCreateError,
    FileDeleteError,
    FileUpdateError,
    GitLabFileError,
)

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
    # File exceptions
    "FileBlameError",
    "FileContentError",
    "FileCreateError",
    "FileDeleteError",
    "FileUpdateError",
    "GitLabFileError",
]
