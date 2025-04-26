"""Tool functions for working with GitLab groups."""

import asyncio
from typing import Any

from src.api.exceptions import GitLabAPIError
from src.schemas.groups import (
    GetGroupByProjectNamespaceInput,
    GetGroupInput,
    GroupAccessLevel,
    ListGroupsInput,
)
from src.services.groups import (
    get_group,
    get_group_by_project_namespace,
    list_groups,
)


def get_group_tool(group_id: str) -> dict[str, Any]:
    """Get details about a specific GitLab group.

    Args:
        group_id: The ID or path of the group to retrieve.

    Returns:
        dict[str, Any]: The group details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetGroupInput(group_id=group_id)

        # Call service function
        response = asyncio.run(get_group(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_groups_tool(
    search: str | None = None,
    owned: bool = False,
    min_access_level: str | None = None,
    top_level_only: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> list[dict[str, Any]]:
    """List GitLab groups with optional filtering.

    Args:
        search: Optional search query to filter groups by name.
        owned: Whether to only include groups owned by the current user.
        min_access_level: Minimum access level required (NO_ACCESS, MINIMAL_ACCESS,
                          GUEST, REPORTER, DEVELOPER, MAINTAINER, OWNER).
        top_level_only: Whether to only include top-level groups.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        list[dict[str, Any]]: The list of groups matching the criteria.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert string access level to enum if provided
        access_level = None
        if min_access_level:
            try:
                access_level = GroupAccessLevel[min_access_level.upper()]
            except KeyError as key_exc:
                raise ValueError(
                    f"Invalid access level: {min_access_level}"
                ) from key_exc

        # Create input model
        input_model = ListGroupsInput(
            search=search,
            owned=owned,
            min_access_level=access_level,
            top_level_only=top_level_only,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = asyncio.run(list_groups(input_model))

        # Convert to list of dicts
        return [group.model_dump() for group in response.items]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_group_by_project_namespace_tool(project_namespace: str) -> dict[str, Any]:
    """Get details about a GitLab group based on a project namespace.

    Args:
        project_namespace: The namespace path of the project.

    Returns:
        dict[str, Any]: The group details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetGroupByProjectNamespaceInput(
            project_namespace=project_namespace
        )

        # Call service function
        response = asyncio.run(get_group_by_project_namespace(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
