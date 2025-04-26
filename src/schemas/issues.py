"""Schema models for GitLab issues."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from .base import GitLabResponseBase, PaginatedResponse


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


class IssueHealthStatus(str, Enum):
    """Health status for GitLab issues.

    Attributes:
        ON_TRACK: Issue is on track.
        AT_RISK: Issue is at risk.
        NEEDS_ATTENTION: Issue needs attention.
    """

    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    NEEDS_ATTENTION = "needs_attention"


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


class IssueOrderBy(str, Enum):
    """Ordering options for GitLab issues.

    Attributes:
        CREATED_AT: Order by creation date.
        UPDATED_AT: Order by last update date.
        PRIORITY: Order by priority.
        DUE_DATE: Order by due date.
        RELATIVE_POSITION: Order by relative position.
        LABEL_PRIORITY: Order by label priority.
        MILESTONE_DUE: Order by milestone due date.
        POPULARITY: Order by popularity.
        WEIGHT: Order by weight.
    """

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PRIORITY = "priority"
    DUE_DATE = "due_date"
    RELATIVE_POSITION = "relative_position"
    LABEL_PRIORITY = "label_priority"
    MILESTONE_DUE = "milestone_due"
    POPULARITY = "popularity"
    WEIGHT = "weight"


class IssueSort(str, Enum):
    """Sort direction for GitLab issues.

    Attributes:
        ASC: Ascending order.
        DESC: Descending order.
    """

    ASC = "asc"
    DESC = "desc"


class IssueScope(str, Enum):
    """Scope for GitLab issues.

    Attributes:
        CREATED_BY_ME: Issues created by the current user.
        ASSIGNED_TO_ME: Issues assigned to the current user.
        ALL: All issues.
    """

    CREATED_BY_ME = "created_by_me"
    ASSIGNED_TO_ME = "assigned_to_me"
    ALL = "all"


class UserBasic(GitLabResponseBase):
    """Basic user information returned in GitLab API responses.

    Attributes:
        id: User ID.
        name: User's full name.
        username: User's username.
        state: User's state (active, blocked, etc.).
        avatar_url: URL to the user's avatar image.
        web_url: URL to the user's GitLab profile.
    """

    id: int
    name: str
    username: str
    state: str
    avatar_url: str | None = None
    web_url: str


class MilestoneBasic(GitLabResponseBase):
    """Basic milestone information returned in GitLab API responses.

    Attributes:
        id: Milestone ID.
        iid: Internal milestone ID within the project.
        project_id: ID of the project the milestone belongs to.
        title: Milestone title.
        description: Milestone description.
        state: Milestone state (active or closed).
        created_at: Timestamp when the milestone was created.
        updated_at: Timestamp when the milestone was last updated.
        due_date: Due date of the milestone.
    """

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: str
    created_at: datetime
    updated_at: datetime
    due_date: str | None = None


class IssueReferences(GitLabResponseBase):
    """References to an issue in different formats.

    Attributes:
        short: Short reference (e.g., #123).
        relative: Relative reference (e.g., project#123).
        full: Full reference (e.g., group/project#123).
    """

    short: str
    relative: str
    full: str


class IssueTimeStats(GitLabResponseBase):
    """Time tracking statistics for an issue.

    Attributes:
        time_estimate: Estimated time in seconds.
        total_time_spent: Total time spent in seconds.
        human_time_estimate: Human-readable time estimate.
        human_total_time_spent: Human-readable total time spent.
    """

    time_estimate: int = 0
    total_time_spent: int = 0
    human_time_estimate: str | None = None
    human_total_time_spent: str | None = None


class IssueTaskCompletionStatus(GitLabResponseBase):
    """Task completion status for an issue.

    Attributes:
        count: Total number of tasks.
        completed_count: Number of completed tasks.
    """

    count: int = 0
    completed_count: int = 0


class IssueLinks(GitLabResponseBase):
    """Links related to an issue.

    Attributes:
        self: Link to the issue API endpoint.
        notes: Link to the issue notes API endpoint.
        award_emoji: Link to the issue award emoji API endpoint.
        project: Link to the project API endpoint.
        closed_as_duplicate_of: Link to the issue that this issue is a duplicate of, if applicable.
    """

    self: str
    notes: str
    award_emoji: str
    project: str
    closed_as_duplicate_of: str | None = None


class EpicInfo(GitLabResponseBase):
    """Information about an epic linked to an issue.

    Attributes:
        id: Epic ID.
        iid: Internal epic ID within the group.
        title: Epic title.
        url: URL to the epic.
        group_id: ID of the group the epic belongs to.
    """

    id: int
    iid: int
    title: str
    url: str
    group_id: int


class GitLabIssue(GitLabResponseBase):
    """Response model for a GitLab issue.

    Attributes:
        id: The unique identifier of the issue.
        iid: The internal ID of the issue within the project.
        project_id: The ID of the project the issue belongs to.
        title: The title of the issue.
        description: The description of the issue.
        state: The state of the issue (opened or closed).
        created_at: Timestamp when the issue was created.
        updated_at: Timestamp when the issue was last updated.
        closed_at: Timestamp when the issue was closed, if applicable.
        closed_by: User who closed the issue, if applicable.
        labels: The labels applied to the issue.
        milestone: Milestone information, if assigned.
        assignees: Users assigned to the issue.
        author: User who created the issue.
        type: Type of the issue.
        assignee: (Deprecated) User assigned to the issue.
        web_url: The web URL of the issue.
        time_stats: Time tracking statistics.
        task_completion_status: Task completion status.
        references: Issue references in different formats.
        upvotes: Number of upvotes.
        downvotes: Number of downvotes.
        merge_requests_count: Number of related merge requests.
        user_notes_count: Number of user notes.
        due_date: Due date of the issue.
        confidential: Whether the issue is confidential.
        discussion_locked: Whether discussion is locked.
        issue_type: Type of the issue (issue, incident, test_case, task).
        severity: Issue severity.
        _links: Links related to the issue.
        weight: Weight of the issue (Premium/Ultimate feature).
        epic_iid: (Deprecated) IID of the epic the issue belongs to.
        epic: Epic information, if linked (Premium/Ultimate feature).
        health_status: Health status of the issue (Ultimate feature).
    """

    id: int
    iid: int
    project_id: int
    title: str
    description: str | None = None
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    closed_by: UserBasic | None = None
    labels: list[str] = Field(default_factory=list)
    milestone: MilestoneBasic | None = None
    assignees: list[UserBasic] = Field(default_factory=list)
    author: UserBasic
    type: str = "ISSUE"
    assignee: UserBasic | None = None  # Deprecated, use assignees instead
    web_url: str
    time_stats: IssueTimeStats
    task_completion_status: IssueTaskCompletionStatus
    references: IssueReferences
    upvotes: int = 0
    downvotes: int = 0
    merge_requests_count: int = 0
    user_notes_count: int = 0
    due_date: str | None = None
    confidential: bool = False
    discussion_locked: bool = False
    issue_type: str = "issue"
    severity: str = "UNKNOWN"
    _links: IssueLinks
    weight: int | None = None  # Premium/Ultimate feature
    epic_iid: int | None = None  # Deprecated
    epic: EpicInfo | None = None  # Premium/Ultimate feature
    health_status: str | None = None  # Ultimate feature


class GitLabIssueListResponse(PaginatedResponse[GitLabIssue]):
    """Response model for listing GitLab issues."""

    pass


class GitLabIssueStatsCount(BaseModel):
    """Issue statistics counts.

    Attributes:
        all: Count of all issues.
        closed: Count of closed issues.
        opened: Count of open issues.
    """

    all: int
    closed: int
    opened: int


class GitLabIssueStats(BaseModel):
    """Issue statistics.

    Attributes:
        counts: Counts of issues by state.
    """

    counts: GitLabIssueStatsCount


class CreateIssueInput(BaseModel):
    """Input model for creating an issue in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        title: The title of the issue.
        description: The description of the issue.
        labels: The labels to apply to the issue.
        assignee_ids: The IDs of users to assign to the issue.
        milestone_id: The ID of the milestone to associate with the issue.
        confidential: Whether the issue is confidential.
        created_at: When the issue was created.
        due_date: The due date in YYYY-MM-DD format.
        epic_id: ID of the epic to add the issue to (Premium/Ultimate).
        issue_type: The type of issue.
        merge_request_to_resolve_discussions_of: IID of merge request to resolve discussions.
        discussion_to_resolve: ID of a discussion to resolve.
        weight: The weight of the issue (Premium/Ultimate).
    """

    project_path: str
    title: str
    description: str | None = None
    labels: list[str] | None = None
    assignee_ids: list[int] | None = None
    milestone_id: int | None = None
    confidential: bool = False
    created_at: str | None = None
    due_date: str | None = None
    epic_id: int | None = None
    issue_type: IssueType | None = None
    merge_request_to_resolve_discussions_of: int | None = None
    discussion_to_resolve: str | None = None
    weight: int | None = None


class UpdateIssueInput(BaseModel):
    """Input model for updating an issue in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        title: The title of the issue.
        description: The description of the issue.
        assignee_ids: The IDs of users to assign to the issue.
        milestone_id: The ID of the milestone to associate with the issue.
        labels: The labels to apply to the issue.
        state_event: Change the state, 'close' or 'reopen'.
        updated_at: When the issue was updated.
        due_date: The due date in YYYY-MM-DD format.
        weight: The weight of the issue (Premium/Ultimate).
        discussion_locked: Flag indicating if discussion is locked.
        epic_id: ID of the epic to add the issue to (Premium/Ultimate).
        issue_type: The type of issue.
        confidential: Whether the issue is confidential.
        add_labels: Comma-separated labels to add.
        remove_labels: Comma-separated labels to remove.
    """

    project_path: str
    issue_iid: int
    title: str | None = None
    description: str | None = None
    assignee_ids: list[int] | None = None
    milestone_id: int | None = None
    labels: str | None = None
    state_event: str | None = None
    updated_at: str | None = None
    due_date: str | None = None
    weight: int | None = None
    discussion_locked: bool | None = None
    epic_id: int | None = None
    issue_type: IssueType | None = None
    confidential: bool | None = None
    add_labels: str | None = None
    remove_labels: str | None = None


class GetIssueInput(BaseModel):
    """Input model for getting a specific issue from a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
    """

    project_path: str
    issue_iid: int


class DeleteIssueInput(BaseModel):
    """Input model for deleting an issue from a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
    """

    project_path: str
    issue_iid: int


class MoveIssueInput(BaseModel):
    """Input model for moving an issue to a different project.

    Attributes:
        project_path: The path of the source project.
        issue_iid: The internal ID of the issue within the project.
        to_project_id: The ID of the target project.
    """

    project_path: str
    issue_iid: int
    to_project_id: int


class ListIssuesInput(BaseModel):
    """Input model for listing issues in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        state: The state of the issues to list (opened, closed, or all).
        labels: The labels to filter issues by.
        milestone: The milestone to filter issues by.
        scope: Return issues for the given scope.
        author_id: Return issues created by the given user id.
        assignee_id: Return issues assigned to the given user id.
        my_reaction_emoji: Return issues with the given emoji reaction.
        search: Search query.
        in: Modify the scope of the search attribute (title, description).
        created_after: Return issues created on or after the given time.
        created_before: Return issues created on or before the given time.
        updated_after: Return issues updated on or after the given time.
        updated_before: Return issues updated on or before the given time.
        confidential: Filter confidential or public issues.
        issue_type: Filter to a given type of issue.
        order_by: Return issues ordered by the specified field.
        sort: Return issues sorted in asc or desc order.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    state: IssueState | None = None
    labels: list[str] | None = None
    milestone: str | None = None
    scope: IssueScope | None = None
    author_id: int | None = None
    assignee_id: int | None = None
    my_reaction_emoji: str | None = None
    search: str | None = None
    in_: str | None = Field(default=None, alias="in")
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    confidential: bool | None = None
    issue_type: IssueType | None = None
    order_by: IssueOrderBy | None = None
    sort: IssueSort | None = None
    page: int = 1
    per_page: int = 20


class ListGroupIssuesInput(BaseModel):
    """Input model for listing issues in a GitLab group.

    Attributes:
        group_id: The ID or path of the group.
        state: The state of the issues to list (opened, closed, or all).
        labels: The labels to filter issues by.
        milestone: The milestone to filter issues by.
        scope: Return issues for the given scope.
        author_id: Return issues created by the given user id.
        assignee_id: Return issues assigned to the given user id.
        my_reaction_emoji: Return issues with the given emoji reaction.
        search: Search query.
        in: Modify the scope of the search attribute (title, description).
        created_after: Return issues created on or after the given time.
        created_before: Return issues created on or before the given time.
        updated_after: Return issues updated on or after the given time.
        updated_before: Return issues updated on or before the given time.
        confidential: Filter confidential or public issues.
        issue_type: Filter to a given type of issue.
        order_by: Return issues ordered by the specified field.
        sort: Return issues sorted in asc or desc order.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    group_id: str
    state: IssueState | None = None
    labels: list[str] | None = None
    milestone: str | None = None
    scope: IssueScope | None = None
    author_id: int | None = None
    assignee_id: int | None = None
    my_reaction_emoji: str | None = None
    search: str | None = None
    in_: str | None = Field(default=None, alias="in")
    created_after: datetime | None = None
    created_before: datetime | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    confidential: bool | None = None
    issue_type: IssueType | None = None
    order_by: IssueOrderBy | None = None
    sort: IssueSort | None = None
    page: int = 1
    per_page: int = 20


class GitLabIssueLinkType(str, Enum):
    """Types of issue links.

    Attributes:
        RELATES_TO: Issues are related.
        BLOCKS: Source issue blocks target issue.
        IS_BLOCKED_BY: Source issue is blocked by target issue.
    """

    RELATES_TO = "relates_to"
    BLOCKS = "blocks"
    IS_BLOCKED_BY = "is_blocked_by"


class GitLabIssueLink(GitLabResponseBase):
    """Issue link information.

    Attributes:
        id: The ID of the linked issue.
        iid: The internal ID of the linked issue.
        issue_link_id: The ID of the issue link.
        project_id: The project ID of the linked issue.
        title: The title of the linked issue.
        state: The state of the linked issue.
        created_at: When the linked issue was created.
        updated_at: When the linked issue was last updated.
        labels: Labels of the linked issue.
        milestone: Milestone of the linked issue.
        assignees: Users assigned to the linked issue.
        author: User who created the linked issue.
        description: Description of the linked issue.
        web_url: URL of the linked issue.
        confidential: Whether the linked issue is confidential.
        weight: Weight of the linked issue.
        link_type: Type of the link.
        link_created_at: When the link was created.
        link_updated_at: When the link was last updated.
    """

    id: int
    iid: int
    issue_link_id: int
    project_id: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    labels: list[str] = Field(default_factory=list)
    milestone: MilestoneBasic | None = None
    assignees: list[UserBasic] = Field(default_factory=list)
    assignee: UserBasic | None = None  # Deprecated
    author: UserBasic
    description: str | None = None
    web_url: str
    confidential: bool = False
    weight: int | None = None
    link_type: GitLabIssueLinkType
    link_created_at: datetime
    link_updated_at: datetime


class ListIssueLinksInput(BaseModel):
    """Input model for listing links to an issue.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
    """

    project_path: str
    issue_iid: int


class GetIssueLinkInput(BaseModel):
    """Input model for getting a specific issue link.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        issue_link_id: The ID of the issue link.
    """

    project_path: str
    issue_iid: int
    issue_link_id: int


class CreateIssueLinkInput(BaseModel):
    """Input model for creating a link between issues.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the source issue.
        target_project_id: The ID of the target project.
        target_issue_iid: The internal ID of the target issue.
        link_type: The type of the relation.
    """

    project_path: str
    issue_iid: int
    target_project_id: str
    target_issue_iid: int
    link_type: GitLabIssueLinkType = GitLabIssueLinkType.RELATES_TO


class DeleteIssueLinkInput(BaseModel):
    """Input model for deleting a link between issues.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        issue_link_id: The ID of the issue link to delete.
    """

    project_path: str
    issue_iid: int
    issue_link_id: int


class IssueLinkResponse(GitLabResponseBase):
    """Response model for issue links.

    Attributes:
        source_issue: Source issue information.
        target_issue: Target issue information.
        link_type: Type of the link.
    """

    source_issue: GitLabIssue
    target_issue: GitLabIssue
    link_type: GitLabIssueLinkType


class CreateIssueCommentInput(BaseModel):
    """Input model for creating a comment on a GitLab issue.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        body: The content of the comment.
    """

    project_path: str
    issue_iid: int
    body: str


class ListIssueCommentsInput(BaseModel):
    """Input model for listing comments on a GitLab issue.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    issue_iid: int
    page: int = 1
    per_page: int = 20
