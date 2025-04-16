from gitlab.base import RESTObject
from gitlab.v4.objects import Issue, ProjectIssue, ProjectIssueNote

from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.filters import IssueFilterParams
from ..schemas.issues import (
    CloseIssueInput,
    CreateIssueCommentInput,
    CreateIssueInput,
    GetIssueInput,
    GitLabIssue,
    GitLabIssueListResponse,
    ListIssueCommentsInput,
    ListIssuesInput,
)
from ..schemas.merge_requests import GitLabComment, GitLabCommentListResponse


def _map_issue_to_schema(issue: Issue | ProjectIssue | RESTObject) -> GitLabIssue:
    """Map a GitLab issue object to our schema.

    Args:
        issue: The GitLab issue object (can be Issue, ProjectIssue, or generic RESTObject).

    Returns:
        GitLabIssue: The mapped issue schema.
    """
    return GitLabIssue(
        id=issue.id,
        iid=issue.iid,
        title=issue.title,
        description=issue.description,
        web_url=issue.web_url,
    )


def _map_comment_to_schema(comment: ProjectIssueNote | RESTObject) -> GitLabComment:
    """Map a GitLab comment object to our schema.

    Args:
        comment: The GitLab comment object (can be ProjectIssueNote or generic RESTObject).

    Returns:
        GitLabComment: The mapped comment schema.
    """
    return GitLabComment(
        id=comment.id,
        body=comment.body,
        author={
            "id": comment.author["id"],
            "name": comment.author["name"],
            "username": comment.author["username"],
        },
        created_at=comment.created_at,
        updated_at=comment.updated_at if hasattr(comment, "updated_at") else None,
    )


def create_issue(input_model: CreateIssueInput) -> GitLabIssue:
    """Create an issue in a GitLab repository.

    Args:
        input_model: The input model containing issue details.

    Returns:
        GitLabIssue: The created issue details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Prepare data
        data = {
            "title": input_model.title,
            "description": input_model.description,
        }

        if input_model.labels:
            data["labels"] = ",".join(input_model.labels)
        if input_model.assignee_ids:
            data["assignee_ids"] = ",".join(str(id) for id in input_model.assignee_ids)
        if input_model.milestone_id:
            data["milestone_id"] = str(input_model.milestone_id)

        # Create the issue
        issue = project.issues.create(data)

        # Map to our schema
        return _map_issue_to_schema(issue)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def list_issues(input_model: ListIssuesInput) -> GitLabIssueListResponse:
    """List issues in a GitLab repository.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabIssueListResponse: The list of issues.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Convert input model to filter params
        filter_params = IssueFilterParams(
            page=input_model.page,
            per_page=input_model.per_page,
            state=input_model.state,
            labels=input_model.labels,
            assignee_id=input_model.assignee_id,
        )

        # Convert to dict, excluding None values
        filters = filter_params.model_dump(exclude_none=True)

        # Get the issues
        issues = project.issues.list(**filters)

        # Map to our schema
        items = [
            _map_issue_to_schema(issue)
            for issue in issues
            if hasattr(issue, "attributes")
        ]

        return GitLabIssueListResponse(
            count=len(items),
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_issue(input_model: GetIssueInput) -> GitLabIssue:
    """Get a specific issue from a GitLab repository.

    Args:
        input_model: The input model containing project path and issue IID.

    Returns:
        GitLabIssue: The issue details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        issue = project.issues.get(input_model.issue_iid)

        # Map to our schema
        return _map_issue_to_schema(issue)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def comment_on_issue(input_model: CreateIssueCommentInput) -> GitLabComment:
    """Add a comment to a GitLab issue.

    Args:
        input_model: The input model containing project path, issue IID, and comment body.

    Returns:
        GitLabComment: The created comment details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        issue = project.issues.get(input_model.issue_iid)

        # Create the comment
        comment = issue.notes.create({"body": input_model.body})

        # Map to our schema
        return _map_comment_to_schema(comment)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def list_issue_comments(
    input_model: ListIssueCommentsInput,
) -> GitLabCommentListResponse:
    """List comments on a GitLab issue.

    Args:
        input_model: The input model containing project path, issue IID, and pagination parameters.

    Returns:
        GitLabCommentListResponse: The list of comments.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        issue = project.issues.get(input_model.issue_iid)

        # Get the comments
        comments = issue.notes.list(
            page=input_model.page,
            per_page=input_model.per_page,
        )

        # Map to our schema
        items = [_map_comment_to_schema(comment) for comment in comments]

        return GitLabCommentListResponse(
            count=len(items),
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def close_issue(input_model: CloseIssueInput) -> GitLabIssue:
    """Close an issue.

    Args:
        input_model: The input model containing the project path and issue IID.

    Returns:
        GitLabIssue: The closed issue.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        issue = project.issues.get(input_model.issue_iid)

        # Close the issue
        issue.state_event = "close"
        issue.save()

        # Get the updated issue
        issue = project.issues.get(input_model.issue_iid)
        return _map_issue_to_schema(issue)
    except Exception as exc:
        # Use a generic error message to avoid TRY003
        error_message = "Issue operation failed"
        raise GitLabAPIError(error_message) from exc


# Async versions of the functions
create_issue_async = to_async(create_issue)
list_issues_async = to_async(list_issues)
get_issue_async = to_async(get_issue)
comment_on_issue_async = to_async(comment_on_issue)
list_issue_comments_async = to_async(list_issue_comments)
close_issue_async = to_async(close_issue)
