"""Pydantic models for filter parameters used across the application."""

from datetime import datetime

from pydantic import BaseModel, Field


class GitLabFilterParams(BaseModel):
    """Base model for GitLab API filter parameters.

    This model provides common pagination parameters used across
    multiple GitLab API endpoints.

    Attributes:
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    page: int = Field(default=1, description="Page number for pagination")
    per_page: int = Field(default=20, description="Number of items per page")


class IssueFilterParams(GitLabFilterParams):
    """Parameters for filtering GitLab issues.

    Attributes:
        state: The state of issues to return (opened, closed, or all).
        labels: The labels to filter issues by.
        assignee_id: The ID of the assignee to filter issues by.
        milestone_id: The ID of the milestone to filter issues by.
        search: Search issues by title and description.
        created_after: Return issues created after the given time.
        created_before: Return issues created before the given time.
        updated_after: Return issues updated after the given time.
        updated_before: Return issues updated before the given time.
        scope: The scope of issues to return (created_by_me, assigned_to_me, or all).
        author_id: The ID of the author to filter issues by.
        order_by: Return issues ordered by this field.
        sort: Sort issues in this order (asc or desc).
    """

    state: str | None = Field(
        default=None, description="State of issues (opened, closed, or all)"
    )
    labels: list[str] | None = Field(
        default=None, description="Labels to filter issues by"
    )
    assignee_id: int | None = Field(
        default=None, description="ID of the assignee to filter by"
    )
    milestone_id: int | None = Field(
        default=None, description="ID of the milestone to filter by"
    )
    search: str | None = Field(
        default=None, description="Search issues by title and description"
    )
    created_after: datetime | None = Field(
        default=None, description="Return issues created after this time"
    )
    created_before: datetime | None = Field(
        default=None, description="Return issues created before this time"
    )
    updated_after: datetime | None = Field(
        default=None, description="Return issues updated after this time"
    )
    updated_before: datetime | None = Field(
        default=None, description="Return issues updated before this time"
    )
    scope: str | None = Field(
        default=None,
        description="Scope of issues (created_by_me, assigned_to_me, or all)",
    )
    author_id: int | None = Field(
        default=None, description="ID of the author to filter by"
    )
    order_by: str | None = Field(default=None, description="Field to order issues by")
    sort: str | None = Field(default=None, description="Sort order (asc or desc)")


class UserFilterParams(GitLabFilterParams):
    """Parameters for filtering GitLab users.

    Attributes:
        search: Search users by username, name or email.
        username: Filter by username.
        active: Filter by active state.
        blocked: Filter by blocked state.
        created_after: Return users created after the given time.
        created_before: Return users created before the given time.
    """

    search: str | None = Field(
        default=None, description="Search users by username, name or email"
    )
    username: str | None = Field(default=None, description="Filter by username")
    active: bool | None = Field(default=None, description="Filter by active state")
    blocked: bool | None = Field(default=None, description="Filter by blocked state")
    created_after: datetime | None = Field(
        default=None, description="Return users created after this time"
    )
    created_before: datetime | None = Field(
        default=None, description="Return users created before this time"
    )


class MergeRequestFilterParams(GitLabFilterParams):
    """Parameters for filtering GitLab merge requests.

    Attributes:
        state: The state of merge requests to return (opened, closed, merged, or all).
        labels: The labels to filter merge requests by.
        milestone_id: The ID of the milestone to filter merge requests by.
        order_by: Return merge requests ordered by this field.
        sort: Sort merge requests in this order (asc or desc).
        scope: The scope of merge requests to return.
        author_id: The ID of the author to filter merge requests by.
        assignee_id: The ID of the assignee to filter merge requests by.
    """

    state: str | None = Field(
        default=None,
        description="State of merge requests (opened, closed, merged, or all)",
    )
    labels: list[str] | None = Field(
        default=None, description="Labels to filter merge requests by"
    )
    milestone_id: int | None = Field(
        default=None, description="ID of the milestone to filter by"
    )
    order_by: str | None = Field(
        default=None, description="Field to order merge requests by"
    )
    sort: str | None = Field(default=None, description="Sort order (asc or desc)")
    scope: str | None = Field(
        default=None, description="Scope of merge requests to return"
    )
    author_id: int | None = Field(
        default=None, description="ID of the author to filter by"
    )
    assignee_id: int | None = Field(
        default=None, description="ID of the assignee to filter by"
    )


class GroupFilterParams(GitLabFilterParams):
    """Parameters for filtering GitLab groups.

    Attributes:
        search: Search groups by name.
        owned: Return only groups owned by the current user.
        min_access_level: Minimum access level required.
        top_level_only: Return only top-level groups.
        statistics: Include group statistics.
        with_custom_attributes: Include custom attributes.
        order_by: Return groups ordered by this field.
        sort: Sort groups in this order (asc or desc).
    """

    search: str | None = Field(default=None, description="Search groups by name")
    owned: bool | None = Field(
        default=None, description="Return only groups owned by the current user"
    )
    min_access_level: int | None = Field(
        default=None, description="Minimum access level required"
    )
    top_level_only: bool | None = Field(
        default=None, description="Return only top-level groups"
    )
    statistics: bool | None = Field(
        default=None, description="Include group statistics"
    )
    with_custom_attributes: bool | None = Field(
        default=None, description="Include custom attributes"
    )
    order_by: str | None = Field(default=None, description="Field to order groups by")
    sort: str | None = Field(default=None, description="Sort order (asc or desc)")


class PipelineFilterParams(GitLabFilterParams):
    """Parameters for filtering GitLab pipelines.

    Attributes:
        scope: The scope of pipelines to return.
        status: The status of pipelines to return.
        ref: The branch or tag name to filter pipelines by.
        sha: The commit SHA to filter pipelines by.
        yaml_errors: Return only pipelines with YAML errors.
        username: The username to filter pipelines by.
        order_by: Return pipelines ordered by this field.
        sort: Sort pipelines in this order (asc or desc).
    """

    scope: str | None = Field(default=None, description="Scope of pipelines to return")
    status: str | None = Field(
        default=None, description="Status of pipelines to return"
    )
    ref: str | None = Field(default=None, description="Branch or tag name to filter by")
    sha: str | None = Field(default=None, description="Commit SHA to filter by")
    yaml_errors: bool | None = Field(
        default=None, description="Return only pipelines with YAML errors"
    )
    username: str | None = Field(default=None, description="Username to filter by")
    order_by: str | None = Field(
        default=None, description="Field to order pipelines by"
    )
    sort: str | None = Field(default=None, description="Sort order (asc or desc)")
