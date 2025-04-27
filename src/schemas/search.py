"""Search schemas for GitLab search API.

This module defines Pydantic models for GitLab search functionality.
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SearchScope(str, Enum):
    """Enumeration of valid search scopes in GitLab."""

    PROJECTS = "projects"
    ISSUES = "issues"
    MERGE_REQUESTS = "merge_requests"
    MILESTONES = "milestones"
    USERS = "users"
    COMMITS = "commits"
    BLOBS = "blobs"
    WIKI_BLOBS = "wiki_blobs"
    NOTES = "notes"


class BlobSearchFilters(BaseModel):
    """Filters for blob search.

    These filters are available only for Premium/Ultimate tier.
    """

    filename: str | None = None
    path: str | None = None
    extension: str | None = None


class SearchRequest(BaseModel):
    """Base search request model for GitLab API."""

    scope: SearchScope = Field(
        ..., description="The scope to search in. Determines the type of results."
    )
    search: str = Field(
        ..., description="The search query to use. Must be at least 3 characters."
    )

    @field_validator("search")
    @classmethod
    def validate_search_length(cls, v: str) -> str:
        """Validate search query length.

        Args:
            v: The search query string.

        Returns:
            The validated search query.

        Raises:
            ValueError: If search query is less than 3 characters.
        """
        if len(v) < 3:
            raise ValueError("Search query must be at least 3 characters")
        return v


class GlobalSearchRequest(SearchRequest):
    """Search request for global GitLab search."""

    pass


class GroupSearchRequest(SearchRequest):
    """Search request for group-specific search."""

    group_id: str = Field(..., description="The ID or URL-encoded path of the group")


class ProjectSearchRequest(SearchRequest):
    """Search request for project-specific search."""

    project_id: str = Field(
        ..., description="The ID or URL-encoded path of the project"
    )
    ref: str | None = Field(
        None, description="The branch or tag to search in (for blobs/commits)"
    )


class SearchResult(BaseModel):
    """Base class for search results."""

    pass


class ProjectSearchResult(SearchResult):
    """Project search result model."""

    id: int
    name: str
    description: str | None = None
    name_with_namespace: str
    path: str
    path_with_namespace: str
    created_at: str
    default_branch: str
    topics: list[str] = []
    ssh_url_to_repo: str
    http_url_to_repo: str
    web_url: str
    readme_url: str | None = None
    avatar_url: str | None = None
    star_count: int
    forks_count: int
    last_activity_at: str


class UserSearchResult(SearchResult):
    """User search result model."""

    id: int
    name: str
    username: str
    state: str
    avatar_url: str
    web_url: str


class IssueSearchResult(SearchResult):
    """Issue search result model."""

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: Literal["opened", "closed"]
    created_at: str
    updated_at: str
    closed_at: str | None = None
    labels: list[str] = []
    milestone: dict | None = None
    assignees: list[dict] = []
    author: dict
    assignee: dict | None = None
    user_notes_count: int
    upvotes: int
    downvotes: int
    due_date: str | None = None
    confidential: bool
    discussion_locked: bool | None = None
    web_url: str
    time_stats: dict


class BlobSearchResult(SearchResult):
    """Blob search result model for file content."""

    basename: str
    data: str
    path: str
    filename: str
    id: str | None = None
    ref: str
    startline: int
    project_id: int


class CommitSearchResult(SearchResult):
    """Commit search result model."""

    id: str
    short_id: str
    title: str
    created_at: str
    message: str
    author_name: str
    author_email: str
    authored_date: str
    committer_name: str
    committer_email: str
    committed_date: str
    project_id: int


class MergeRequestSearchResult(SearchResult):
    """Merge request search result model."""

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: str
    created_at: str
    updated_at: str
    target_branch: str
    source_branch: str
    author: dict
    assignee: dict | None = None
    assignees: list[dict] = []
    reviewer: dict | None = None
    reviewers: list[dict] = []
    source_project_id: int
    target_project_id: int
    web_url: str


class MilestoneSearchResult(SearchResult):
    """Milestone search result model."""

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: str
    created_at: str
    updated_at: str
    due_date: str | None = None
    start_date: str | None = None
    web_url: str


class NoteSearchResult(SearchResult):
    """Note (comment) search result model."""

    id: int
    body: str
    author: dict
    created_at: str
    updated_at: str
    noteable_type: str
    noteable_id: int
    project_id: int


class SearchResponse(BaseModel):
    """Generic search response containing results of different types."""

    projects: list[ProjectSearchResult] = []
    issues: list[IssueSearchResult] = []
    merge_requests: list[MergeRequestSearchResult] = []
    milestones: list[MilestoneSearchResult] = []
    users: list[UserSearchResult] = []
    commits: list[CommitSearchResult] = []
    blobs: list[BlobSearchResult] = []
    wiki_blobs: list[BlobSearchResult] = []
    notes: list[NoteSearchResult] = []
