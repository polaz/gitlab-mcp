from enum import Enum

from src.schemas.base import BaseModel, BaseResponseList


class PipelineStatus(str, Enum):
    """GitLab pipeline status values.

    Attributes:
        CREATED: Pipeline is created but not yet started.
        WAITING_FOR_RESOURCE: Pipeline is waiting for resources.
        PREPARING: Pipeline is preparing to run.
        PENDING: Pipeline is pending.
        RUNNING: Pipeline is running.
        SUCCESS: Pipeline completed successfully.
        FAILED: Pipeline failed.
        CANCELED: Pipeline was canceled.
        SKIPPED: Pipeline was skipped.
        MANUAL: Pipeline is waiting for manual action.
        SCHEDULED: Pipeline is scheduled to run.
    """

    CREATED = "created"
    WAITING_FOR_RESOURCE = "waiting_for_resource"
    PREPARING = "preparing"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class ListPipelinesInput(BaseModel):
    """Input model for listing pipelines in a GitLab project.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        status: Optional filter for pipeline status.
        ref: Optional filter for the branch or tag name.
        sha: Optional filter for the commit SHA.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    status: PipelineStatus | None = None
    ref: str | None = None
    sha: str | None = None
    page: int = 1
    per_page: int = 20


class GitLabPipeline(BaseModel):
    """Response model for a GitLab pipeline.

    Attributes:
        id: The unique identifier of the pipeline.
        iid: The internal ID of the pipeline within the project.
        project_id: The ID of the project the pipeline belongs to.
        sha: The commit SHA the pipeline is running for.
        ref: The branch or tag name the pipeline is running for.
        status: The status of the pipeline.
        created_at: The creation timestamp of the pipeline.
        updated_at: The last update timestamp of the pipeline.
        web_url: The web URL of the pipeline.
    """

    id: int
    iid: int
    project_id: int
    sha: str
    ref: str
    status: PipelineStatus
    created_at: str
    updated_at: str
    web_url: str


class GitLabPipelineListResponse(BaseResponseList[GitLabPipeline]):
    """Response model for listing GitLab pipelines."""

    pass


class GetPipelineInput(BaseModel):
    """Input model for getting a specific pipeline from a GitLab project.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
    """

    project_path: str
    pipeline_id: int


class CreatePipelineInput(BaseModel):
    """Input model for creating a new pipeline in a GitLab project.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        ref: The branch or tag name to run the pipeline for.
        variables: Optional variables to pass to the pipeline.
    """

    project_path: str
    ref: str
    variables: dict[str, str] | None = None


class PipelineAction(str, Enum):
    """Actions that can be performed on a GitLab pipeline.

    Attributes:
        CANCEL: Cancel a running pipeline.
        RETRY: Retry a failed pipeline.
    """

    CANCEL = "cancel"
    RETRY = "retry"


class PipelineActionInput(BaseModel):
    """Input model for performing an action on a GitLab pipeline.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        action: The action to perform (cancel or retry).
    """

    project_path: str
    pipeline_id: int
    action: PipelineAction
