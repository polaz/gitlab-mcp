"""Schema definitions for GitLab merge requests."""

from datetime import datetime
from enum import Enum
from typing import Any

from .base import BaseModel, BaseResponseList


class MergeStatus(str, Enum):
    """Enum for merge request statuses."""

    UNCHECKED = "unchecked"
    CHECKING = "checking"
    CAN_BE_MERGED = "can_be_merged"
    CANNOT_BE_MERGED = "cannot_be_merged"
    CANNOT_BE_MERGED_RECHECK = "cannot_be_merged_recheck"


class DetailedMergeStatus(str, Enum):
    """Enum for detailed merge request statuses."""

    CHECKING = "checking"
    UNCHECKED = "unchecked"
    CAN_BE_MERGED = "mergeable"
    NOT_OPEN = "not_open"
    CONFLICT = "conflict"
    CI_MUST_PASS = "ci_must_pass"
    CI_STILL_RUNNING = "ci_still_running"
    DISCUSSIONS_NOT_RESOLVED = "discussions_not_resolved"
    DRAFT_STATUS = "draft_status"
    JIRA_ASSOCIATION_MISSING = "jira_association_missing"
    MERGE_REQUEST_BLOCKED = "merge_request_blocked"
    NEED_REBASE = "need_rebase"
    NOT_APPROVED = "not_approved"
    PREPARING = "preparing"
    REQUESTED_CHANGES = "requested_changes"
    SECURITY_POLICY_VIOLATIONS = "security_policy_violations"
    STATUS_CHECKS_MUST_PASS = "status_checks_must_pass"
    COMMITS_STATUS = "commits_status"
    MERGE_TIME = "merge_time"


class MergeRequestState(str, Enum):
    """Enum for merge request states."""

    OPENED = "opened"
    CLOSED = "closed"
    LOCKED = "locked"
    MERGED = "merged"
    ALL = "all"


class UserInfo(BaseModel):
    """User information model."""

    id: int
    name: str
    username: str
    state: str
    avatar_url: str | None = None
    web_url: str


# Time statistics removed


class TaskCompletionStatus(BaseModel):
    """Task completion status model."""

    count: int = 0
    completed_count: int = 0


class MilestoneInfo(BaseModel):
    """Milestone information model."""

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: str
    created_at: datetime
    updated_at: datetime
    due_date: str | None = None
    start_date: str | None = None
    web_url: str


class PipelineInfo(BaseModel):
    """Pipeline information model."""

    id: int
    sha: str
    ref: str
    status: str
    web_url: str


class DiffRefs(BaseModel):
    """Diff references model."""

    base_sha: str
    head_sha: str
    start_sha: str


class MergeRequestReferences(BaseModel):
    """References model."""

    short: str
    relative: str
    full: str


class CreateMergeRequestInput(BaseModel):
    """Input model for creating a merge request in a GitLab repository."""

    project_path: str
    source_branch: str
    target_branch: str
    title: str
    description: str | None = None
    assignee_ids: list[int] | None = None
    reviewer_ids: list[int] | None = None
    labels: list[str] | None = None
    milestone_id: int | None = None
    remove_source_branch: bool | None = None
    allow_collaboration: bool | None = None
    squash: bool | None = None
    merge_after: str | None = None


class GitLabMergeRequest(BaseModel):
    """Response model for a GitLab merge request."""

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: str
    created_at: datetime
    updated_at: datetime
    target_branch: str
    source_branch: str
    web_url: str
    merge_status: MergeStatus | None = None
    detailed_merge_status: DetailedMergeStatus | None = None
    merged_at: datetime | None = None
    closed_at: datetime | None = None
    merge_commit_sha: str | None = None
    squash_commit_sha: str | None = None
    sha: str | None = None
    prepared_at: datetime | None = None
    merge_after: str | None = None

    # User related
    author: UserInfo | None = None
    assignees: list[UserInfo] | None = None
    reviewers: list[UserInfo] | None = None
    merge_user: UserInfo | None = None

    # Metrics
    user_notes_count: int | None = None
    upvotes: int | None = None
    downvotes: int | None = None

    # References
    references: MergeRequestReferences | None = None

    # Related objects
    source_project_id: int | None = None
    target_project_id: int | None = None
    labels: list[str] = []
    milestone: MilestoneInfo | None = None
    pipeline: PipelineInfo | None = None
    diff_refs: DiffRefs | None = None

    # Flags
    draft: bool = False
    work_in_progress: bool = False
    merge_when_pipeline_succeeds: bool = False
    should_remove_source_branch: bool | None = None
    force_remove_source_branch: bool | None = None
    squash: bool = False
    allow_collaboration: bool | None = None
    discussion_locked: bool | None = None
    has_conflicts: bool | None = None
    blocking_discussions_resolved: bool | None = None

    # Stats
    task_completion_status: TaskCompletionStatus | None = None
    changes_count: str | None = None
    diverged_commits_count: int | None = None


