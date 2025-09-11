"""Search schemas for GitLab search API.

This module defines Pydantic models for GitLab search functionality.
"""

from enum import Enum
from typing import Any, ClassVar

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
    """Project search result model with optimized field ordering for Claude Code UX.

    CRITICAL: id and name are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ Project: {id: 42, name: "my-project", ...}
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    id: int = Field(..., description="Project ID (shows first in Claude Code)")
    name: str = Field(..., description="Project name (shows second in Claude Code)")

    # Other fields
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
    """Blob search result model for file content with enhanced context."""

    # Core file information
    basename: str = Field(..., description="Base filename")
    filename: str = Field(..., description="Full filename with extension")
    path: str = Field(..., description="Full file path in repository")

    # Content information
    data: str = Field(..., description="File content excerpt around match")
    startline: int = Field(..., description="Line number where match starts")

    # Context information
    id: str | None = Field(None, description="Blob ID")
    ref: str = Field(..., description="Git reference (branch/tag) where file was found")
    project_id: int | None = Field(None, description="Project ID containing the file")

    # Enhanced contextual fields
    project: dict[str, Any] | None = Field(None, description="Project information including name and namespace")
    blob_url: str | None = Field(None, description="Direct URL to view the blob")
    repository_url: str | None = Field(None, description="Repository URL")
    commit_id: str | None = Field(None, description="Latest commit ID for this file")
    file_size: int | None = Field(None, description="File size in bytes")
    language: str | None = Field(None, description="Detected programming language")
    binary: bool = Field(False, description="Whether the file is binary")


class IssueSearchResult(SearchResult):
    """Issue search result model with optimized field ordering for Claude Code UX.

    CRITICAL: iid and title are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ Issue: {iid: 42, title: "Feature X", ...}
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    iid: int = Field(..., description="Issue internal ID (shows first in Claude Code)")
    title: str = Field(..., description="Issue title (shows second in Claude Code)")

    # Other identification fields
    id: int
    project_id: int
    description: str | None = None
    state: str
    created_at: str
    updated_at: str
    web_url: str
    author: dict[str, Any] | None = None
    labels: list[str] = []
    assignees: list[dict[str, Any]] = []

    # Enhanced contextual fields
    project: dict[str, Any] | None = Field(None, description="Project information including name and namespace")
    milestone: dict[str, Any] | None = Field(None, description="Milestone information if assigned")
    closed_at: str | None = Field(None, description="Issue close date if closed")
    assignee: dict[str, Any] | None = Field(None, description="Primary assignee (legacy field)")
    confidential: bool = Field(False, description="Whether the issue is confidential")
    discussion_locked: bool = Field(False, description="Whether discussion is locked")
    due_date: str | None = Field(None, description="Issue due date if set")
    time_stats: dict[str, Any] | None = Field(None, description="Time tracking statistics")
    weight: int | None = Field(None, description="Issue weight for prioritization")
    upvotes: int = Field(0, description="Number of upvotes")
    downvotes: int = Field(0, description="Number of downvotes")
    user_notes_count: int = Field(0, description="Number of comments on the issue")


