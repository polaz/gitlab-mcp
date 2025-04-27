"""Services for interacting with GitLab merge requests."""

from dataclasses import dataclass
from typing import Any, cast

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.merge_requests import (
    AcceptedMergeRequest,
    CreateMergeRequestInput,
    GitLabComment,
    GitLabMergeRequest,
    GitLabMergeRequestListResponse,
    ListMergeRequestsInput,
    MergeRequestChanges,
    MergeRequestSuggestion,
)


@dataclass
class MergeOptions:
    """Options for merging a merge request."""

    merge_commit_message: str | None = None
    squash_commit_message: str | None = None
    auto_merge: bool | None = None
    should_remove_source_branch: bool | None = None
    sha: str | None = None
    squash: bool | None = None


async def create_merge_request(
    input_model: CreateMergeRequestInput,
) -> GitLabMergeRequest:
    """Create a new merge request.

    Args:
        input_model: The input model containing merge request details.

    Returns:
        GitLabMergeRequest: The created merge request details.

    Raises:
        GitLabAPIError: If creating the merge request fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        payload = input_model.model_dump(exclude={"project_path"})

        response = await gitlab_rest_client.post_async(
            f"/projects/{project_path}/merge_requests", json_data=payload
        )

        return GitLabMergeRequest.model_validate(response)
    except GitLabAPIError as exc:
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": "Failed to create merge request",
                "operation": "create_merge_request",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error creating merge request",
                "operation": "create_merge_request",
            },
        ) from exc


async def list_merge_requests(
    input_model: ListMergeRequestsInput,
) -> GitLabMergeRequestListResponse:
    """List merge requests for a project.

    Args:
        input_model: The input model containing query parameters.

    Returns:
        GitLabMergeRequestListResponse: A list of merge requests.

    Raises:
        GitLabAPIError: If retrieving the merge requests fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        params = input_model.model_dump(
            exclude={"project_path"},
            exclude_none=True,
        )

        # Convert state enum to string if present
        if "state" in params and params["state"] is not None:
            params["state"] = params["state"].value

        # Convert labels list to comma-separated string if present
        if "labels" in params and params["labels"] is not None:
            params["labels"] = ",".join(params["labels"])

        response = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/merge_requests",
            params=params,
        )

        return GitLabMergeRequestListResponse(
            items=[GitLabMergeRequest.model_validate(mr) for mr in response]
        )
    except GitLabAPIError as exc:
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list merge requests for project {input_model.project_path}",
                "operation": "list_merge_requests",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing merge requests",
                "operation": "list_merge_requests",
            },
        ) from exc


async def get_merge_request(
    project_path: str,
    mr_iid: int,
    include_diverged_commits_count: bool = False,
    include_rebase_in_progress: bool = False,
    render_html: bool = False,
) -> GitLabMergeRequest:
    """Get a specific merge request.

    Args:
        project_path: The path of the project.
        mr_iid: The internal ID of the merge request.
        include_diverged_commits_count: Whether to include the count of diverged commits.
        include_rebase_in_progress: Whether to include rebase in progress status.
        render_html: Whether to render HTML for title and description.

    Returns:
        GitLabMergeRequest: The merge request details.

    Raises:
        GitLabAPIError: If retrieving the merge request fails.
    """
    try:
        project_path_encoded = gitlab_rest_client._encode_path_parameter(project_path)

        params = {
            "include_diverged_commits_count": include_diverged_commits_count,
            "include_rebase_in_progress": include_rebase_in_progress,
            "render_html": render_html,
        }

        response = await gitlab_rest_client.get_async(
            f"/projects/{project_path_encoded}/merge_requests/{mr_iid}",
            params=params,
        )

        return GitLabMergeRequest.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Merge request {mr_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get merge request {mr_iid}",
                "operation": "get_merge_request",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error getting merge request",
                "operation": "get_merge_request",
            },
        ) from exc


