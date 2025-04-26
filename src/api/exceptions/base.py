# filepath: c:\Users\aditp\Desktop\python\gitlab-mcp-main\src\api\exceptions\base.py
"""Base exception classes for GitLab API errors."""


class GitLabAPIError(Exception):
    """Custom exception for GitLab API errors with actionable messages."""

    def __init__(self, message: str, code: int | None = None) -> None:
        """Initialize the GitLab API error.

        Args:
            message: A descriptive error message.
            code: Optional HTTP status code.
        """
        self.code = code
        super().__init__(message)


class GitLabAuthError(GitLabAPIError):
    """Raised when GitLab authentication fails due to missing or invalid credentials."""

    pass
