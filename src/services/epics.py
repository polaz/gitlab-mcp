"""Epic services for GitLab API.

This module provides functions for managing epics in GitLab groups.
Epics are available in GitLab Premium and Ultimate tiers only.
"""

from typing import Any

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.epics import (
    AssignIssueToEpicInput,
    CreateEpicInput,
    DeleteEpicInput,
    EpicIssueAssociation,
    GetEpicInput,
    GitLabEpic,
    ListEpicIssuesInput,
    ListEpicsInput,
    RemoveIssueFromEpicInput,
    UpdateEpicInput,
    UpdateEpicIssueAssociationInput,
)


async def create_epic(input_model: CreateEpicInput) -> GitLabEpic:
    """Create a new epic in a GitLab group.

    Creates a new epic within the specified group. Epics are containers
    for organizing related issues and child epics (Premium/Ultimate only).

    Args:
        input_model: Epic creation parameters including group_id, title,
                    and optional fields like description, labels, dates.

    Returns:
        GitLabEpic: The created epic with full details.

    Raises:
        GitLabAPIError: If epic creation fails, group not found, or insufficient permissions.

    Example:
        create_epic(CreateEpicInput(
            group_id="my-team",
            title="User Authentication Epic",
            description="Implement OAuth2 with SSO support",
            labels=["backend", "security"]
        ))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        payload = input_model.model_dump(exclude={"group_id"}, exclude_none=True)

        # Handle labels field - GitLab API expects comma-separated string
        if "labels" in payload and payload["labels"] is not None:
            payload["labels"] = ",".join(payload["labels"])

        response_data = await gitlab_rest_client.post_async(
            f"/groups/{group_id}/epics",
            json_data=payload
        )
        return GitLabEpic.model_validate(response_data)

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Group {input_model.group_id} not found"},
            ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to create epic in group {input_model.group_id}",
                "operation": "create_epic",
                "title": input_model.title,
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error creating epic",
                "operation": "create_epic",
                "group_id": input_model.group_id,
            },
        ) from exc


async def list_epics(input_model: ListEpicsInput) -> list[GitLabEpic]:
    """List epics in a GitLab group with comprehensive filtering options.

    Retrieves epics from the specified group with support for state filtering,
    label filtering, author filtering, search, date ranges, and more.

    Args:
        input_model: Epic listing parameters including group_id and optional
                    filters like state, labels, author, search terms, dates.

    Returns:
        list[GitLabEpic]: List of epics matching the specified criteria.

    Raises:
        GitLabAPIError: If group not found, insufficient permissions, or API error.

    Example:
        list_epics(ListEpicsInput(
            group_id="my-team",
            state="opened",
            labels="backend,security",
            search="authentication"
        ))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        params = input_model.model_dump(exclude={"group_id"}, exclude_none=True)

        response_data = await gitlab_rest_client.get_async(
            f"/groups/{group_id}/epics",
            params=params
        )
        return [GitLabEpic.model_validate(epic_data) for epic_data in response_data]

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Group {input_model.group_id} not found"},
            ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list epics in group {input_model.group_id}",
                "operation": "list_epics",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing epics",
                "operation": "list_epics",
                "group_id": input_model.group_id,
            },
        ) from exc


