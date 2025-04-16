from dataclasses import dataclass
from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.merge_requests import (
    ApproveMergeRequestInput,
    CloseMergeRequestInput,
    CreateMergeRequestCommentInput,
    CreateMergeRequestInput,
    GetMergeRequestDiffInput,
    GetMergeRequestInput,
    ListMergeRequestCommentsInput,
    ListMergeRequestsInput,
    MergeMergeRequestInput,
    SuggestMergeRequestCodeInput,
)
from ..services.merge_requests import (
    approve_merge_request,
    close_merge_request,
    comment_on_merge_request,
    create_merge_request,
    get_merge_request,
    get_merge_request_diff,
    list_merge_request_changes,
    list_merge_request_comments,
    list_merge_requests,
    merge_merge_request,
    suggest_code_in_merge_request,
)


@dataclass
class SuggestCodeRequest:
    """Request model for suggest_code_in_merge_request_tool."""

    project_path: str
    mr_iid: int
    file_path: str
    line_number: int
    suggested_code: str
    comment: str
    base_sha: str | None = None
    start_sha: str | None = None
    head_sha: str | None = None


def create_merge_request_tool(
    project_path: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a new merge request in a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        source_branch: The source branch for the merge request.
        target_branch: The target branch for the merge request.
        title: The title of the merge request.
        description: Optional description of the merge request.

    Returns:
        dict[str, Any]: Details of the created merge request.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = CreateMergeRequestInput(
            project_path=project_path,
            source_branch=source_branch,
            target_branch=target_branch,
            title=title,
            description=description,
        )

        # Call service function
        response = create_merge_request(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_merge_requests_tool(
    project_path: str,
    state: str | None = None,
    labels: list[str] | None = None,
    order_by: str | None = None,
    sort: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List merge requests for a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        state: Optional filter for merge request state (opened, closed, merged, or all).
        labels: Optional list of labels to filter merge requests by.
        order_by: Optional field to order merge requests by.
        sort: Optional sort direction (asc or desc).
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict[str, Any]: The list of merge requests.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = ListMergeRequestsInput(
            project_path=project_path,
            state=state,
            labels=labels,
            order_by=order_by,
            sort=sort,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = list_merge_requests(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_merge_request_tool(project_path: str, mr_iid: int) -> dict[str, Any]:
    """Get details for a specific GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.

    Returns:
        dict[str, Any]: The merge request details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetMergeRequestInput(
            project_path=project_path,
            mr_iid=mr_iid,
        )

        # Call service function
        response = get_merge_request(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def comment_on_merge_request_tool(
    project_path: str, mr_iid: int, body: str
) -> dict[str, Any]:
    """Add a comment to a GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        body: The content of the comment.

    Returns:
        dict[str, Any]: The created comment details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = CreateMergeRequestCommentInput(
            project_path=project_path,
            mr_iid=mr_iid,
            body=body,
        )

        # Call service function
        response = comment_on_merge_request(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_merge_request_comments_tool(
    project_path: str, mr_iid: int, page: int = 1, per_page: int = 20
) -> dict[str, Any]:
    """List comments for a GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict[str, Any]: The list of comments.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = ListMergeRequestCommentsInput(
            project_path=project_path,
            mr_iid=mr_iid,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = list_merge_request_comments(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_merge_request_changes_tool(project_path: str, mr_iid: int) -> dict[str, Any]:
    """List files changed in a GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.

    Returns:
        dict[str, Any]: The list of changed files.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetMergeRequestInput(
            project_path=project_path,
            mr_iid=mr_iid,
        )

        # Call service function
        response = list_merge_request_changes(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_merge_request_diff_tool(
    project_path: str, mr_iid: int, file_path: str
) -> dict[str, Any]:
    """Get the diff of a specific file in a GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        file_path: The path of the file to get the diff for.

    Returns:
        dict[str, Any]: The diff of the file.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetMergeRequestDiffInput(
            project_path=project_path,
            mr_iid=mr_iid,
            file_path=file_path,
        )

        # Call service function
        response = get_merge_request_diff(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def suggest_code_in_merge_request_tool(
    request: SuggestCodeRequest,
) -> dict[str, Any]:
    """Create a code suggestion comment on a GitLab merge request.

    Args:
        request: The request model containing all parameters.

    Returns:
        dict[str, Any]: The created comment details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = SuggestMergeRequestCodeInput(
            project_path=request.project_path,
            mr_iid=request.mr_iid,
            file_path=request.file_path,
            line_number=request.line_number,
            suggested_code=request.suggested_code,
            comment=request.comment,
            base_sha=request.base_sha,
            start_sha=request.start_sha,
            head_sha=request.head_sha,
        )

        # Call service function
        response = suggest_code_in_merge_request(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def approve_merge_request_tool(
    project_path: str, mr_iid: int, sha: str | None = None
) -> bool:
    """Approve a GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        sha: Optional SHA of the commit to approve.

    Returns:
        bool: True if the merge request was approved successfully.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = ApproveMergeRequestInput(
            project_path=project_path,
            mr_iid=mr_iid,
            sha=sha,
        )

        # Call service function
        return approve_merge_request(input_model)
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def merge_merge_request_tool(
    project_path: str,
    mr_iid: int,
    merge_commit_message: str | None = None,
    should_remove_source_branch: bool = False,
    merge_when_pipeline_succeeds: bool = False,
    sha: str | None = None,
) -> dict[str, Any]:
    """Merge a GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.
        merge_commit_message: Optional custom merge commit message.
        should_remove_source_branch: Whether to remove the source branch after merging.
        merge_when_pipeline_succeeds: Whether to merge only when the pipeline succeeds.
        sha: Optional SHA of the commit to merge.

    Returns:
        dict[str, Any]: The merged merge request details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = MergeMergeRequestInput(
            project_path=project_path,
            mr_iid=mr_iid,
            merge_commit_message=merge_commit_message,
            should_remove_source_branch=should_remove_source_branch,
            merge_when_pipeline_succeeds=merge_when_pipeline_succeeds,
            sha=sha,
        )

        # Call service function
        response = merge_merge_request(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def close_merge_request_tool(project_path: str, mr_iid: int) -> dict[str, Any]:
    """Close a GitLab merge request.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        mr_iid: The internal ID of the merge request within the project.

    Returns:
        dict[str, Any]: The closed merge request details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = CloseMergeRequestInput(
            project_path=project_path,
            mr_iid=mr_iid,
        )

        # Call service function
        response = close_merge_request(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
