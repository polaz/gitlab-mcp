from typing import Any

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.pipelines import (
    GetPipelineInput,
    GitLabPipeline,
    GitLabPipelineListResponse,
    ListPipelinesInput,
)


async def list_project_pipelines(
    input_model: ListPipelinesInput,
) -> GitLabPipelineListResponse:
    """List pipelines in a GitLab project.

    Args:
        input_model: The input model containing filter parameters.

    Returns:
        GitLabPipelineListResponse: A paginated list of pipelines.

    Raises:
        GitLabAPIError: If retrieving the pipelines fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        params: dict[str, Any] = {
            "page": input_model.page,
            "per_page": input_model.per_page,
        }
        if input_model.status:
            params["status"] = input_model.status.value
        if input_model.ref:
            params["ref"] = input_model.ref
        if input_model.sha:
            params["sha"] = input_model.sha

        response_data = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/pipelines", params=params
        )
        items = [GitLabPipeline.model_validate(p) for p in response_data]
        return GitLabPipelineListResponse(items=items)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Project {input_model.project_path} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list pipelines for project {input_model.project_path}",
                "operation": "list_project_pipelines",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing project pipelines",
                "operation": "list_project_pipelines",
            },
        ) from exc


async def get_single_pipeline(input_model: GetPipelineInput) -> GitLabPipeline:
    """Get a single pipeline by ID for a GitLab project.

    Args:
        input_model: The input model with project path and pipeline ID.

    Returns:
        GitLabPipeline: The pipeline details.

    Raises:
        GitLabAPIError: If retrieving the pipeline fails.
    """
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        response_data = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/pipelines/{input_model.pipeline_id}"
        )
        return GitLabPipeline.model_validate(response_data)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Pipeline {input_model.pipeline_id} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get pipeline {input_model.pipeline_id}",
                "operation": "get_single_pipeline",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error getting pipeline",
                "operation": "get_single_pipeline",
            },
        ) from exc


async def get_latest_pipeline(
    project_path: str, ref: str | None = None
) -> GitLabPipeline:
    """Get the latest pipeline for the most recent commit on a specific ref.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        ref: The branch or tag to check for the latest pipeline.

    Returns:
        GitLabPipeline: The latest pipeline details.

    Raises:
        GitLabAPIError: If retrieving the latest pipeline fails.
    """
    try:
        encoded_path = gitlab_rest_client._encode_path_parameter(project_path)
        params = {"ref": ref} if ref else None
        response_data = await gitlab_rest_client.get_async(
            f"/projects/{encoded_path}/pipelines/latest", params=params
        )
        return GitLabPipeline.model_validate(response_data)
    except GitLabAPIError as exc:
        ref_info = f" for ref '{ref}'" if ref else ""
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {
                    "message": f"Latest pipeline{ref_info} not found for project {project_path}"
                },
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get latest pipeline{ref_info} for project {project_path}",
                "operation": "get_latest_pipeline",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error getting latest pipeline",
                "operation": "get_latest_pipeline",
            },
        ) from exc
