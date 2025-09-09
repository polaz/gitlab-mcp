"""Service functions for interacting with GitLab labels using the REST API."""

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.labels import (
    CreateLabelInput,
    DeleteLabelInput,
    GetLabelInput,
    GitLabLabel,
    GitLabLabelListResponse,
    ListLabelsInput,
    SubscribeToLabelInput,
    UnsubscribeFromLabelInput,
    UpdateLabelInput,
)


async def list_labels(input_model: ListLabelsInput) -> GitLabLabelListResponse:
    """List GitLab labels using the REST API.

    This function can list labels at both project and group levels based on the input parameters.
    If project_path is provided, it lists project-specific labels.
    If group_id is provided, it lists group-level labels.

    Args:
        input_model: The input model containing filter and pagination parameters.

    Returns:
        GitLabLabelListResponse: The list of labels.

    Raises:
        GitLabAPIError: If retrieving the labels fails or if neither project_path nor group_id is provided.
    """
    # Determine the API endpoint based on input
    if input_model.project_path:
        # Project-level labels
        project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
        endpoint = f"/projects/{project_path}/labels"
    elif input_model.group_id:
        # Group-level labels
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        endpoint = f"/groups/{group_id}/labels"
    else:
        raise GitLabAPIError(
            GitLabErrorType.BAD_REQUEST,
            {"operation": "list_labels", "message": "Either project_path or group_id must be provided"},
            code=400,
        )

    # Prepare query parameters
    params = {
        "page": input_model.page,
        "per_page": input_model.per_page,
    }

    # Add filtering parameters
    if input_model.search:
        params["search"] = input_model.search
    if input_model.include_ancestor_groups:
        params["include_ancestor_groups"] = "true"
    if input_model.with_counts:
        params["with_counts"] = "true"

    try:
        # Make the API call
        response_data = await gitlab_rest_client.get_async(endpoint, params=params)

        # Parse the response into our schema
        items = [GitLabLabel.model_validate(label) for label in response_data]

        return GitLabLabelListResponse(items=items)
    except GitLabAPIError:
        raise  # Re-raise GitLabAPIError as is
    except Exception as exc:
        context = {"operation": "list_labels"}
        if input_model.project_path:
            context["project_path"] = input_model.project_path
        if input_model.group_id:
            context["group_id"] = input_model.group_id
        raise GitLabAPIError(GitLabErrorType.SERVER_ERROR, context, code=500) from exc


async def get_label(input_model: GetLabelInput) -> GitLabLabel:
    """Get a specific GitLab label using the REST API.

    Args:
        input_model: The input model containing the project path or group ID and label identifier.

    Returns:
        GitLabLabel: The requested label.

    Raises:
        GitLabAPIError: If the label does not exist or if retrieving the label fails.
    """
    # Determine the API endpoint based on input
    if input_model.project_path:
        # Project-level label
        project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
        label_id = gitlab_rest_client._encode_path_parameter(input_model.label_id)
        endpoint = f"/projects/{project_path}/labels/{label_id}"
    elif input_model.group_id:
        # Group-level label
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        label_id = gitlab_rest_client._encode_path_parameter(input_model.label_id)
        endpoint = f"/groups/{group_id}/labels/{label_id}"
    else:
        raise GitLabAPIError(
            GitLabErrorType.BAD_REQUEST,
            {"operation": "get_label", "message": "Either project_path or group_id must be provided"},
            code=400,
        )

    try:
        # Make the API call
        response = await gitlab_rest_client.get_async(endpoint)

        # Parse the response into our schema
        return GitLabLabel.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            context = {"label_id": input_model.label_id}
            if input_model.project_path:
                context["project_path"] = input_model.project_path
            if input_model.group_id:
                context["group_id"] = input_model.group_id
            raise GitLabAPIError(GitLabErrorType.NOT_FOUND, context, code=404) from exc
        raise  # Re-raise original GitLabAPIError for other API errors
    except Exception as exc:
        context = {"operation": "get_label", "label_id": input_model.label_id}
        if input_model.project_path:
            context["project_path"] = input_model.project_path
        if input_model.group_id:
            context["group_id"] = input_model.group_id
        raise GitLabAPIError(GitLabErrorType.SERVER_ERROR, context, code=500) from exc


