from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.groups import (
    GetGroupInput,
    GroupAccessLevel,
    ListGroupsInput,
)
from ..services.groups import (
    get_group,
    list_groups,
)


def _raise_invalid_access_level_error(min_access_level: int) -> None:
    """Helper function to raise invalid access level error.

    Args:
        min_access_level: The invalid access level value.

    Raises:
        ValueError: Always raised with appropriate message.
    """
    error_message = "Invalid group access level"
    raise ValueError(error_message) from None


def list_groups_tool(
    search: str | None = None,
    owned: bool = False,
    min_access_level: int | None = None,
    top_level_only: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List GitLab groups.

    Args:
        search: Optional search query to filter groups by name.
        owned: Whether to only include groups owned by the current user.
        min_access_level: Minimum access level required.
        top_level_only: Whether to only include top-level groups.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict[str, Any]: The list of groups.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert access level to enum if provided
        access_level_enum = None
        if min_access_level is not None:
            try:
                access_level_enum = GroupAccessLevel(min_access_level)
            except ValueError:
                _raise_invalid_access_level_error(min_access_level)

        # Create input model
        input_model = ListGroupsInput(
            search=search,
            owned=owned,
            min_access_level=access_level_enum,
            top_level_only=top_level_only,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = list_groups(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_group_tool(group_id: str) -> dict[str, Any]:
    """Get a specific GitLab group.

    Args:
        group_id: The ID or path of the group.

    Returns:
        dict[str, Any]: The group details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetGroupInput(group_id=group_id)

        # Call service function
        response = get_group(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
