# filepath: c:\Users\aditp\Desktop\python\gitlab-mcp-main\src\services\branches.py
"""Service functions for interacting with GitLab branches using the REST API."""

from typing import cast

from src.api.exceptions import (
    BranchCreationError,
    BranchDeleteError,
    BranchListError,
    BranchProtectionError,
    DefaultBranchError,
    MergedBranchesDeleteError,
)
from src.api.rest_client import gitlab_rest_client
from src.schemas.branches import (
    CreateBranchInput,
    DeleteBranchInput,
    DeleteMergedBranchesInput,
    GetBranchInput,
    GetDefaultBranchRefInput,
    GitLabBranchList,
    GitLabReference,
    ListBranchesInput,
    ProtectBranchInput,
    UnprotectBranchInput,
)


# Asynchronous implementations
async def create_branch(input_model: CreateBranchInput) -> GitLabReference:
    """Create a new branch in a GitLab repository using the REST API.

    Args:
        input_model: The input model containing project path, branch name, and ref.

    Returns:
        GitLabReference: The created branch details.

    Raises:
        BranchCreationError: If the branch creation operation fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        endpoint = f"/projects/{project_path}/repository/branches"
        payload = {"branch": input_model.branch_name, "ref": input_model.ref}

        data = await gitlab_rest_client.post_async(endpoint, json_data=payload)

        return GitLabReference(
            name=data["name"],
            commit=data["commit"],
        )
    except Exception as exc:
        raise BranchCreationError(cause=exc) from exc


async def get_default_branch_ref(input_model: GetDefaultBranchRefInput) -> str:
    """Get the default branch reference for a GitLab repository using the REST API.

    Args:
        input_model: The input model containing project path.

    Returns:
        str: The default branch reference.

    Raises:
        DefaultBranchError: If retrieving the default branch information fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        endpoint = f"/projects/{project_path}"

        data = await gitlab_rest_client.get_async(endpoint)
        return cast(str, data["default_branch"])
    except Exception as exc:
        raise DefaultBranchError(cause=exc) from exc


async def list_branches(input_model: ListBranchesInput) -> GitLabBranchList:
    """List branches in a GitLab repository.

    Args:
        input_model: The input model containing project path and optional search pattern.

    Returns:
        GitLabBranchList: List of branches in the repository.

    Raises:
        BranchListError: If listing branches fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        endpoint = f"/projects/{project_path}/repository/branches"

        params = {}
        if input_model.search:
            params["search"] = input_model.search

        data = await gitlab_rest_client.get_async(endpoint, params=params)

        branches = [GitLabReference(**branch) for branch in data]
        return GitLabBranchList(items=branches)
    except Exception as exc:
        raise BranchListError(cause=exc) from exc


async def get_branch(input_model: GetBranchInput) -> GitLabReference:
    """Get details for a specific branch in a GitLab repository.

    Args:
        input_model: The input model containing project path and branch name.

    Returns:
        GitLabReference: Details of the specified branch.

    Raises:
        BranchListError: If retrieving branch details fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        branch_name = gitlab_rest_client._encode_path_parameter(input_model.branch_name)
        endpoint = f"/projects/{project_path}/repository/branches/{branch_name}"

        data = await gitlab_rest_client.get_async(endpoint)

        return GitLabReference(**data)
    except Exception as exc:
        raise BranchListError(cause=exc) from exc


async def delete_branch(input_model: DeleteBranchInput) -> None:
    """Delete a branch from a GitLab repository.

    Args:
        input_model: The input model containing project path and branch name.

    Raises:
        BranchDeleteError: If deleting the branch fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        branch_name = gitlab_rest_client._encode_path_parameter(input_model.branch_name)
        endpoint = f"/projects/{project_path}/repository/branches/{branch_name}"

        await gitlab_rest_client.delete_async(endpoint)
    except Exception as exc:
        raise BranchDeleteError(cause=exc) from exc


async def delete_merged_branches(input_model: DeleteMergedBranchesInput) -> None:
    """Delete all merged branches from a GitLab repository.

    Args:
        input_model: The input model containing project path.

    Raises:
        MergedBranchesDeleteError: If deleting merged branches fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        endpoint = f"/projects/{project_path}/repository/merged_branches"

        await gitlab_rest_client.delete_async(endpoint)
    except Exception as exc:
        raise MergedBranchesDeleteError(cause=exc) from exc


async def protect_branch(input_model: ProtectBranchInput) -> None:
    """Protect a branch in a GitLab repository.

    Args:
        input_model: The input model with protection settings.

    Raises:
        BranchProtectionError: If protecting the branch fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        endpoint = f"/projects/{project_path}/protected_branches"

        # Transform the access levels to GitLab API format
        allowed_to_push = [
            {"access_level": level.access_level}
            for level in input_model.allowed_to_push
        ]

        allowed_to_merge = [
            {"access_level": level.access_level}
            for level in input_model.allowed_to_merge
        ]

        payload = {
            "name": input_model.branch_name,
            "allowed_to_push": allowed_to_push,
            "allowed_to_merge": allowed_to_merge,
            "allow_force_push": input_model.allow_force_push,
            "code_owner_approval_required": input_model.code_owner_approval_required,
        }

        await gitlab_rest_client.post_async(endpoint, json_data=payload)
    except Exception as exc:
        raise BranchProtectionError(cause=exc) from exc


async def unprotect_branch(input_model: UnprotectBranchInput) -> None:
    """Unprotect a branch in a GitLab repository.

    Args:
        input_model: The input model containing project path and branch name.

    Raises:
        BranchProtectionError: If unprotecting the branch fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        branch_name = gitlab_rest_client._encode_path_parameter(input_model.branch_name)
        endpoint = f"/projects/{project_path}/protected_branches/{branch_name}"

        await gitlab_rest_client.delete_async(endpoint)
    except Exception as exc:
        raise BranchProtectionError(cause=exc) from exc