async def create_label(input_model: CreateLabelInput) -> GitLabLabel:
    """Create a new GitLab label using the REST API.

    Args:
        input_model: The input model containing label creation parameters.

    Returns:
        GitLabLabel: The created label.

    Raises:
        GitLabAPIError: If creating the label fails.
    """
    # Determine the API endpoint based on input
    if input_model.project_path:
        # Project-level label
        project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
        endpoint = f"/projects/{project_path}/labels"
    elif input_model.group_id:
        # Group-level label
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        endpoint = f"/groups/{group_id}/labels"
    else:
        raise GitLabAPIError(
            GitLabErrorType.BAD_REQUEST,
            {"operation": "create_label", "message": "Either project_path or group_id must be provided"},
            code=400,
        )

    # Prepare the request data
    data = {
        "name": input_model.name,
        "color": input_model.color,
    }

    if input_model.description:
        data["description"] = input_model.description
    if input_model.priority is not None:
        data["priority"] = input_model.priority

    try:
        # Make the API call
        response = await gitlab_rest_client.post_async(endpoint, data=data)

        # Parse the response into our schema
        return GitLabLabel.model_validate(response)
    except GitLabAPIError:
        raise  # Re-raise GitLabAPIError as is
    except Exception as exc:
        context = {"operation": "create_label", "name": input_model.name}
        if input_model.project_path:
            context["project_path"] = input_model.project_path
        if input_model.group_id:
            context["group_id"] = input_model.group_id
        raise GitLabAPIError(GitLabErrorType.SERVER_ERROR, context, code=500) from exc


def _get_label_endpoint(project_path: str | None, group_id: str | None, label_id: str) -> str:
    """Get the API endpoint for label operations."""
    if project_path:
        project_encoded = gitlab_rest_client._encode_path_parameter(project_path)
        label_encoded = gitlab_rest_client._encode_path_parameter(label_id)
        return f"/projects/{project_encoded}/labels/{label_encoded}"
    elif group_id:
        group_encoded = gitlab_rest_client._encode_path_parameter(group_id)
        label_encoded = gitlab_rest_client._encode_path_parameter(label_id)
        return f"/groups/{group_encoded}/labels/{label_encoded}"
    else:
        raise GitLabAPIError(
            GitLabErrorType.BAD_REQUEST,
            {"message": "Either project_path or group_id must be provided"},
            code=400,
        )


def _build_update_data(input_model: UpdateLabelInput) -> dict:
    """Build the update data dictionary from input model."""
    data = {}
    if input_model.new_name:
        data["new_name"] = input_model.new_name
    if input_model.color:
        data["color"] = input_model.color
    if input_model.description is not None:  # Allow empty string
        data["description"] = input_model.description
    if input_model.priority is not None:
        data["priority"] = input_model.priority

    if not data:
        raise GitLabAPIError(
            GitLabErrorType.BAD_REQUEST,
            {"message": "At least one field to update must be provided"},
            code=400,
        )
    return data


async def update_label(input_model: UpdateLabelInput) -> GitLabLabel:
    """Update an existing GitLab label using the REST API.

    Args:
        input_model: The input model containing label update parameters.

    Returns:
        GitLabLabel: The updated label.

    Raises:
        GitLabAPIError: If updating the label fails.
    """
    endpoint = _get_label_endpoint(input_model.project_path, input_model.group_id, input_model.label_id)
    data = _build_update_data(input_model)

    try:
        response = await gitlab_rest_client.put_async(endpoint, data=data)
        return GitLabLabel.model_validate(response)
    except GitLabAPIError:
        raise  # Re-raise GitLabAPIError as is
    except Exception as exc:
        context = {"operation": "update_label", "label_id": input_model.label_id}
        if input_model.project_path:
            context["project_path"] = input_model.project_path
        if input_model.group_id:
            context["group_id"] = input_model.group_id
        raise GitLabAPIError(GitLabErrorType.SERVER_ERROR, context, code=500) from exc


