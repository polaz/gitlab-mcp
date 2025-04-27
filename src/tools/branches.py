import asyncio
from typing import cast

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.branches import (
    AccessLevel,
    AccessLevelModel,
    CreateBranchInput,
    DeleteBranchInput,
    DeleteMergedBranchesInput,
    GetBranchInput,
    GetDefaultBranchRefInput,
    ListBranchesInput,
    ProtectBranchInput,
    UnprotectBranchInput,
)
from src.services.branches import (
    create_branch,
    delete_branch,
    delete_merged_branches,
    get_branch,
    get_default_branch_ref,
    list_branches,
    protect_branch,
    unprotect_branch,
)


def create_branch_tool(project_path: str, branch_name: str, ref: str) -> dict:
    """Create a new branch in a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").
        branch_name (str): The name of the branch to create.
        ref (str): The reference (branch, tag, or commit) to create the branch from.

    Returns:
        dict: Details of the created branch.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = CreateBranchInput(
            project_path=project_path,
            branch_name=branch_name,
            ref=ref,
        )
        response = asyncio.run(create_branch(input_model))
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_default_branch_ref_tool(project_path: str) -> str:
    """Get the default branch reference for a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").

    Returns:
        str: The default branch reference.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = GetDefaultBranchRefInput(
            project_path=project_path,
        )
        return asyncio.run(get_default_branch_ref(input_model))
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_branches_tool(
    project_path: str, search: str | None = None
) -> list[dict]:
    """List branches in a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").
        search (str | None): Optional search pattern for branch names.

    Returns:
        list[dict]: List of branches matching the criteria.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = ListBranchesInput(
            project_path=project_path,
            search=search,
        )
        response = asyncio.run(list_branches(input_model))
        return [branch.model_dump() for branch in response.items]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_branch_tool(project_path: str, branch_name: str) -> dict:
    """Get details for a specific branch in a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").
        branch_name (str): The name of the branch to retrieve.

    Returns:
        dict: Details of the specified branch.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = GetBranchInput(
            project_path=project_path,
            branch_name=branch_name,
        )
        response = asyncio.run(get_branch(input_model))
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def delete_branch_tool(project_path: str, branch_name: str) -> None:
    """Delete a branch from a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").
        branch_name (str): The name of the branch to delete.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = DeleteBranchInput(
            project_path=project_path,
            branch_name=branch_name,
        )
        asyncio.run(delete_branch(input_model))
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def delete_merged_branches_tool(project_path: str) -> None:
    """Delete all merged branches from a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = DeleteMergedBranchesInput(
            project_path=project_path,
        )
        asyncio.run(delete_merged_branches(input_model))
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def protect_branch_tool(
    project_path: str,
    branch_name: str,
    allowed_to_push: list[int] | None = None,
    allowed_to_merge: list[int] | None = None,
    allow_force_push: bool = False,
    code_owner_approval_required: bool = False,
) -> None:
    """Protect a branch in a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").
        branch_name (str): The name of the branch to protect.
        allowed_to_push (list[int] | None): List of access levels allowed to push to the branch. Use values from AccessLevel enum.
        allowed_to_merge (list[int] | None): List of access levels allowed to merge to the branch. Use values from AccessLevel enum.
        allow_force_push (bool): Whether to allow force push to the branch.
        code_owner_approval_required (bool): Whether code owner approval is required.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        if allowed_to_push is None:
            allowed_to_push = [AccessLevel.MAINTAINER]
        if allowed_to_merge is None:
            allowed_to_merge = [AccessLevel.MAINTAINER]
        push_levels = [
            AccessLevelModel(access_level=cast(AccessLevel, level))
            for level in allowed_to_push
        ]
        merge_levels = [
            AccessLevelModel(access_level=cast(AccessLevel, level))
            for level in allowed_to_merge
        ]
        input_model = ProtectBranchInput(
            project_path=project_path,
            branch_name=branch_name,
            allowed_to_push=push_levels,
            allowed_to_merge=merge_levels,
            allow_force_push=allow_force_push,
            code_owner_approval_required=code_owner_approval_required,
        )
        asyncio.run(protect_branch(input_model))
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def unprotect_branch_tool(project_path: str, branch_name: str) -> None:
    """Unprotect a branch in a GitLab repository.

    Args:
        project_path (str): The path of the project (e.g., "namespace/project").
        branch_name (str): The name of the branch to unprotect.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = UnprotectBranchInput(
            project_path=project_path,
            branch_name=branch_name,
        )
        asyncio.run(unprotect_branch(input_model))
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
