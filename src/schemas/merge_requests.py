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
    """Input model for creating a merge request in a GitLab repository.

    Creates a new merge request to propose changes from one branch to another.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        source_branch: Name of the branch containing changes (REQUIRED).
                      This branch will be merged into the target branch.
                      Examples: 'feature/new-login', 'bugfix/auth-issue', 'main'
        target_branch: Name of the branch to merge changes into (REQUIRED).
                      Usually 'main', 'master', 'develop', or a release branch.
                      Examples: 'main', 'develop', 'release/v2.0'
        title: Title of the merge request (REQUIRED).
              Should be descriptive and concise.
              Examples: 'Add user authentication', 'Fix login bug', 'Feature: Dark mode'
        description: Detailed description of the changes (OPTIONAL).
                    Supports GitLab Flavored Markdown.
                    Can include checklists, references to issues, etc.
        labels: List of label names to apply (OPTIONAL).
               Labels must exist in the project or group.
               Examples: ['bug', 'frontend'], ['enhancement', 'priority::high']
        remove_source_branch: Delete source branch after merge (OPTIONAL).
                             true = delete branch, false = keep branch (default)
        allow_collaboration: Allow target project maintainers to push to source branch (OPTIONAL).
                            Only relevant for merge requests from forks.
        squash: Squash commits into single commit when merging (OPTIONAL).
               true = squash commits, false = preserve individual commits
        merge_after: ISO 8601 datetime to schedule automatic merge (OPTIONAL).
                    Examples: '2024-01-15T10:00:00Z'

    Example Usage:
        - Simple MR: project_path='my/project', source_branch='feature', target_branch='main', title='New feature'
        - With labels: project_path='team/app', source_branch='fix', target_branch='main', title='Bug fix', labels=['bug']
    """

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
    """Input model for listing merge requests in a GitLab repository.

    Retrieves a paginated list of merge requests with optional filtering.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        state: Filter merge requests by state (OPTIONAL).
              Values: OPENED, CLOSED, MERGED, LOCKED, ALL
              Default: Returns all merge requests regardless of state.
        labels: List of label names to filter by (OPTIONAL).
               Only returns MRs that have ALL specified labels.
               Examples: ['bug'], ['enhancement', 'frontend']
        source_branch: Filter by source branch name (OPTIONAL).
                      Examples: 'feature/login', 'bugfix/auth'
        target_branch: Filter by target branch name (OPTIONAL).
                      Examples: 'main', 'develop', 'release/v2.0'
        page: Page number for pagination (starts at 1).
        per_page: Number of merge requests per page (1-100, default 20).

    Example Usage:
        - List all open MRs: project_path='my/project', state=MergeRequestState.OPENED
        - List MRs to main: project_path='my/project', target_branch='main'
        - List bug fixes: project_path='my/project', labels=['bug']
    """

    project_path: str
    state: MergeRequestState | None = None
    labels: list[str] | None = None
    source_branch: str | None = None
    target_branch: str | None = None
    page: int = 1
    per_page: int = 20


class GitLabMergeRequestListResponse(BaseResponseList[GitLabMergeRequest]):
    """Response model for listing GitLab merge requests."""



class GetMergeRequestInput(BaseModel):
    """Input model for getting a specific merge request from a GitLab repository.

    Retrieves detailed information about a specific merge request.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        mr_iid: The internal merge request ID within the project (REQUIRED).
               This is the MR number you see in GitLab UI (e.g., !123).
               NOT the global MR ID - use the project-specific MR number.
               Example: 42 for merge request !42 in the project.

    Example Usage:
        - Get MR !15: project_path='my-group/my-project', mr_iid=15
    """

    project_path: str
    mr_iid: int


