import os

import gitlab
from gitlab.v4.objects import Project

from .async_utils import to_async
from .exceptions import GitLabAuthError


class GitLabClient:
    """Async-compatible GitLab client wrapper.

    This class provides both synchronous and asynchronous methods for interacting
    with the GitLab API, using the python-gitlab library underneath.
    """

    def __init__(self) -> None:
        self._client: gitlab.Gitlab | None = None

    def _get_sync_client(self) -> gitlab.Gitlab:
        """Get or create a synchronous GitLab client instance.

        Returns:
            gitlab.Gitlab: An authenticated GitLab client instance.

        Raises:
            GitLabAuthError: If authentication fails due to missing or invalid credentials.
        """
        if self._client is not None:
            return self._client

        token = os.getenv(key="GITLAB_PERSONAL_ACCESS_TOKEN")
        url = os.getenv(key="GITLAB_API_URL", default="https://gitlab.com")

        if not token:
            raise GitLabAuthError(
                message="GITLAB_PERSONAL_ACCESS_TOKEN environment variable is not set."
            )

        try:
            gl = gitlab.Gitlab(url=url, private_token=token)
            gl.auth()
        except Exception as exc:
            raise GitLabAuthError(
                message=f"Failed to authenticate with GitLab: {exc}"
            ) from exc
        else:
            self._client = gl
            return gl

    # Synchronous methods
    def get_project(self, project_path: str) -> Project:
        """Get a project by path.

        Args:
            project_path: The project path (e.g., 'namespace/project').

        Returns:
            Project: The GitLab project object.
        """
        client = self._get_sync_client()
        return client.projects.get(id=project_path)

    # Async methods
    @to_async
    def get_project_async(self, project_path: str) -> Project:
        """Async version of get_project.

        Args:
            project_path: The project path (e.g., 'namespace/project').

        Returns:
            Project: The GitLab project object.
        """
        return self.get_project(project_path=project_path)


# Singleton instance for global use
gitlab_client = GitLabClient()
