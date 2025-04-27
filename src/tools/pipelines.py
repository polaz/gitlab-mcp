import asyncio

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.pipelines import (
    GetPipelineInput,
    ListPipelinesInput,
)
from src.services.pipelines import (
    get_latest_pipeline,
    get_single_pipeline,
    list_project_pipelines,
)


def list_project_pipelines_tool(
    project_path: str,
    status: str | None = None,
    ref: str | None = None,
    sha: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> list[dict]:
    """List pipelines in a GitLab project.

    Args:
        project_path (str): Path of the project (e.g., 'namespace/project').
        status (str, optional): Pipeline status (e.g., 'success', 'failed').
        ref (str, optional): Branch or tag name to filter pipelines.
        sha (str, optional): Commit SHA to filter pipelines.
        page (int, optional): Page number for pagination.
        per_page (int, optional): Number of items per page.

    Returns:
        list[dict]: List of pipelines as dictionaries.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        status_enum = None
        if status:
            from src.schemas.pipelines import PipelineStatus

            status_enum = PipelineStatus(status)
        input_model = ListPipelinesInput(
            project_path=project_path,
            status=status_enum,
            ref=ref,
            sha=sha,
            page=page,
            per_page=per_page,
        )
        response = asyncio.run(list_project_pipelines(input_model))
        return [pipeline.model_dump() for pipeline in response.items]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_single_pipeline_tool(
    project_path: str,
    pipeline_id: int,
) -> dict:
    """Get a single pipeline by ID for a GitLab project.

    Args:
        project_path (str): Path of the project (e.g., 'namespace/project').
        pipeline_id (int): The pipeline ID.

    Returns:
        dict: The pipeline details as a dictionary.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        input_model = GetPipelineInput(
            project_path=project_path,
            pipeline_id=pipeline_id,
        )
        response = asyncio.run(get_single_pipeline(input_model))
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_latest_pipeline_tool(
    project_path: str,
    ref: str | None = None,
) -> dict:
    """Get the latest pipeline for the most recent commit on a specific ref.

    Args:
        project_path (str): Path of the project (e.g., 'namespace/project').
        ref (str, optional): Branch or tag to check for the latest pipeline.

    Returns:
        dict: The latest pipeline details as a dictionary.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        response = asyncio.run(get_latest_pipeline(project_path, ref))
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
