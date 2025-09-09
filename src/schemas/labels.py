"""Schema models for GitLab labels."""

from pydantic import BaseModel

from src.schemas.base import BaseResponseList, GitLabResponseBase


class GitLabLabel(GitLabResponseBase):
    """Response model for a GitLab label.

    Attributes:
        id: The unique identifier of the label.
        name: The name of the label.
        color: The color of the label (hexadecimal format).
        description: Optional description of the label.
        description_html: HTML-formatted description of the label.
        text_color: The text color for the label.
        open_issues_count: Number of open issues with this label.
        closed_issues_count: Number of closed issues with this label.
        open_merge_requests_count: Number of open merge requests with this label.
        subscribed: Whether the current user is subscribed to this label.
        priority: The priority of the label (lower numbers = higher priority).
        is_project_label: Whether this is a project-level label.
    """

    id: int
    name: str
    color: str
    description: str | None = None
    description_html: str | None = None
    text_color: str
    open_issues_count: int
    closed_issues_count: int
    open_merge_requests_count: int
    subscribed: bool | None = None
    priority: int | None = None
    is_project_label: bool


class ListLabelsInput(BaseModel):
    """Input model for listing GitLab labels.

    Attributes:
        project_path: Optional project path to list project-specific labels.
        group_id: Optional group ID to list group-level labels.
        search: Optional search query to filter labels by name.
        include_ancestor_groups: Whether to include labels from ancestor groups (group labels only).
        with_counts: Whether to include issue and merge request counts.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str | None = None
    group_id: str | None = None
    search: str | None = None
    include_ancestor_groups: bool = True
    with_counts: bool = False
    page: int = 1
    per_page: int = 20


class GetLabelInput(BaseModel):
    """Input model for getting a specific GitLab label.

    Attributes:
        project_path: Optional project path (required for project labels).
        group_id: Optional group ID (required for group labels).
        label_id: The ID or name of the label.
    """

    project_path: str | None = None
    group_id: str | None = None
    label_id: str


class CreateLabelInput(BaseModel):
    """Input model for creating a new GitLab label.

    Attributes:
        project_path: Optional project path (required for project labels).
        group_id: Optional group ID (required for group labels).
        name: The name of the label.
        color: The color of the label (hexadecimal format, e.g., '#FF0000').
        description: Optional description of the label.
        priority: Optional priority of the label (lower numbers = higher priority).
    """

    project_path: str | None = None
    group_id: str | None = None
    name: str
    color: str
    description: str | None = None
    priority: int | None = None


class UpdateLabelInput(BaseModel):
    """Input model for updating a GitLab label.

    Attributes:
        project_path: Optional project path (required for project labels).
        group_id: Optional group ID (required for group labels).
        label_id: The ID or name of the label to update.
        new_name: Optional new name for the label.
        color: Optional new color for the label.
        description: Optional new description for the label.
        priority: Optional new priority for the label.
    """

    project_path: str | None = None
    group_id: str | None = None
    label_id: str
    new_name: str | None = None
    color: str | None = None
    description: str | None = None
    priority: int | None = None


class DeleteLabelInput(BaseModel):
    """Input model for deleting a GitLab label.

    Attributes:
        project_path: Optional project path (required for project labels).
        group_id: Optional group ID (required for group labels).
        label_id: The ID or name of the label to delete.
    """

    project_path: str | None = None
    group_id: str | None = None
    label_id: str


class SubscribeToLabelInput(BaseModel):
    """Input model for subscribing to a GitLab label.

    Attributes:
        project_path: The project path (required for project labels).
        label_id: The ID or name of the label to subscribe to.
    """

    project_path: str
    label_id: str


class UnsubscribeFromLabelInput(BaseModel):
    """Input model for unsubscribing from a GitLab label.

    Attributes:
        project_path: The project path (required for project labels).
        label_id: The ID or name of the label to unsubscribe from.
    """

    project_path: str
    label_id: str


class GitLabLabelListResponse(BaseResponseList[GitLabLabel]):
    """Response model for listing GitLab labels."""

    pass