class ListMergeRequestsInput(BaseModel):
    """Input model for listing merge requests in a GitLab repository."""

    project_path: str
    state: MergeRequestState | None = None
    labels: list[str] | None = None
    milestone: str | None = None
    scope: str | None = None
    author_id: int | None = None
    assignee_id: int | None = None
    reviewer_id: int | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    search: str | None = None
    source_branch: str | None = None
    target_branch: str | None = None
    with_merge_status_recheck: bool | None = None
    order_by: str | None = None
    sort: str | None = None
    page: int = 1
    per_page: int = 20


class GitLabMergeRequestListResponse(BaseResponseList[GitLabMergeRequest]):
    """Response model for listing GitLab merge requests."""

    pass


class GetMergeRequestInput(BaseModel):
    """Input model for getting a specific merge request from a GitLab repository."""

    project_path: str
    mr_iid: int
    include_diverged_commits_count: bool | None = None
    include_rebase_in_progress: bool | None = None
    render_html: bool | None = None


class UpdateMergeRequestInput(BaseModel):
    """Input model for updating a merge request in GitLab."""

    project_path: str
    mr_iid: int
    title: str | None = None
    description: str | None = None
    target_branch: str | None = None
    assignee_ids: list[int] | None = None
    reviewer_ids: list[int] | None = None
    labels: list[str] | None = None
    add_labels: list[str] | None = None
    remove_labels: list[str] | None = None
    milestone_id: int | None = None
    state_event: str | None = None
    remove_source_branch: bool | None = None
    squash: bool | None = None
    discussion_locked: bool | None = None
    allow_collaboration: bool | None = None
    merge_after: str | None = None


class MergeMergeRequestInput(BaseModel):
    """Input model for merging a merge request in GitLab."""

    project_path: str
    mr_iid: int
    merge_commit_message: str | None = None
    squash_commit_message: str | None = None
    auto_merge: bool | None = None
    should_remove_source_branch: bool | None = None
    sha: str | None = None
    squash: bool | None = None


class AcceptedMergeRequest(GitLabMergeRequest):
    """Response model for an accepted merge request."""

    pass


class MergeRequestThread(BaseModel):
    """Response model for a merge request thread."""

    id: str
    body: str | None = None
    author: UserInfo
    created_at: datetime
    updated_at: datetime
    position: dict[str, Any] | None = None
    resolved: bool | None = None
    resolvable: bool | None = None


class MergeRequestSuggestion(BaseModel):
    """Response model for a merge request suggestion."""

    id: int
    from_line: int
    to_line: int
    applicable: bool
    applied: bool
    from_content: str
    to_content: str


class CreateMergeRequestCommentInput(BaseModel):
    """Input model for creating a comment on a GitLab merge request."""

    project_path: str
    mr_iid: int
    body: str


class CreateMergeRequestThreadInput(BaseModel):
    """Input model for creating a thread on a GitLab merge request."""

    project_path: str
    mr_iid: int
    body: str
    position: dict[str, Any]


class ApplySuggestionInput(BaseModel):
    """Input model for applying a suggestion in a GitLab merge request."""

    id: int
    commit_message: str | None = None


class ApplyMultipleSuggestionsInput(BaseModel):
    """Input model for applying multiple suggestions in a GitLab merge request."""

    ids: list[int]
    commit_message: str | None = None


class GitLabComment(BaseModel):
    """Response model for a GitLab comment."""

    id: int
    body: str
    author: UserInfo
    created_at: datetime
    updated_at: datetime | None = None


class MergeRequestChanges(BaseModel):
    """Response model for merge request changes."""

    id: int
    iid: int
    project_id: int
    title: str
    changes: list[dict[str, Any]]
    overflow: bool = False
