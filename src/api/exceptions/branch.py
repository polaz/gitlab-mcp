# filepath: c:\Users\aditp\Desktop\python\gitlab-mcp-main\src\api\exceptions\branch.py
"""Exceptions specific to GitLab branch operations."""

from src.api.exceptions.base import GitLabAPIError


class GitLabBranchError(GitLabAPIError):
    """Base exception for branch-related errors."""

    pass


class BranchCreationError(GitLabBranchError):
    """Raised when branch creation fails in GitLab."""

    def __init__(self, cause: Exception | None = None) -> None:
        """Initialize with standard error message and optional cause.

        Args:
            cause: The original exception that caused this error.
        """
        message = "Failed to create branch in GitLab repository"
        if cause:
            super().__init__(f"{message}: {cause}", getattr(cause, "code", None))
        else:
            super().__init__(message)


class DefaultBranchError(GitLabBranchError):
    """Raised when retrieving the default branch reference fails."""

    def __init__(self, cause: Exception | None = None) -> None:
        """Initialize with standard error message and optional cause.

        Args:
            cause: The original exception that caused this error.
        """
        message = "Failed to retrieve default branch reference"
        if cause:
            super().__init__(f"{message}: {cause}", getattr(cause, "code", None))
        else:
            super().__init__(message)


class BranchListError(GitLabBranchError):
    """Raised when listing branches fails."""

    def __init__(self, cause: Exception | None = None) -> None:
        """Initialize with standard error message and optional cause.

        Args:
            cause: The original exception that caused this error.
        """
        message = "Failed to retrieve branch list from GitLab repository"
        if cause:
            super().__init__(f"{message}: {cause}", getattr(cause, "code", None))
        else:
            super().__init__(message)


class BranchDeleteError(GitLabBranchError):
    """Raised when branch deletion fails."""

    def __init__(self, cause: Exception | None = None) -> None:
        """Initialize with standard error message and optional cause.

        Args:
            cause: The original exception that caused this error.
        """
        message = "Failed to delete branch in GitLab repository"
        if cause:
            super().__init__(f"{message}: {cause}", getattr(cause, "code", None))
        else:
            super().__init__(message)


class BranchProtectionError(GitLabBranchError):
    """Raised when branch protection operations fail."""

    def __init__(self, cause: Exception | None = None) -> None:
        """Initialize with standard error message and optional cause.

        Args:
            cause: The original exception that caused this error.
        """
        message = "Failed to modify branch protection in GitLab repository"
        if cause:
            super().__init__(f"{message}: {cause}", getattr(cause, "code", None))
        else:
            super().__init__(message)


class MergedBranchesDeleteError(GitLabBranchError):
    """Raised when deleting merged branches fails."""

    def __init__(self, cause: Exception | None = None) -> None:
        """Initialize with standard error message and optional cause.

        Args:
            cause: The original exception that caused this error.
        """
        message = "Failed to delete merged branches in GitLab repository"
        if cause:
            super().__init__(f"{message}: {cause}", getattr(cause, "code", None))
        else:
            super().__init__(message)
