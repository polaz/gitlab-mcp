"""Tool functions for interacting with GitLab CI/CD jobs."""

import asyncio

from src.api.custom_exceptions import GitLabAPIError
from src.schemas.jobs import (
    JobScope,
    ListPipelineJobsInput,
    ListPipelineTriggerJobsInput,
    ListProjectJobsInput,
)
from src.services.jobs import (
    get_job,
    get_job_logs,
    list_pipeline_jobs,
    list_pipeline_trigger_jobs,
    list_project_jobs,
)


def list_project_jobs_tool(
    project_path: str,
    scope: list[str] | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List jobs for a project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        scope: The scope of jobs to show (created, pending, running, failed, success, canceled, skipped, waiting_for_resource, or manual).
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        A dictionary containing the list of jobs.
    """
    try:
        input_model = ListProjectJobsInput(
            project_path=project_path,
            scope=[JobScope(s) for s in scope] if scope else None,
            page=page,
            per_page=per_page,
        )
        result = list_project_jobs(input_model)
        jobs_response = asyncio.run(result)
        return {"jobs": [job.model_dump() for job in jobs_response.items]}
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_pipeline_jobs_tool(
    project_path: str,
    pipeline_id: int,
    include_retried: bool = False,
    scope: list[str] | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List jobs for a pipeline.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        include_retried: Whether to include retried jobs.
        scope: The scope of jobs to show (created, pending, running, failed, success, canceled, skipped, waiting_for_resource, or manual).
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        A dictionary containing the list of jobs.
    """
    try:
        input_model = ListPipelineJobsInput(
            project_path=project_path,
            pipeline_id=pipeline_id,
            include_retried=include_retried,
            scope=[JobScope(s) for s in scope] if scope else None,
            page=page,
            per_page=per_page,
        )
        result = list_pipeline_jobs(input_model)
        jobs_response = asyncio.run(result)
        return {"jobs": [job.model_dump() for job in jobs_response.items]}
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def list_pipeline_trigger_jobs_tool(
    project_path: str,
    pipeline_id: int,
    scope: list[str] | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List trigger jobs (bridges) for a pipeline.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        scope: The scope of jobs to show (created, pending, running, failed, success, canceled, skipped, waiting_for_resource, or manual).
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        A dictionary containing the list of trigger jobs.
    """
    try:
        input_model = ListPipelineTriggerJobsInput(
            project_path=project_path,
            pipeline_id=pipeline_id,
            scope=[JobScope(s) for s in scope] if scope else None,
            page=page,
            per_page=per_page,
        )
        result = list_pipeline_trigger_jobs(input_model)
        jobs_response = asyncio.run(result)
        return {"bridge_jobs": [job.model_dump() for job in jobs_response.items]}
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_job_tool(
    project_path: str,
    job_id: int,
) -> dict:
    """Get a specific job.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        job_id: The ID of the job.

    Returns:
        A dictionary containing the job details.
    """
    try:
        input_dict = {
            "project_path": project_path,
            "job_id": job_id,
        }
        result = get_job(input_dict)
        job = asyncio.run(result)
        job_data = job.model_dump()
        if "user" in job_data:
            del job_data["user"]
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
    else:
        return job_data


def get_job_logs_tool(
    project_path: str,
    job_id: int,
) -> dict:
    """Get logs for a specific job.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        job_id: The ID of the job.

    Returns:
        A dictionary containing the job logs.
    """
    try:
        input_dict = {
            "project_path": project_path,
            "job_id": job_id,
        }
        result = get_job_logs(input_dict)
        logs = asyncio.run(result)
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
    else:
        return {"logs": logs.content}


def get_job_failure_info_tool(
    project_path: str,
    job_id: int,
) -> dict:
    """Get detailed information about why a job failed.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        job_id: The ID of the job.

    Returns:
        A dictionary containing failure information, including reason and logs excerpt.
    """
    # Get job details
    try:
        input_dict = {
            "project_path": project_path,
            "job_id": job_id,
        }

        job_result = get_job(input_dict)
        job = asyncio.run(job_result)

        # Get job logs
        logs_result = get_job_logs(input_dict)
        logs = asyncio.run(logs_result)

        # Process logs to extract relevant error information
        log_lines = logs.content.split("\n")
        error_lines = []

        # Check if the job failed
        if job.status != "failed":
            return {
                "status": job.status,
                "message": "Job did not fail",
                "failure_reason": None,
                "error_excerpt": None,
                "stage": job.stage,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "finished_at": job.finished_at,
            }

        # Extract error information from logs
        # Look for lines with ERROR, FATAL, Exception, etc.
        for i, line in enumerate(log_lines):
            lower_line = line.lower()
            if any(
                err in lower_line
                for err in ["error", "exception", "fatal", "failed", "failure"]
            ):
                # Get context (5 lines before and after)
                start = max(0, i - 5)
                end = min(len(log_lines), i + 6)  # +6 to include the current line
                error_lines.extend(log_lines[start:end])
                error_lines.append("---")  # Separator between different error contexts

        # If no specific errors were found, get the last 20 lines
        if not error_lines and log_lines:
            error_lines = log_lines[-20:]

        return {
            "status": job.status,
            "failure_reason": job.failure_reason,
            "stage": job.stage,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "duration": job.duration,
            "error_excerpt": "\n".join(error_lines) if error_lines else None,
        }
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
