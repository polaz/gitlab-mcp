import asyncio
from typing import Any

from src.api.exceptions import GitLabAPIError
from src.api.rest_client import gitlab_rest_client
from src.schemas.repositories import CreateRepositoryInput, GitLabRepository


def create_repository(input_model: CreateRepositoryInput) -> GitLabRepository:
    """Create a new GitLab repository using the REST API.

    Args:
        input_model: The input model containing repository details.

    Returns:
        GitLabRepository: The created repository details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """

    def raise_api_error(project: dict[str, Any]) -> None:
        raise GitLabAPIError(project.get("message", str(project)))

    try:
        data = {
            "name": input_model.name,
            "description": input_model.description,
            "visibility": input_model.visibility.value,
            "initialize_with_readme": input_model.initialize_with_readme,
        }
        client = gitlab_rest_client.get_httpx_client()
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            client.post(
                "/projects",
                headers=gitlab_rest_client._get_headers(),
                json=data,
            )
        )
        project = response.json()
        if response.status_code not in (200, 201):
            raise_api_error(project)
        return GitLabRepository(
            id=project["id"],
            name=project["name"],
            path=project["path"],
            description=project.get("description"),
            web_url=project["web_url"],
            default_branch=project.get("default_branch"),
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


async def list_repository_tree(
    project_path: str,
    path: str | None = None,
    ref: str | None = None,
    recursive: bool = False,
    per_page: int = 20,
    page_token: str | None = None,
) -> list[dict[str, Any]]:
    """List repository tree for a project (files and directories).

    Args:
        project_path: The path or ID of the project.
        path: The path inside the repository (subdirectory).
        ref: The branch or tag name.
        recursive: Whether to get a recursive tree.
        per_page: Number of results per page.
        page_token: Keyset pagination token (if using keyset pagination).

    Returns:
        List of dicts representing files and directories in the repository tree.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    encoded_path = gitlab_rest_client._encode_path_parameter(project_path)
    params: dict[str, Any] = {"per_page": per_page}
    if path:
        params["path"] = path
    if ref:
        params["ref"] = ref
    if recursive:
        params["recursive"] = True
    if page_token:
        params["page_token"] = page_token
        params["pagination"] = "keyset"
    try:
        return await gitlab_rest_client.get_async(
            f"/projects/{encoded_path}/repository/tree", params=params
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc
