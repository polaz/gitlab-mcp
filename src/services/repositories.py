"""Service functions for interacting with GitLab repositories using the REST API."""

from typing import Any

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.repositories import (
    CreateRepositoryInput,
    DeleteRepositoryInput,
    GetRepositoryInput,
    ListRepositoriesInput,
    ListRepositoryTreeInput,
    RepositoryTreeResponse,
    UpdateRepositoryInput,
)


async def create_repository(input_model: CreateRepositoryInput) -> dict[str, Any]:
    """Create a new GitLab repository using the REST API.

    Args:
        input_model: The input model containing repository details.

    Returns:
        dict[str, Any]: The created repository details as raw GitLab API response.

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
        if input_model.namespace_id:
            payload["namespace_id"] = input_model.namespace_id
        response = await gitlab_rest_client.post_async("/projects", json_data=payload)
        return response
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
    input_model: ListRepositoryTreeInput,
) -> RepositoryTreeResponse:
    """List files and directories in a repository.

    Args:
        input_model: Input parameters containing project path and optional filters.

    Returns:
        RepositoryTreeResponse: A response containing the list of files and directories.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        encoded_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        params: dict[str, Any] = {"per_page": input_model.per_page}
        if input_model.ref:
            params["ref"] = input_model.ref
        if input_model.recursive:
            params["recursive"] = str(input_model.recursive).lower()

        response = await gitlab_rest_client.get_async(
            f"/projects/{encoded_path}/repository/tree", params=params
        )

        return response
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Project {input_model.project_path} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list repository contents for {input_model.project_path}",
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


async def get_repository(input_model: GetRepositoryInput) -> dict[str, Any]:
    """Get a specific GitLab repository using the REST API.

    Args:
        input_model: The input model containing project path.

    Returns:
        dict[str, Any]: The repository details as raw GitLab API response.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        encoded_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
        response = await gitlab_rest_client.get_async(f"/projects/{encoded_path}")
        return response
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Repository {input_model.project_path} not found"},
            ) from exc
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Internal error retrieving repository: {exc!s}",
                "operation": "get_repository",
            },
        ) from exc


async def list_repositories(input_model: ListRepositoriesInput) -> list[dict[str, Any]]:
    """List GitLab repositories using the REST API.

    Args:
        input_model: The input model containing listing parameters.

    Returns:
        list[dict[str, Any]]: List of repositories as raw GitLab API responses.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        params = {
            "page": input_model.page,
            "per_page": input_model.per_page,
        }

        # Determine the endpoint based on whether we're filtering by group
        if input_model.group_id:
            # Use group-specific endpoint for group projects
            encoded_group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
            endpoint = f"/groups/{encoded_group_id}/projects"
            # Group endpoint supports different parameters
            if input_model.search:
                params["search"] = input_model.search
        else:
            # Use general projects endpoint
            endpoint = "/projects"
            if input_model.owned:
                params["owned"] = "true"
            if input_model.starred:
                params["starred"] = "true"
            if input_model.search:
                params["search"] = input_model.search

        response = await gitlab_rest_client.get_async(endpoint, params=params)

        return response
    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Internal error listing repositories: {exc!s}",
                "operation": "list_repositories",
            },
        ) from exc


async def update_repository(input_model: UpdateRepositoryInput) -> dict[str, Any]:
    """Update a GitLab repository using the REST API.

    Args:
        input_model: The input model containing update parameters.

    Returns:
        dict[str, Any]: The updated repository details as raw GitLab API response.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        encoded_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

        payload = {}
        if input_model.name:
            payload["name"] = input_model.name
        if input_model.description is not None:
            payload["description"] = input_model.description
        if input_model.visibility:
            payload["visibility"] = input_model.visibility.value
        if input_model.default_branch:
            payload["default_branch"] = input_model.default_branch

        response = await gitlab_rest_client.put_async(f"/projects/{encoded_path}", json_data=payload)
        return response
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Repository {input_model.project_path} not found"},
            ) from exc
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Internal error updating repository: {exc!s}",
                "operation": "update_repository",
            },
        ) from exc


async def delete_repository(input_model: DeleteRepositoryInput) -> bool:
    """Delete a GitLab repository using the REST API.

    Args:
        input_model: The input model containing project path.

    Returns:
        bool: True if repository was deleted successfully.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        encoded_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
        await gitlab_rest_client.delete_async(f"/projects/{encoded_path}")
        return True
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Repository {input_model.project_path} not found"},
            ) from exc
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Internal error deleting repository: {exc!s}",
                "operation": "delete_repository",
            },
        ) from exc
