"""Schema models for GitLab issues."""

from enum import Enum

from pydantic import BaseModel

from src.schemas.base import GitLabResponseBase, PaginatedResponse


class IssueType(str, Enum):
    """Types of GitLab issues.

    Attributes:
        ISSUE: Standard issue.
        INCIDENT: Incident issue type.
        TEST_CASE: Test case issue type.
        TASK: Task issue type.
    """

    ISSUE = "issue"
    INCIDENT = "incident"
    TEST_CASE = "test_case"
    TASK = "task"


class IssueSeverity(str, Enum):
    """Severity levels for GitLab issues.

    Attributes:
        UNKNOWN: Unknown severity.
        LOW: Low severity.
        MEDIUM: Medium severity.
        HIGH: High severity.
        CRITICAL: Critical severity.
    """

    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IssueState(str, Enum):
    """State of GitLab issues.

    Attributes:
        OPENED: Issue is open.
        CLOSED: Issue is closed.
        ALL: All issue states.
    """

    OPENED = "opened"
    CLOSED = "closed"
    ALL = "all"


class GitLabIssue(GitLabResponseBase):
    """Simplified response model for a GitLab issue.

    Attributes:
        id: The unique identifier of the issue.
        iid: The internal ID of the issue within the project.
        project_id: The ID of the project the issue belongs to.
        title: The title of the issue.
        description: The description of the issue.
        state: The state of the issue (opened or closed).
        web_url: The web URL of the issue.
        labels: List of labels associated with the issue.
        _links: Links related to the issue.
    """

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: str
    web_url: str
    labels: list[str] | None = None


class CreateIssueInput(BaseModel):
    """Input model for creating a new issue in a GitLab project.

    Attributes:
        project_path: The full namespace path of the project (REQUIRED).
                     Must include the complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        title: The title of the issue (REQUIRED).
               Should be descriptive and concise.
               Example: 'Fix authentication bug in login form'
        description: The detailed description of the issue (OPTIONAL).
                    Supports GitLab Flavored Markdown.
                    Example: 'Steps to reproduce:\n1. Go to login page\n2. Enter invalid credentials'
        labels: List of label names to apply to the issue (OPTIONAL).
               Each label must exist in the project or group.
               Examples: ['bug', 'priority::high'], ['enhancement', 'frontend']

    Example Usage:
        - Create a bug report: project_path='my/project', title='Login fails', labels=['bug']
    """

    project_path: str
    title: str
    description: str | None = None
    labels: list[str] | None = None


class GetIssueInput(BaseModel):
    """Input model for getting a specific issue from a GitLab repository.

    This tool retrieves a single issue by its internal issue ID within a specific project.

    Attributes:
        project_path: The full namespace path of the project (REQUIRED).
                     Must include the complete path including group/subgroup.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project', 'user/repo'
                     This is the path you see in the GitLab URL, not just the project name.
        issue_iid: The internal issue ID within the project (REQUIRED).
                  This is the issue number you see in the GitLab UI (e.g., #123).
                  NOT the global issue ID - use the project-specific issue number.
                  Example: 42 for issue #42 in the project.

    Example Usage:
        - Get issue #15 from 'my-group/my-project':
          project_path='my-group/my-project', issue_iid=15
    """

    project_path: str
    issue_iid: int


class DeleteIssueInput(BaseModel):
    """Input model for deleting an issue from a GitLab repository.

    WARNING: This permanently deletes the issue and cannot be undone.

    Attributes:
        project_path: The full namespace path of the project (REQUIRED).
                     Must include the complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        issue_iid: The internal issue ID within the project (REQUIRED).
                  This is the issue number shown in GitLab UI (e.g., #123).
                  Example: 42 for issue #42 in the project.

    Example Usage:
        - Delete issue #15: project_path='my-group/project', issue_iid=15
    """

    project_path: str
    issue_iid: int


class MoveIssueInput(BaseModel):
    """Input model for moving an issue to a different project.

    Moves an issue from one project to another. The issue will get a new issue_iid in the target project.

    Attributes:
        project_path: The full namespace path of the SOURCE project (REQUIRED).
                     Must include the complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/old-project'
        issue_iid: The internal issue ID within the SOURCE project (REQUIRED).
                  This is the issue number in the source project (e.g., #123).
                  Example: 42 for issue #42 in the source project.
        to_project_id: The numeric ID of the TARGET project (REQUIRED).
                      This must be the numeric project ID, not the path.
                      You can get this from the project details or GitLab UI.
                      Example: 12345

    Example Usage:
        - Move issue #15 from 'old/project' to project ID 999:
          project_path='old/project', issue_iid=15, to_project_id=999
    """

    project_path: str
    issue_iid: int
    to_project_id: int


class CreateIssueCommentInput(BaseModel):
    """Input model for creating a comment on a GitLab issue.

    Adds a new comment to an existing issue.

    Attributes:
        project_path: The full namespace path of the project (REQUIRED).
                     Must include the complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        issue_iid: The internal issue ID within the project (REQUIRED).
                  This is the issue number shown in GitLab UI (e.g., #123).
                  Example: 42 for issue #42 in the project.
        body: The content of the comment (REQUIRED).
             Supports GitLab Flavored Markdown.
             Example: 'This is fixed in the latest commit.'

    Example Usage:
        - Add comment to issue #15:
          project_path='my/project', issue_iid=15, body='Thanks for the report!'
    """

    project_path: str
    issue_iid: int
    body: str


