from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.users import (
    GetUserInput,
    ListUsersInput,
)
from ..services.users import (
    get_user,
    list_users,
)


@dataclass
class ListUsersRequest:
    """Request model for list_users_tool."""

    search: str | None = None
    username: str | None = None
    active: bool | None = None
    blocked: bool | None = None
    created_after: str | None = None
    created_before: str | None = None
    page: int = 1
    per_page: int = 20


def _validate_iso_date(date_str: str, date_type: str) -> datetime:
    """Helper function to validate and parse ISO format dates.

    Args:
        date_str: The date string to validate.
        date_type: The type of date (created_after or created_before).

    Returns:
        datetime: The parsed datetime object.

    Raises:
        ValueError: If the date string is not in valid ISO format.
    """
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        error_message = f"Invalid {date_type} date format"
        raise ValueError(error_message) from None


def list_users_tool(request: ListUsersRequest) -> dict[str, Any]:
    """List GitLab users.

    Args:
        request: The request model containing all parameters.

    Returns:
        dict[str, Any]: The list of users.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Parse date strings if provided
        created_after_date = None
        created_before_date = None

        if request.created_after:
            created_after_date = _validate_iso_date(
                request.created_after, "created_after"
            )

        if request.created_before:
            created_before_date = _validate_iso_date(
                request.created_before, "created_before"
            )

        input_model = ListUsersInput(
            search=request.search,
            username=request.username,
            active=request.active,
            blocked=request.blocked,
            created_after=created_after_date,
            created_before=created_before_date,
            page=request.page,
            per_page=request.per_page,
        )

        response = list_users(input_model)

        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_user_tool(user_id: str) -> dict[str, Any]:
    """Get a specific GitLab user.

    Args:
        user_id: The ID or username of the user.

    Returns:
        dict[str, Any]: The user details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = GetUserInput(user_id=user_id)
        response = get_user(input_model)
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
