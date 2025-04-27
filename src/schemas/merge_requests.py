"""Schema definitions for GitLab merge requests."""

from datetime import datetime
from enum import Enum
from typing import Any, ClassVar

from src.schemas.base import BaseModel, BaseResponseList


class MergeStatus(str, Enum):
    """Enum for merge request statuses."""

    UNCHECKED = "unchecked"
    CHECKING = "checking"
    CAN_BE_MERGED = "can_be_merged"
    CANNOT_BE_MERGED = "cannot_be_merged"
    CANNOT_BE_MERGED_RECHECK = "cannot_be_merged_recheck"


class MergeRequestState(str, Enum):
    """Enum for merge request states."""

    OPENED = "opened"
    CLOSED = "closed"
    LOCKED = "locked"
    MERGED = "merged"
    ALL = "all"


class DiffRefs(BaseModel):
    """Diff references model."""

    base_sha: str
    head_sha: str
    start_sha: str


class CreateMergeRequestInput(BaseModel):
    """Input model for creating a merge request in a GitLab repository."""

    project_path: str
    source_branch: str
    target_branch: str
    title: str
    description: str | None = None
    labels: list[str] | None = None
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
    target_branch: str
    source_branch: str
    web_url: str
    merge_status: MergeStatus | None = None
    merge_commit_sha: str | None = None
    squash_commit_sha: str | None = None
    sha: str | None = None
    merge_after: str | None = None
    labels: ClassVar[list[str]] = []
    diff_refs: DiffRefs | None = None
    draft: bool = False


class ListMergeRequestsInput(BaseModel):
    """Input model for listing merge requests in a GitLab repository."""

    project_path: str
    state: MergeRequestState | None = None
    labels: list[str] | None = None
    source_branch: str | None = None
    target_branch: str | None = None
    page: int = 1
    per_page: int = 20


class GitLabMergeRequestListResponse(BaseResponseList[GitLabMergeRequest]):
    """Response model for listing GitLab merge requests."""

    pass


class GetMergeRequestInput(BaseModel):
    """Input model for getting a specific merge request from a GitLab repository."""

    project_path: str
    mr_iid: int


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


class MergeRequestChanges(BaseModel):
    """Response model for merge request changes."""

    id: int
    iid: int
    project_id: int
    title: str
    changes: list[dict[str, Any]]
    overflow: bool = False