class ListIssueCommentsInput(BaseModel):
    """Input model for listing comments on a GitLab issue.

    Retrieves all comments/notes on a specific issue in chronological order.

    Attributes:
        project_path: The full namespace path of the project (REQUIRED).
                     Must include the complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        issue_iid: The internal issue ID within the project (REQUIRED).
                  This is the issue number shown in GitLab UI (e.g., #123).
                  Example: 42 for issue #42 in the project.
        page: Page number for pagination (starts at 1).
        per_page: Number of comments per page (1-100, default 20).

    Example Usage:
        - Get all comments on issue #15:
          project_path='my-group/project', issue_iid=15
    """

    project_path: str
    issue_iid: int
    page: int = 1
    per_page: int = 20


class ListIssuesInput(BaseModel):
    """Input model for listing issues in a GitLab project or globally.

    Retrieves a paginated list of issues with optional filtering.
    If project_path is provided, lists issues from that specific project.
    If project_path is not provided, lists all issues the user has access to globally.

    Attributes:
        project_path: The full namespace path of the project (OPTIONAL).
                     Must include the complete group/subgroup path when provided.
                     Examples: 'gitlab-org/gitlab', 'my-group/subgroup/project'
                     If not provided, searches globally across all accessible issues.
        state: Filter issues by state (OPTIONAL).
               Valid values: 'opened', 'closed', 'all'
               Default: Returns all issues regardless of state.
        labels: Comma-separated list of label names to filter by (OPTIONAL).
               Examples: 'bug', 'bug,enhancement', 'priority::high'
               Only returns issues that have ALL specified labels.
        confidential: Filter for confidential issues only (OPTIONAL).
                     true = only confidential, false = only non-confidential, null = both
        page: Page number for pagination (starts at 1).
        per_page: Number of issues per page (1-100, default 20).

    Example Usage:
        - List all open bugs in project: project_path='my-org/project', state='opened', labels='bug'
        - List all issues in project: project_path='group/project'
        - List all global issues: (no project_path specified)
    """

    project_path: str | None = None
    state: str | None = None
    labels: str | None = None
    confidential: bool | None = None
    page: int = 1
    per_page: int = 20


class UpdateIssueInput(BaseModel):
    """Input model for updating an existing issue in a GitLab project.

    Updates properties of an existing issue. Only provided fields will be changed.

    Attributes:
        project_path: The full namespace path of the project (REQUIRED).
                     Must include the complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        issue_iid: The internal issue ID to update (REQUIRED).
                  This is the issue number shown in GitLab UI (e.g., #123).
                  Example: 42 for issue #42.
        title: New title for the issue (OPTIONAL).
              Examples: 'Updated feature request', 'Fix: Authentication bug'
        description: New description for the issue (OPTIONAL).
                    Supports GitLab Flavored Markdown.
                    Pass empty string to clear description.
        state_event: Change the issue state (OPTIONAL).
                    Values: 'close', 'reopen'
                    Examples: 'close' to close issue, 'reopen' to reopen closed issue
        assignee_ids: List of user IDs to assign as assignees (OPTIONAL).
                     Replaces existing assignees. Issues can have multiple assignees.
                     Examples: [123, 456], [] (to clear assignees)
                     Note: Issues only support assignees, not reviewers (unlike merge requests)
        milestone_id: Milestone ID to assign to the issue (OPTIONAL).
                     Examples: 123, null (to clear milestone)
        labels: List of label names to replace existing labels (OPTIONAL).
               Replaces ALL existing labels.
               Examples: ['bug', 'frontend'], [] (to clear all labels)
        add_labels: List of label names to add to existing labels (OPTIONAL).
                   Keeps existing labels and adds these.
                   Examples: ['priority::high'], ['area::ux']
        remove_labels: List of label names to remove from existing labels (OPTIONAL).
                      Examples: ['wip'], ['needs-review']
        discussion_locked: Lock discussions on the issue (OPTIONAL).
        due_date: ISO 8601 date for issue due date (OPTIONAL).
                 Examples: '2024-12-31', null (to clear due date)
        weight: Issue weight for project management (OPTIONAL).
               Examples: 5, null (to clear weight)
        epic_id: Epic ID to associate issue with (OPTIONAL, GitLab Premium).
        epic_iid: Epic internal ID to associate issue with (OPTIONAL, GitLab Premium).
        confidential: Make issue confidential (OPTIONAL).
                     Examples: true, false
        issue_type: Type of issue (OPTIONAL).
                   Values: 'issue', 'incident', 'test_case', 'requirement', 'task'
        iteration_id: Iteration ID to assign issue to (OPTIONAL, GitLab Premium).
                     Examples: 15, null (to clear iteration)

    Example Usage:
        - Update title: project_path='my/project', issue_iid=15, title='New title'
        - Add labels: project_path='my/project', issue_iid=15, add_labels=['area::backend', 'kind::bug']
        - Close issue: project_path='my/project', issue_iid=15, state_event='close'
        - Update assignees: project_path='my/project', issue_iid=15, assignee_ids=[123, 456]
        - Set milestone: project_path='my/project', issue_iid=15, milestone_id=10
        - Link to epic (Premium): project_path='my/project', issue_iid=15, epic_id=42
    """

    project_path: str
    issue_iid: int
    title: str | None = None
    description: str | None = None
    state_event: str | None = None
    assignee_ids: list[int] | None = None
    milestone_id: int | None = None
    labels: list[str] | None = None
    add_labels: list[str] | None = None
    remove_labels: list[str] | None = None
    discussion_locked: bool | None = None
    due_date: str | None = None
    weight: int | None = None
    epic_id: int | None = None
    epic_iid: int | None = None
    confidential: bool | None = None
    issue_type: str | None = None
    iteration_id: int | None = None


class GitLabIssueListResponse(PaginatedResponse[GitLabIssue]):
    """Paginated response model for a list of GitLab issues.

    Attributes:
        count: Total number of issues available.
        items: The list of issues returned.
    """

