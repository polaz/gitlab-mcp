from src.schemas.base import (
    BaseModel,
    GitLabResponseBase,
    PaginatedResponse,
    VisibilityLevel,
)


class ForkRepositoryInput(BaseModel):
    """Input model for forking a GitLab repository.

    Attributes:
        project_path: The path of the project to fork (e.g., 'namespace/project').
        target_namespace: The namespace where the fork will be created.
    """

    project_path: str
    target_namespace: str


class GitLabFork(GitLabResponseBase):
    """Response model for a forked GitLab repository.

    Attributes:
        id: The unique identifier of the fork.
        name: The name of the forked repository.
        path: The path of the forked repository.
        web_url: The web URL of the forked repository.
    """

    id: int
    name: str
    path: str
    web_url: str


class CreateRepositoryInput(BaseModel):
    """Input model for creating a new GitLab repository.

    Attributes:
        name: The name of the repository.
        description: Optional description of the repository.
        visibility: The visibility level of the repository (private, internal, public).
        initialize_with_readme: Whether to initialize the repository with a README file.
    """

    name: str
    description: str | None = None
    visibility: VisibilityLevel = VisibilityLevel.PRIVATE
    initialize_with_readme: bool = False


class GitLabRepository(GitLabResponseBase):
    """Response model for a GitLab repository.

    Attributes:
        id: The unique identifier of the repository.
        name: The name of the repository.
        path: The path of the repository.
        description: Optional description of the repository.
        web_url: The web URL of the repository.
        default_branch: The default branch of the repository.
    """

    id: int
    name: str
    path: str
    description: str | None = None
    web_url: str
    default_branch: str | None = None


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

    pass
