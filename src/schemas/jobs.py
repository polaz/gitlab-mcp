"""Schema definitions for GitLab CI/CD jobs."""

from enum import Enum
from typing import Any

from pydantic import Field

from src.schemas.base import BaseModel, BaseResponseList


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
        WAITING_FOR_RESOURCE: Job is waiting for resources.
    """

    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"
    WAITING_FOR_RESOURCE = "waiting_for_resource"


class JobScope(str, Enum):
    """GitLab job scope values for filtering.

    Attributes:
        CREATED: Filter by created jobs.
        PENDING: Filter by pending jobs.
        RUNNING: Filter by running jobs.
        FAILED: Filter by failed jobs.
        SUCCESS: Filter by successful jobs.
        CANCELED: Filter by canceled jobs.
        SKIPPED: Filter by skipped jobs.
        WAITING_FOR_RESOURCE: Filter by jobs waiting for resources.
        MANUAL: Filter by manual jobs.
    """

    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    WAITING_FOR_RESOURCE = "waiting_for_resource"
    MANUAL = "manual"


class FailureReason(str, Enum):
    """GitLab job failure reason.

    Attributes:
        SCRIPT_FAILURE: Job failed due to a script error.
        RUNNER_SYSTEM_FAILURE: Job failed due to a runner system failure.
        STUCK_OR_TIMEOUT_FAILURE: Job failed because it was stuck or timed out.
        UNKNOWN_FAILURE: Job failed due to an unknown reason.
    """

    SCRIPT_FAILURE = "script_failure"
    RUNNER_SYSTEM_FAILURE = "runner_system_failure"
    STUCK_OR_TIMEOUT_FAILURE = "stuck_or_timeout_failure"
    UNKNOWN_FAILURE = "unknown_failure"


class ListProjectJobsInput(BaseModel):
    """Input model for listing jobs in a GitLab project.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        scope: The scope of jobs to show.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    scope: list[JobScope] | None = None
    page: int = 1
    per_page: int = 20


