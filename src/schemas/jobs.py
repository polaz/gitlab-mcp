"""Schema definitions for GitLab CI/CD jobs."""

from enum import Enum
from typing import Any

from .base import BaseModel, BaseResponseList


class JobStatus(str, Enum):
    """GitLab job status values.

    Attributes:
        CREATED: Job is created but not yet started.
        PENDING: Job is pending.
        RUNNING: Job is running.
        SUCCESS: Job completed successfully.
        FAILED: Job failed.
        CANCELED: Job was canceled.
        SKIPPED: Job was skipped.
        MANUAL: Job is waiting for manual action.
    """

    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"


class ListPipelineJobsInput(BaseModel):
    """Input model for listing jobs in a GitLab pipeline.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    pipeline_id: int
    page: int = 1
    per_page: int = 20


class GetJobInput(BaseModel):
    """Input model for getting a specific job from a GitLab project.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        job_id: The ID of the job.
    """

    project_path: str
    job_id: int


class GetJobLogsInput(BaseModel):
    """Input model for retrieving logs from a GitLab job.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        job_id: The ID of the job.
    """

    project_path: str
    job_id: int


class GitLabJob(BaseModel):
    """Response model for a GitLab pipeline job.

    Attributes:
        id: The unique identifier of the job.
        name: The name of the job.
        status: The status of the job.
        stage: The pipeline stage the job belongs to.
        created_at: The creation timestamp of the job.
        started_at: The timestamp when the job started, null if not started.
        finished_at: The timestamp when the job finished, null if not finished.
        duration: The duration of the job in seconds, null if not finished.
        web_url: The web URL of the job.
        pipeline_id: The ID of the pipeline the job belongs to.
        user: Information about the user who triggered the job, structure varies.
        ref: The branch or tag name the job is running for.
    """

    id: int
    name: str
    status: JobStatus
    stage: str
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    duration: float | None = None
    web_url: str
    pipeline_id: int
    user: Any | None = None
    ref: str


class GitLabJobListResponse(BaseResponseList[GitLabJob]):
    """Response model for listing GitLab pipeline jobs."""

    pass


class GitLabJobLog(BaseModel):
    """Response model for GitLab job logs.

    Attributes:
        id: The ID of the job.
        content: The content of the job logs.
    """

    id: int
    content: str
