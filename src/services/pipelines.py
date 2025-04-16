from gitlab.v4.objects import ProjectPipeline as Pipeline

from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.filters import PipelineFilterParams
from ..schemas.pipelines import (
    CreatePipelineInput,
    GetPipelineInput,
    GitLabPipeline,
    GitLabPipelineListResponse,
    ListPipelinesInput,
    PipelineAction,
    PipelineActionInput,
)


def _map_pipeline_to_schema(pipeline: Pipeline) -> GitLabPipeline:
    """Map a GitLab pipeline object to our schema.

    Args:
        pipeline: The GitLab pipeline object.

    Returns:
        GitLabPipeline: The mapped pipeline schema.
    """
    return GitLabPipeline(
        id=pipeline.id,
        iid=pipeline.iid,
        project_id=pipeline.project_id,
        sha=pipeline.sha,
        ref=pipeline.ref,
        status=pipeline.status,
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at,
        web_url=pipeline.web_url,
    )


def list_pipelines(input_model: ListPipelinesInput) -> GitLabPipelineListResponse:
    """List pipelines in a GitLab project.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabPipelineListResponse: The list of pipelines.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Convert input model to filter params
        filter_params = PipelineFilterParams(
            page=input_model.page,
            per_page=input_model.per_page,
            status=input_model.status.value if input_model.status else None,
            ref=input_model.ref,
            sha=input_model.sha,
        )

        # Convert to dict, excluding None values
        filters = filter_params.model_dump(exclude_none=True)

        pipelines = project.pipelines.list(**filters)

        # Map to our schema
        items = [
            _map_pipeline_to_schema(project.pipelines.get(pipeline.id))
            for pipeline in pipelines
        ]

        return GitLabPipelineListResponse(
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_pipeline(input_model: GetPipelineInput) -> GitLabPipeline:
    """Get a specific pipeline from a GitLab project.

    Args:
        input_model: The input model containing the project path and pipeline ID.

    Returns:
        GitLabPipeline: The pipeline details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        pipeline = project.pipelines.get(input_model.pipeline_id)

        return _map_pipeline_to_schema(pipeline)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def create_pipeline(input_model: CreatePipelineInput) -> GitLabPipeline:
    """Create a new pipeline in a GitLab project.

    Args:
        input_model: The input model containing the project path, ref, and variables.

    Returns:
        GitLabPipeline: The created pipeline details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Build parameters
        params: dict[str, str | list[dict[str, str]]] = {"ref": input_model.ref}
        if input_model.variables:
            params["variables"] = [
                {"key": key, "value": value}
                for key, value in input_model.variables.items()
            ]

        pipeline = project.pipelines.create(params)

        return _map_pipeline_to_schema(pipeline)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def pipeline_action(input_model: PipelineActionInput) -> GitLabPipeline:
    """Perform an action on a GitLab pipeline (cancel or retry).

    Args:
        input_model: The input model containing the project path, pipeline ID, and action.

    Returns:
        GitLabPipeline: The updated pipeline details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        pipeline = project.pipelines.get(input_model.pipeline_id)

        # Perform the action
        if input_model.action == PipelineAction.CANCEL:
            pipeline.cancel()
        elif input_model.action == PipelineAction.RETRY:
            pipeline.retry()

        # Refresh pipeline data
        pipeline = project.pipelines.get(input_model.pipeline_id)

        return _map_pipeline_to_schema(pipeline)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


# Async versions of the functions
list_pipelines_async = to_async(list_pipelines)
get_pipeline_async = to_async(get_pipeline)
create_pipeline_async = to_async(create_pipeline)
pipeline_action_async = to_async(pipeline_action)
