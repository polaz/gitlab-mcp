from enum import Enum

from pydantic import BaseModel


class GitLabResponseBase(BaseModel):
    """Base class for GitLab API responses."""



class BaseResponseList[T](GitLabResponseBase):
    """Base class for list responses from the GitLab API.

    Provides a consistent structure for all list-type responses that contain
    multiple items of the same type.

    Attributes:
        items: List of items of type T.
    """

    items: list[T]


class PaginatedResponse[T](GitLabResponseBase):
    """Base class for paginated GitLab API responses.

    Provides a consistent structure for all paginated responses from the GitLab API.

    Attributes:
        count: Total number of items.
        items: List of items of type T.
    """

    count: int
    items: list[T]


class VisibilityLevel(str, Enum):
    """GitLab repository visibility levels.

    Attributes:
        PRIVATE: Only project members can access.
        INTERNAL: Any authenticated user can access.
        PUBLIC: Anyone can access.
    """

    PRIVATE = "private"
    INTERNAL = "internal"
    PUBLIC = "public"
