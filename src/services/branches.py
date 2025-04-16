from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.branches import (
    CreateBranchInput,
    GetDefaultBranchRefInput,
    GitLabReference,
)


def create_branch(input_model: CreateBranchInput) -> GitLabReference:
    """Create a new branch in a GitLab repository.

    Args:
        input_model: The input model containing project path, branch name, and ref.

    Returns:
        GitLabReference: The created branch details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Create the branch
        branch = project.branches.create(
            {
                "branch": input_model.branch_name,
                "ref": input_model.ref,
            }
        )

        # Map to our schema
        return GitLabReference(
            name=branch.name,
            commit={
                "id": branch.commit["id"],
                "short_id": branch.commit["short_id"],
                "title": branch.commit["title"],
                "message": branch.commit["message"],
                "author_name": branch.commit["author_name"],
                "created_at": branch.commit["created_at"],
            },
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_default_branch_ref(input_model: GetDefaultBranchRefInput) -> str:
    """Get the default branch reference for a GitLab repository.

    Args:
        input_model: The input model containing project path.

    Returns:
        str: The default branch reference.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc
    else:
        return project.default_branch


# Async versions of the functions
create_branch_async = to_async(create_branch)
get_default_branch_ref_async = to_async(get_default_branch_ref)
