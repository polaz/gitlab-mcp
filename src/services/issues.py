"""Service functions for interacting with GitLab issues using the REST API."""

from typing import Any, cast

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


async def list_issues(input_model: ListIssuesInput) -> GitLabIssueListResponse:
    """List issues in a GitLab project using the REST API.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabIssueListResponse: A paginated list of issues.

    Raises:
        GitLabAPIError: If retrieving the issues fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Prepare query parameters
    params: dict[str, Any] = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    # Add optional filters
    if input_model.state:
        params["state"] = input_model.state.value
    if input_model.labels:
        params["labels"] = ",".join(input_model.labels)
    if input_model.assignee_id:
        params["assignee_id"] = str(input_model.assignee_id)
    if input_model.milestone:
        params["milestone"] = input_model.milestone
    if input_model.scope:
        params["scope"] = input_model.scope.value
    if input_model.author_id:
        params["author_id"] = str(input_model.author_id)
    if input_model.my_reaction_emoji:
        params["my_reaction_emoji"] = input_model.my_reaction_emoji
    if input_model.search:
        params["search"] = input_model.search
    if input_model.in_:
        params["in"] = input_model.in_
    if input_model.created_after:
        params["created_after"] = input_model.created_after.isoformat()
    if input_model.created_before:
        params["created_before"] = input_model.created_before.isoformat()
    if input_model.updated_after:
        params["updated_after"] = input_model.updated_after.isoformat()
    if input_model.updated_before:
        params["updated_before"] = input_model.updated_before.isoformat()
    if input_model.confidential is not None:
        params["confidential"] = str(input_model.confidential).lower()
    if input_model.issue_type:
        params["issue_type"] = input_model.issue_type.value
    if input_model.order_by:
        params["order_by"] = input_model.order_by.value
    if input_model.sort:
        params["sort"] = input_model.sort.value

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


async def list_all_issues(input_model: ListIssuesInput) -> GitLabIssueListResponse:
    """List all issues the authenticated user has access to.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabIssueListResponse: A paginated list of issues.

    Raises:
        GitLabAPIError: If retrieving the issues fails.
    """
    # Prepare query parameters
    params: dict[str, Any] = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    # Add optional filters (same as project issues but without project_path)
    if input_model.state:
        params["state"] = input_model.state.value
    if input_model.labels:
        params["labels"] = ",".join(input_model.labels)
    if input_model.assignee_id:
        params["assignee_id"] = str(input_model.assignee_id)
    if input_model.milestone:
        params["milestone"] = input_model.milestone
    if input_model.scope:
        params["scope"] = input_model.scope.value
    if input_model.author_id:
        params["author_id"] = str(input_model.author_id)
    if input_model.my_reaction_emoji:
        params["my_reaction_emoji"] = input_model.my_reaction_emoji
    if input_model.search:
        params["search"] = input_model.search
    if input_model.in_:
        params["in"] = input_model.in_
    if input_model.created_after:
        params["created_after"] = input_model.created_after.isoformat()
    if input_model.created_before:
        params["created_before"] = input_model.created_before.isoformat()
    if input_model.updated_after:
        params["updated_after"] = input_model.updated_after.isoformat()
    if input_model.updated_before:
        params["updated_before"] = input_model.updated_before.isoformat()
    if input_model.confidential is not None:
        params["confidential"] = str(input_model.confidential).lower()
    if input_model.issue_type:
        params["issue_type"] = input_model.issue_type.value
    if input_model.order_by:
        params["order_by"] = input_model.order_by.value
    if input_model.sort:
        params["sort"] = input_model.sort.value

    # Make the API call
    response_data = await gitlab_rest_client.get_async("/issues", params=params)

    # Get total count - in a real implementation we would use the headers
    # For now, just use the length of the response
    total_count = len(response_data)

    # Parse the response into our schema
    items = [GitLabIssue.model_validate(issue) for issue in response_data]

    return GitLabIssueListResponse(
        items=items,
        count=total_count,
    )


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
    # URL encode the group ID or path
    group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

    # Prepare query parameters
    params: dict[str, Any] = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    # Add optional filters
    if input_model.state:
        params["state"] = input_model.state.value
    if input_model.labels:
        params["labels"] = ",".join(input_model.labels)
    if input_model.assignee_id:
        params["assignee_id"] = str(input_model.assignee_id)
    if input_model.milestone:
        params["milestone"] = input_model.milestone
    if input_model.scope:
        params["scope"] = input_model.scope.value
    if input_model.author_id:
        params["author_id"] = str(input_model.author_id)
    if input_model.my_reaction_emoji:
        params["my_reaction_emoji"] = input_model.my_reaction_emoji
    if input_model.search:
        params["search"] = input_model.search
    if input_model.in_:
        params["in"] = input_model.in_
    if input_model.created_after:
        params["created_after"] = input_model.created_after.isoformat()
    if input_model.created_before:
        params["created_before"] = input_model.created_before.isoformat()
    if input_model.updated_after:
        params["updated_after"] = input_model.updated_after.isoformat()
    if input_model.updated_before:
        params["updated_before"] = input_model.updated_before.isoformat()
    if input_model.confidential is not None:
        params["confidential"] = str(input_model.confidential).lower()
    if input_model.issue_type:
        params["issue_type"] = input_model.issue_type.value
    if input_model.order_by:
        params["order_by"] = input_model.order_by.value
    if input_model.sort:
        params["sort"] = input_model.sort.value

    # Make the API call
    response_data = await gitlab_rest_client.get_async(
        f"/groups/{group_id}/issues", params=params
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


async def get_issue(input_model: GetIssueInput) -> GitLabIssue:
    """Get a specific issue from a GitLab project using the REST API.

    Args:
        input_model: The input model containing the project path and issue IID.

    Returns:
        GitLabIssue: The requested issue.

    Raises:
        GitLabAPIError: If retrieving the issue fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Make the API call
    response_data = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}"
    )

    # Parse the response into our schema
    return GitLabIssue.model_validate(response_data)


