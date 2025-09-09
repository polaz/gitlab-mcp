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

    IMPORTANT: This creates a project within your personal namespace or default group.
    To create in a specific group, use the group's project creation API instead.

    Example Usage:
        - Basic project: name='my-app', description='My application'
        - Public project: name='open-source-lib', visibility=VisibilityLevel.PUBLIC, initialize_with_readme=True
    """

    name: str
    description: str | None = None
    visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    initialize_with_readme: bool = False


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


class GitLabSearchResponse(PaginatedResponse[dict[str, str | int | bool | None]]):
    """Response model for GitLab project search results."""

