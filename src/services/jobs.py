"""Services for interacting with GitLab CI/CD jobs."""

from typing import Any

from src.api.rest_client import gitlab_rest_client
from src.schemas import (
    GitLabJob,
    GitLabJobListResponse,
    GitLabJobLogsResponse,
    GitLabJobTokenResponse,
    ListPipelineJobsInput,
    ListPipelineTriggerJobsInput,
    ListProjectJobsInput,
)


async def list_project_jobs(input_model: ListProjectJobsInput) -> GitLabJobListResponse:
    """List jobs for a project.

    Args:
        input_model: The input parameters.

    Returns:
        A response containing the list of jobs.
    """
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    params: dict[str, Any] = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    if input_model.scope:
        params["scope[]"] = [scope.value for scope in input_model.scope]

    response = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/jobs", params=params
    )

    return GitLabJobListResponse(
        items=[GitLabJob.model_validate(job) for job in response]
    )


async def list_pipeline_jobs(
    input_model: ListPipelineJobsInput,
) -> GitLabJobListResponse:
    """List jobs for a pipeline.

    Args:
        input_model: The input parameters.

    Returns:
        A response containing the list of jobs.
    """
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    params: dict[str, Any] = {
        "page": input_model.page,
        "per_page": input_model.per_page,
        "include_retried": input_model.include_retried,
    }

    if input_model.scope:
        params["scope[]"] = [scope.value for scope in input_model.scope]

    response = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/pipelines/{input_model.pipeline_id}/jobs",
        params=params,
    )

    return GitLabJobListResponse(
        items=[GitLabJob.model_validate(job) for job in response]
    )


async def list_pipeline_trigger_jobs(
    input_model: ListPipelineTriggerJobsInput,
) -> GitLabJobListResponse:
    """List trigger jobs (bridges) for a pipeline.

    Args:
        input_model: The input parameters.

    Returns:
        A response containing the list of trigger jobs.
    """
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)

    params: dict[str, Any] = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    if input_model.scope:
        params["scope[]"] = [scope.value for scope in input_model.scope]

    response = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/pipelines/{input_model.pipeline_id}/bridges",
        params=params,
    )

    return GitLabJobListResponse(
        items=[GitLabJob.model_validate(job) for job in response]
    )


async def get_job(input_dict: dict[str, Any]) -> GitLabJob:
    """Get a specific job.

    Args:
        input_dict: The input parameters containing project_path and job_id.

    Returns:
        The job details.
    """
    project_path = gitlab_rest_client._encode_path_parameter(input_dict["project_path"])
    job_id = input_dict["job_id"]

    response = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/jobs/{job_id}"
    )

    return GitLabJob.model_validate(response)


async def get_job_logs(input_dict: dict[str, Any]) -> GitLabJobLogsResponse:
    """Get logs for a job.

    Args:
        input_dict: The input parameters containing project_path and job_id.

    Returns:
        The job logs.
    """
    project_path = gitlab_rest_client._encode_path_parameter(input_dict["project_path"])
    job_id = input_dict["job_id"]

    response = await gitlab_rest_client.get_async(
        f"/projects/{project_path}/jobs/{job_id}/trace"
    )

    return GitLabJobLogsResponse(content=response)


async def get_job_token_job() -> GitLabJob:
    """Get the job that generated a job token.

    This must be run from within a CI job with a CI_JOB_TOKEN.

    Returns:
        The job details.
    """
    response = await gitlab_rest_client.get_async("/job")

    return GitLabJob.model_validate(response)


async def get_job_token_allowed_agents() -> GitLabJobTokenResponse:
    """Get the job and allowed GitLab agents by CI_JOB_TOKEN.

    This must be run from within a CI job with a CI_JOB_TOKEN.

    Returns:
        The job token response with allowed agents.
    """
    response = await gitlab_rest_client.get_async("/job/allowed_agents")

    return GitLabJobTokenResponse.model_validate(response)
