"""Service functions for interacting with GitLab CI/CD jobs."""

from gitlab.base import RESTObject
from gitlab.v4.objects import ProjectJob

from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.jobs import (
    GetJobInput,
    GetJobLogsInput,
    GitLabJob,
    GitLabJobListResponse,
    GitLabJobLog,
    ListPipelineJobsInput,
)


def _map_job_to_schema(job: ProjectJob | RESTObject) -> GitLabJob:
    """Map a GitLab job object to our schema.

    Args:
        job: The GitLab job object.

    Returns:
        GitLabJob: The mapped job schema.
    """
    # Extract pipeline_id safely, defaulting to 0 if not available
    pipeline_id = (
        job.pipeline.get("id", 0) if hasattr(job, "pipeline") and job.pipeline else 0
    )

    return GitLabJob(
        id=job.id,
        name=job.name,
        status=job.status,
        stage=job.stage,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        duration=job.duration,
        web_url=job.web_url,
        pipeline_id=pipeline_id,
        user=job.user if hasattr(job, "user") else None,
        ref=job.ref,
    )


def list_pipeline_jobs(input_model: ListPipelineJobsInput) -> GitLabJobListResponse:
    """List jobs in a GitLab pipeline.

    Args:
        input_model: The input model containing project path and pipeline ID.

    Returns:
        GitLabJobListResponse: The list of jobs in the pipeline.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        pipeline = project.pipelines.get(input_model.pipeline_id)

        # Get jobs for the pipeline
        filters = {
            "page": input_model.page,
            "per_page": input_model.per_page,
        }

        jobs = pipeline.jobs.list(**filters)

        # Map to our schema
        items = [_map_job_to_schema(job) for job in jobs]

        return GitLabJobListResponse(
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_job(input_model: GetJobInput) -> GitLabJob:
    """Get a specific job from a GitLab project.

    Args:
        input_model: The input model containing the project path and job ID.

    Returns:
        GitLabJob: The job details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        job = project.jobs.get(input_model.job_id)

        return _map_job_to_schema(job)
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def get_job_logs(input_model: GetJobLogsInput) -> GitLabJobLog:
    """Get logs from a GitLab job.

    Args:
        input_model: The input model containing the project path and job ID.

    Returns:
        GitLabJobLog: The job logs.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)
        job = project.jobs.get(input_model.job_id)

        # Get job logs
        logs = job.trace().decode("utf-8")

        return GitLabJobLog(
            id=job.id,
            content=logs,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


# Async versions of the job functions
list_pipeline_jobs_async = to_async(list_pipeline_jobs)
get_job_async = to_async(get_job)
get_job_logs_async = to_async(get_job_logs)
