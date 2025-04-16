from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.repositories import (
    CreateRepositoryInput,
    ForkRepositoryInput,
    SearchProjectsInput,
    VisibilityLevel,
)
from ..services.repositories import (
    create_repository,
    fork_project,
    search_projects,
)


def _raise_invalid_visibility_error(visibility: str) -> None:
    """Helper function to raise invalid visibility error.

    Args:
        visibility: The invalid visibility value.

    Raises:
        ValueError: Always raised with appropriate message.
    """
    error_message = "Invalid repository visibility level"
    raise ValueError(error_message) from None


def fork_repository_tool(project_path: str, target_namespace: str) -> dict[str, Any]:
    """Fork a GitLab repository.

    Args:
        project_path: The path of the project to fork (e.g., 'namespace/project').
        target_namespace: The namespace where the fork will be created.

    Returns:
        dict[str, Any]: Details of the forked repository.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = ForkRepositoryInput(
            project_path=project_path,
            target_namespace=target_namespace,
        )

        # Call service function
        response = fork_project(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def create_repository_tool(
    name: str,
    namespace: str,
    visibility: str,
    description: str | None = None,
    initialize_with_readme: bool = False,
) -> dict[str, Any]:
    """Create a new GitLab repository.

    Args:
        name: The name of the repository.
        namespace: The namespace where the repository will be created.
        visibility: The visibility level of the repository (private, internal, public).
        description: Optional description of the repository.
        initialize_with_readme: Whether to initialize the repository with a README file.

    Returns:
        dict[str, Any]: Details of the created repository.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert visibility string to enum
        visibility_enum: (
            VisibilityLevel  # Type annotation to fix "possibly unbound" warning
        )

        try:
            visibility_enum = VisibilityLevel(value=visibility)
        except ValueError:
            _raise_invalid_visibility_error(visibility)
            # This line is unreachable but helps type checker understand control flow
            visibility_enum = VisibilityLevel.PRIVATE

        # Create input model
        input_model = CreateRepositoryInput(
            name=name,
            description=description,
            visibility=visibility_enum,
            initialize_with_readme=initialize_with_readme,
        )

        # Call service function
        response = create_repository(input_model=input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(object=exc)) from exc


def search_projects_tool(
    search_query: str,
    visibility: str | None = None,
    order_by: str | None = None,
    sort: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """Search for GitLab projects by name or keyword.

    Args:
        search_query: The search query.
        visibility: Optional filter for visibility level (private, internal, public).
        order_by: Optional field to order results by.
        sort: Optional sort direction (asc or desc).
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict[str, Any]: The search results.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = SearchProjectsInput(
            search=search_query,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = search_projects(input_model=input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(object=exc)) from exc