async def get_epic(input_model: GetEpicInput) -> GitLabEpic:
    """Get details for a specific epic in a GitLab group.

    Retrieves comprehensive information about a specific epic including
    all metadata, dates, labels, and relationships.

    Args:
        input_model: Epic identification parameters (group_id, epic_iid).

    Returns:
        GitLabEpic: Detailed epic information.

    Raises:
        GitLabAPIError: If epic not found, group not found, or insufficient permissions.

    Example:
        get_epic(GetEpicInput(group_id="my-team", epic_iid=42))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

        response_data = await gitlab_rest_client.get_async(
            f"/groups/{group_id}/epics/{input_model.epic_iid}"
        )
        return GitLabEpic.model_validate(response_data)

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            if "group" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {input_model.group_id} not found"},
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic {input_model.epic_iid} not found in group {input_model.group_id}"},
                ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get epic {input_model.epic_iid} from group {input_model.group_id}",
                "operation": "get_epic",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error getting epic",
                "operation": "get_epic",
                "group_id": input_model.group_id,
                "epic_iid": input_model.epic_iid,
            },
        ) from exc


async def update_epic(input_model: UpdateEpicInput) -> GitLabEpic:
    """Update an existing epic in a GitLab group.

    Updates epic properties including title, description, state, labels, dates,
    and hierarchy relationships. Supports comprehensive label management with
    add/remove operations.

    Args:
        input_model: Epic update parameters including group_id, epic_iid,
                    and optional fields to update like title, description,
                    state_event, labels, dates.

    Returns:
        GitLabEpic: The updated epic with all changes applied.

    Raises:
        GitLabAPIError: If epic not found, update fails, or insufficient permissions.

    Example:
        update_epic(UpdateEpicInput(
            group_id="my-team",
            epic_iid=42,
            title="Updated Epic Title",
            add_labels=["reviewed"],
            state_event="close"
        ))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        payload = input_model.model_dump(exclude={"group_id", "epic_iid"}, exclude_none=True)

        # Handle label fields - GitLab API expects comma-separated strings
        for key in ("labels", "add_labels", "remove_labels"):
            if key in payload and payload[key] is not None:
                payload[key] = ",".join(payload[key])

        response_data = await gitlab_rest_client.put_async(
            f"/groups/{group_id}/epics/{input_model.epic_iid}",
            json_data=payload
        )
        return GitLabEpic.model_validate(response_data)

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            if "group" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {input_model.group_id} not found"},
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic {input_model.epic_iid} not found in group {input_model.group_id}"},
                ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to update epic {input_model.epic_iid} in group {input_model.group_id}",
                "operation": "update_epic",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error updating epic",
                "operation": "update_epic",
                "group_id": input_model.group_id,
                "epic_iid": input_model.epic_iid,
            },
        ) from exc


async def delete_epic(input_model: DeleteEpicInput) -> dict[str, Any]:
    """Delete an epic from a GitLab group.

    WARNING: This permanently deletes the epic and cannot be undone.
    All epic-issue associations will be removed, but the issues themselves
    will remain in their projects.

    Args:
        input_model: Epic deletion parameters (group_id, epic_iid).

    Returns:
        dict: API response confirming deletion.

    Raises:
        GitLabAPIError: If epic not found, deletion fails, or insufficient permissions.

    Example:
        delete_epic(DeleteEpicInput(group_id="my-team", epic_iid=42))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

        response_data = await gitlab_rest_client.delete_async(
            f"/groups/{group_id}/epics/{input_model.epic_iid}"
        )
        return response_data

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            if "group" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {input_model.group_id} not found"},
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic {input_model.epic_iid} not found in group {input_model.group_id}"},
                ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to delete epic {input_model.epic_iid} from group {input_model.group_id}",
                "operation": "delete_epic",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error deleting epic",
                "operation": "delete_epic",
                "group_id": input_model.group_id,
                "epic_iid": input_model.epic_iid,
            },
        ) from exc


# Epic-Issue Association Functions

async def list_epic_issues(input_model: ListEpicIssuesInput) -> list[dict[str, Any]]:
    """List all issues assigned to a specific epic.

    Retrieves all issues that are currently associated with the specified epic.
    Returns issue details along with association metadata.

    Args:
        input_model: Epic identification parameters (group_id, epic_iid).

    Returns:
        list[dict]: List of issues assigned to the epic with association details.

    Raises:
        GitLabAPIError: If epic not found, group not found, or insufficient permissions.

    Example:
        list_epic_issues(ListEpicIssuesInput(group_id="my-team", epic_iid=42))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

        response_data = await gitlab_rest_client.get_async(
            f"/groups/{group_id}/epics/{input_model.epic_iid}/issues"
        )
        return response_data

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            if "group" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {input_model.group_id} not found"},
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic {input_model.epic_iid} not found in group {input_model.group_id}"},
                ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list issues for epic {input_model.epic_iid} in group {input_model.group_id}",
                "operation": "list_epic_issues",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing epic issues",
                "operation": "list_epic_issues",
                "group_id": input_model.group_id,
                "epic_iid": input_model.epic_iid,
            },
        ) from exc