class UpdateMergeRequestInput(BaseModel):
    """Input model for updating a merge request in GitLab.

    Updates properties of an existing merge request. Only provided fields will be changed.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        mr_iid: The internal merge request ID to update (REQUIRED).
               This is the MR number shown in GitLab UI (e.g., !123).
               Example: 42 for merge request !42.
        title: New title for the merge request (OPTIONAL).
              Examples: 'Updated feature implementation', 'Fix: Authentication bug'
        description: New description for the merge request (OPTIONAL).
                    Supports GitLab Flavored Markdown.
                    Pass empty string to clear description.
        target_branch: Change the target branch (OPTIONAL).
                      Examples: 'main', 'develop', 'release/v2.0'
        assignee_ids: List of user IDs to assign as assignees (OPTIONAL).
                     Replaces existing assignees.
                     Examples: [123, 456], [] (to clear assignees)
        reviewer_ids: List of user IDs to assign as reviewers (OPTIONAL).
                     Replaces existing reviewers.
                     Examples: [789, 101], [] (to clear reviewers)
        labels: List of label names to replace existing labels (OPTIONAL).
               Replaces ALL existing labels.
               Examples: ['bug', 'frontend'], [] (to clear all labels)
        add_labels: List of label names to add to existing labels (OPTIONAL).
                   Keeps existing labels and adds these.
                   Examples: ['priority::high'], ['reviewed']
        remove_labels: List of label names to remove from existing labels (OPTIONAL).
                      Examples: ['wip'], ['needs-review']
        remove_source_branch: Delete source branch after merge (OPTIONAL).
        squash: Enable squashing commits when merged (OPTIONAL).
        discussion_locked: Lock discussions on the merge request (OPTIONAL).
        allow_collaboration: Allow target project maintainers to push (OPTIONAL).
        merge_after: ISO 8601 datetime for scheduled merge (OPTIONAL).

    Example Usage:
        - Update title: project_path='my/project', mr_iid=15, title='New title'
        - Add reviewers: project_path='my/project', mr_iid=15, reviewer_ids=[123, 456]
        - Add labels: project_path='my/project', mr_iid=15, add_labels=['reviewed']
    """

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
    """Input model for merging a merge request in GitLab.

    Merges an approved merge request into the target branch.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        mr_iid: The internal merge request ID to merge (REQUIRED).
               This is the MR number shown in GitLab UI (e.g., !123).
               Example: 42 for merge request !42.
        merge_commit_message: Custom commit message for merge commit (OPTIONAL).
                             If not provided, GitLab generates default message.
                             Examples: 'Merge branch feature/auth into main', 'Release v2.0'
        squash_commit_message: Custom commit message for squashed commit (OPTIONAL).
                              Only used if squashing is enabled.
                              Examples: 'Add user authentication feature'
        auto_merge: Enable auto-merge when conditions are met (OPTIONAL).
                   true = merge automatically when ready, false = merge immediately
        should_remove_source_branch: Delete source branch after merge (OPTIONAL).
                                   Overrides the merge request's default setting.
        sha: Expected SHA of the source branch HEAD (OPTIONAL).
            Used to ensure branch hasn't changed since review.
            Examples: 'a1b2c3d4e5f6789...' (40-character SHA)
        squash: Override the project's squash setting (OPTIONAL).
               true = squash commits, false = preserve commits

    IMPORTANT: The merge request must be in a mergeable state (approved, no conflicts, etc.)

    Example Usage:
        - Simple merge: project_path='my/project', mr_iid=15
        - Custom message: project_path='my/project', mr_iid=15, merge_commit_message='Release v1.0'
        - Squash and merge: project_path='my/project', mr_iid=15, squash=True
    """

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
    """Input model for creating a comment on a GitLab merge request.

    Adds a general comment to the merge request discussion.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        mr_iid: The internal merge request ID (REQUIRED).
               This is the MR number shown in GitLab UI (e.g., !123).
               Example: 42 for merge request !42.
        body: The content of the comment (REQUIRED).
             Supports GitLab Flavored Markdown.
             Examples: 'LGTM!', 'Please update the documentation', 'Great work!'

    Example Usage:
        - Add approval comment: project_path='my/project', mr_iid=15, body='LGTM! 👍'
        - Request changes: project_path='my/project', mr_iid=15, body='Please fix the linting errors'
    """

    project_path: str
    mr_iid: int
    body: str


class CreateMergeRequestThreadInput(BaseModel):
    """Input model for creating a thread (suggestion) on a GitLab merge request.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request.
        body: The content of the thread (should include suggestion block for suggestions).
        position_type: The type of position (usually 'text').
        base_sha: The base commit SHA.
        start_sha: The start commit SHA.
        head_sha: The head commit SHA.
        old_path: The old file path (for changes, required).
        new_path: The new file path (for changes, required).
        old_line: The line number in the old file (optional).
        new_line: The line number in the new file (optional).
    """

    project_path: str
    mr_iid: int
    body: str
    position_type: str
    base_sha: str
    start_sha: str
    head_sha: str
    old_path: str
    new_path: str
    old_line: int | None = None
    new_line: int | None = None

    @classmethod
    def validate_line(cls, values):
        if values.get("old_line") is None and values.get("new_line") is None:
            raise ValueError("At least one of old_line or new_line must be provided.")
        return values

    def to_position(self) -> dict[str, Any]:
        position = {
            "position_type": self.position_type,
            "base_sha": self.base_sha,
            "start_sha": self.start_sha,
            "head_sha": self.head_sha,
            "old_path": self.old_path,
            "new_path": self.new_path,
        }
        if self.old_line is not None:
            position["old_line"] = str(self.old_line)
        if self.new_line is not None:
            position["new_line"] = str(self.new_line)
        return position


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