async def delete_label(input_model: DeleteLabelInput) -> None:
    """Delete a GitLab label using the REST API.

    Args:
        input_model: The input model containing the label deletion parameters.

    Raises:
        GitLabAPIError: If deleting the label fails.
    """
    # Determine the API endpoint based on input
    if input_model.project_path:
        # Project-level label
        project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
        label_id = gitlab_rest_client._encode_path_parameter(input_model.label_id)
        endpoint = f"/projects/{project_path}/labels/{label_id}"
    elif input_model.group_id:
        # Group-level label
        group_id = gitlab_rest_client._encode_path_parameter(input_model.group_id)
        label_id = gitlab_rest_client._encode_path_parameter(input_model.label_id)
        endpoint = f"/groups/{group_id}/labels/{label_id}"
    else:
        raise GitLabAPIError(
            GitLabErrorType.BAD_REQUEST,
            {"operation": "delete_label", "message": "Either project_path or group_id must be provided"},
            code=400,
        )

    try:
        # Make the API call
        await gitlab_rest_client.delete_async(endpoint)
    except GitLabAPIError:
        raise  # Re-raise GitLabAPIError as is
    except Exception as exc:
        context = {"operation": "delete_label", "label_id": input_model.label_id}
        if input_model.project_path:
            context["project_path"] = input_model.project_path
        if input_model.group_id:
            context["group_id"] = input_model.group_id
        raise GitLabAPIError(GitLabErrorType.SERVER_ERROR, context, code=500) from exc


async def subscribe_to_label(input_model: SubscribeToLabelInput) -> GitLabLabel:
    """Subscribe to a GitLab project label using the REST API.

    Args:
        input_model: The input model containing the project path and label identifier.

    Returns:
        GitLabLabel: The updated label with subscription status.

    Raises:
        GitLabAPIError: If subscribing to the label fails.
    """
    # Encode parameters
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
    label_id = gitlab_rest_client._encode_path_parameter(input_model.label_id)
    endpoint = f"/projects/{project_path}/labels/{label_id}/subscribe"

    try:
        # Make the API call
        response = await gitlab_rest_client.post_async(endpoint)

        # Parse the response into our schema
        return GitLabLabel.model_validate(response)
    except GitLabAPIError:
        raise  # Re-raise GitLabAPIError as is
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "operation": "subscribe_to_label",
                "project_path": input_model.project_path,
                "label_id": input_model.label_id,
            },
            code=500,
        ) from exc


async def unsubscribe_from_label(input_model: UnsubscribeFromLabelInput) -> GitLabLabel:
    """Unsubscribe from a GitLab project label using the REST API.

    Args:
        input_model: The input model containing the project path and label identifier.

    Returns:
        GitLabLabel: The updated label with subscription status.

    Raises:
        GitLabAPIError: If unsubscribing from the label fails.
    """
    # Encode parameters
    project_path = gitlab_rest_client._encode_path_parameter(input_model.project_path)
    label_id = gitlab_rest_client._encode_path_parameter(input_model.label_id)
    endpoint = f"/projects/{project_path}/labels/{label_id}/unsubscribe"

    try:
        # Make the API call
        response = await gitlab_rest_client.post_async(endpoint)

        # Parse the response into our schema
        return GitLabLabel.model_validate(response)
    except GitLabAPIError:
        raise  # Re-raise GitLabAPIError as is
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "operation": "unsubscribe_from_label",
                "project_path": input_model.project_path,
                "label_id": input_model.label_id,
            },
            code=500,
        ) from exc
