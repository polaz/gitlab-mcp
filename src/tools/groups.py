"""Tool functions for working with GitLab groups."""

import asyncio

from src.api.custom_exceptions import GitLabAPIError
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


class InvalidAccessLevelError(ValueError):
    def __init__(self) -> None:
        super().__init__("Invalid access level")


def get_group_tool(group_id: str) -> dict:
    """Get details about a specific GitLab group.

    Args:
        group_id: The ID or path of the group to retrieve.

    Returns:
        dict: The group details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = GetGroupInput(group_id=group_id)
        response = asyncio.run(get_group(input_model))
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
) -> list[dict]:
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
        list[dict]: The list of groups matching the criteria.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        access_level = None
        if min_access_level:
            try:
                access_level = GroupAccessLevel[min_access_level.upper()]
            except KeyError as key_exc:
                raise InvalidAccessLevelError() from key_exc
        input_model = ListGroupsInput(
            search=search,
            owned=owned,
            min_access_level=access_level,
            top_level_only=top_level_only,
            page=page,
            per_page=per_page,
        )
        response = asyncio.run(list_groups(input_model))
        return [group.model_dump() for group in response.items]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_group_by_project_namespace_tool(project_namespace: str) -> dict:
    """Get details about a GitLab group based on a project namespace.

    Args:
        project_namespace: The namespace path of the project.

    Returns:
        dict: The group details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = GetGroupByProjectNamespaceInput(
            project_namespace=project_namespace
        )
        response = asyncio.run(get_group_by_project_namespace(input_model))
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
