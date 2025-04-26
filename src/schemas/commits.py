# filepath: c:\Users\aditp\Desktop\python\gitlab-mcp-main\src\schemas\commits.py
"""Pydantic schemas for GitLab commit data structures."""

from datetime import datetime

from pydantic import BaseModel, Field

from .base import GitLabResponseBase


class GitLabCommitter(BaseModel):
    """GitLab committer information.

    Attributes:
        name: Name of the committer.
        email: Email of the committer.
    """

    name: str
    email: str


class GitLabCommit(BaseModel):
    """Detailed GitLab commit information.

    Attributes:
        id: Full commit SHA.
        short_id: Shortened commit SHA.
        title: Commit title (first line of commit message).
        message: Full commit message.
        author_name: Name of the commit author.
        author_email: Email of the commit author.
        authored_date: Date the commit was authored.
        committer_name: Name of the committer.
        committer_email: Email of the committer.
        committed_date: Date the commit was committed.
        created_at: Date the commit was created.
        parent_ids: List of parent commit SHAs.
        web_url: URL to view the commit.
    """

    id: str
    short_id: str
    title: str
    message: str
    author_name: str
    author_email: str | None = None
    authored_date: datetime | None = None
    committer_name: str | None = None
    committer_email: str | None = None
    committed_date: datetime | None = None
    created_at: str
    parent_ids: list[str] | None = None
    web_url: str | None = None


class GitLabCommitDetail(GitLabResponseBase):
    """Response model for GitLab commit details.

    Attributes:
        id: Full commit SHA.
        short_id: Shortened commit SHA.
        title: Commit title.
        message: Full commit message.
        author_name: Name of the commit author.
        committer_name: Name of the committer.
        created_at: Date the commit was created.
        stats: Commit statistics (additions, deletions).
    """

    id: str
    short_id: str
    title: str
    message: str
    author_name: str
    committer_name: str | None = None
    created_at: str
    stats: dict[str, int] | None = Field(default_factory=dict)
