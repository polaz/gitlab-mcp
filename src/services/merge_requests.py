from gitlab.base import RESTObject
from gitlab.v4.objects import MergeRequest, ProjectMergeRequestNote

from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.filters import MergeRequestFilterParams
from ..schemas.merge_requests import (
    ApproveMergeRequestInput,
    CloseMergeRequestInput,
    CreateMergeRequestCommentInput,
    CreateMergeRequestInput,
    GetMergeRequestDiffInput,
    GetMergeRequestInput,
    GitLabComment,
    GitLabCommentListResponse,
    GitLabMergeRequest,
    GitLabMergeRequestChangesResponse,
    GitLabMergeRequestDiffResponse,
    GitLabMergeRequestListResponse,
    ListMergeRequestCommentsInput,
    ListMergeRequestsInput,
    MergeMergeRequestInput,
    SuggestMergeRequestCodeInput,
)


def _map_mr_to_schema(mr: MergeRequest | RESTObject) -> GitLabMergeRequest:
    """Map a GitLab merge request object to our schema.

    Args:
        mr: The GitLab merge request object.

    Returns:
        GitLabMergeRequest: The mapped merge request schema.
    """
    return GitLabMergeRequest(
        id=mr.id,
        iid=mr.iid,
        title=mr.title,
        description=mr.description,
        web_url=mr.web_url,
    )


def _map_comment_to_schema(
    comment: ProjectMergeRequestNote | RESTObject,
) -> GitLabComment:
    """Map a GitLab comment object to our schema.

    Args:
        comment: The GitLab comment object, either a ProjectMergeRequestNote or RESTObject.

    Returns:
        GitLabComment: The mapped comment schema.
    """
    return GitLabComment(
        id=comment.id,
        body=comment.body,
        author={
            "id": comment.author["id"],
            "name": comment.author["name"],
            "username": comment.author["username"],
        },
        created_at=comment.created_at,
        updated_at=comment.updated_at if hasattr(comment, "updated_at") else None,
    )


def _format_suggestion_body(suggested_code: str, comment: str) -> str:
    """Format a suggestion body according to GitLab's syntax.

    Args:
        suggested_code: The suggested code.
        comment: The comment explaining the suggestion.

    Returns:
        str: The formatted suggestion body.
    """
    # Format according to GitLab's suggestion syntax
    return f"{comment}\n\n```suggestion\n{suggested_code}\n```"


def _raise_file_not_found_error(file_path: str, mr_iid: int) -> None:
    """Helper function to raise file not found error.

    Args:
        file_path: The path of the file that was not found.
        mr_iid: The merge request IID.

    Raises:
        GitLabAPIError: Always raised with appropriate message.
    """
    error_message = "File not found in merge request"
    raise GitLabAPIError(error_message)


