"""Service functions for interacting with GitLab issues using the REST API."""

from typing import Any, cast

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.issues import (
    CreateIssueCommentInput,
    CreateIssueInput,
    CreateIssueLinkInput,
    DeleteIssueInput,
    DeleteIssueLinkInput,
    GetIssueInput,
    GetIssueLinkInput,
    GitLabIssue,
    GitLabIssueLink,
    GitLabIssueListResponse,
    IssueLinkResponse,
    ListGroupIssuesInput,
    ListIssueCommentsInput,
    ListIssueLinksInput,
    ListIssuesInput,
    MoveIssueInput,
    UpdateIssueInput,
)
from src.services.utils.issue_utils import (
    build_issue_create_payload,
    build_issue_filter_params,
    build_issue_update_payload,
)


async def list_issues(input_model: ListIssuesInput) -> GitLabIssueListResponse:
    """List issues in a GitLab project using the REST API.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabIssueListResponse: A paginated list of issues.

    Raises:
        GitLabAPIError: If retrieving the issues fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Build query parameters using utility function
        params = build_issue_filter_params(input_model)

        # Add project-specific filters not covered by common utility
        if input_model.my_reaction_emoji:
            params["my_reaction_emoji"] = input_model.my_reaction_emoji
        if input_model.in_:
            params["in"] = input_model.in_
        if input_model.issue_type:
            params["issue_type"] = input_model.issue_type.value

        # Make the API call
        response_data = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/issues", params=params
        )

        # Get total count - in a real implementation we would use the headers
        # For now, just use the length of the response
        total_count = len(response_data)

        # Parse the response into our schema
        items = [GitLabIssue.model_validate(issue) for issue in response_data]

        return GitLabIssueListResponse(
            items=items,
            count=total_count,
        )
    except GitLabAPIError as exc:
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {"message": "Failed to list issues", "operation": "list_issues"},
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error listing issues", "operation": "list_issues"},
        ) from exc


async def list_all_issues(input_model: ListIssuesInput) -> GitLabIssueListResponse:
    """List all issues the authenticated user has access to.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabIssueListResponse: A paginated list of issues.

    Raises:
        GitLabAPIError: If retrieving the issues fails.
    """
    try:
        # Build query parameters using utility function
        params = build_issue_filter_params(input_model)

        # Add specific filters not covered by common utility
        if input_model.my_reaction_emoji:
            params["my_reaction_emoji"] = input_model.my_reaction_emoji
        if input_model.in_:
            params["in"] = input_model.in_
        if input_model.issue_type:
            params["issue_type"] = input_model.issue_type.value

        # Make the API call
        response_data = await gitlab_rest_client.get_async("/issues", params=params)

        # Get total count
        total_count = len(response_data)

        # Parse the response into our schema
        items = [GitLabIssue.model_validate(issue) for issue in response_data]

        return GitLabIssueListResponse(
            items=items,
            count=total_count,
        )
    except GitLabAPIError as exc:
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {"message": "Failed to list all issues", "operation": "list_all_issues"},
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing all issues",
                "operation": "list_all_issues",
            },
        ) from exc


async def list_group_issues(
    input_model: ListGroupIssuesInput,
) -> GitLabIssueListResponse:
    """List issues in a GitLab group using the REST API.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabIssueListResponse: A paginated list of issues.

    Raises:
        GitLabAPIError: If retrieving the issues fails.
    """
    try:
        # URL encode the group ID or path
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

        # Build query parameters using utility function
        params = build_issue_filter_params(input_model)

        # Add specific filters not covered by common utility
        if input_model.my_reaction_emoji:
            params["my_reaction_emoji"] = input_model.my_reaction_emoji
        if input_model.in_:
            params["in"] = input_model.in_
        if input_model.issue_type:
            params["issue_type"] = input_model.issue_type.value

        # Make the API call
        response_data = await gitlab_rest_client.get_async(
            f"/groups/{group_id}/issues", params=params
        )

        # Get total count
        total_count = len(response_data)

        # Parse the response into our schema
        items = [GitLabIssue.model_validate(issue) for issue in response_data]

        return GitLabIssueListResponse(
            items=items,
            count=total_count,
        )
    except GitLabAPIError as exc:
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list issues for group {input_model.group_id}",
                "operation": "list_group_issues",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing group issues",
                "operation": "list_group_issues",
            },
        ) from exc


async def get_issue(input_model: GetIssueInput) -> GitLabIssue:
    """Get a specific issue from a GitLab project using the REST API.

    Args:
        input_model: The input model containing the project path and issue IID.

    Returns:
        GitLabIssue: The requested issue.

    Raises:
        GitLabAPIError: If retrieving the issue fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Make the API call
        response_data = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}"
        )

        # Parse the response into our schema
        return GitLabIssue.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get issue {input_model.issue_iid}",
                "operation": "get_issue",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error getting issue", "operation": "get_issue"},
        ) from exc


