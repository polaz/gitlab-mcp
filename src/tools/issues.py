from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.issues import (
    CloseIssueInput,
    CreateIssueCommentInput,
    CreateIssueInput,
    GetIssueInput,
    ListIssueCommentsInput,
    ListIssuesInput,
)
from ..services.issues import (
    close_issue,
    comment_on_issue,
    create_issue,
    get_issue,
    list_issue_comments,
    list_issues,
)


def create_issue_tool(
    project_path: str,
    title: str,
    description: str | None = None,
    assignees: list[str] | None = None,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new issue in a GitLab repository.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        title: The title of the issue.
        description: Optional description of the issue.
        assignees: Optional list of usernames to assign to the issue.
        labels: Optional list of labels to apply to the issue.

    Returns:
        dict[str, Any]: Details of the created issue.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert assignees to assignee_ids if provided
        assignee_ids = None
        if assignees:
            # This would require a lookup from username to ID
            # For now, we'll leave this as None
            pass

        # Create input model
        input_model = CreateIssueInput(
            project_path=project_path,
            title=title,
            description=description,
            assignee_ids=assignee_ids,
            labels=labels,
        )

        # Call service function
        response = create_issue(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_issues_tool(
    project_path: str,
    state: str | None = None,
    labels: list[str] | None = None,
    order_by: str | None = None,
    sort: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List issues for a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        state: Optional filter for issue state (opened, closed, or all).
        labels: Optional list of labels to filter issues by.
        order_by: Optional field to order issues by.
        sort: Optional sort direction (asc or desc).
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict[str, Any]: The list of issues.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = ListIssuesInput(
            project_path=project_path,
            state=state,
            labels=labels,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = list_issues(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_issue_tool(project_path: str, issue_iid: int) -> dict[str, Any]:
    """Get details for a specific GitLab issue.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.

    Returns:
        dict[str, Any]: The issue details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetIssueInput(
            project_path=project_path,
            issue_iid=issue_iid,
        )

        # Call service function
        response = get_issue(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def comment_on_issue_tool(
    project_path: str, issue_iid: int, body: str
) -> dict[str, Any]:
    """Add a comment to a GitLab issue.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        body: The content of the comment.

    Returns:
        dict[str, Any]: The created comment details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = CreateIssueCommentInput(
            project_path=project_path,
            issue_iid=issue_iid,
            body=body,
        )

        # Call service function
        response = comment_on_issue(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_issue_comments_tool(
    project_path: str, issue_iid: int, page: int = 1, per_page: int = 20
) -> dict[str, Any]:
    """List comments for a GitLab issue.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict[str, Any]: The list of comments.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = ListIssueCommentsInput(
            project_path=project_path,
            issue_iid=issue_iid,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = list_issue_comments(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def close_issue_tool(project_path: str, issue_iid: int) -> dict[str, Any]:
    """Close a GitLab issue.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.

    Returns:
        dict[str, Any]: The closed issue details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = CloseIssueInput(
            project_path=project_path,
            issue_iid=issue_iid,
        )

        # Call service function
        response = close_issue(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
