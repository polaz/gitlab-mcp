"""Service functions for interacting with GitLab repositories using the REST API."""

import asyncio
from typing import Any

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.repositories import CreateRepositoryInput, GitLabRepository


async def create_repository(input_model: CreateRepositoryInput) -> GitLabRepository:
    """Create a new GitLab repository using the REST API.

    Args:
        input_model: The input model containing repository details.

    Returns:
        GitLabRepository: The created repository details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        payload = {
            "name": input_model.name,
            "description": input_model.description,
            "visibility": input_model.visibility.value,
            "initialize_with_readme": input_model.initialize_with_readme,
        }
        response = await gitlab_rest_client.post_async("/projects", json_data=payload)
        project = response.json()
        return GitLabRepository(
            id=project["id"],
            name=project["name"],
            path=project["path"],
            description=project.get("description"),
            web_url=project["web_url"],
            default_branch=project.get("default_branch"),
        )
    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Internal error creating repository: {exc!s}",
                "operation": "create_repository",
            },
        ) from exc


async def list_repository_tree(
    project_path: str,
    path: str | None = None,
    ref: str | None = None,
    recursive: bool = False,
    per_page: int = 20,
) -> list[dict[str, Any]]:
    """List files and directories in a repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        path: The path inside the repository (defaults to repository root).
        ref: The name of the branch, tag, or commit.
        recursive: Whether to get the contents recursively.
        per_page: Number of items to list per page.

    Returns:
        list[dict[str, Any]]: List of files and directories.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        encoded_path = gitlab_rest_client._encode_path_parameter(project_path)

        params: dict[str, Any] = {"per_page": per_page}
        if path:
            params["path"] = path
        if ref:
            params["ref"] = ref
        if recursive:
            params["recursive"] = str(recursive).lower()

        response = await gitlab_rest_client.get_async(
            f"/projects/{encoded_path}/repository/tree", params=params
        )

        return response
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Project {project_path} or path {path} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list repository contents for {project_path}",
                "operation": "list_repository_contents",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing repository contents",
                "operation": "list_repository_contents",
            },
        ) from exc
