"""Service functions for interacting with GitLab groups using the REST API."""

from src.api import gitlab_rest_client
from src.schemas import (
    GetGroupByProjectNamespaceInput,
    GetGroupInput,
    GitLabGroup,
    GitLabGroupListResponse,
    ListGroupsInput,
)


async def list_groups(input_model: ListGroupsInput) -> GitLabGroupListResponse:
    """List GitLab groups using the REST API.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabGroupListResponse: The paginated list of groups.

    Raises:
        GitLabAPIError: If retrieving the groups fails.
    """
    # Prepare query parameters
    params = {}

    # Add pagination parameters
    params["page"] = input_model.page
    params["per_page"] = input_model.per_page

    # Add filtering parameters
    if input_model.search:
        params["search"] = input_model.search
    if input_model.owned:
        params["owned"] = "true"
    if input_model.min_access_level:
        params["min_access_level"] = str(input_model.min_access_level.value)
    if input_model.top_level_only:
        params["top_level_only"] = "true"

    # Make the API call
    response_data = await gitlab_rest_client.get_async("/groups", params=params)

    # Get total count - in a real implementation we would use the headers
    # For now, just use the length of the response
    total_count = len(response_data)

    # Parse the response into our schema
    items = [GitLabGroup.model_validate(group) for group in response_data]

    return GitLabGroupListResponse(
        items=items,
        count=total_count,
    )


async def get_group(input_model: GetGroupInput) -> GitLabGroup:
    """Get a specific GitLab group using the REST API.

    Args:
        input_model: The input model containing the group ID or path.

    Returns:
        GitLabGroup: The requested group.

    Raises:
        GitLabAPIError: If retrieving the group fails.
    """
    # Encode the group ID/path
    group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

    # Make the API call
    response = await gitlab_rest_client.get_async(f"/groups/{group_id}")

    # Parse the response into our schema
    return GitLabGroup.model_validate(response)


async def get_group_by_project_namespace(
    input_model: GetGroupByProjectNamespaceInput,
) -> GitLabGroup:
    """Get a GitLab group based on a project namespace using the REST API.

    Args:
        input_model: The input model containing the project namespace.

    Returns:
        GitLabGroup: The requested group.

    Raises:
        GitLabAPIError: If retrieving the group fails.
    """
    # In GitLab, the project namespace is the group path or subgroup path
    # We'll encode it as a path parameter
    namespace = gitlab_rest_client._encode_path_parameter(input_model.project_namespace)

    # Make the API call
    response = await gitlab_rest_client.get_async(f"/groups/{namespace}")

    # Parse the response into our schema
    return GitLabGroup.model_validate(response)
