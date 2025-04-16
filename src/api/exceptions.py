class GitLabAPIError(Exception):
    """Custom exception for GitLab API errors with actionable messages."""

    def __init__(self, message: str, code: int | None = None) -> None:
        self.code = code
        super().__init__(message)


class GitLabAuthError(GitLabAPIError):
    """Raised when GitLab authentication fails due to missing or invalid credentials."""

    pass
