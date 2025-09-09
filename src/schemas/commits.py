"""Pydantic schemas for GitLab commit data structures."""

from src.schemas.base import GitLabResponseBase


class GitLabCommitDetail(GitLabResponseBase):
    """Response model for GitLab commit details.

    Represents detailed information about a specific Git commit in a GitLab project.

    Attributes:
        id: The full 40-character SHA hash of the commit.
           Unique identifier for this commit across all Git repositories.
           Examples: 'a1b2c3d4e5f6789012345678901234567890abcd'
        short_id: The shortened commit SHA (usually first 8-12 characters).
                 More readable identifier commonly shown in UI.
                 Examples: 'a1b2c3d4', '1234567890ab'
        title: The first line of the commit message (subject line).
              Examples: 'Fix authentication bug', 'Add user registration feature'
        message: The complete commit message including title and body.
                May include multiple lines, descriptions, references, etc.
                Examples: 'Fix login\\n\\nResolves issue with OAuth provider'
        created_at: ISO 8601 timestamp when the commit was created.
                   Examples: '2024-01-15T10:30:00.000Z'
        stats: Optional commit statistics (additions, deletions, files changed).
              May be null if statistics weren't requested or calculated.

    Note: This model represents commit metadata, not the actual file changes.
    Use separate APIs to get commit diffs or file contents.
    """

    id: str
    short_id: str
    title: str
    message: str
    created_at: str
