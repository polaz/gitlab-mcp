from gitlab.base import RESTObject
from gitlab.v4.objects import User

from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.filters import UserFilterParams
from ..schemas.users import (
    BlockUserInput,
    CreateUserInput,
    GetUserInput,
    GitLabUser,
    GitLabUserListResponse,
    ListUsersInput,
    UnblockUserInput,
    UpdateUserInput,
)


def _map_user_to_schema(user: User | RESTObject) -> GitLabUser:
    """Map a GitLab user object to our schema.

    Args:
        user: The GitLab user object.

    Returns:
        GitLabUser: The mapped user schema.
    """
    return GitLabUser(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email if hasattr(user, "email") else None,
        state=user.state,
        avatar_url=user.avatar_url if hasattr(user, "avatar_url") else None,
        web_url=user.web_url,
        created_at=user.created_at,
        is_admin=user.is_admin if hasattr(user, "is_admin") else False,
    )


def list_users(input_model: ListUsersInput) -> GitLabUserListResponse:
    """List GitLab users.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabUserListResponse: The list of users.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()

        # Convert input model to filter params
        filter_params = UserFilterParams(
            page=input_model.page,
            per_page=input_model.per_page,
            search=input_model.search,
            username=input_model.username,
            active=input_model.active,
            blocked=input_model.blocked,
            created_after=input_model.created_after,
            created_before=input_model.created_before,
        )

        # Convert to dict and handle date formatting
        filters = filter_params.model_dump(exclude_none=True)
        if filters.get("created_after"):
            filters["created_after"] = filters["created_after"].isoformat()
        if filters.get("created_before"):
            filters["created_before"] = filters["created_before"].isoformat()

        # Get the users
        users = client.users.list(**filters)

        # Map to our schema
        items = [
            _map_user_to_schema(user) for user in users if hasattr(user, "attributes")
        ]

        return GitLabUserListResponse(
            count=len(items),
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_user(input_model: GetUserInput) -> GitLabUser:
    """Get a specific GitLab user.

    Args:
        input_model: The input model containing the user ID or username.

    Returns:
        GitLabUser: The user details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        user = client.users.get(input_model.user_id)

        # Map to our schema
        return _map_user_to_schema(user)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def create_user(input_model: CreateUserInput) -> GitLabUser:
    """Create a new GitLab user.

    Args:
        input_model: The input model containing user details.

    Returns:
        GitLabUser: The created user details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()

        # Create the user
        user = client.users.create(
            {
                "email": input_model.email,
                "username": input_model.username,
                "name": input_model.name,
                "password": input_model.password,
                "skip_confirmation": input_model.skip_confirmation,
                "admin": input_model.admin,
                "projects_limit": input_model.projects_limit,
            }
        )

        # Map to our schema
        return _map_user_to_schema(user)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def update_user(input_model: UpdateUserInput) -> GitLabUser:
    """Update a GitLab user.

    Args:
        input_model: The input model containing updated user details.

    Returns:
        GitLabUser: The updated user details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        user = client.users.get(input_model.user_id)

        # Build update data
        data = {}
        if input_model.email is not None:
            data["email"] = input_model.email
        if input_model.username is not None:
            data["username"] = input_model.username
        if input_model.name is not None:
            data["name"] = input_model.name
        if input_model.password is not None:
            data["password"] = input_model.password
        if input_model.admin is not None:
            data["admin"] = input_model.admin
        if input_model.projects_limit is not None:
            data["projects_limit"] = input_model.projects_limit

        # Update the user
        user.update(data)

        # Map to our schema
        return _map_user_to_schema(user)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def block_user(input_model: BlockUserInput) -> GitLabUser:
    """Block a GitLab user.

    Args:
        input_model: The input model containing the user ID or username.

    Returns:
        GitLabUser: The updated user details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        user = client.users.get(input_model.user_id)

        # Block the user
        user.block()

        # Refresh user data
        user = client.users.get(input_model.user_id)

        # Map to our schema
        return _map_user_to_schema(user)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def unblock_user(input_model: UnblockUserInput) -> GitLabUser:
    """Unblock a GitLab user.

    Args:
        input_model: The input model containing the user ID or username.

    Returns:
        GitLabUser: The updated user details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        user = client.users.get(input_model.user_id)

        # Unblock the user
        user.unblock()

        # Refresh user data
        user = client.users.get(input_model.user_id)

        # Map to our schema
        return _map_user_to_schema(user)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


# Async versions of the functions
list_users_async = to_async(list_users)
get_user_async = to_async(get_user)
create_user_async = to_async(create_user)
update_user_async = to_async(update_user)
block_user_async = to_async(block_user)
unblock_user_async = to_async(unblock_user)
