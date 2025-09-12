from enum import Enum

from src.schemas.base import (
    BaseModel,
    BaseResponseList,
    GitLabResponseBase,
    PaginatedResponse,
    VisibilityLevel,
)


class CreateRepositoryInput(BaseModel):
    """Input model for creating a new GitLab project/repository.

    Creates a new project (GitLab's term for repositories) within a group or user namespace.

    Attributes:
        name: The name of the project (REQUIRED).
             This will be used as the project identifier and URL path.
             Should be URL-safe (lowercase, alphanumeric, hyphens, underscores).
             Examples: 'my-api', 'frontend-app', 'data-processor'
             NOT the full namespace path - just the project name.
        description: Optional description of the project's purpose.
                    Shown on the project page and in search results.
                    Examples: 'REST API for user management', 'React frontend application'
        visibility: The visibility level of the project (OPTIONAL).
                   PRIVATE (default) = only members can access
                   INTERNAL = any authenticated user can access
                   PUBLIC = anyone can access, including anonymous users
        initialize_with_readme: Create an initial README.md file (OPTIONAL).
                               true = create README, false (default) = empty repository
        namespace_id: The namespace (group or user) ID to create the project in (OPTIONAL).
                     If not provided, creates in your personal namespace.
                     Can be a group ID number or group path string.
                     Examples: '123', 'my-group', 'parent-group/sub-group'

    Example Usage:
        - Personal project: name='my-app', description='My application'
        - Group project: name='team-app', namespace_id='my-group'
        - Public project: name='open-source-lib', visibility=VisibilityLevel.PUBLIC, initialize_with_readme=True
    """

    name: str
    description: str | None = None
    visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    initialize_with_readme: bool = False
    namespace_id: str | int | None = None


class GitLabRepository(GitLabResponseBase):
    """Response model for a GitLab project/repository.

    Represents a GitLab project (which GitLab calls repositories in some contexts).

    Attributes:
        id: The unique numeric identifier of the project.
           Used in API calls that require project ID.
           Examples: 12345, 67890
        name: The display name of the project.
             Examples: 'My API', 'Frontend App', 'Data Processor'
        path: The URL path identifier of the project.
             Used in project URLs and API calls.
             Examples: 'my-api', 'frontend-app', 'data-processor'
        description: Optional description of the project's purpose.
                    May be null if no description was provided.
        web_url: The full web URL to access the project.
                Examples: 'https://gitlab.com/user/my-project', 'https://gitlab.com/group/subgroup/project'
        default_branch: The default branch name for the project.
                       Usually 'main', 'master', or 'develop'.
                       May be null for empty repositories.

    Note: The full project path (namespace/project) can be extracted from web_url if needed.
    """

    id: int
    name: str
    path: str
    description: str | None = None
    web_url: str
    default_branch: str | None = None


class TreeItemType(str, Enum):
    """Types of items in the repository tree.

    Represents different types of objects that can exist in a Git repository tree.

    Attributes:
        TREE: Directory/folder in the repository.
        BLOB: File in the repository.
        COMMIT: Submodule commit reference.

    Attributes:
        BLOB: A file.
        TREE: A directory.
    """

    BLOB = "blob"
    TREE = "tree"


class ListRepositoryTreeInput(BaseModel):
    """Input model for listing files and directories in a repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        path: The path inside the repository (defaults to repository root).
        ref: The name of the branch, tag, or commit.
        recursive: Whether to get the contents recursively.
        per_page: Number of items to list per page.
    """

    project_path: str
    ref: str | None = None
    recursive: bool = False
    per_page: int = 20


class RepositoryTreeItem(GitLabResponseBase):
    """Response model for an item in the repository tree.

    Attributes:
        id: SHA1 identifier of the tree item.
        name: The name of the item.
        type: The type of the item (blob for files, tree for directories).
        path: The path of the item within the repository.
        mode: File mode.
    """

    id: str
    name: str
    type: TreeItemType
    path: str
    mode: str


class RepositoryTreeResponse(BaseResponseList[RepositoryTreeItem]):
    """Response model for repository tree listing."""



class SearchProjectsInput(BaseModel):
    """Input model for searching GitLab projects.

    Attributes:
        search: The search query.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    search: str
    page: int = 1
    per_page: int = 20


class GetRepositoryInput(BaseModel):
    """Input model for getting a specific repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
    """

    project_path: str


class ListRepositoriesInput(BaseModel):
    """Input model for listing repositories.

    Attributes:
        page: The page number for pagination.
        per_page: The number of items per page.
        owned: Show only owned projects.
        starred: Show only starred projects.
        search: Search query to filter projects.
        group_id: Filter projects by group/namespace path or ID.
    """

    page: int = 1
    per_page: int = 20
    owned: bool = False
    starred: bool = False
    search: str | None = None
    group_id: str | None = None


class UpdateRepositoryInput(BaseModel):
    """Input model for updating a repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        name: New name for the project.
        description: New description for the project.
        visibility: New visibility level for the project.
        default_branch: New default branch name.
    """

    project_path: str
    name: str | None = None
    description: str | None = None
    visibility: VisibilityLevel | None = None
    default_branch: str | None = None


class DeleteRepositoryInput(BaseModel):
    """Input model for deleting a repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
    """

    project_path: str


class GitLabSearchResponse(PaginatedResponse[dict[str, str | int | bool | None]]):
    """Response model for GitLab project search results."""