class MergeRequestSearchResult(SearchResult):
    """Merge request search result model with optimized field ordering for Claude Code UX.

    CRITICAL: iid and title are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ MergeRequest: {iid: 42, title: "Feature X", ...}
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    iid: int = Field(..., description="MR internal ID (shows first in Claude Code)")
    title: str = Field(..., description="MR title (shows second in Claude Code)")

    # Other identification fields
    id: int
    project_id: int
    description: str | None = None
    state: str
    created_at: str
    updated_at: str
    web_url: str
    author: dict[str, Any] | None = None
    labels: list[str] = []
    assignees: list[dict[str, Any]] = []
    source_branch: str | None = None
    target_branch: str | None = None

    # Enhanced contextual fields
    project: dict[str, Any] | None = Field(None, description="Project information including name and namespace")
    milestone: dict[str, Any] | None = Field(None, description="Milestone information if assigned")
    merged_at: str | None = Field(None, description="Merge date if merged")
    closed_at: str | None = Field(None, description="Close date if closed")
    assignee: dict[str, Any] | None = Field(None, description="Primary assignee (legacy field)")
    merge_status: str | None = Field(None, description="Merge status (can_be_merged, cannot_be_merged, etc.)")
    merge_when_pipeline_succeeds: bool = Field(False, description="Auto-merge when pipeline succeeds")
    draft: bool = Field(False, description="Whether the MR is a draft")
    work_in_progress: bool = Field(False, description="Whether marked as work in progress")
    squash: bool = Field(False, description="Whether to squash commits when merging")
    discussion_locked: bool = Field(False, description="Whether discussion is locked")
    should_remove_source_branch: bool = Field(False, description="Whether to delete source branch after merge")
    force_remove_source_branch: bool = Field(False, description="Force remove source branch")
    allow_collaboration: bool = Field(False, description="Allow commits from members of target project")
    allow_maintainer_to_push: bool = Field(False, description="Allow maintainer to push to source branch")
    squash_commit_sha: str | None = Field(None, description="SHA of squash commit if squashed")
    merge_commit_sha: str | None = Field(None, description="SHA of merge commit if merged")
    upvotes: int = Field(0, description="Number of upvotes")
    downvotes: int = Field(0, description="Number of downvotes")
    user_notes_count: int = Field(0, description="Number of comments on the MR")
    changes_count: str | None = Field(None, description="Summary of changes (additions/deletions)")
    pipeline: dict[str, Any] | None = Field(None, description="Latest pipeline information")
    head_pipeline: dict[str, Any] | None = Field(None, description="Head pipeline information")
    diff_refs: dict[str, Any] | None = Field(None, description="Diff reference information")
    merge_error: str | None = Field(None, description="Error message if merge failed")
    rebase_in_progress: bool = Field(False, description="Whether rebase is in progress")
    diverged_commits_count: int = Field(0, description="Number of commits target is ahead")
    time_stats: dict[str, Any] | None = Field(None, description="Time tracking statistics")


class CommitSearchResult(SearchResult):
    """Commit search result model with enhanced context.

    CRITICAL: short_id and title are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ Commit: {short_id: "abc12345", title: "Fix bug in auth", ...}
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    short_id: str = Field(..., description="Short commit SHA (shows first in Claude Code)")
    title: str = Field(..., description="Commit title/subject (shows second in Claude Code)")

    # Other identification fields
    id: str = Field(..., description="Full commit SHA")
    message: str = Field(..., description="Full commit message")
    created_at: str = Field(..., description="Commit creation timestamp")

    # Author information
    author_name: str | None = Field(None, description="Commit author name")
    author_email: str | None = Field(None, description="Commit author email")

    # Context information
    web_url: str | None = Field(None, description="URL to view commit in GitLab")
    project_id: int | None = Field(None, description="Project ID containing the commit")

    # Enhanced contextual fields
    project: dict[str, Any] | None = Field(None, description="Project information including name and namespace")
    committer_name: str | None = Field(None, description="Committer name if different from author")
    committer_email: str | None = Field(None, description="Committer email if different from author")
    committed_date: str | None = Field(None, description="Commit date (may differ from created_at)")
    authored_date: str | None = Field(None, description="Author date (may differ from created_at)")
    parent_ids: list[str] = Field([], description="Parent commit SHAs")
    stats: dict[str, Any] | None = Field(None, description="Commit statistics (additions, deletions, total)")
    pipeline: dict[str, Any] | None = Field(None, description="Associated pipeline information")
    trailers: dict[str, Any] | None = Field(None, description="Git trailers (Signed-off-by, etc.)")
    extended_trailers: dict[str, Any] | None = Field(None, description="Extended trailer information")
    last_pipeline: dict[str, Any] | None = Field(None, description="Last pipeline status")


class MilestoneSearchResult(SearchResult):
    """Milestone search result model with optimized field ordering for Claude Code UX.

    CRITICAL: id and title are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ Milestone: {id: 42, title: "v2.0 Release", ...}
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    id: int = Field(..., description="Milestone ID (shows first in Claude Code)")
    title: str = Field(..., description="Milestone title (shows second in Claude Code)")

    # Other fields
    iid: int | None = None
    description: str | None = None
    state: str
    created_at: str
    updated_at: str
    web_url: str | None = None
    project_id: int | None = None
    group_id: int | None = None


class NoteSearchResult(SearchResult):
    """Note/comment search result model with enhanced context.

    CRITICAL: id and body are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ Note: {id: 42, body: "This looks good to me...", ...}
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    id: int = Field(..., description="Note ID (shows first in Claude Code)")
    body: str = Field(..., description="Note content (shows second in Claude Code)")

    # Basic fields
    created_at: str = Field(..., description="Note creation timestamp")
    updated_at: str = Field(..., description="Note last update timestamp")
    author: dict[str, Any] | None = Field(None, description="Note author information")

    # Context information
    noteable_type: str | None = Field(None, description="Type of object the note is attached to (Issue, MergeRequest, etc.)")
    noteable_id: int | None = Field(None, description="ID of the object the note is attached to")

    # Enhanced contextual fields
    project: dict[str, Any] | None = Field(None, description="Project information including name and namespace")
    noteable: dict[str, Any] | None = Field(None, description="Full information about the object being commented on")
    system: bool = Field(False, description="Whether this is a system-generated note")
    resolvable: bool = Field(False, description="Whether the note can be resolved")
    resolved: bool = Field(False, description="Whether the note has been resolved")
    resolved_by: dict[str, Any] | None = Field(None, description="User who resolved the note")
    resolved_at: str | None = Field(None, description="When the note was resolved")
    confidential: bool = Field(False, description="Whether the note is confidential")
    internal: bool = Field(False, description="Whether the note is internal only")
    web_url: str | None = Field(None, description="URL to view the note in GitLab")
    commands_changes: dict[str, Any] | None = Field(None, description="Quick actions applied by this note")
    attachment: dict[str, Any] | None = Field(None, description="File attachment information")
    type: str | None = Field(None, description="Note type (DiscussionNote, etc.)")


class SearchResponse(BaseModel):
    """Generic search response containing only project and blob results."""

    projects: list[ProjectSearchResult] = []
    blobs: list[BlobSearchResult] = []
    wiki_blobs: list[BlobSearchResult] = []
