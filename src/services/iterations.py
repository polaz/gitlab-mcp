"""GitLab iteration service operations."""

from typing import Any

from ..api.rest_client import GitLabRestClient
from ..schemas.iterations import (
    CreateIterationInput,
    DeleteIterationInput,
    GetIterationInput,
    GitLabIteration,
    IterationListResponse,
    ListIterationsInput,
    UpdateIterationInput,
)


class GitLabIterationService:
    """Service for GitLab iteration operations."""

    def __init__(self, client: GitLabRestClient):
        self.client = client

    async def create_iteration(self, input_data: CreateIterationInput) -> GitLabIteration:
        """Create a new iteration in GitLab."""
        payload = {
            "title": input_data.title,
            "start_date": input_data.start_date,
            "due_date": input_data.due_date,
        }

        if input_data.description:
            payload["description"] = input_data.description

        endpoint = f"/groups/{input_data.group_id}/iterations"
        response = await self.client.post_async(endpoint, json_data=payload)
        return GitLabIteration(**response)

    async def list_iterations(self, input_data: ListIterationsInput) -> IterationListResponse:
        """List iterations from GitLab."""
        params = {
            "page": input_data.page,
            "per_page": input_data.per_page,
        }

        if input_data.state:
            params["state"] = input_data.state
        if input_data.search:
            params["search"] = input_data.search
        if input_data.include_ancestors is not None:
            params["include_ancestors"] = input_data.include_ancestors

        endpoint = f"/groups/{input_data.group_id}/iterations"
        response = await self.client.get_async(endpoint, params=params)
        iterations = [GitLabIteration(**iteration) for iteration in response]

        return IterationListResponse(
            iterations=iterations,
            count=len(iterations)
        )

    async def get_iteration(self, input_data: GetIterationInput) -> GitLabIteration:
        """Get details for a specific iteration."""
        endpoint = f"/groups/{input_data.group_id}/iterations/{input_data.iteration_id}"
        response = await self.client.get_async(endpoint)
        return GitLabIteration(**response)

    async def update_iteration(self, input_data: UpdateIterationInput) -> GitLabIteration:
        """Update an existing iteration."""
        payload = {}

        if input_data.title:
            payload["title"] = input_data.title
        if input_data.description is not None:
            payload["description"] = input_data.description
        if input_data.start_date:
            payload["start_date"] = input_data.start_date
        if input_data.due_date:
            payload["due_date"] = input_data.due_date
        if input_data.state_event:
            payload["state_event"] = input_data.state_event

        endpoint = f"/groups/{input_data.group_id}/iterations/{input_data.iteration_id}"
        response = await self.client.put_async(endpoint, json_data=payload)
        return GitLabIteration(**response)

    async def delete_iteration(self, input_data: DeleteIterationInput) -> dict[str, Any]:
        """Delete an iteration from GitLab."""
        endpoint = f"/groups/{input_data.group_id}/iterations/{input_data.iteration_id}"
        await self.client.delete_async(endpoint)
        return {"success": True, "message": "Iteration deleted successfully"}


def _get_client():
    """Get GitLab client instance."""
    return GitLabRestClient()

def _get_service():
    return GitLabIterationService(_get_client())

# Functions for fastmcp integration
async def create_iteration(input_model: CreateIterationInput):
    """Create a new iteration in GitLab."""
    service = _get_service()
    result = await service.create_iteration(input_model)
    return result.model_dump()

async def list_iterations(input_model: ListIterationsInput):
    """List iterations from GitLab."""
    service = _get_service()
    result = await service.list_iterations(input_model)
    return result.model_dump()

async def get_iteration(input_model: GetIterationInput):
    """Get details for a specific iteration."""
    service = _get_service()
    result = await service.get_iteration(input_model)
    return result.model_dump()

async def update_iteration(input_model: UpdateIterationInput):
    """Update an existing iteration."""
    service = _get_service()
    result = await service.update_iteration(input_model)
    return result.model_dump()

async def delete_iteration(input_model: DeleteIterationInput):
    """Delete an iteration from GitLab."""
    service = _get_service()
    return await service.delete_iteration(input_model)
