"""Tools for interacting with GitLab merge requests."""

import asyncio
from typing import Any

from ..schemas.merge_requests import (
    ApplyMultipleSuggestionsInput,
    ApplySuggestionInput,
    CreateMergeRequestCommentInput,
    CreateMergeRequestInput,
    CreateMergeRequestThreadInput,
    GetMergeRequestInput,
    ListMergeRequestsInput,
    MergeMergeRequestInput,
    UpdateMergeRequestInput,
)
from ..services import merge_requests as service


def _sanitize_user_data(data: dict) -> dict:
    """Remove sensitive user information from response data.

    Args:
        data: Response data dictionary.

    Returns:
        Sanitized data with sensitive user info removed.
    """
    user_fields = ["author", "reviewers", "assignees", "merge_user"]

    result = data.copy()
    for field in user_fields:
        if field in result:
            del result[field]

    return result


async def create_merge_request_tool(input_model: dict) -> dict:
    """Create a new merge request.

    Args:
        input_model: Dictionary containing merge request details.

    Returns:
        dict: The created merge request.
    """
    validated_input = CreateMergeRequestInput.model_validate(input_model)
    result = await service.create_merge_request(validated_input)
    return _sanitize_user_data(result.model_dump())


def create_merge_request_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for creating a merge request.

    Args:
        input_model: Dictionary containing merge request details.

    Returns:
        dict: The created merge request.
    """
    return asyncio.run(create_merge_request_tool(input_model))


async def list_merge_requests_tool(input_model: dict) -> dict:
    """List merge requests for a project.

    Args:
        input_model: Dictionary containing query parameters.

    Returns:
        dict: List of merge requests.
    """
    validated_input = ListMergeRequestsInput.model_validate(input_model)
    result = await service.list_merge_requests(validated_input)

    # Sanitize user data in each merge request
    sanitized_items = [_sanitize_user_data(mr.model_dump()) for mr in result.items]

    return {"items": sanitized_items}


def list_merge_requests_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for listing merge requests.

    Args:
        input_model: Dictionary containing query parameters.

    Returns:
        dict: List of merge requests.
    """
    return asyncio.run(list_merge_requests_tool(input_model))


async def get_merge_request_tool(input_model: dict) -> dict:
    """Get a specific merge request.

    Args:
        input_model: Dictionary containing project_path and mr_iid.

    Returns:
        dict: The merge request details.
    """
    validated_input = GetMergeRequestInput.model_validate(input_model)
    result = await service.get_merge_request(
        validated_input.project_path,
        validated_input.mr_iid,
        validated_input.include_diverged_commits_count or False,
        validated_input.include_rebase_in_progress or False,
        validated_input.render_html or False,
    )
    return _sanitize_user_data(result.model_dump())


def get_merge_request_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for getting a merge request.

    Args:
        input_model: Dictionary containing project_path and mr_iid.

    Returns:
        dict: The merge request details.
    """
    return asyncio.run(get_merge_request_tool(input_model))


async def update_merge_request_tool(input_model: dict) -> dict:
    """Update a merge request.

    Args:
        input_model: Dictionary containing project_path, mr_iid, and fields to update.

    Returns:
        dict: The updated merge request details.
    """
    validated_input = UpdateMergeRequestInput.model_validate(input_model)
    update_data = validated_input.model_dump(
        exclude={"project_path", "mr_iid"}, exclude_none=True
    )

    result = await service.update_merge_request(
        validated_input.project_path, validated_input.mr_iid, **update_data
    )
    return _sanitize_user_data(result.model_dump())


def update_merge_request_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for updating a merge request.

    Args:
        input_model: Dictionary containing project_path, mr_iid, and fields to update.

    Returns:
        dict: The updated merge request details.
    """
    return asyncio.run(update_merge_request_tool(input_model))


async def delete_merge_request_tool(input_model: dict) -> dict:
    """Delete a merge request.

    Args:
        input_model: Dictionary containing project_path and mr_iid.

    Returns:
        dict: Empty success response.
    """
    project_path = input_model["project_path"]
    mr_iid = input_model["mr_iid"]

    await service.delete_merge_request(project_path, mr_iid)
    return {"success": True}


def delete_merge_request_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for deleting a merge request.

    Args:
        input_model: Dictionary containing project_path and mr_iid.

    Returns:
        dict: Empty success response.
    """
    return asyncio.run(delete_merge_request_tool(input_model))


async def merge_request_changes_tool(input_model: dict) -> dict:
    """Get the changes of a merge request.

    Args:
        input_model: Dictionary containing project_path and mr_iid.

    Returns:
        dict: The changes in the merge request.
    """
    project_path = input_model["project_path"]
    mr_iid = input_model["mr_iid"]

    result = await service.merge_request_changes(project_path, mr_iid)
    return result.model_dump()


def merge_request_changes_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for getting merge request changes.

    Args:
        input_model: Dictionary containing project_path and mr_iid.

    Returns:
        dict: The changes in the merge request.
    """
    return asyncio.run(merge_request_changes_tool(input_model))