async def assign_issue_to_epic(input_model: AssignIssueToEpicInput) -> EpicIssueAssociation:
    """Assign an issue to an epic, creating an association between them.

    Creates a relationship between an issue and an epic. If the issue was
    previously assigned to another epic, it will be reassigned to this epic.

    Args:
        input_model: Assignment parameters (group_id, epic_iid, issue_id).
                    Note: issue_id is the global issue ID, not issue_iid.

    Returns:
        EpicIssueAssociation: The created association with metadata.

    Raises:
        GitLabAPIError: If epic/issue not found, assignment fails, or insufficient permissions.

    Example:
        assign_issue_to_epic(AssignIssueToEpicInput(
            group_id="my-team",
            epic_iid=42,
            issue_id=12345
        ))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

        response_data = await gitlab_rest_client.post_async(
            f"/groups/{group_id}/epics/{input_model.epic_iid}/issues/{input_model.issue_id}",
            json_data={}
        )
        return EpicIssueAssociation.model_validate(response_data)

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            if "group" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {input_model.group_id} not found"},
                ) from exc
            elif "epic" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic {input_model.epic_iid} not found in group {input_model.group_id}"},
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Issue {input_model.issue_id} not found"},
                ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to assign issue {input_model.issue_id} to epic {input_model.epic_iid}",
                "operation": "assign_issue_to_epic",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error assigning issue to epic",
                "operation": "assign_issue_to_epic",
                "group_id": input_model.group_id,
                "epic_iid": input_model.epic_iid,
                "issue_id": input_model.issue_id,
            },
        ) from exc


async def remove_issue_from_epic(input_model: RemoveIssueFromEpicInput) -> dict[str, Any]:
    """Remove an issue from an epic, breaking their association.

    Removes the relationship between an issue and an epic. The issue will
    no longer be associated with the epic but remains in its project.

    Args:
        input_model: Removal parameters (group_id, epic_iid, epic_issue_id).
                    Note: epic_issue_id is the association ID, not the issue ID.
                    Get this from list_epic_issues response.

    Returns:
        dict: API response confirming removal.

    Raises:
        GitLabAPIError: If association not found, removal fails, or insufficient permissions.

    Example:
        remove_issue_from_epic(RemoveIssueFromEpicInput(
            group_id="my-team",
            epic_iid=42,
            epic_issue_id=54321
        ))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)

        response_data = await gitlab_rest_client.delete_async(
            f"/groups/{group_id}/epics/{input_model.epic_iid}/issues/{input_model.epic_issue_id}"
        )
        return response_data

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            if "group" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {input_model.group_id} not found"},
                ) from exc
            elif "epic" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic {input_model.epic_iid} not found in group {input_model.group_id}"},
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic-issue association {input_model.epic_issue_id} not found"},
                ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to remove issue from epic {input_model.epic_iid}",
                "operation": "remove_issue_from_epic",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error removing issue from epic",
                "operation": "remove_issue_from_epic",
                "group_id": input_model.group_id,
                "epic_iid": input_model.epic_iid,
                "epic_issue_id": input_model.epic_issue_id,
            },
        ) from exc


async def update_epic_issue_association(input_model: UpdateEpicIssueAssociationInput) -> EpicIssueAssociation:
    """Update the position/order of an issue within an epic.

    Changes the relative position of an issue within an epic's issue list.
    Useful for prioritizing or organizing issues within an epic.

    Args:
        input_model: Update parameters (group_id, epic_iid, epic_issue_id)
                    and position modifiers (move_before_id or move_after_id).

    Returns:
        EpicIssueAssociation: The updated association with new position.

    Raises:
        GitLabAPIError: If association not found, update fails, or insufficient permissions.

    Example:
        update_epic_issue_association(UpdateEpicIssueAssociationInput(
            group_id="my-team",
            epic_iid=42,
            epic_issue_id=54321,
            move_before_id=12345
        ))
    """
    try:
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        payload = input_model.model_dump(
            exclude={"group_id", "epic_iid", "epic_issue_id"},
            exclude_none=True
        )

        response_data = await gitlab_rest_client.put_async(
            f"/groups/{group_id}/epics/{input_model.epic_iid}/issues/{input_model.epic_issue_id}",
            json_data=payload
        )
        return EpicIssueAssociation.model_validate(response_data)

    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            if "group" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Group {input_model.group_id} not found"},
                ) from exc
            elif "epic" in str(exc).lower():
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic {input_model.epic_iid} not found in group {input_model.group_id}"},
                ) from exc
            else:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Epic-issue association {input_model.epic_issue_id} not found"},
                ) from exc
        elif "premium" in str(exc).lower() or "ultimate" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.PERMISSION_DENIED,
                {"message": "Epics require GitLab Premium or Ultimate subscription"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to update epic-issue association {input_model.epic_issue_id}",
                "operation": "update_epic_issue_association",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error updating epic-issue association",
                "operation": "update_epic_issue_association",
                "group_id": input_model.group_id,
                "epic_iid": input_model.epic_iid,
                "epic_issue_id": input_model.epic_issue_id,
            },
        ) from exc
