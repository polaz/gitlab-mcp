"""Utility functions for GitLab issues service operations."""

from typing import Any

from src.schemas.issues import (
    CreateIssueInput,
    ListGroupIssuesInput,
    ListIssuesInput,
    UpdateIssueInput,
)


def build_issue_filter_params(
    input_model: ListIssuesInput | ListGroupIssuesInput,
) -> dict[str, Any]:
    """Build query parameters for filtering issues.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        A dictionary of query parameters.
    """
    params: dict[str, Any] = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    # Add optional filters if they are set
    optional_params = {
        "state": lambda x: x.state.value if x.state else None,
        "labels": lambda x: ",".join(x.labels) if x.labels else None,
        "milestone": lambda x: x.milestone,
        "scope": lambda x: x.scope.value if x.scope else None,
        "author_id": lambda x: x.author_id,
        "assignee_id": lambda x: x.assignee_id,
        "search": lambda x: x.search,
        "created_after": lambda x: x.created_after.isoformat()
        if x.created_after
        else None,
        "created_before": lambda x: x.created_before.isoformat()
        if x.created_before
        else None,
        "updated_after": lambda x: x.updated_after.isoformat()
        if x.updated_after
        else None,
        "updated_before": lambda x: x.updated_before.isoformat()
        if x.updated_before
        else None,
        "confidential": lambda x: str(x.confidential).lower()
        if x.confidential is not None
        else None,
        "order_by": lambda x: x.order_by.value if x.order_by else None,
        "sort": lambda x: x.sort.value if x.sort else None,
    }

    # Add only parameters that have values
    for param, func in optional_params.items():
        if value := func(input_model):
            params[param] = value

    return params


def build_issue_create_payload(input_model: CreateIssueInput) -> dict[str, Any]:
    """Build payload for creating an issue.

    Args:
        input_model: The input model containing issue details.

    Returns:
        A dictionary containing the issue creation payload.
    """
    payload = {
        "title": input_model.title,
        "description": input_model.description,
    }

    optional_params = {
        "assignee_ids": lambda x: x.assignee_ids,
        "milestone_id": lambda x: x.milestone_id,
        "labels": lambda x: ",".join(x.labels) if x.labels else None,
        "due_date": lambda x: x.due_date.isoformat() if x.due_date else None,
        "confidential": lambda x: x.confidential,
        "discussion_to_resolve": lambda x: x.discussion_to_resolve,
        "merge_request_to_resolve_discussions_of": lambda x: x.merge_request_to_resolve_discussions_of,
    }

    for param, func in optional_params.items():
        if value := func(input_model):
            payload[param] = value

    return payload


def build_issue_update_payload(input_model: UpdateIssueInput) -> dict[str, Any]:
    """Build payload for updating an issue.

    Args:
        input_model: The input model containing updated issue details.

    Returns:
        A dictionary containing the issue update payload.
    """
    payload: dict[str, Any] = {}

    optional_params = {
        "title": lambda x: x.title,
        "description": lambda x: x.description,
        "assignee_ids": lambda x: x.assignee_ids
        if x.assignee_ids is not None
        else None,
        "milestone_id": lambda x: x.milestone_id
        if x.milestone_id is not None
        else None,
        "labels": lambda x: ",".join(x.labels) if x.labels is not None else None,
        "state_event": lambda x: x.state_event.value if x.state_event else None,
        "due_date": lambda x: x.due_date.isoformat() if x.due_date else None,
        "confidential": lambda x: x.confidential
        if x.confidential is not None
        else None,
        "discussion_locked": lambda x: x.discussion_locked
        if x.discussion_locked is not None
        else None,
    }

    for param, func in optional_params.items():
        if (value := func(input_model)) is not None:
            payload[param] = value

    return payload
