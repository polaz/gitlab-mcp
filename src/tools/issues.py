"""Tool functions for working with GitLab issues."""

import asyncio
from typing import Any, cast

from src.api.exceptions import GitLabAPIError
from src.schemas.issues import (
    CreateIssueCommentInput,
    CreateIssueInput,
    CreateIssueLinkInput,
    DeleteIssueInput,
    DeleteIssueLinkInput,
    GetIssueInput,
    GetIssueLinkInput,
    GitLabIssueLinkType,
    IssueScope,
    IssueState,
    IssueType,
    ListGroupIssuesInput,
    ListIssueCommentsInput,
    ListIssueLinksInput,
    ListIssuesInput,
    MoveIssueInput,
    UpdateIssueInput,
)
from src.services.issues import (
    close_issue,
    comment_on_issue,
    create_issue,
    create_issue_link,
    delete_issue,
    delete_issue_link,
    get_issue,
    get_issue_link,
    list_all_issues,
    list_group_issues,
    list_issue_comments,
    list_issue_links,
    list_issues,
    move_issue,
    update_issue,
)


def list_issues_tool(
    project_path: str,
    state: str | None = None,
    labels: str | None = None,
    milestone: str | None = None,
    scope: str | None = None,
    author_id: int | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    confidential: bool | None = None,
    issue_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> list[dict[str, Any]]:
    """List issues in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        state: The state of the issues to list (opened, closed, or all).
        labels: Comma-separated list of label names to filter issues by.
        milestone: The milestone title to filter issues by.
        scope: Return issues for the given scope (created_by_me, assigned_to_me, or all).
        author_id: Return issues created by the given user ID.
        assignee_id: Return issues assigned to the given user ID.
        search: Search query to filter issues by title and description.
        confidential: Filter confidential or public issues.
        issue_type: Filter to a given type of issue (issue, incident, test_case, or task).
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        List[Dict[str, Any]]: The list of issues.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert comma-separated labels to list if provided
        label_list = None
        if labels:
            label_list = [label.strip() for label in labels.split(",")]

        # Convert string enums to enum values if provided
        state_enum = None
        if state:
            state_enum = IssueState(state)

        scope_enum = None
        if scope:
            scope_enum = IssueScope(scope)

        issue_type_enum = None
        if issue_type:
            issue_type_enum = IssueType(issue_type)

        # Create input model
        input_model = ListIssuesInput(
            project_path=project_path,
            state=state_enum,
            labels=label_list,
            milestone=milestone,
            scope=scope_enum,
            author_id=author_id,
            assignee_id=assignee_id,
            search=search,
            confidential=confidential,
            issue_type=issue_type_enum,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = asyncio.run(list_issues(input_model))

        # Convert to list of dicts
        return [issue.model_dump() for issue in response.items]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_all_issues_tool(
    state: str | None = None,
    labels: str | None = None,
    milestone: str | None = None,
    scope: str | None = None,
    author_id: int | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    confidential: bool | None = None,
    page: int = 1,
    per_page: int = 20,
) -> list[dict[str, Any]]:
    """List all issues the authenticated user has access to.

    Args:
        state: The state of the issues to list (opened, closed, or all).
        labels: Comma-separated list of label names to filter issues by.
        milestone: The milestone title to filter issues by.
        scope: Return issues for the given scope (created_by_me, assigned_to_me, or all).
        author_id: Return issues created by the given user ID.
        assignee_id: Return issues assigned to the given user ID.
        search: Search query to filter issues by title and description.
        confidential: Filter confidential or public issues.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        List[Dict[str, Any]]: The list of issues.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert comma-separated labels to list if provided
        label_list = None
        if labels:
            label_list = [label.strip() for label in labels.split(",")]

        # Convert string enums to enum values if provided
        state_enum = None
        if state:
            state_enum = IssueState(state)

        scope_enum = None
        if scope:
            scope_enum = IssueScope(scope)

        # Create input model - use an empty project path since it's not needed for all issues
        input_model = ListIssuesInput(
            project_path="",
            state=state_enum,
            labels=label_list,
            milestone=milestone,
            scope=scope_enum,
            author_id=author_id,
            assignee_id=assignee_id,
            search=search,
            confidential=confidential,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = asyncio.run(list_all_issues(input_model))

        # Convert to list of dicts
        return [issue.model_dump() for issue in response.items]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_group_issues_tool(
    group_id: str,
    state: str | None = None,
    labels: str | None = None,
    milestone: str | None = None,
    scope: str | None = None,
    author_id: int | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    confidential: bool | None = None,
    page: int = 1,
    per_page: int = 20,
) -> list[dict[str, Any]]:
    """List issues in a GitLab group.

    Args:
        group_id: The ID or path of the group.
        state: The state of the issues to list (opened, closed, or all).
        labels: Comma-separated list of label names to filter issues by.
        milestone: The milestone title to filter issues by.
        scope: Return issues for the given scope (created_by_me, assigned_to_me, or all).
        author_id: Return issues created by the given user ID.
        assignee_id: Return issues assigned to the given user ID.
        search: Search query to filter issues by title and description.
        confidential: Filter confidential or public issues.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        List[Dict[str, Any]]: The list of issues.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert comma-separated labels to list if provided
        label_list = None
        if labels:
            label_list = [label.strip() for label in labels.split(",")]

        # Convert string enums to enum values if provided
        state_enum = None
        if state:
            state_enum = IssueState(state)

        scope_enum = None
        if scope:
            scope_enum = IssueScope(scope)

        # Create input model
        input_model = ListGroupIssuesInput(
            group_id=group_id,
            state=state_enum,
            labels=label_list,
            milestone=milestone,
            scope=scope_enum,
            author_id=author_id,
            assignee_id=assignee_id,
            search=search,
            confidential=confidential,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = asyncio.run(list_group_issues(input_model))

        # Convert to list of dicts
        return [issue.model_dump() for issue in response.items]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_issue_tool(project_path: str, issue_iid: int) -> dict[str, Any]:
    """Get a specific issue from a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.

    Returns:
        Dict[str, Any]: The issue details.

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
        response = asyncio.run(get_issue(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def create_issue_tool(
    project_path: str,
    title: str,
    description: str | None = None,
    labels: str | None = None,
    assignee_ids: list[int] | None = None,
    milestone_id: int | None = None,
    confidential: bool = False,
    due_date: str | None = None,
    issue_type: str | None = None,
    weight: int | None = None,
) -> dict[str, Any]:
    """Create a new issue in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        title: The title of the issue.
        description: The description of the issue.
        labels: Comma-separated list of label names to apply to the issue.
        assignee_ids: The IDs of users to assign to the issue.
        milestone_id: The ID of the milestone to associate with the issue.
        confidential: Whether the issue is confidential.
        due_date: The due date in YYYY-MM-DD format.
        issue_type: The type of issue (issue, incident, test_case, or task).
        weight: The weight of the issue.

    Returns:
        Dict[str, Any]: The created issue.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert comma-separated labels to list if provided
        label_list = None
        if labels:
            label_list = [label.strip() for label in labels.split(",")]

        # Convert issue_type string to enum if provided
        issue_type_enum = None
        if issue_type:
            issue_type_enum = IssueType(issue_type)

        # Create input model
        input_model = CreateIssueInput(
            project_path=project_path,
            title=title,
            description=description,
            labels=label_list,
            assignee_ids=assignee_ids,
            milestone_id=milestone_id,
            confidential=confidential,
            due_date=due_date,
            issue_type=issue_type_enum,
            weight=weight,
        )

        # Call service function
        response = asyncio.run(create_issue(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def update_issue_tool(
    project_path: str,
    issue_iid: int,
    title: str | None = None,
    description: str | None = None,
    state_event: str | None = None,
    labels: str | None = None,
    add_labels: str | None = None,
    remove_labels: str | None = None,
    assignee_ids: list[int] | None = None,
    milestone_id: int | None = None,
    confidential: bool | None = None,
    due_date: str | None = None,
    discussion_locked: bool | None = None,
    weight: int | None = None,
) -> dict[str, Any]:
    """Update an existing issue in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        title: The title of the issue.
        description: The description of the issue.
        state_event: Change the state ('close' or 'reopen').
        labels: Comma-separated list of label names to set on the issue.
        add_labels: Comma-separated list of label names to add to the issue.
        remove_labels: Comma-separated list of label names to remove from the issue.
        assignee_ids: The IDs of users to assign to the issue.
        milestone_id: The ID of the milestone to associate with the issue.
        confidential: Whether the issue is confidential.
        due_date: The due date in YYYY-MM-DD format.
        discussion_locked: Flag indicating if the issue's discussion is locked.
        weight: The weight of the issue.

    Returns:
        Dict[str, Any]: The updated issue.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = UpdateIssueInput(
            project_path=project_path,
            issue_iid=issue_iid,
            title=title,
            description=description,
            state_event=state_event,
            labels=labels,
            add_labels=add_labels,
            remove_labels=remove_labels,
            assignee_ids=assignee_ids,
            milestone_id=milestone_id,
            confidential=confidential,
            due_date=due_date,
            discussion_locked=discussion_locked,
            weight=weight,
        )

        # Call service function
        response = asyncio.run(update_issue(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def close_issue_tool(project_path: str, issue_iid: int) -> dict[str, Any]:
    """Close an issue in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.

    Returns:
        Dict[str, Any]: The updated issue.

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
        response = asyncio.run(close_issue(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def delete_issue_tool(project_path: str, issue_iid: int) -> None:
    """Delete an issue from a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = DeleteIssueInput(
            project_path=project_path,
            issue_iid=issue_iid,
        )

        # Call service function
        asyncio.run(delete_issue(input_model))
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def move_issue_tool(
    project_path: str, issue_iid: int, to_project_id: int
) -> dict[str, Any]:
    """Move an issue to a different project.

    Args:
        project_path: The path of the source project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the source project.
        to_project_id: The ID of the target project.

    Returns:
        Dict[str, Any]: The moved issue.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = MoveIssueInput(
            project_path=project_path,
            issue_iid=issue_iid,
            to_project_id=to_project_id,
        )

        # Call service function
        response = asyncio.run(move_issue(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def comment_on_issue_tool(
    project_path: str, issue_iid: int, body: str
) -> dict[str, Any]:
    """Create a comment on an issue in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        body: The content of the comment.

    Returns:
        Dict[str, Any]: The created comment.

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
        response = asyncio.run(comment_on_issue(input_model))

        # Return the comment data
        return response
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_issue_comments_tool(
    project_path: str, issue_iid: int, page: int = 1, per_page: int = 20
) -> list[dict[str, Any]]:
    """List comments on an issue in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        List[Dict[str, Any]]: The list of comments.

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
        response = asyncio.run(list_issue_comments(input_model))

        # Return the comments data
        return cast(list[dict[str, Any]], response)
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_issue_links_tool(project_path: str, issue_iid: int) -> list[dict[str, Any]]:
    """List links to an issue.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.

    Returns:
        List[Dict[str, Any]]: The list of issue links.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = ListIssueLinksInput(
            project_path=project_path,
            issue_iid=issue_iid,
        )

        # Call service function
        response = asyncio.run(list_issue_links(input_model))

        # Convert to list of dicts
        return [link.model_dump() for link in response]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_issue_link_tool(
    project_path: str, issue_iid: int, issue_link_id: int
) -> dict[str, Any]:
    """Get details about an issue link.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        issue_link_id: The ID of the issue link.

    Returns:
        Dict[str, Any]: The issue link details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetIssueLinkInput(
            project_path=project_path,
            issue_iid=issue_iid,
            issue_link_id=issue_link_id,
        )

        # Call service function
        response = asyncio.run(get_issue_link(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def create_issue_link_tool(
    project_path: str,
    issue_iid: int,
    target_project_id: str,
    target_issue_iid: int,
    link_type: str = "relates_to",
) -> dict[str, Any]:
    """Create a link between issues.

    Args:
        project_path: The path of the source project (e.g., 'namespace/project').
        issue_iid: The internal ID of the source issue within the project.
        target_project_id: The ID or path of the target project.
        target_issue_iid: The internal ID of the target issue within the target project.
        link_type: The type of the relation (relates_to, blocks, is_blocked_by).

    Returns:
        Dict[str, Any]: The created issue link.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert link_type string to enum
        link_type_enum = GitLabIssueLinkType(link_type)

        # Create input model
        input_model = CreateIssueLinkInput(
            project_path=project_path,
            issue_iid=issue_iid,
            target_project_id=target_project_id,
            target_issue_iid=target_issue_iid,
            link_type=link_type_enum,
        )

        # Call service function
        response = asyncio.run(create_issue_link(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def delete_issue_link_tool(
    project_path: str, issue_iid: int, issue_link_id: int
) -> dict[str, Any]:
    """Delete a link between issues.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        issue_iid: The internal ID of the issue within the project.
        issue_link_id: The ID of the issue link to delete.

    Returns:
        Dict[str, Any]: The deleted issue link.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = DeleteIssueLinkInput(
            project_path=project_path,
            issue_iid=issue_iid,
            issue_link_id=issue_link_id,
        )

        # Call service function
        response = asyncio.run(delete_issue_link(input_model))

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
