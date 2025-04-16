"""Tools for interacting with GitLab CI/CD jobs."""



from src.schemas.jobs import GetJobInput, GetJobLogsInput, ListPipelineJobsInput
from src.services.jobs import get_job, get_job_logs, list_pipeline_jobs


def list_pipeline_jobs_tool(
    project_path: str, pipeline_id: int, page: int = 1, per_page: int = 20
) -> dict:
    """List jobs in a GitLab pipeline.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict: The list of jobs in the pipeline.
    """
    input_model = ListPipelineJobsInput(
        project_path=project_path,
        pipeline_id=pipeline_id,
        page=page,
        per_page=per_page,
    )
    return list_pipeline_jobs(input_model).model_dump()


def get_job_tool(project_path: str, job_id: int) -> dict:
    """Get a specific job from a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        job_id: The ID of the job.

    Returns:
        dict: The job details.
    """
    input_model = GetJobInput(
        project_path=project_path,
        job_id=job_id,
    )
    return get_job(input_model).model_dump()


def get_job_logs_tool(project_path: str, job_id: int) -> dict:
    """Get logs from a GitLab job.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        job_id: The ID of the job.

    Returns:
        dict: The job logs.
    """
    input_model = GetJobLogsInput(
        project_path=project_path,
        job_id=job_id,
    )
    return get_job_logs(input_model).model_dump()


