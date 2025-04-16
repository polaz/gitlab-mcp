from typing import Any

from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.filters import GroupFilterParams
from ..schemas.groups import (
    CreateGroupInput,
    DeleteGroupInput,
    GetGroupInput,
    GitLabGroup,
    GitLabGroupListResponse,
    ListGroupsInput,
    UpdateGroupInput,
)


def _map_group_to_schema(group: Any) -> GitLabGroup:
    """Map a GitLab group object to our schema.

    Args:
        group: The GitLab group object.

    Returns:
        GitLabGroup: The mapped group schema.
    """
    return GitLabGroup(
        id=group.id,
        name=group.name,
        path=group.path,
        description=group.description,
        visibility=group.visibility,
        web_url=group.web_url,
        parent_id=group.parent_id if hasattr(group, "parent_id") else None,
    )


def list_groups(input_model: ListGroupsInput) -> GitLabGroupListResponse:
    """List GitLab groups.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabGroupListResponse: The list of groups.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()

        # Convert input model to filter params
        filter_params = GroupFilterParams(
            page=input_model.page,
            per_page=input_model.per_page,
            search=input_model.search,
            owned=input_model.owned,
            min_access_level=input_model.min_access_level.value
            if input_model.min_access_level
            else None,
            top_level_only=input_model.top_level_only,
        )

        # Convert to dict, excluding None values
        filters = filter_params.model_dump(exclude_none=True)

        # Get the groups
        groups = client.groups.list(**filters)

        # Map to our schema
        items = [
            _map_group_to_schema(group)
            for group in groups
            if hasattr(group, "attributes")
        ]

        return GitLabGroupListResponse(
            count=len(items),
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_group(input_model: GetGroupInput) -> GitLabGroup:
    """Get a specific GitLab group.

    Args:
        input_model: The input model containing the group ID or path.

    Returns:
        GitLabGroup: The group details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        group = client.groups.get(input_model.group_id)

        # Map to our schema
        return _map_group_to_schema(group)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def create_group(input_model: CreateGroupInput) -> GitLabGroup:
    """Create a new GitLab group.

    Args:
        input_model: The input model containing group details.

    Returns:
        GitLabGroup: The created group details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()

        # Create the group
        group = client.groups.create(
            {
                "name": input_model.name,
                "path": input_model.path,
                "description": input_model.description,
                "visibility": input_model.visibility.value,
                "parent_id": input_model.parent_id,
                "auto_devops_enabled": input_model.auto_devops_enabled,
            }
        )

        # Map to our schema
        return _map_group_to_schema(group)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def update_group(input_model: UpdateGroupInput) -> GitLabGroup:
    """Update a GitLab group.

    Args:
        input_model: The input model containing updated group details.

    Returns:
        GitLabGroup: The updated group details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        group = client.groups.get(input_model.group_id)

        # Build update data
        data = {}
        if input_model.name is not None:
            data["name"] = input_model.name
        if input_model.path is not None:
            data["path"] = input_model.path
        if input_model.description is not None:
            data["description"] = input_model.description
        if input_model.visibility is not None:
            data["visibility"] = input_model.visibility.value

        # Update the group
        group.update(data)

        # Map to our schema
        return _map_group_to_schema(group)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def delete_group(input_model: DeleteGroupInput) -> bool:
    """Delete a GitLab group.

    Args:
        input_model: The input model containing the group ID or path.

    Returns:
        bool: True if the group was deleted successfully.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        group = client.groups.get(input_model.group_id)
        group.delete()
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc
    else:
        return True


# Async versions of the functions
list_groups_async = to_async(list_groups)
get_group_async = to_async(get_group)
create_group_async = to_async(create_group)
update_group_async = to_async(update_group)
delete_group_async = to_async(delete_group)