async def create_issue(input_model: CreateIssueInput) -> GitLabIssue:
    """Create a new issue in a GitLab project using the REST API.

    Args:
        input_model: The input model containing the issue details.

    Returns:
        GitLabIssue: The created issue.

    Raises:
        GitLabAPIError: If creating the issue fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Build payload using utility function
        data = build_issue_create_payload(input_model)

        # Add fields not covered by the utility
        optional_fields = {
            "created_at": input_model.created_at,
            "epic_id": input_model.epic_id,
            "issue_type": input_model.issue_type.value
            if input_model.issue_type
            else None,
            "weight": input_model.weight,
        }

        for field, value in optional_fields.items():
            if value is not None:
                data[field] = value

        # Make the API call
        response_data = await gitlab_rest_client.post_async(
            f"/projects/{project_path}/issues", json_data=data
        )

        # Parse the response into our schema
        return GitLabIssue.model_validate(response_data)
    except GitLabAPIError as exc:
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {"message": "Failed to create issue", "operation": "create_issue"},
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error creating issue", "operation": "create_issue"},
        ) from exc


async def update_issue(input_model: UpdateIssueInput) -> GitLabIssue:
    """Update an existing issue in a GitLab project.

    Args:
        input_model: The input model containing the updated issue details.

    Returns:
        GitLabIssue: The updated issue.

    Raises:
        GitLabAPIError: If updating the issue fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Build payload using utility function
        data = build_issue_update_payload(input_model)

        # Add fields not covered by the utility
        optional_fields = {
            "updated_at": input_model.updated_at,
            "weight": input_model.weight,
            "epic_id": input_model.epic_id,
            "issue_type": input_model.issue_type.value
            if input_model.issue_type
            else None,
            "add_labels": input_model.add_labels,
            "remove_labels": input_model.remove_labels,
        }

        for field, value in optional_fields.items():
            if value is not None:
                data[field] = value

        # Make the API call
        response_data = await gitlab_rest_client.put_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}", json_data=data
        )

        # Parse the response into our schema
        return GitLabIssue.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to update issue {input_model.issue_iid}",
                "operation": "update_issue",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error updating issue", "operation": "update_issue"},
        ) from exc


async def close_issue(input_model: GetIssueInput) -> GitLabIssue:
    """Close an issue in a GitLab project using the REST API.

    Args:
        input_model: The input model containing the project path and issue IID.

    Returns:
        GitLabIssue: The updated issue.

    Raises:
        GitLabAPIError: If closing the issue fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Prepare the request body to update the issue state to closed
        data = {
            "state_event": "close",
        }

        # Make the API call
        response_data = await gitlab_rest_client.put_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}", json_data=data
        )

        # Parse the response into our schema
        return GitLabIssue.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to close issue {input_model.issue_iid}",
                "operation": "close_issue",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error closing issue", "operation": "close_issue"},
        ) from exc


async def delete_issue(input_model: DeleteIssueInput) -> None:
    """Delete an issue from a GitLab project.

    Args:
        input_model: The input model containing the project path and issue IID.

    Raises:
        GitLabAPIError: If deleting the issue fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Make the API call
        await gitlab_rest_client.delete_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}"
        )
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to delete issue {input_model.issue_iid}",
                "operation": "delete_issue",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error deleting issue", "operation": "delete_issue"},
        ) from exc


async def move_issue(input_model: MoveIssueInput) -> GitLabIssue:
    """Move an issue to a different project.

    Args:
        input_model: The input model containing the source and target project details.

    Returns:
        GitLabIssue: The moved issue.

    Raises:
        GitLabAPIError: If moving the issue fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Prepare the request body
        data = {
            "to_project_id": input_model.to_project_id,
        }

        # Make the API call
        response_data = await gitlab_rest_client.post_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}/move",
            json_data=data,
        )

        # Parse the response into our schema
        return GitLabIssue.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to move issue {input_model.issue_iid}",
                "operation": "move_issue",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error moving issue", "operation": "move_issue"},
        ) from exc


async def comment_on_issue(input_model: CreateIssueCommentInput) -> dict[str, Any]:
    """Create a comment on an issue in a GitLab project using the REST API.

    Args:
        input_model: The input model containing the comment details.

    Returns:
        Dict[str, Any]: The created comment.

    Raises:
        GitLabAPIError: If creating the comment fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Prepare the request body
        data = {
            "body": input_model.body,
        }

        # Make the API call
        response_data = await gitlab_rest_client.post_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}/notes",
            json_data=data,
        )

        # Return the comment data
        return response_data
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to comment on issue {input_model.issue_iid}",
                "operation": "comment_on_issue",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error commenting on issue",
                "operation": "comment_on_issue",
            },
        ) from exc