async def update_merge_request(
    project_path: str, mr_iid: int, **kwargs: Any
) -> GitLabMergeRequest:
    """Update a merge request.

    Args:
        project_path: The path of the project.
        mr_iid: The internal ID of the merge request.
        **kwargs: Fields to update.

    Returns:
        GitLabMergeRequest: The updated merge request details.

    Raises:
        GitLabAPIError: If updating the merge request fails.
    """
    try:
        project_path_encoded = gitlab_rest_client._encode_path_parameter(project_path)

        # Convert labels list to comma-separated string if present
        if "labels" in kwargs and kwargs["labels"] is not None:
            kwargs["labels"] = ",".join(kwargs["labels"])

        # Handle add/remove labels lists
        if "add_labels" in kwargs and kwargs["add_labels"] is not None:
            kwargs["add_labels"] = ",".join(kwargs["add_labels"])
        if "remove_labels" in kwargs and kwargs["remove_labels"] is not None:
            kwargs["remove_labels"] = ",".join(kwargs["remove_labels"])

        response = await gitlab_rest_client.put_async(
            f"/projects/{project_path_encoded}/merge_requests/{mr_iid}",
            json_data=kwargs,
        )

        return GitLabMergeRequest.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Merge request {mr_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to update merge request {mr_iid}",
                "operation": "update_merge_request",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error updating merge request",
                "operation": "update_merge_request",
            },
        ) from exc


async def delete_merge_request(project_path: str, mr_iid: int) -> None:
    """Delete a merge request.

    Args:
        project_path: The path of the project.
        mr_iid: The internal ID of the merge request.

    Raises:
        GitLabAPIError: If deleting the merge request fails.
    """
    try:
        project_path_encoded = gitlab_rest_client._encode_path_parameter(project_path)

        await gitlab_rest_client.delete_async(
            f"/projects/{project_path_encoded}/merge_requests/{mr_iid}"
        )
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Merge request {mr_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to delete merge request {mr_iid}",
                "operation": "delete_merge_request",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error deleting merge request",
                "operation": "delete_merge_request",
            },
        ) from exc


async def merge_request_changes(project_path: str, mr_iid: int) -> MergeRequestChanges:
    """Get the changes of a merge request.

    Args:
        project_path: The path of the project.
        mr_iid: The internal ID of the merge request.

    Returns:
        MergeRequestChanges: The changes in the merge request.

    Raises:
        GitLabAPIError: If retrieving the changes fails.
    """
    try:
        project_path_encoded = gitlab_rest_client._encode_path_parameter(project_path)

        response = await gitlab_rest_client.get_async(
            f"/projects/{project_path_encoded}/merge_requests/{mr_iid}/changes"
        )

        return MergeRequestChanges.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Merge request {mr_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get changes for merge request {mr_iid}",
                "operation": "merge_request_changes",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error getting merge request changes",
                "operation": "merge_request_changes",
            },
        ) from exc


async def merge_merge_request(
    project_path: str, mr_iid: int, options: MergeOptions | None = None
) -> AcceptedMergeRequest:
    """Merge a merge request.

    Args:
        project_path: The path of the project.
        mr_iid: The internal ID of the merge request.
        options: Options for merging the merge request.

    Returns:
        AcceptedMergeRequest: The merged merge request details.

    Raises:
        GitLabAPIError: If merging the merge request fails.
    """
    try:
        project_path_encoded = gitlab_rest_client._encode_path_parameter(project_path)

        if options is None:
            options = MergeOptions()

        payload = {
            "merge_commit_message": options.merge_commit_message,
            "squash_commit_message": options.squash_commit_message,
            "auto_merge": options.auto_merge,
            "should_remove_source_branch": options.should_remove_source_branch,
            "sha": options.sha,
            "squash": options.squash,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        response = await gitlab_rest_client.put_async(
            f"/projects/{project_path_encoded}/merge_requests/{mr_iid}/merge",
            json_data=payload,
        )

        return AcceptedMergeRequest.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Merge request {mr_iid} not found"},
            ) from exc
        if (
            "cannot be merged" in str(exc).lower()
            or "is not mergeable" in str(exc).lower()
        ):
            raise GitLabAPIError(
                GitLabErrorType.INVALID_REQUEST,
                {
                    "message": f"Merge request {mr_iid} cannot be merged",
                    "details": str(exc),
                },
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to merge merge request {mr_iid}",
                "operation": "merge_merge_request",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error merging merge request",
                "operation": "merge_merge_request",
            },
        ) from exc


