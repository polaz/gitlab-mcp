"""Schema definitions for GitLab CI/CD jobs."""

from pydantic import BaseModel


class JobLogsInput(BaseModel):
    """Input model for retrieving GitLab CI/CD job logs.

    Retrieves the execution logs from a specific CI/CD job run.

    Attributes:
        project_path: Full namespace path of the project (REQUIRED).
                     Must include complete group/subgroup path.
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        job_id: The numeric ID of the specific job (REQUIRED).
               This is the unique job ID, not the job name.
               Can be found in the GitLab CI/CD pipelines UI or API.
               Examples: 12345, 67890

    Example Usage:
        - Get logs for job: project_path='my/project', job_id=12345

    Note: You need appropriate permissions to view job logs.
    Private projects require at least Developer access.
    """

    project_path: str
    job_id: int


class JobLogsResponse(BaseModel):
    """Response model for GitLab CI/CD job logs.

    Contains the raw execution logs from a CI/CD job.

    Attributes:
        content: The raw text content of the job execution logs.
                Includes timestamps, command outputs, error messages, etc.
                May be very long for complex jobs.
                Examples: Build logs, test outputs, deployment logs.

    Note: Logs are returned as plain text and may contain ANSI color codes.
    Large log files may be truncated - check GitLab's log retention settings.
    """

    content: str