async def list_issue_comments(
    input_model: ListIssueCommentsInput,
) -> list[dict[str, Any]]:
    """List comments on an issue in a GitLab project using the REST API.

    Args:
        input_model: The input model containing the issue details.

    Returns:
        List[Dict[str, Any]]: The list of comments.

    Raises:
        GitLabAPIError: If retrieving the comments fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Prepare query parameters
        params = {
            "page": input_model.page,
            "per_page": input_model.per_page,
        }

        # Make the API call
        response_data = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}/notes",
            params=params,
        )

        # Return the comments data
        return cast(list[dict[str, Any]], response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list comments for issue {input_model.issue_iid}",
                "operation": "list_issue_comments",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing issue comments",
                "operation": "list_issue_comments",
            },
        ) from exc


async def list_issue_links(input_model: ListIssueLinksInput) -> list[GitLabIssueLink]:
    """List links to an issue.

    Args:
        input_model: The input model containing the project path and issue IID.

    Returns:
        List[GitLabIssueLink]: The list of issue links.

    Raises:
        GitLabAPIError: If retrieving the issue links fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Make the API call
        response_data = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}/links"
        )

        # Parse the response into our schema
        return [GitLabIssueLink.model_validate(link) for link in response_data]
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list links for issue {input_model.issue_iid}",
                "operation": "list_issue_links",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing issue links",
                "operation": "list_issue_links",
            },
        ) from exc


async def get_issue_link(input_model: GetIssueLinkInput) -> IssueLinkResponse:
    """Get details about an issue link.

    Args:
        input_model: The input model containing the project path, issue IID, and link ID.

    Returns:
        IssueLinkResponse: The issue link details.

    Raises:
        GitLabAPIError: If retrieving the issue link fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Make the API call
        response_data = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}/links/{input_model.issue_link_id}"
        )

        # Parse the response into our schema
        return IssueLinkResponse.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue link {input_model.issue_link_id} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get issue link {input_model.issue_link_id}",
                "operation": "get_issue_link",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error getting issue link",
                "operation": "get_issue_link",
            },
        ) from exc


async def create_issue_link(input_model: CreateIssueLinkInput) -> IssueLinkResponse:
    """Create a link between issues.

    Args:
        input_model: The input model containing the source and target issue details.

    Returns:
        IssueLinkResponse: The created issue link.

    Raises:
        GitLabAPIError: If creating the issue link fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Prepare the request body
        data = {
            "target_project_id": input_model.target_project_id,
            "target_issue_iid": input_model.target_issue_iid,
            "link_type": input_model.link_type.value,
        }

        # Make the API call
        response_data = await gitlab_rest_client.post_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}/links",
            json_data=data,
        )

        # Parse the response into our schema
        return IssueLinkResponse.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue {input_model.issue_iid} or target issue not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to create link for issue {input_model.issue_iid}",
                "operation": "create_issue_link",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error creating issue link",
                "operation": "create_issue_link",
            },
        ) from exc


async def delete_issue_link(input_model: DeleteIssueLinkInput) -> IssueLinkResponse:
    """Delete a link between issues.

    Args:
        input_model: The input model containing the project path, issue IID, and link ID.

    Returns:
        IssueLinkResponse: The deleted issue link.

    Raises:
        GitLabAPIError: If deleting the issue link fails.
    """
    try:
        # URL encode the project path
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )

        # Make the API call
        response_data = await gitlab_rest_client.delete_async(
            f"/projects/{project_path}/issues/{input_model.issue_iid}/links/{input_model.issue_link_id}"
        )

        # Parse the response into our schema
        return IssueLinkResponse.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Issue link {input_model.issue_link_id} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to delete issue link {input_model.issue_link_id}",
                "operation": "delete_issue_link",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error deleting issue link",
                "operation": "delete_issue_link",
            },
        ) from exc
