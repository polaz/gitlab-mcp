"""GitLab milestone data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateMilestoneInput(BaseModel):
    """Input model for creating a new milestone in GitLab.

    Creates a new milestone within a project or group for organizing issues and merge requests.

    Attributes:
        project_path: The full namespace path of the project (OPTIONAL).
                     Must include complete group/subgroup path when provided.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
                     If not provided, creates group milestone.
        group_id: The numeric ID OR path of the group (OPTIONAL).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
                 If not provided, creates project milestone.
        title: The title of the milestone (REQUIRED).
               Should be descriptive and concise.
               Examples: 'Release v1.0', 'Q1 2024', 'Sprint 15'
        description: Detailed description of the milestone (OPTIONAL).
                    Supports GitLab Flavored Markdown.
                    Examples: 'Major release with new authentication features'
        due_date: Due date for the milestone in YYYY-MM-DD format (OPTIONAL).
                 Examples: '2024-12-31', '2024-03-15'
        start_date: Start date for the milestone in YYYY-MM-DD format (OPTIONAL).
                   Examples: '2024-01-01', '2024-03-01'

    Example Usage:
        - Project milestone: project_path='my/project', title='Release 1.0'
        - Group milestone: group_id='my-team', title='Q1 Goals', due_date='2024-03-31'
    """

    project_path: str | None = Field(None, description="The full namespace path of the project")
    group_id: str | None = Field(None, description="The numeric ID or path of the group")
    title: str = Field(description="The title of the milestone")
    description: str | None = Field(None, description="The description of the milestone")
    due_date: str | None = Field(None, description="Due date (YYYY-MM-DD format)")
    start_date: str | None = Field(None, description="Start date (YYYY-MM-DD format)")


class UpdateMilestoneInput(BaseModel):
    """Input model for updating an existing milestone in GitLab.

    Updates properties of an existing milestone. Only provided fields will be changed.

    Attributes:
        project_path: The full namespace path of the project (OPTIONAL).
                     Required for project milestones.
        group_id: The numeric ID OR path of the group (OPTIONAL).
                 Required for group milestones.
        milestone_id: The numeric ID of the milestone (REQUIRED).
        title: New title for the milestone (OPTIONAL).
        description: New description for the milestone (OPTIONAL).
        due_date: New due date in YYYY-MM-DD format (OPTIONAL).
        start_date: New start date in YYYY-MM-DD format (OPTIONAL).
        state_event: State change action (OPTIONAL).
                    Values: 'close' to close milestone, 'activate' to reopen

    Example Usage:
        - Update title: project_path='my/project', milestone_id=15, title='New Title'
        - Close milestone: group_id='team', milestone_id=42, state_event='close'
    """

    project_path: str | None = Field(None, description="The full namespace path of the project")
    group_id: str | None = Field(None, description="The numeric ID or path of the group")
    milestone_id: int = Field(description="The numeric ID of the milestone")
    title: str | None = Field(None, description="New title for the milestone")
    description: str | None = Field(None, description="New description for the milestone")
    due_date: str | None = Field(None, description="New due date (YYYY-MM-DD format)")
    start_date: str | None = Field(None, description="New start date (YYYY-MM-DD format)")
    state_event: str | None = Field(None, description="State change action ('close' or 'activate')")


class ListMilestonesInput(BaseModel):
    """Input model for listing milestones in GitLab.

    Retrieves a paginated list of milestones from a project or group with optional filtering.

    Attributes:
        project_path: The full namespace path of the project (OPTIONAL).
                     Required for project milestones.
        group_id: The numeric ID OR path of the group (OPTIONAL).
                 Required for group milestones.
        state: Filter milestones by state (OPTIONAL).
              Values: 'active', 'closed', 'all'
              Default: Returns all milestones regardless of state.
        search: Search milestones by title (OPTIONAL).
               Examples: 'release', 'v1.0', 'sprint'
        page: Page number for pagination (starts at 1).
        per_page: Number of milestones per page (1-100, default 20).

    Example Usage:
        - List project milestones: project_path='my/project'
        - List active group milestones: group_id='team', state='active'
        - Search milestones: project_path='project', search='release'
    """

    project_path: str | None = Field(None, description="The full namespace path of the project")
    group_id: str | None = Field(None, description="The numeric ID or path of the group")
    state: str | None = Field(None, description="Filter milestones by state")
    search: str | None = Field(None, description="Search milestones by title")
    page: int = Field(1, description="Page number for pagination")
    per_page: int = Field(20, description="Number of milestones per page")


class GetMilestoneInput(BaseModel):
    """Input model for getting a specific milestone from GitLab.

    Retrieves detailed information about a specific milestone.

    Attributes:
        project_path: The full namespace path of the project (OPTIONAL).
                     Required for project milestones.
        group_id: The numeric ID OR path of the group (OPTIONAL).
                 Required for group milestones.
        milestone_id: The numeric ID of the milestone (REQUIRED).

    Example Usage:
        - Get project milestone: project_path='my/project', milestone_id=15
        - Get group milestone: group_id='team', milestone_id=42
    """

    project_path: str | None = Field(None, description="The full namespace path of the project")
    group_id: str | None = Field(None, description="The numeric ID or path of the group")
    milestone_id: int = Field(description="The numeric ID of the milestone")


class DeleteMilestoneInput(BaseModel):
    """Input model for deleting a milestone from GitLab.

    WARNING: This permanently deletes the milestone and cannot be undone.

    Attributes:
        project_path: The full namespace path of the project (OPTIONAL).
                     Required for project milestones.
        group_id: The numeric ID OR path of the group (OPTIONAL).
                 Required for group milestones.
        milestone_id: The numeric ID of the milestone (REQUIRED).

    Example Usage:
        - Delete project milestone: project_path='my/project', milestone_id=15
        - Delete group milestone: group_id='team', milestone_id=42
    """

    project_path: str | None = Field(None, description="The full namespace path of the project")
    group_id: str | None = Field(None, description="The numeric ID or path of the group")
    milestone_id: int = Field(description="The numeric ID of the milestone")


class GitLabMilestone(BaseModel):
    """GitLab milestone model with optimized field ordering for Claude Code UX.

    CRITICAL: id and title are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ Milestone: {id: 42, title: "Release v1.0", ...}
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    id: int = Field(..., description="Milestone ID (shows first in Claude Code)")
    title: str = Field(..., description="Milestone title (shows second in Claude Code)")
    description: str | None = Field(None, description="Milestone description")
    state: str = Field(description="Milestone state")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    due_date: str | None = Field(None, description="Due date")
    start_date: str | None = Field(None, description="Start date")
    web_url: str = Field(description="Web URL of the milestone")
    group_id: int | None = Field(None, description="Group ID if group milestone")
    project_id: int | None = Field(None, description="Project ID if project milestone")


class MilestoneListResponse(BaseModel):
    """Response model for milestone list operations."""

    milestones: list[GitLabMilestone] = Field(description="List of milestones")
    count: int = Field(description="Total number of milestones")
