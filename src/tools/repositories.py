from typing import Any

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.repositories import CreateRepositoryInput
from src.services.repositories import create_repository, list_repository_tree


def create_repository_tool(
    name: str,
    description: str | None = None,
    visibility: str = "private",
    initialize_with_readme: bool = False,
) -> dict:
    """Create a new GitLab repository via the REST API.

    Args:
        name (str): Name of the repository.
        description (str, optional): Description of the repository.
        visibility (str, optional): Visibility level ('private', 'public', 'internal').
        initialize_with_readme (bool, optional): Whether to initialize with a README.

    Returns:
        dict: The created repository details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        from src.schemas.repositories import VisibilityLevel

        input_model = CreateRepositoryInput(
            name=name,
            description=description,
            visibility=VisibilityLevel(visibility),
            initialize_with_readme=initialize_with_readme,
        )
        repo = create_repository(input_model)
        return repo.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_repository_tree_tool(
    project_path: str,
    path: str | None = None,
    ref: str | None = None,
    recursive: bool = False,
    per_page: int = 20,
    page_token: str | None = None,
) -> list[dict]:
    """List repository tree for a project (files and directories).

    Args:
        project_path (str): Path of the project (e.g., 'namespace/project').
        path (str, optional): Path inside the repository (defaults to root).
        ref (str, optional): Branch, tag, or commit to list from.
        recursive (bool, optional): Whether to list recursively.
        per_page (int, optional): Number of items per page.
        page_token (str, optional): Token for pagination.

    Returns:
        list[dict]: List of files and directories as dictionaries.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        import asyncio
        result = asyncio.run(
            list_repository_tree(
                project_path=project_path,
                path=path,
                ref=ref,
                recursive=recursive,
                per_page=per_page,
            )
        )
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
    else:
        return result
