"""GitLab milestone service operations."""

from typing import Any

from ..api.rest_client import GitLabRestClient
from ..schemas.milestones import (
    CreateMilestoneInput,
    DeleteMilestoneInput,
    GetMilestoneInput,
    GitLabMilestone,
    ListMilestonesInput,
    MilestoneListResponse,
    UpdateMilestoneInput,
)


class GitLabMilestoneService:
    """Service for GitLab milestone operations."""

    def __init__(self, client: GitLabRestClient):
        self.client = client

    async def create_milestone(self, input_data: CreateMilestoneInput) -> GitLabMilestone:
        """Create a new milestone in GitLab."""
        if not input_data.project_path and not input_data.group_id:
            raise ValueError("Either project_path or group_id must be provided")

        if input_data.project_path and input_data.group_id:
            raise ValueError("Cannot specify both project_path and group_id")

        payload = {
            "title": input_data.title,
        }

        if input_data.description:
            payload["description"] = input_data.description
        if input_data.due_date:
            payload["due_date"] = input_data.due_date
        if input_data.start_date:
            payload["start_date"] = input_data.start_date

        if input_data.project_path:
            endpoint = f"/projects/{input_data.project_path.replace('/', '%2F')}/milestones"
        else:
            endpoint = f"/groups/{input_data.group_id}/milestones"

        response = await self.client.post_async(endpoint, json_data=payload)
        return GitLabMilestone(**response)

    async def list_milestones(self, input_data: ListMilestonesInput) -> MilestoneListResponse:
        """List milestones from GitLab."""
        if not input_data.project_path and not input_data.group_id:
            raise ValueError("Either project_path or group_id must be provided")

        if input_data.project_path and input_data.group_id:
            raise ValueError("Cannot specify both project_path and group_id")

        params = {
            "page": input_data.page,
            "per_page": input_data.per_page,
        }

        if input_data.state:
            params["state"] = input_data.state
        if input_data.search:
            params["search"] = input_data.search

        if input_data.project_path:
            endpoint = f"/projects/{input_data.project_path.replace('/', '%2F')}/milestones"
        else:
            endpoint = f"/groups/{input_data.group_id}/milestones"

        response = await self.client.get_async(endpoint, params=params)
        milestones = [GitLabMilestone(**milestone) for milestone in response]

        return MilestoneListResponse(
            milestones=milestones,
            count=len(milestones)
        )

    async def get_milestone(self, input_data: GetMilestoneInput) -> GitLabMilestone:
        """Get details for a specific milestone."""
        if not input_data.project_path and not input_data.group_id:
            raise ValueError("Either project_path or group_id must be provided")

        if input_data.project_path and input_data.group_id:
            raise ValueError("Cannot specify both project_path and group_id")

        if input_data.project_path:
            endpoint = f"/projects/{input_data.project_path.replace('/', '%2F')}/milestones/{input_data.milestone_id}"
        else:
            endpoint = f"/groups/{input_data.group_id}/milestones/{input_data.milestone_id}"

        response = await self.client.get_async(endpoint)
        return GitLabMilestone(**response)

    async def update_milestone(self, input_data: UpdateMilestoneInput) -> GitLabMilestone:
        """Update an existing milestone."""
        if not input_data.project_path and not input_data.group_id:
            raise ValueError("Either project_path or group_id must be provided")

        if input_data.project_path and input_data.group_id:
            raise ValueError("Cannot specify both project_path and group_id")

        payload = {}

        if input_data.title:
            payload["title"] = input_data.title
        if input_data.description is not None:
            payload["description"] = input_data.description
        if input_data.due_date is not None:
            payload["due_date"] = input_data.due_date
        if input_data.start_date is not None:
            payload["start_date"] = input_data.start_date
        if input_data.state_event:
            payload["state_event"] = input_data.state_event

        if input_data.project_path:
            endpoint = f"/projects/{input_data.project_path.replace('/', '%2F')}/milestones/{input_data.milestone_id}"
        else:
            endpoint = f"/groups/{input_data.group_id}/milestones/{input_data.milestone_id}"

        response = await self.client.put_async(endpoint, json_data=payload)
        return GitLabMilestone(**response)

    async def delete_milestone(self, input_data: DeleteMilestoneInput) -> dict[str, Any]:
        """Delete a milestone from GitLab."""
        if not input_data.project_path and not input_data.group_id:
            raise ValueError("Either project_path or group_id must be provided")

        if input_data.project_path and input_data.group_id:
            raise ValueError("Cannot specify both project_path and group_id")

        if input_data.project_path:
            endpoint = f"/projects/{input_data.project_path.replace('/', '%2F')}/milestones/{input_data.milestone_id}"
        else:
            endpoint = f"/groups/{input_data.group_id}/milestones/{input_data.milestone_id}"

        await self.client.delete_async(endpoint)
        return {"success": True, "message": "Milestone deleted successfully"}


def _get_client():
    """Get GitLab client instance."""
    return GitLabRestClient()

def _get_service():
    return GitLabMilestoneService(_get_client())

# Functions for fastmcp integration
async def create_milestone(input_model: CreateMilestoneInput):
    """Create a new milestone in GitLab."""
    service = _get_service()
    result = await service.create_milestone(input_model)
    return result.model_dump()

async def list_milestones(input_model: ListMilestonesInput):
    """List milestones from GitLab."""
    service = _get_service()
    result = await service.list_milestones(input_model)
    return result.model_dump()

async def get_milestone(input_model: GetMilestoneInput):
    """Get details for a specific milestone."""
    service = _get_service()
    result = await service.get_milestone(input_model)
    return result.model_dump()

async def update_milestone(input_model: UpdateMilestoneInput):
    """Update an existing milestone."""
    service = _get_service()
    result = await service.update_milestone(input_model)
    return result.model_dump()

async def delete_milestone(input_model: DeleteMilestoneInput):
    """Delete a milestone from GitLab."""
    service = _get_service()
    return await service.delete_milestone(input_model)