def create_merge_request(input_model: CreateMergeRequestInput) -> GitLabMergeRequest:
    """Create a merge request in a GitLab repository.

    Args:
        input_model: The input model containing merge request details.

    Returns:
        GitLabMergeRequest: The created merge request details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Create the merge request
        mr = project.mergerequests.create(
            {
                "source_branch": input_model.source_branch,
                "target_branch": input_model.target_branch,
                "title": input_model.title,
                "description": input_model.description,
            }
        )

        # Map to our schema
        return _map_mr_to_schema(mr)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def list_merge_requests(
    input_model: ListMergeRequestsInput,
) -> GitLabMergeRequestListResponse:
    """List merge requests in a GitLab repository.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabMergeRequestListResponse: The list of merge requests.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Convert input model to filter params
        filter_params = MergeRequestFilterParams(
            page=input_model.page,
            per_page=input_model.per_page,
            state=input_model.state,
            labels=input_model.labels,
            order_by=input_model.order_by,
            sort=input_model.sort,
        )

        # Convert to dict, excluding None values
        filters = filter_params.model_dump(exclude_none=True)

        # Get the merge requests
        mrs = project.mergerequests.list(**filters)

        # Map to our schema
        items = [_map_mr_to_schema(mr) for mr in mrs if hasattr(mr, "attributes")]

        return GitLabMergeRequestListResponse(
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_merge_request(input_model: GetMergeRequestInput) -> GitLabMergeRequest:
    """Get a specific merge request from a GitLab repository.

    Args:
        input_model: The input model containing project path and merge request IID.

    Returns:
        GitLabMergeRequest: The merge request details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Map to our schema
        return _map_mr_to_schema(mr)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def comment_on_merge_request(
    input_model: CreateMergeRequestCommentInput,
) -> GitLabComment:
    """Add a comment to a GitLab merge request.

    Args:
        input_model: The input model containing project path, merge request IID, and comment body.

    Returns:
        GitLabComment: The created comment details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Create the comment
        comment = mr.notes.create({"body": input_model.body})

        # Map to our schema
        return _map_comment_to_schema(comment)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def list_merge_request_comments(
    input_model: ListMergeRequestCommentsInput,
) -> GitLabCommentListResponse:
    """List comments on a GitLab merge request.

    Args:
        input_model: The input model containing project path, merge request IID, and pagination parameters.

    Returns:
        GitLabCommentListResponse: The list of comments.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Get the comments
        comments = mr.notes.list(
            page=input_model.page,
            per_page=input_model.per_page,
        )

        # Map to our schema
        items = [_map_comment_to_schema(comment) for comment in comments]

        return GitLabCommentListResponse(
            count=len(items),
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def list_merge_request_changes(
    input_model: GetMergeRequestInput,
) -> GitLabMergeRequestChangesResponse:
    """List files changed in a GitLab merge request.

    Args:
        input_model: The input model containing project path and merge request IID.

    Returns:
        GitLabMergeRequestChangesResponse: The list of changed files.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Get the changes
        changes_data = mr.changes()

        # Extract changes data based on the return type
        if isinstance(changes_data, dict):
            changes_list = changes_data.get("changes", [])
        else:
            # Assuming it's a response object with json method
            changes_list = changes_data.json().get("changes", [])

        # Map to our schema
        return GitLabMergeRequestChangesResponse(
            mr_iid=input_model.mr_iid,
            files=changes_list,
            total_count=len(changes_list),
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_merge_request_diff(
    input_model: GetMergeRequestDiffInput,
) -> GitLabMergeRequestDiffResponse:
    """Get the diff of a specific file in a GitLab merge request.

    Args:
        input_model: The input model containing project path, merge request IID, and file path.

    Returns:
        GitLabMergeRequestDiffResponse: The diff of the file.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Get the changes
        changes_data = mr.changes()

        # Extract changes data based on the return type
        if isinstance(changes_data, dict):
            changes_list = changes_data.get("changes", [])
        else:
            # Assuming it's a requests.Response object
            changes_list = changes_data.json().get("changes", [])

        # Find the specific file
        file_diff = {}
        for change in changes_list:
            if (
                change["new_path"] == input_model.file_path
                or change["old_path"] == input_model.file_path
            ):
                file_diff = change
                break

        if not file_diff:
            _raise_file_not_found_error(input_model.file_path, input_model.mr_iid)

        # Map to our schema
        return GitLabMergeRequestDiffResponse(
            mr_iid=input_model.mr_iid,
            file_path=input_model.file_path,
            diff=file_diff["diff"],
            old_path=file_diff["old_path"],
            new_path=file_diff["new_path"],
            renamed_file=file_diff.get("renamed_file", False),
            deleted_file=file_diff.get("deleted_file", False),
            new_file=file_diff.get("new_file", False),
            content=None,  # We don't have the content in the diff
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def suggest_code_in_merge_request(
    input_model: SuggestMergeRequestCodeInput,
) -> GitLabComment:
    """Create a code suggestion comment on a GitLab merge request.

    Args:
        input_model: The input model containing suggestion details.

    Returns:
        GitLabComment: The created comment details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Format the suggestion body
        body = _format_suggestion_body(input_model.suggested_code, input_model.comment)

        # Create position data
        position_data = {
            "position_type": "text",
            "base_sha": input_model.base_sha,
            "start_sha": input_model.start_sha,
            "head_sha": input_model.head_sha,
            "new_path": input_model.file_path,
            "new_line": input_model.line_number,
        }

        # Create the comment with suggestion
        comment = mr.discussions.create(
            {
                "body": body,
                "position": position_data,
            }
        )

        # Map to our schema
        return GitLabComment(
            id=comment.id,
            body=body,
            author={
                "id": comment.attributes["author"]["id"],
                "name": comment.attributes["author"]["name"],
                "username": comment.attributes["author"]["username"],
            },
            created_at=comment.attributes["created_at"],
            updated_at=None,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def approve_merge_request(input_model: ApproveMergeRequestInput) -> bool:
    """Approve a merge request.

    Args:
        input_model: The input model containing the project path, merge request IID, and optional SHA.

    Returns:
        bool: True if the merge request was approved successfully.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Prepare parameters
        params = {}
        if input_model.sha:
            params["sha"] = input_model.sha

        # Approve the merge request
        mr.approve(**params)
    except Exception as exc:
        error_message = f"Approval operation failed: {exc!s}"
        raise GitLabAPIError(error_message) from exc
    else:
        return True


def merge_merge_request(input_model: MergeMergeRequestInput) -> GitLabMergeRequest:
    """Merge a merge request.

    Args:
        input_model: The input model containing the project path, merge request IID, and merge options.

    Returns:
        GitLabMergeRequest: The merged merge request.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Prepare parameters
        params = {}
        if input_model.merge_commit_message:
            params["merge_commit_message"] = input_model.merge_commit_message
        if input_model.should_remove_source_branch:
            params["should_remove_source_branch"] = (
                input_model.should_remove_source_branch
            )
        if input_model.merge_when_pipeline_succeeds:
            params["merge_when_pipeline_succeeds"] = (
                input_model.merge_when_pipeline_succeeds
            )
        if input_model.sha:
            params["sha"] = input_model.sha

        # Merge the merge request
        mr.merge(**params)

        # Get the updated merge request - use consistent parameter style
        mr = project.mergerequests.get(input_model.mr_iid)
        return _map_mr_to_schema(mr)
    except Exception as exc:
        # Include the original GitLab error for better debugging
        error_message = f"Merge operation failed: {exc!s}"
        raise GitLabAPIError(error_message) from exc


def close_merge_request(input_model: CloseMergeRequestInput) -> GitLabMergeRequest:
    """Close a merge request.

    Args:
        input_model: The input model containing the project path and merge request IID.

    Returns:
        GitLabMergeRequest: The closed merge request.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        mr = project.mergerequests.get(input_model.mr_iid)

        # Close the merge request
        mr.state_event = "close"
        mr.save()

        # Get the updated merge request
        mr = project.mergerequests.get(input_model.mr_iid)
        return _map_mr_to_schema(mr)
    except Exception as exc:
        error_message = f"Close operation failed: {exc!s}"
        raise GitLabAPIError(error_message) from exc


# Async versions of the functions
create_merge_request_async = to_async(create_merge_request)
list_merge_requests_async = to_async(list_merge_requests)
get_merge_request_async = to_async(get_merge_request)
comment_on_merge_request_async = to_async(comment_on_merge_request)
list_merge_request_comments_async = to_async(list_merge_request_comments)
list_merge_request_changes_async = to_async(list_merge_request_changes)
get_merge_request_diff_async = to_async(get_merge_request_diff)
suggest_code_in_merge_request_async = to_async(suggest_code_in_merge_request)
approve_merge_request_async = to_async(approve_merge_request)
merge_merge_request_async = to_async(merge_merge_request)
close_merge_request_async = to_async(close_merge_request)
