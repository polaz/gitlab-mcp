from ..api.async_utils import to_async
from ..api.client import gitlab_client
from ..api.exceptions import GitLabAPIError
from ..schemas.repositories import (
    CreateRepositoryInput,
    ForkRepositoryInput,
    GitLabFork,
    GitLabRepository,
    GitLabSearchResponse,
    SearchProjectsInput,
)


def fork_project(input_model: ForkRepositoryInput) -> GitLabFork:
    """Fork a GitLab repository.

    Args:
        input_model: The input model containing project path and target namespace.

    Returns:
        GitLabFork: The forked repository details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()
        project = client.projects.get(input_model.project_path)

        # Fork the project
        fork = project.forks.create({"namespace": input_model.target_namespace})

        # Map to our schema
        return GitLabFork(
            id=fork.id,
            name=fork.name,
            path=fork.path,
            web_url=fork.web_url,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def create_repository(input_model: CreateRepositoryInput) -> GitLabRepository:
    """Create a new GitLab repository.

    Args:
        input_model: The input model containing repository details.

    Returns:
        GitLabRepository: The created repository details.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()

        # Create the project
        project = client.projects.create(
            {
                "name": input_model.name,
                "description": input_model.description,
                "visibility": input_model.visibility.value,
                "initialize_with_readme": input_model.initialize_with_readme,
            }
        )

        # Map to our schema
        return GitLabRepository(
            id=project.id,
            name=project.name,
            path=project.path,
            description=project.description,
            web_url=project.web_url,
            default_branch=project.default_branch,
        )
    except Exception as exc:
        raise GitLabAPIError(str(exc)) from exc


def search_projects(input_model: SearchProjectsInput) -> GitLabSearchResponse:
    """Search for GitLab projects by name or keyword.

    Args:
        input_model: The input model containing search parameters.

    Returns:
        GitLabSearchResponse: The search results.

    Raises:
        GitLabAPIError: If the GitLab API returns an error.
    """
    try:
        client = gitlab_client._get_sync_client()

        # Search for projects
        projects = client.projects.list(
            search=input_model.search,
            page=input_model.page,
            per_page=input_model.per_page,
        )

        # Map to our schema
        items = [
            {
                "id": project.id,
                "name": project.name,
                "path": project.path,
                "description": project.description,
                "web_url": project.web_url,
                "default_branch": project.default_branch,
            }
            for project in projects
        ]

        return GitLabSearchResponse(
            count=len(items),
            items=items,
        )
    except Exception as exc:
        raise GitLabAPIError(message=str(exc)) from exc


# Async versions of the functions
fork_project_async = to_async(fork_project)
create_repository_async = to_async(create_repository)
search_projects_async = to_async(search_projects)
