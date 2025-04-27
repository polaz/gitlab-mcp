from typing import Any

from src.api.exceptions import GitLabAPIError
from src.schemas.repositories import CreateRepositoryInput
from src.services.repositories import create_repository, list_repository_tree


def create_repository_tool(
    name: str,
    description: str | None = None,
    visibility: str = "private",
    initialize_with_readme: bool = False,
) -> dict[str, Any]:
    """Create a new GitLab repository via the REST API."""
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
) -> list[dict[str, Any]]:
    """List repository tree for a project (files and directories)."""
    try:
        import asyncio

        result = asyncio.run(
            list_repository_tree(
                project_path=project_path,
                path=path,
                ref=ref,
                recursive=recursive,
                per_page=per_page,
                page_token=page_token,
            )
        )
        return result
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
