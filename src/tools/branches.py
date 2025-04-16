from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.branches import (
    CreateBranchInput,
    GetDefaultBranchRefInput,
)
from ..services.branches import (
    create_branch,
    get_default_branch_ref,
)


def create_branch_tool(project_path: str, branch_name: str, ref: str) -> dict[str, Any]:
    """Create a new branch in a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        branch_name: The name of the branch to create.
        ref: The reference (branch, tag, or commit) to create the branch from.

    Returns:
        dict[str, Any]: Details of the created branch.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = CreateBranchInput(
            project_path=project_path,
            branch_name=branch_name,
            ref=ref,
        )

        # Call service function
        response = create_branch(input_model=input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(object=exc)) from exc


def get_default_branch_ref_tool(project_path: str) -> str:
    """Get the default branch reference for a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').

    Returns:
        str: The default branch reference.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetDefaultBranchRefInput(
            project_path=project_path,
        )

        # Call service function
        return get_default_branch_ref(input_model=input_model)
    except GitLabAPIError as exc:
        raise ValueError(str(object=exc)) from exc