async def create_issue(input_model: CreateIssueInput) -> GitLabIssue:
    """Create a new issue in a GitLab project using the REST API.

    Args:
        input_model: The input model containing the issue details.

    Returns:
        GitLabIssue: The created issue.

    Raises:
        GitLabAPIError: If creating the issue fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Prepare the request body
    data: dict[str, Any] = {
        "title": input_model.title,
    }

    # Add optional fields
    if input_model.description:
        data["description"] = input_model.description
    if input_model.labels:
        data["labels"] = ",".join(input_model.labels)
    if input_model.assignee_ids:
        data["assignee_ids"] = input_model.assignee_ids
    if input_model.milestone_id:
        data["milestone_id"] = input_model.milestone_id
    if input_model.confidential:
        data["confidential"] = input_model.confidential
    if input_model.created_at:
        data["created_at"] = input_model.created_at
    if input_model.due_date:
        data["due_date"] = input_model.due_date
    if input_model.epic_id:
        data["epic_id"] = input_model.epic_id
    if input_model.issue_type:
        data["issue_type"] = input_model.issue_type.value
    if input_model.merge_request_to_resolve_discussions_of:
        data["merge_request_to_resolve_discussions_of"] = (
            input_model.merge_request_to_resolve_discussions_of
        )
    if input_model.discussion_to_resolve:
        data["discussion_to_resolve"] = input_model.discussion_to_resolve
    if input_model.weight:
        data["weight"] = input_model.weight

    # Make the API call
    response_data = await gitlab_rest_client.post_async(
        f"/projects/{project_path}/issues", json_data=data
    )

    # Parse the response into our schema
    return GitLabIssue.model_validate(response_data)


async def update_issue(input_model: UpdateIssueInput) -> GitLabIssue:
    """Update an existing issue in a GitLab project.

    Args:
        input_model: The input model containing the updated issue details.

    Returns:
        GitLabIssue: The updated issue.

    Raises:
        GitLabAPIError: If updating the issue fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Prepare the request body
    data: dict[str, Any] = {}

    # Add fields to update (only if they are provided)
    if input_model.title:
        data["title"] = input_model.title
    if input_model.description is not None:  # Allow empty strings
        data["description"] = input_model.description
    if input_model.assignee_ids is not None:
        data["assignee_ids"] = input_model.assignee_ids
    if input_model.milestone_id is not None:
        data["milestone_id"] = input_model.milestone_id
    if input_model.labels is not None:
        data["labels"] = input_model.labels
    if input_model.state_event:
        data["state_event"] = input_model.state_event
    if input_model.updated_at:
        data["updated_at"] = input_model.updated_at
    if input_model.due_date is not None:
        data["due_date"] = input_model.due_date
    if input_model.weight is not None:
        data["weight"] = input_model.weight
    if input_model.discussion_locked is not None:
        data["discussion_locked"] = input_model.discussion_locked
    if input_model.epic_id is not None:
        data["epic_id"] = input_model.epic_id
    if input_model.issue_type:
        data["issue_type"] = input_model.issue_type.value
    if input_model.confidential is not None:
        data["confidential"] = input_model.confidential
    if input_model.add_labels:
        data["add_labels"] = input_model.add_labels
    if input_model.remove_labels:
        data["remove_labels"] = input_model.remove_labels

    # Make the API call
    response_data = await gitlab_rest_client.put_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}", json_data=data
    )

    # Parse the response into our schema
    return GitLabIssue.model_validate(response_data)


