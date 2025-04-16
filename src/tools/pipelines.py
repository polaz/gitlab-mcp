from typing import Any

from ..api.exceptions import GitLabAPIError
from ..schemas.pipelines import (
    CreatePipelineInput,
    GetPipelineInput,
    ListPipelinesInput,
    PipelineAction,
    PipelineActionInput,
    PipelineStatus,
)
from ..services.pipelines import (
    create_pipeline,
    get_pipeline,
    list_pipelines,
    pipeline_action,
)


def _raise_invalid_status_error(status: str) -> None:
    """Helper function to raise invalid status error.

    Args:
        status: The invalid status value.

    Raises:
        ValueError: Always raised with appropriate message.
    """
    error_message = "Invalid pipeline status"
    raise ValueError(error_message) from None


def _raise_invalid_action_error(action: str) -> None:
    """Helper function to raise invalid action error.

    Args:
        action: The invalid action value.

    Raises:
        ValueError: Always raised with appropriate message.
    """
    error_message = "Invalid pipeline action"
    raise ValueError(error_message) from None


def list_pipelines_tool(
    project_path: str,
    status: str | None = None,
    ref: str | None = None,
    sha: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List pipelines in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        status: Optional filter for pipeline status.
        ref: Optional filter for the branch or tag name.
        sha: Optional filter for the commit SHA.
        page: The page number for pagination.
        per_page: The number of items per page.

    Returns:
        dict[str, Any]: The list of pipelines.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert status string to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = PipelineStatus(status)
            except ValueError:
                _raise_invalid_status_error(status)

        # Create input model
        input_model = ListPipelinesInput(
            project_path=project_path,
            status=status_enum,
            ref=ref,
            sha=sha,
            page=page,
            per_page=per_page,
        )

        # Call service function
        response = list_pipelines(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def get_pipeline_tool(project_path: str, pipeline_id: int) -> dict[str, Any]:
    """Get a specific pipeline from a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.

    Returns:
        dict[str, Any]: The pipeline details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = GetPipelineInput(
            project_path=project_path,
            pipeline_id=pipeline_id,
        )

        # Call service function
        response = get_pipeline(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def create_pipeline_tool(
    project_path: str, ref: str, variables: dict[str, str] | None = None
) -> dict[str, Any]:
    """Create a new pipeline in a GitLab project.

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        ref: The branch or tag name to run the pipeline for.
        variables: Optional variables to pass to the pipeline.

    Returns:
        dict[str, Any]: The created pipeline details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Create input model
        input_model = CreatePipelineInput(
            project_path=project_path,
            ref=ref,
            variables=variables,
        )

        # Call service function
        response = create_pipeline(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc


def pipeline_action_tool(
    project_path: str, pipeline_id: int, action: str
) -> dict[str, Any]:
    """Perform an action on a GitLab pipeline (cancel or retry).

    Args:
        project_path: The path of the project (e.g., 'namespace/project').
        pipeline_id: The ID of the pipeline.
        action: The action to perform (cancel or retry).

    Returns:
        dict[str, Any]: The updated pipeline details.

    Raises:
        ValueError: If the GitLab API returns an error.
    """
    try:
        # Convert action string to enum
        try:
            action_enum = PipelineAction(action)
        except ValueError:
            # Will raise a ValueError and exit the function
            _raise_invalid_action_error(action)
            # This return is unreachable but satisfies type checkers
            # by ensuring action_enum is bound in all code paths
            return {}

        # Create input model
        input_model = PipelineActionInput(
            project_path=project_path,
            pipeline_id=pipeline_id,
            action=action_enum,
        )

        # Call service function
        response = pipeline_action(input_model)

        # Convert to dict
        return response.model_dump()
    except GitLabAPIError as exc:
        raise ValueError(str(exc)) from exc
