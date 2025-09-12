"""GitLab iteration data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class UpdateIterationInput(BaseModel):
    """Input model for updating an existing iteration in GitLab.

    Updates properties of an existing iteration. Only provided fields will be changed.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
        iteration_id: The numeric ID of the iteration (REQUIRED).
        title: New title for the iteration (OPTIONAL).
        description: New description for the iteration (OPTIONAL).
        start_date: New start date in YYYY-MM-DD format (OPTIONAL).
        due_date: New due date in YYYY-MM-DD format (OPTIONAL).
        state_event: State change action (OPTIONAL).
                    Values: 'start' to start iteration, 'close' to close iteration

    Example Usage:
        - Update title: group_id='team', iteration_id=15, title='New Title'
        - Close iteration: group_id='team', iteration_id=42, state_event='close'
    """

    group_id: str = Field(description="The numeric ID or path of the group")
    iteration_id: int = Field(description="The numeric ID of the iteration")
    title: str | None = Field(None, description="New title for the iteration")
    description: str | None = Field(None, description="New description for the iteration")
    start_date: str | None = Field(None, description="New start date (YYYY-MM-DD format)")
    due_date: str | None = Field(None, description="New due date (YYYY-MM-DD format)")
    state_event: str | None = Field(None, description="State change action ('start' or 'close')")


class ListIterationsInput(BaseModel):
    """Input model for listing iterations in a GitLab group.

    Retrieves a paginated list of iterations from a group with optional filtering.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        state: Filter iterations by state (OPTIONAL).
              Values: 'opened', 'upcoming', 'current', 'closed', 'all'
              Default: Returns all iterations regardless of state.
        search: Search iterations by title (OPTIONAL).
               Examples: 'sprint', 'release', 'Q1'
        include_ancestors: Include iterations from ancestor groups (OPTIONAL).
                          true = search parent groups too, false = only this group
        page: Page number for pagination (starts at 1).
        per_page: Number of iterations per page (1-100, default 20).

    Example Usage:
        - List group iterations: group_id='my-team'
        - List current iterations: group_id='team', state='current'
        - Search iterations: group_id='team', search='sprint'
    """

    group_id: str = Field(description="The numeric ID or path of the group")
    state: str | None = Field(None, description="Filter iterations by state")
    search: str | None = Field(None, description="Search iterations by title")
    include_ancestors: bool | None = Field(None, description="Include iterations from ancestor groups")
    page: int = Field(1, description="Page number for pagination")
    per_page: int = Field(20, description="Number of iterations per page")


class GetIterationInput(BaseModel):
    """Input model for getting a specific iteration from GitLab.

    Retrieves detailed information about a specific iteration.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        iteration_id: The numeric ID of the iteration (REQUIRED).

    Example Usage:
        - Get iteration: group_id='team', iteration_id=42
    """

    group_id: str = Field(description="The numeric ID or path of the group")
    iteration_id: int = Field(description="The numeric ID of the iteration")


class DeleteIterationInput(BaseModel):
    """Input model for deleting an iteration from GitLab.

    WARNING: This permanently deletes the iteration and cannot be undone.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
        iteration_id: The numeric ID of the iteration (REQUIRED).

    Example Usage:
        - Delete iteration: group_id='team', iteration_id=42
    """

    group_id: str = Field(description="The numeric ID or path of the group")
    iteration_id: int = Field(description="The numeric ID of the iteration")


class GitLabIteration(BaseModel):
    """GitLab iteration model."""

    id: int = Field(description="Iteration ID")
    iid: int = Field(description="Iteration internal ID")
    sequence: int = Field(description="Iteration sequence number")
    group_id: int = Field(description="Group ID")
    title: str | None = Field(description="Iteration title (null for auto-scheduled iterations)")
    description: str | None = Field(None, description="Iteration description")
    state: int = Field(description="Iteration state (1=upcoming, 2=started, 3=closed)")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    start_date: str = Field(description="Start date")
    due_date: str = Field(description="Due date")
    web_url: str = Field(description="Web URL of the iteration")


class IterationListResponse(BaseModel):
    """Response model for iteration list operations."""

    iterations: list[GitLabIteration] = Field(description="List of iterations")
    count: int = Field(description="Total number of iterations")