async def merge_merge_request_tool(input_model: dict) -> dict:
    """Merge a merge request.

    Args:
        input_model: Dictionary containing merge details.

    Returns:
        dict: The merged merge request details.
    """
    validated_input = MergeMergeRequestInput.model_validate(input_model)

    # Create merge options
    merge_options = service.MergeOptions(
        merge_commit_message=validated_input.merge_commit_message,
        squash_commit_message=validated_input.squash_commit_message,
        auto_merge=validated_input.auto_merge,
        should_remove_source_branch=validated_input.should_remove_source_branch,
        sha=validated_input.sha,
        squash=validated_input.squash,
    )

    result = await service.merge_merge_request(
        validated_input.project_path, validated_input.mr_iid, merge_options
    )
    return _sanitize_user_data(result.model_dump())


def merge_merge_request_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for merging a merge request.

    Args:
        input_model: Dictionary containing merge details.

    Returns:
        dict: The merged merge request details.
    """
    return asyncio.run(merge_merge_request_tool(input_model))


async def create_merge_request_comment_tool(input_model: dict) -> dict:
    """Create a comment on a merge request.

    Args:
        input_model: Dictionary containing project_path, mr_iid, and body.

    Returns:
        dict: The created comment.
    """
    validated_input = CreateMergeRequestCommentInput.model_validate(input_model)

    result = await service.create_merge_request_comment(
        validated_input.project_path,
        validated_input.mr_iid,
        validated_input.body,
    )

    # Remove author information from the comment
    comment_data = result.model_dump()
    if "author" in comment_data:
        del comment_data["author"]

    return comment_data


def create_merge_request_comment_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for creating a merge request comment.

    Args:
        input_model: Dictionary containing project_path, mr_iid, and body.

    Returns:
        dict: The created comment.
    """
    return asyncio.run(create_merge_request_comment_tool(input_model))


async def create_merge_request_thread_tool(input_model: dict) -> dict:
    """Create a thread on a merge request.

    Args:
        input_model: Dictionary containing project_path, mr_iid, body, and position.

    Returns:
        dict: The created thread.
    """
    validated_input = CreateMergeRequestThreadInput.model_validate(input_model)

    result = await service.create_merge_request_thread(
        validated_input.project_path,
        validated_input.mr_iid,
        validated_input.body,
        validated_input.position,
    )

    # Sanitize author information in the thread
    if "notes" in result and isinstance(result["notes"], list):
        for note in result["notes"]:
            if "author" in note:
                del note["author"]

    return result


def create_merge_request_thread_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for creating a merge request thread.

    Args:
        input_model: Dictionary containing project_path, mr_iid, body, and position.

    Returns:
        dict: The created thread.
    """
    return asyncio.run(create_merge_request_thread_tool(input_model))


async def apply_suggestion_tool(input_model: dict) -> dict:
    """Apply a suggestion to a merge request.

    Args:
        input_model: Dictionary containing suggestion_id and commit_message.

    Returns:
        dict: The suggestion details.
    """
    validated_input = ApplySuggestionInput.model_validate(input_model)

    result = await service.apply_suggestion(
        validated_input.id,
        validated_input.commit_message,
    )
    return result.model_dump()


def apply_suggestion_tool_sync(input_model: dict) -> dict:
    """Synchronous wrapper for applying a suggestion.

    Args:
        input_model: Dictionary containing suggestion_id and commit_message.

    Returns:
        dict: The suggestion details.
    """
    return asyncio.run(apply_suggestion_tool(input_model))


async def apply_multiple_suggestions_tool(input_model: dict) -> list[dict[str, Any]]:
    """Apply multiple suggestions to a merge request.

    Args:
        input_model: Dictionary containing ids and commit_message.

    Returns:
        list[dict[str, Any]]: The suggestions details.
    """
    validated_input = ApplyMultipleSuggestionsInput.model_validate(input_model)

    results = await service.apply_multiple_suggestions(
        validated_input.ids,
        validated_input.commit_message,
    )
    return [result.model_dump() for result in results]


def apply_multiple_suggestions_tool_sync(input_model: dict) -> list[dict[str, Any]]:
    """Synchronous wrapper for applying multiple suggestions.

    Args:
        input_model: Dictionary containing ids and commit_message.

    Returns:
        list[dict[str, Any]]: The suggestions details.
    """
    return asyncio.run(apply_multiple_suggestions_tool(input_model))
