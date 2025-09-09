from enum import Enum

from pydantic import BaseModel

from src.schemas.base import GitLabResponseBase, PaginatedResponse, VisibilityLevel


class GroupAccessLevel(int, Enum):
    """GitLab group access levels.

    Attributes:
        NO_ACCESS: No access.
        MINIMAL_ACCESS: Minimal access - only view.
        GUEST: Guest access.
        REPORTER: Reporter access.
        DEVELOPER: Developer access.
        MAINTAINER: Maintainer access.
        OWNER: Owner access.
    """

    NO_ACCESS = 0
    MINIMAL_ACCESS = 5
    GUEST = 10
    REPORTER = 20
    DEVELOPER = 30
    MAINTAINER = 40
    OWNER = 50


class GitLabGroup(GitLabResponseBase):
    """Response model for a GitLab group.

    Attributes:
        id: The unique identifier of the group.
        name: The name of the group.
        path: The path of the group.
        description: Optional description of the group.
        visibility: The visibility level of the group.
        web_url: The web URL of the group.
        parent_id: The ID of the parent group, if any.
        labels: Optional list of labels associated with the group.
    """

    id: int
    name: str
    path: str
    description: str | None = None
    visibility: VisibilityLevel
    web_url: str
    parent_id: int | None = None
    labels: list[str] | None = None


class ListGroupsInput(BaseModel):
    """Input model for listing GitLab groups.

    Lists groups visible to the current user with optional filtering and pagination.

    Attributes:
        search: Search query to filter groups by name or path (OPTIONAL).
               Searches in group name, path, and description.
               Examples: 'backend', 'my-team', 'api'
        owned: Whether to only include groups owned by current user (OPTIONAL).
              true = only groups you own, false = all visible groups (default)
        min_access_level: Minimum access level required to see the group (OPTIONAL).
                         Values from GroupAccessLevel enum:
                         - NO_ACCESS (0), MINIMAL_ACCESS (5), GUEST (10)
                         - REPORTER (20), DEVELOPER (30), MAINTAINER (40), OWNER (50)
        top_level_only: Whether to only include top-level groups (OPTIONAL).
                       true = exclude subgroups, false = include all groups (default)
        page: Page number for pagination (starts at 1).
        per_page: Number of groups per page (1-100, default 20).

    Example Usage:
        - List all groups: (no parameters)
        - Search for 'api' groups: search='api'
        - List owned groups only: owned=True
    """

    search: str | None = None
    owned: bool = False
    min_access_level: GroupAccessLevel | None = None
    top_level_only: bool = False
    page: int = 1
    per_page: int = 20


class GitLabGroupListResponse(PaginatedResponse[GitLabGroup]):
    """Response model for listing GitLab groups."""



class GetGroupInput(BaseModel):
    """Input model for getting a specific GitLab group.

    Retrieves detailed information about a specific group, optionally including its labels.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Can be either:
                 - Numeric ID: '42'
                 - Group path: 'my-group' (for top-level groups)
                 - Full path: 'parent-group/subgroup' (for nested groups)
                 Examples: '123', 'gitlab-org', 'company/backend-team'
                 This is different from project paths - use just the group identifier.
        with_labels: Whether to fetch and include group labels in response (OPTIONAL).
                    true = include labels array, false = exclude labels (default)
                    Note: Fetching labels requires additional API call.

    Example Usage:
        - Get basic group info: group_id='my-group'
        - Get group with labels: group_id='parent/subgroup', with_labels=True
    """

    group_id: str
    with_labels: bool = False


class CreateGroupInput(BaseModel):
    """Input model for creating a new GitLab group.

    Creates a new group (namespace) that can contain projects and subgroups.

    Attributes:
        name: The display name of the group (REQUIRED).
             This is shown in the GitLab UI.
             Examples: 'Backend Team', 'My Company', 'API Development'
        path: The URL path identifier for the group (REQUIRED).
             Must be lowercase, URL-safe (alphanumeric, hyphens, underscores).
             This becomes part of project URLs: gitlab.com/GROUP_PATH/project
             Examples: 'backend-team', 'my-company', 'api-dev'
        description: Optional description of the group's purpose.
                    Supports markdown formatting.
                    Example: 'Team responsible for backend services and APIs.'
        visibility: The visibility level of the group (OPTIONAL).
                   Values: PRIVATE (default), INTERNAL, PUBLIC
                   Affects who can see the group and its projects.
        parent_id: Numeric ID of parent group to create a subgroup (OPTIONAL).
                  Leave empty for top-level group.
                  Example: 42 (to create subgroup under group ID 42)
        auto_devops_enabled: Enable Auto DevOps for projects in this group (OPTIONAL).
                           Default: false

    Example Usage:
        - Create top-level group: name='My Team', path='my-team'
        - Create subgroup: name='Backend', path='backend', parent_id=42
    """

    name: str
    path: str
    description: str | None = None
    visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    parent_id: int | None = None
    auto_devops_enabled: bool = False


class UpdateGroupInput(BaseModel):
    """Input model for updating a GitLab group.

    Updates properties of an existing group. Only provided fields will be changed.

    Attributes:
        group_id: The numeric ID OR path of the group to update (REQUIRED).
                 Examples: '123', 'my-group', 'parent/subgroup'
        name: New display name for the group (OPTIONAL).
             Examples: 'Updated Team Name', 'Backend Services'
        path: New URL path identifier for the group (OPTIONAL).
             Must be URL-safe and will change group URLs.
             WARNING: This affects all project URLs in the group.
             Examples: 'new-team-name', 'backend-services'
        description: New description for the group (OPTIONAL).
                    Pass empty string to clear description.
                    Supports markdown formatting.
        visibility: New visibility level for the group (OPTIONAL).
                   Values: PRIVATE, INTERNAL, PUBLIC

    Example Usage:
        - Update name only: group_id='my-group', name='New Team Name'
        - Change visibility: group_id='123', visibility=VisibilityLevel.PUBLIC
    """

    group_id: str
    name: str | None = None
    path: str | None = None
    description: str | None = None
    visibility: VisibilityLevel | None = None


class DeleteGroupInput(BaseModel):
    """Input model for deleting a GitLab group.

    WARNING: This permanently deletes the group and ALL its projects, subgroups, and data.
    This action cannot be undone!

    Attributes:
        group_id: The numeric ID OR path of the group to delete (REQUIRED).
                 Examples: '123', 'my-group', 'parent/subgroup'
                 Ensure you have the correct group before deletion.

    Example Usage:
        - Delete group: group_id='old-team'
        - Delete by ID: group_id='42'
    """

    group_id: str


class GetGroupByProjectNamespaceInput(BaseModel):
    """Input model for getting a GitLab group based on a project namespace.

    Extracts and retrieves the group that owns a specific project based on the project's namespace.
    Useful when you have a project path and need its parent group information.

    Attributes:
        project_namespace: The namespace portion of a project path (REQUIRED).
                          This is the group/subgroup part of a project path.
                          For project 'group/subgroup/project', use 'group/subgroup'
                          For project 'my-group/project', use 'my-group'
                          Examples: 'gitlab-org', 'company/backend-team', 'user-name'

    Example Usage:
        - Get group for project 'gitlab-org/gitlab': project_namespace='gitlab-org'
        - Get group for project 'company/team/api': project_namespace='company/team'
    """

    project_namespace: str
