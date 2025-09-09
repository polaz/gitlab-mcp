"""Search schemas for GitLab search API.

This module defines Pydantic models for GitLab search functionality.
"""

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator


class SearchScope(str, Enum):
    """Enumeration of valid search scopes in GitLab.

    Defines what types of content can be searched across GitLab.

    Attributes:
        PROJECTS: Search for projects by name, description, or path.
        BLOBS: Search within file contents (requires Premium/Ultimate).
        WIKI_BLOBS: Search within wiki page contents.
        COMMITS: Search commit messages and content.
        ISSUES: Search issue titles and descriptions.
        MERGE_REQUESTS: Search merge request titles and descriptions.
        MILESTONES: Search milestone titles and descriptions.
        NOTES: Search comments/notes on issues and merge requests.
    """

    PROJECTS = "projects"
    BLOBS = "blobs"
    WIKI_BLOBS = "wiki_blobs"
    COMMITS = "commits"
    ISSUES = "issues"
    MERGE_REQUESTS = "merge_requests"
    MILESTONES = "milestones"
    NOTES = "notes"


class BlobSearchFilters(BaseModel):
    """Filters for blob search (Premium/Ultimate tier only).

    Advanced filters to narrow down file content searches.

    Attributes:
        filename: Filter by specific filename pattern (OPTIONAL).
                 Examples: 'config.json', '*.py', 'README*'
        path: Filter by file path pattern (OPTIONAL).
             Examples: 'src/', 'tests/**', 'docs/api/'
        extension: Filter by file extension (OPTIONAL).
                  Examples: 'py', 'js', 'md', 'json'

    Note: These filters are only available with GitLab Premium or Ultimate subscriptions.
    """

    filename: str | None = None
    path: str | None = None
    extension: str | None = None


class SearchRequest(BaseModel):
    """Base search request model for GitLab API."""

    MIN_SEARCH_LENGTH: ClassVar[int] = 3
    scope: SearchScope = Field(
        ..., description="The scope to search in. Determines the type of results.",
    )
    search: str = Field(
        ..., description="The search query to use. Must be at least 3 characters.",
    )

    @field_validator("search")
    @classmethod
    def validate_search_length(cls, v: str) -> str:
        if len(v) < cls.MIN_SEARCH_LENGTH:
            raise ValueError(
                f"Search query must be at least {cls.MIN_SEARCH_LENGTH} characters",
            )
        return v


class GlobalSearchRequest(SearchRequest):
    """Search request for global GitLab search.

    Searches across all GitLab content that the user has access to.
    This includes public projects and any private projects the user is a member of.

    Example Usage:
        - Search all projects: scope=SearchScope.PROJECTS, search='my-app'
        - Search all issues: scope=SearchScope.ISSUES, search='authentication bug'

    Note: Results are limited by user permissions and GitLab's search limits.
    """



class GroupSearchRequest(SearchRequest):
    """Search request for group-specific search.

    Searches within a specific group and its subgroups/projects.
    More focused than global search, faster results.

    Attributes:
        group_id: The numeric ID OR path of the group to search within (REQUIRED).
                 Examples: '42', 'my-group', 'parent/subgroup'

    Example Usage:
        - Search group projects: group_id='my-team', scope=SearchScope.PROJECTS, search='api'
        - Search group issues: group_id='123', scope=SearchScope.ISSUES, search='bug'
    """

    group_id: str = Field(..., description="The numeric ID or URL-encoded path of the group")


class ProjectSearchRequest(SearchRequest):
    """Search request for project-specific search.

    Searches within a specific project only.
    Most focused search scope, fastest results.

    Attributes:
        project_id: The numeric ID OR full path of the project to search (REQUIRED).
                   Examples: '12345', 'gitlab-org/gitlab', 'my-group/my-project'
        ref: The branch or tag to search within (OPTIONAL).
            Only applies to blob and commit searches.
            Examples: 'main', 'develop', 'v1.0.0', 'feature/auth'
            Default: searches default branch.

    Example Usage:
        - Search project code: project_id='my/project', scope=SearchScope.BLOBS, search='function auth'
        - Search specific branch: project_id='my/project', scope=SearchScope.BLOBS, search='TODO', ref='develop'
        - Search project issues: project_id='123', scope=SearchScope.ISSUES, search='login bug'
    """

    project_id: str = Field(
        ..., description="The numeric ID or URL-encoded full path of the project",
    )
    ref: str | None = Field(
        None, description="The branch or tag to search in (for blobs/commits). Defaults to default branch.",
    )


class SearchResult(BaseModel):
    """Base class for search results."""



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


class SearchResponse(BaseModel):
    """Generic search response containing only project and blob results."""

    projects: list[ProjectSearchResult] = []
    blobs: list[BlobSearchResult] = []
    wiki_blobs: list[BlobSearchResult] = []