async def close_issue(input_model: GetIssueInput) -> GitLabIssue:
    """Close an issue in a GitLab project using the REST API.

    Args:
        input_model: The input model containing the project path and issue IID.

    Returns:
        GitLabIssue: The updated issue.

    Raises:
        GitLabAPIError: If closing the issue fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

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


async def delete_issue(input_model: DeleteIssueInput) -> None:
    """Delete an issue from a GitLab project.

    Args:
        input_model: The input model containing the project path and issue IID.

    Raises:
        GitLabAPIError: If deleting the issue fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Make the API call
    await gitlab_rest_client.delete_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}"
    )


async def move_issue(input_model: MoveIssueInput) -> GitLabIssue:
    """Move an issue to a different project.

    Args:
        input_model: The input model containing the source and target project details.

    Returns:
        GitLabIssue: The moved issue.

    Raises:
        GitLabAPIError: If moving the issue fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Prepare the request body
    data = {
        "to_project_id": input_model.to_project_id,
    }

    # Make the API call
    response_data = await gitlab_rest_client.post_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}/move", json_data=data
    )

    # Parse the response into our schema
    return GitLabIssue.model_validate(response_data)


async def comment_on_issue(input_model: CreateIssueCommentInput) -> dict[str, Any]:
    """Create a comment on an issue in a GitLab project using the REST API.

    Args:
        input_model: The input model containing the comment details.

    Returns:
        Dict[str, Any]: The created comment.

    Raises:
        GitLabAPIError: If creating the comment fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Prepare the request body
    data = {
        "body": input_model.body,
    }

    # Make the API call
    response_data = await gitlab_rest_client.post_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}/notes", json_data=data
    )

    # Return the comment data
    return response_data


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
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Prepare query parameters
    params = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    # Make the API call
    response_data = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}/notes", params=params
    )

    # Return the comments data
    return cast(list[dict[str, Any]], response_data)


async def list_issue_links(input_model: ListIssueLinksInput) -> list[GitLabIssueLink]:
    """List links to an issue.

    Args:
        input_model: The input model containing the project path and issue IID.

    Returns:
        List[GitLabIssueLink]: The list of issue links.

    Raises:
        GitLabAPIError: If retrieving the issue links fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Make the API call
    response_data = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}/links"
    )

    # Parse the response into our schema
    return [GitLabIssueLink.model_validate(link) for link in response_data]


async def get_issue_link(input_model: GetIssueLinkInput) -> IssueLinkResponse:
    """Get details about an issue link.

    Args:
        input_model: The input model containing the project path, issue IID, and link ID.

    Returns:
        IssueLinkResponse: The issue link details.

    Raises:
        GitLabAPIError: If retrieving the issue link fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Make the API call
    response_data = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}/links/{input_model.issue_link_id}"
    )

    # Parse the response into our schema
    return IssueLinkResponse.model_validate(response_data)


async def create_issue_link(input_model: CreateIssueLinkInput) -> IssueLinkResponse:
    """Create a link between issues.

    Args:
        input_model: The input model containing the source and target issue details.

    Returns:
        IssueLinkResponse: The created issue link.

    Raises:
        GitLabAPIError: If creating the issue link fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Prepare the request body
    data = {
        "target_project_id": input_model.target_project_id,
        "target_issue_iid": input_model.target_issue_iid,
        "link_type": input_model.link_type.value,
    }

    # Make the API call
    response_data = await gitlab_rest_client.post_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}/links", json_data=data
    )

    # Parse the response into our schema
    return IssueLinkResponse.model_validate(response_data)


async def delete_issue_link(input_model: DeleteIssueLinkInput) -> IssueLinkResponse:
    """Delete a link between issues.

    Args:
        input_model: The input model containing the project path, issue IID, and link ID.

    Returns:
        IssueLinkResponse: The deleted issue link.

    Raises:
        GitLabAPIError: If deleting the issue link fails.
    """
    # URL encode the project path
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    # Make the API call
    response_data = await gitlab_rest_client.delete_async(
        f"/projects/{project_path}/issues/{input_model.issue_iid}/links/{input_model.issue_link_id}"
    )

    # Parse the response into our schema
    return IssueLinkResponse.model_validate(response_data)
