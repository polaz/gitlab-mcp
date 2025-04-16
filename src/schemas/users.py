from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from .base import GitLabResponseBase, PaginatedResponse


class UserState(str, Enum):
    """GitLab user states.

    Attributes:
        ACTIVE: User is active.
        BLOCKED: User is blocked.
        DEACTIVATED: User is deactivated.
    """

    ACTIVE = "active"
    BLOCKED = "blocked"
    DEACTIVATED = "deactivated"


class GitLabUser(GitLabResponseBase):
    """Response model for a GitLab user.

    Attributes:
        id: The unique identifier of the user.
        username: The username of the user.
        name: The name of the user.
        email: The email of the user.
        state: The state of the user (active, blocked, deactivated).
        avatar_url: The URL of the user's avatar.
        web_url: The web URL of the user's profile.
        created_at: When the user was created.
        is_admin: Whether the user is an admin.
    """

    id: int
    username: str
    name: str
    email: str | None = None
    state: UserState
    avatar_url: str | None = None
    web_url: str
    created_at: str
    is_admin: bool = False


class ListUsersInput(BaseModel):
    """Input model for listing GitLab users.

    Attributes:
        search: Optional search query to filter users by username or name.
        username: Optional filter for exact username match.
        active: Whether to only include active users.
        blocked: Whether to only include blocked users.
        created_after: Only include users created after this date.
        created_before: Only include users created before this date.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    search: str | None = None
    username: str | None = None
    active: bool | None = None
    blocked: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    page: int = 1
    per_page: int = 20


class GitLabUserListResponse(PaginatedResponse[GitLabUser]):
    """Response model for listing GitLab users."""

    pass


class GetUserInput(BaseModel):
    """Input model for getting a specific GitLab user.

    Attributes:
        user_id: The ID or username of the user.
    """

    user_id: str  # Can be either an ID (int) or a username (str)


class CreateUserInput(BaseModel):
    """Input model for creating a new GitLab user.

    Attributes:
        email: The email of the user.
        username: The username of the user.
        name: The name of the user.
        password: The password of the user.
        skip_confirmation: Whether to skip email confirmation.
        admin: Whether the user should be an admin.
        projects_limit: The maximum number of projects the user can create.
    """

    email: str
    username: str
    name: str
    password: str
    skip_confirmation: bool = False
    admin: bool = False
    projects_limit: int = 100


class UpdateUserInput(BaseModel):
    """Input model for updating a GitLab user.

    Attributes:
        user_id: The ID or username of the user.
        email: Optional new email for the user.
        username: Optional new username for the user.
        name: Optional new name for the user.
        password: Optional new password for the user.
        admin: Optional whether the user should be an admin.
        projects_limit: Optional new maximum number of projects the user can create.
    """

    user_id: str  # Can be either an ID (int) or a username (str)
    email: str | None = None
    username: str | None = None
    name: str | None = None
    password: str | None = None
    admin: bool | None = None
    projects_limit: int | None = None


class BlockUserInput(BaseModel):
    """Input model for blocking a GitLab user.

    Attributes:
        user_id: The ID or username of the user.
    """

    user_id: str  # Can be either an ID (int) or a username (str)


class UnblockUserInput(BaseModel):
    """Input model for unblocking a GitLab user.

    Attributes:
        user_id: The ID or username of the user.
    """

    user_id: str  # Can be either an ID (int) or a username (str)