class ListPipelineJobsInput(BaseModel):
    """Input model for listing jobs in a GitLab pipeline.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        include_retried: Whether to include retried jobs.
        scope: The scope of jobs to show.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    pipeline_id: int
    include_retried: bool = False
    scope: list[JobScope] | None = None
    page: int = 1
    per_page: int = 20


class ListPipelineTriggerJobsInput(BaseModel):
    """Input model for listing trigger jobs in a GitLab pipeline.

    Attributes:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        scope: The scope of jobs to show.
        page: The page number for pagination.
        per_page: The number of items per page.
    """

    project_path: str
    pipeline_id: int
    scope: list[JobScope] | None = None
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


class GitLabCommit(BaseModel):
    """Model for commit information in a GitLab job.

    Attributes:
        id: The commit SHA.
        short_id: The short commit SHA.
        author_name: The author name.
        author_email: The author email.
        title: The commit title.
        message: The commit message.
        created_at: The commit creation timestamp.
    """

    id: str
    short_id: str
    author_name: str
    author_email: str
    title: str
    message: str
    created_at: str


class GitLabPipelineInfo(BaseModel):
    """Model for pipeline information in a GitLab job.

    Attributes:
        id: The pipeline ID.
        project_id: The project ID.
        ref: The branch or tag name.
        sha: The commit SHA.
        status: The pipeline status.
        web_url: The pipeline web URL.
        created_at: The pipeline creation timestamp.
        updated_at: The pipeline update timestamp.
    """

    id: int
    project_id: int
    ref: str
    sha: str
    status: str
    web_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class GitLabArtifactFile(BaseModel):
    """Model for artifact file information.

    Attributes:
        filename: The artifact filename.
        size: The artifact size.
    """

    filename: str
    size: int


class GitLabArtifact(BaseModel):
    """Model for artifact information.

    Attributes:
        file_type: The artifact file type.
        size: The artifact size.
        filename: The artifact filename.
        file_format: The artifact file format.
    """

    file_type: str
    size: int
    filename: str
    file_format: str


class GitLabRunner(BaseModel):
    """Model for runner information.

    Attributes:
        id: The runner ID.
        description: The runner description.
        ip_address: The runner IP address.
        active: Whether the runner is active.
        paused: Whether the runner is paused.
        is_shared: Whether the runner is shared.
        runner_type: The runner type.
        name: The runner name.
        online: Whether the runner is online.
        status: The runner status.
    """

    id: int
    description: str
    ip_address: str | None = None
    active: bool
    paused: bool
    is_shared: bool
    runner_type: str
    name: str | None = None
    online: bool
    status: str


class GitLabRunnerManager(BaseModel):
    """Model for runner manager information.

    Attributes:
        id: The runner manager ID.
        system_id: The system ID.
        version: The version.
        revision: The revision.
        platform: The platform.
        architecture: The architecture.
        created_at: The creation timestamp.
        contacted_at: The last contact timestamp.
        ip_address: The IP address.
        status: The status.
    """

    id: int
    system_id: str
    version: str
    revision: str
    platform: str
    architecture: str
    created_at: str
    contacted_at: str
    ip_address: str
    status: str


class GitLabProjectInfo(BaseModel):
    """Model for project information in a job.

    Attributes:
        ci_job_token_scope_enabled: Whether the CI job token scope is enabled.
    """

    ci_job_token_scope_enabled: bool


class GitLabUser(BaseModel):
    """Model for user information in a job.

    Attributes:
        id: The user ID.
        name: The user name.
        username: The username.
        state: The user state.
        avatar_url: The user avatar URL.
        web_url: The user web URL.
        created_at: The user creation timestamp.
        bio: The user bio.
        location: The user location.
        public_email: The user public email.
        skype: The user Skype.
        linkedin: The user LinkedIn.
        twitter: The user Twitter.
        website_url: The user website URL.
        organization: The user organization.
    """

    id: int
    name: str
    username: str
    state: str
    avatar_url: str
    web_url: str
    created_at: str
    bio: str | None = None
    location: str | None = None
    public_email: str = ""
    skype: str = ""
    linkedin: str = ""
    twitter: str = ""
    website_url: str = ""
    organization: str = ""


class GitLabDownstreamPipeline(BaseModel):
    """Model for downstream pipeline information.

    Attributes:
        id: The pipeline ID.
        sha: The commit SHA.
        ref: The branch or tag name.
        status: The pipeline status.
        created_at: The pipeline creation timestamp.
        updated_at: The pipeline update timestamp.
        web_url: The pipeline web URL.
    """

    id: int
    sha: str
    ref: str
    status: str
    created_at: str
    updated_at: str
    web_url: str


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
        queued_duration: The queued duration of the job in seconds.
        web_url: The web URL of the job.
        tag: Whether the job has tags.
        ref: The branch or tag name the job is running for.
        tag_list: List of tags associated with the job.
        pipeline: Information about the pipeline the job belongs to.
        commit: Information about the commit the job is running for.
        runner: Information about the runner the job is running on.
        runner_manager: Information about the runner manager.
        artifacts_file: Information about the artifacts file.
        artifacts: List of artifacts.
        artifacts_expire_at: The expiration timestamp of the artifacts.
        user: Information about the user who triggered the job.
        project: Information about the project.
        allow_failure: Whether the job is allowed to fail.
        archived: Whether the job is archived.
        failure_reason: The reason for the job failure.
        erased_at: The timestamp when the job was erased.
        source: The source of the job.
        coverage: The code coverage of the job.
        downstream_pipeline: Information about the downstream pipeline.
    """

    id: int
    name: str
    status: JobStatus
    stage: str
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    duration: float | None = None
    queued_duration: float | None = None
    web_url: str
    tag: bool
    ref: str
    tag_list: list[str] | None = None
    pipeline: GitLabPipelineInfo
    commit: GitLabCommit | None = None
    runner: GitLabRunner | None = None
    runner_manager: GitLabRunnerManager | None = None
    artifacts_file: GitLabArtifactFile | None = None
    artifacts: list[GitLabArtifact] | None = Field(default_factory=list)
    artifacts_expire_at: str | None = None
    user: GitLabUser | None = None
    project: GitLabProjectInfo | None = None
    allow_failure: bool = False
    archived: bool = False
    failure_reason: FailureReason | None = None
    erased_at: str | None = None
    source: str | None = None
    coverage: float | None = None
    downstream_pipeline: GitLabDownstreamPipeline | None = None


class GitLabAgentInfo(BaseModel):
    """Model for GitLab agent information.

    Attributes:
        id: The agent ID.
        config_project: Information about the configuration project.
    """

    id: int
    config_project: dict[str, Any]


class GitLabGroupInfo(BaseModel):
    """Model for GitLab group information in job token response.

    Attributes:
        id: The group ID.
    """

    id: int


class GitLabProjectInfoExtended(BaseModel):
    """Model for extended project information in job token response.

    Attributes:
        id: The project ID.
        groups: List of group information.
    """

    id: int
    groups: list[GitLabGroupInfo]


class GitLabJobTokenResponse(BaseModel):
    """Response model for a GitLab job token request.

    Attributes:
        allowed_agents: List of allowed agents.
        job: Information about the job.
        pipeline: Information about the pipeline.
        project: Information about the project.
        user: Information about the user.
    """

    allowed_agents: list[GitLabAgentInfo] = Field(default_factory=list)
    job: dict[str, Any]
    pipeline: dict[str, Any]
    project: GitLabProjectInfoExtended
    user: GitLabUser


class GitLabJobListResponse(BaseResponseList):
    """Response model for a list of GitLab jobs."""

    items: list[GitLabJob] = Field(default_factory=list)


class GitLabJobLogsResponse(BaseModel):
    """Response model for GitLab job logs.

    Attributes:
        content: The content of the job logs.
    """

    content: str
