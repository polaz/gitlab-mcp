"""Exceptions for GitLab file operations.

This module contains exception classes specific to GitLab file operations.
"""

from .base import GitLabAPIError


class GitLabFileError(GitLabAPIError):
    """Base exception for GitLab file errors.

    Attributes:
        message: The error message.
        cause: The original exception that caused this error.
    """

    def __init__(
        self,
        message: str = "GitLab file operation failed",
        cause: Exception | None = None,
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            cause: The original exception that caused this error.
        """
        super().__init__(message=message)
        self.cause = cause


class FileContentError(GitLabFileError):
    """Exception for errors retrieving file content.

    Attributes:
        message: The error message.
        cause: The original exception that caused this error.
    """

    def __init__(
        self,
        message: str = "Failed to get file content",
        cause: Exception | None = None,
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            cause: The original exception that caused this error.
        """
        super().__init__(message=message, cause=cause)


class FileCreateError(GitLabFileError):
    """Exception for errors creating files.

    Attributes:
        message: The error message.
        cause: The original exception that caused this error.
    """

    def __init__(
        self, message: str = "Failed to create file", cause: Exception | None = None
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            cause: The original exception that caused this error.
        """
        super().__init__(message=message, cause=cause)


class FileUpdateError(GitLabFileError):
    """Exception for errors updating files.

    Attributes:
        message: The error message.
        cause: The original exception that caused this error.
    """

    def __init__(
        self, message: str = "Failed to update file", cause: Exception | None = None
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            cause: The original exception that caused this error.
        """
        super().__init__(message=message, cause=cause)


class FileDeleteError(GitLabFileError):
    """Exception for errors deleting files.

    Attributes:
        message: The error message.
        cause: The original exception that caused this error.
    """

    def __init__(
        self, message: str = "Failed to delete file", cause: Exception | None = None
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            cause: The original exception that caused this error.
        """
        super().__init__(message=message, cause=cause)


class FileBlameError(GitLabFileError):
    """Exception for errors retrieving file blame information.

    Attributes:
        message: The error message.
        cause: The original exception that caused this error.
    """

    def __init__(
        self,
        message: str = "Failed to get file blame information",
        cause: Exception | None = None,
    ):
        """Initialize the exception.

        Args:
            message: The error message.
            cause: The original exception that caused this error.
        """
        super().__init__(message=message, cause=cause)
