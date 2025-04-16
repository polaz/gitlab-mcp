from pydantic import BaseModel

from .base import GitLabResponseBase, PaginatedResponse


class CreateIssueInput(BaseModel):
    """Input model for creating an issue in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        title: The title of the issue.
        description: The description of the issue.
        labels: The labels to apply to the issue.
        assignee_ids: The IDs of users to assign to the issue.
        milestone_id: The ID of the milestone to associate with the issue.
    """

    project_path: str
    title: str
    description: str | None = None
    labels: list[str] | None = None
    assignee_ids: list[int] | None = None
    milestone_id: int | None = None


class GitLabIssue(GitLabResponseBase):
    """Response model for a GitLab issue.

    Attributes:
        id: The unique identifier of the issue.
        iid: The internal ID of the issue within the project.
        title: The title of the issue.
        description: The description of the issue.
        web_url: The web URL of the issue.
    """

    id: int
    iid: int
    title: str
    description: str | None = None
    web_url: str


class ListIssuesInput(BaseModel):
    """Input model for listing issues in a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        state: The state of the issues to list (opened, closed, or all).
        labels: The labels to filter issues by.
        assignee_id: The ID of the user to filter issues by assignee.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    state: str | None = None
    labels: list[str] | None = None
    assignee_id: int | None = None
    page: int = 1
    per_page: int = 20


class GitLabIssueListResponse(PaginatedResponse[GitLabIssue]):
    """Response model for listing GitLab issues."""

    pass


class GetIssueInput(BaseModel):
    """Input model for getting a specific issue from a GitLab repository.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
    """

    project_path: str
    issue_iid: int


class CreateIssueCommentInput(BaseModel):
    """Input model for creating a comment on a GitLab issue.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        body: The content of the comment.
    """

    project_path: str
    issue_iid: int
    body: str


class ListIssueCommentsInput(BaseModel):
    """Input model for listing comments on a GitLab issue.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    issue_iid: int
    page: int = 1
    per_page: int = 20


class CloseIssueInput(BaseModel):
    """Input model for closing an issue."""

    project_path: str
    issue_iid: int