async def create_merge_request_comment(
    project_path: str, mr_iid: int, body: str
) -> GitLabComment:
    """Create a comment on a merge request.

    Args:
        project_path: The path of the project.
        mr_iid: The internal ID of the merge request.
        body: The content of the comment.

    Returns:
        GitLabComment: The created comment.

    Raises:
        GitLabAPIError: If creating the comment fails.
    """
    try:
        project_path_encoded = gitlab_rest_client._encode_path_parameter(project_path)

        response = await gitlab_rest_client.post_async(
            f"/projects/{project_path_encoded}/merge_requests/{mr_iid}/notes",
            json_data={"body": body},
        )

        return GitLabComment.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Merge request {mr_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to comment on merge request {mr_iid}",
                "operation": "create_merge_request_comment",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error creating merge request comment",
                "operation": "create_merge_request_comment",
            },
        ) from exc


async def create_merge_request_thread(
    project_path: str, mr_iid: int, body: str, position: dict[str, Any]
) -> dict[str, Any]:
    """Create a thread on a merge request.

    Args:
        project_path: The path of the project.
        mr_iid: The internal ID of the merge request.
        body: The content of the thread.
        position: The position in the diff where the thread should be placed.

    Returns:
        dict[str, Any]: The created thread.

    Raises:
        GitLabAPIError: If creating the thread fails.
    """
    try:
        project_path_encoded = gitlab_rest_client._encode_path_parameter(project_path)

        payload = {
            "body": body,
            "position": position,
        }

        response = await gitlab_rest_client.post_async(
            f"/projects/{project_path_encoded}/merge_requests/{mr_iid}/discussions",
            json_data=payload,
        )

        return cast(dict[str, Any], response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Merge request {mr_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to create thread on merge request {mr_iid}",
                "operation": "create_merge_request_thread",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error creating merge request thread",
                "operation": "create_merge_request_thread",
            },
        ) from exc


async def apply_suggestion(
    suggestion_id: int, commit_message: str | None = None
) -> MergeRequestSuggestion:
    """Apply a suggestion to a merge request.

    Args:
        suggestion_id: The ID of the suggestion.
        commit_message: The commit message for applying the suggestion.

    Returns:
        MergeRequestSuggestion: The suggestion details.

    Raises:
        GitLabAPIError: If applying the suggestion fails.
    """
    try:
        payload: dict[str, Any] = {}
        if commit_message:
            payload["commit_message"] = commit_message

        response = await gitlab_rest_client.put_async(
            f"/suggestions/{suggestion_id}/apply",
            json_data=payload,
        )

        return MergeRequestSuggestion.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Suggestion {suggestion_id} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to apply suggestion {suggestion_id}",
                "operation": "apply_suggestion",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error applying suggestion",
                "operation": "apply_suggestion",
            },
        ) from exc


async def apply_multiple_suggestions(
    ids: list[int], commit_message: str | None = None
) -> list[MergeRequestSuggestion]:
    """Apply multiple suggestions to a merge request.

    Args:
        ids: The IDs of the suggestions.
        commit_message: The commit message for applying the suggestions.

    Returns:
        list[MergeRequestSuggestion]: The suggestions details.

    Raises:
        GitLabAPIError: If applying the suggestions fails.
    """
    try:
        payload: dict[str, Any] = {"ids": ids}
        if commit_message:
            payload["commit_message"] = commit_message

        response = await gitlab_rest_client.put_async(
            "/suggestions/batch_apply",
            json_data=payload,
        )

        return [MergeRequestSuggestion.model_validate(sugg) for sugg in response]
    except GitLabAPIError as exc:
        id_list = ", ".join(str(id_) for id_ in ids)
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"One or more suggestions not found: {id_list}"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to apply suggestions: {id_list}",
                "operation": "apply_multiple_suggestions",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error applying multiple suggestions",
                "operation": "apply_multiple_suggestions",
            },
        ) from exc
