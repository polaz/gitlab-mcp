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

    Lists labels from either a specific project OR group. Exactly one of project_path or group_id must be provided.

    Attributes:
        project_path: Full namespace path of project to list labels from (OPTIONAL but EXCLUSIVE).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
                     Use this for project-specific labels.
        group_id: Numeric ID OR path of group to list labels from (OPTIONAL but EXCLUSIVE).
                 Examples: '42', 'my-group', 'parent/subgroup'
                 Use this for group-level labels (inherited by projects).
        search: Search query to filter labels by name (OPTIONAL).
               Partial matching, case-insensitive.
               Examples: 'bug', 'priority', 'backend'
        include_ancestor_groups: Include labels from parent groups (OPTIONAL).
                               Only applies when using group_id.
                               true (default) = include parent group labels
                               false = only direct group labels
        with_counts: Include issue/MR counts for each label (OPTIONAL).
                    true = include usage statistics, false (default) = exclude counts
        page: Page number for pagination (starts at 1).
        per_page: Number of labels per page (1-100, default 20).

    IMPORTANT: Provide either project_path OR group_id, never both.

    Example Usage:
        - List project labels: project_path='my-group/project'
        - List group labels: group_id='my-group'
        - Search group labels: group_id='42', search='bug'
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

    Retrieves detailed information about a specific label. Must specify the scope (project or group).

    Attributes:
        project_path: Full namespace path of project (REQUIRED for project labels).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
                     Use when getting a project-specific label.
        group_id: Numeric ID OR path of group (REQUIRED for group labels).
                 Examples: '42', 'my-group', 'parent/subgroup'
                 Use when getting a group-level label.
        label_id: The numeric ID OR name of the label to retrieve (REQUIRED).
                 Can be either:
                 - Numeric ID: '123'
                 - Label name: 'bug' (case-sensitive)
                 - Label name with special chars: 'priority::high'

    IMPORTANT: Provide either project_path OR group_id, never both.

    Example Usage:
        - Get project label by name: project_path='my/project', label_id='bug'
        - Get group label by ID: group_id='my-group', label_id='42'
    """

    project_path: str | None = None
    group_id: str | None = None
    label_id: str


class CreateLabelInput(BaseModel):
    """Input model for creating a new GitLab label.

    Creates a new label in either a specific project or group.

    Attributes:
        project_path: Full namespace path of project (REQUIRED for project labels).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
                     Use to create a project-specific label.
        group_id: Numeric ID OR path of group (REQUIRED for group labels).
                 Examples: '42', 'my-group', 'parent/subgroup'
                 Use to create a group-level label (inherited by projects).
        name: The name of the new label (REQUIRED).
             Must be unique within the project/group.
             Examples: 'bug', 'priority::high', 'frontend', 'needs-review'
        color: The color of the label in hexadecimal format (REQUIRED).
              Must include '#' prefix.
              Examples: '#FF0000' (red), '#00FF00' (green), '#0052CC' (blue)
        description: Optional description explaining the label's purpose.
                    Examples: 'Issues related to bugs', 'High priority items'
        priority: Optional priority for label ordering (lower = higher priority).
                 Numeric value, typically 0-10.
                 Example: 1 (high priority), 5 (normal), 10 (low priority)

    IMPORTANT: Provide either project_path OR group_id, never both.

    Example Usage:
        - Create project label: project_path='my/project', name='bug', color='#FF0000'
        - Create group label: group_id='my-group', name='backend', color='#0052CC'
    """

    project_path: str | None = None
    group_id: str | None = None
    name: str
    color: str
    description: str | None = None
    priority: int | None = None


class UpdateLabelInput(BaseModel):
    """Input model for updating a GitLab label.

    Updates properties of an existing label. At least one update field must be provided.

    Attributes:
        project_path: Full namespace path of project (REQUIRED for project labels).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        group_id: Numeric ID OR path of group (REQUIRED for group labels).
                 Examples: '42', 'my-group', 'parent/subgroup'
        label_id: The numeric ID OR current name of the label to update (REQUIRED).
                 Examples: '123', 'old-name', 'priority::high'
        new_name: New name for the label (OPTIONAL).
                 Must be unique within the project/group.
                 Examples: 'updated-name', 'priority::critical'
        color: New color in hexadecimal format (OPTIONAL).
              Must include '#' prefix.
              Examples: '#FF0000', '#00FF00', '#0052CC'
        description: New description for the label (OPTIONAL).
                    Pass empty string to clear description.
                    Examples: 'Updated description', ''
        priority: New priority value (OPTIONAL).
                 Lower numbers = higher priority.
                 Examples: 1, 5, 10

    IMPORTANT:
    - Provide either project_path OR group_id, never both.
    - At least one of new_name, color, description, or priority must be provided.

    Example Usage:
        - Rename label: project_path='my/project', label_id='old', new_name='new'
        - Change color: group_id='my-group', label_id='bug', color='#FF5722'
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

    WARNING: This permanently deletes the label and removes it from all issues/MRs.
    This action cannot be undone!

    Attributes:
        project_path: Full namespace path of project (REQUIRED for project labels).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        group_id: Numeric ID OR path of group (REQUIRED for group labels).
                 Examples: '42', 'my-group', 'parent/subgroup'
        label_id: The numeric ID OR name of the label to delete (REQUIRED).
                 Examples: '123', 'bug', 'priority::high'

    IMPORTANT: Provide either project_path OR group_id, never both.

    Example Usage:
        - Delete project label: project_path='my/project', label_id='old-label'
        - Delete group label: group_id='my-group', label_id='unused-label'
    """

    project_path: str | None = None
    group_id: str | None = None
    label_id: str


class SubscribeToLabelInput(BaseModel):
    """Input model for subscribing to a GitLab label.

    Subscribe to notifications for issues/MRs that get this label applied.
    Only available for project labels, not group labels.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        label_id: The numeric ID OR name of the label to subscribe to (REQUIRED).
                 Examples: '123', 'bug', 'priority::high'

    Example Usage:
        - Subscribe to bug label: project_path='my/project', label_id='bug'
    """

    project_path: str
    label_id: str


class UnsubscribeFromLabelInput(BaseModel):
    """Input model for unsubscribing from a GitLab label.

    Stop receiving notifications for issues/MRs that get this label applied.
    Only available for project labels, not group labels.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        label_id: The numeric ID OR name of the label to unsubscribe from (REQUIRED).
                 Examples: '123', 'bug', 'priority::high'

    Example Usage:
        - Unsubscribe from bug label: project_path='my/project', label_id='bug'
    """

    project_path: str
    label_id: str


class GitLabLabelListResponse(BaseResponseList[GitLabLabel]):
    """Response model for listing GitLab labels."""

