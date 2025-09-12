"""Work Item Types discovery and management service.

This module provides dynamic discovery of work item types from the GitLab instance,
eliminating the need for hardcoded type mappings that vary between instances.
"""

import logging

from src.api.graphql_client import GitLabGraphQLClientSingleton

logger = logging.getLogger(__name__)


class WorkItemTypeManager:
    """Manager for work item types with dynamic discovery capabilities."""

    def __init__(self):
        self._type_mappings: dict[str, str] = {}
        self._reverse_mappings: dict[str, str] = {}
        self._discovered = False

    async def discover_types(self, project_path: str | None = None) -> dict[str, str]:
        """Discover work item types from the GitLab instance.

        Args:
            project_path: Optional project path to query types from.
                         If not provided, will attempt to use a default project.

        Returns:
            Dictionary mapping type names to their global IDs.
        """
        try:
            client = GitLabGraphQLClientSingleton.get_instance()
            project_path = await self._resolve_project_path(project_path)

            if not project_path:
                logger.warning("No accessible project found for work item type discovery")
                return self._get_fallback_types()

            work_item_types = await self._query_work_item_types(client, project_path)
            if not work_item_types:
                logger.warning(f"Could not discover work item types from project {project_path}")
                return self._get_fallback_types()

            return self._build_type_mappings(work_item_types, project_path)

        except Exception as e:
            logger.warning(f"Work item type discovery failed: {e}, using fallback values")
            return self._get_fallback_types()

    async def _resolve_project_path(self, project_path: str | None) -> str | None:
        """Resolve project path for type discovery."""
        if not project_path:
            return await self._find_accessible_project()
        return project_path

    async def _query_work_item_types(self, client, project_path: str) -> list[dict] | None:
        """Query work item types from GitLab GraphQL API."""
        query = """
        query getProjectWorkItemTypes($projectPath: ID!) {
          project(fullPath: $projectPath) {
            workItemTypes {
              nodes {
                id
                name
              }
            }
          }
        }
        """

        variables = {"projectPath": project_path}
        result = await client.query(query, variables)

        if "project" in result and result["project"] and "workItemTypes" in result["project"]:
            return result["project"]["workItemTypes"]["nodes"]
        return None

    def _build_type_mappings(self, work_item_types: list[dict], project_path: str) -> dict[str, str]:
        """Build type mappings from discovered work item types."""
        type_mappings = {}
        reverse_mappings = {}

        for wit in work_item_types:
            name = wit["name"]
            id_value = wit["id"]

            # Store both exact name and uppercase version
            type_mappings[name.upper()] = id_value
            type_mappings[name] = id_value
            reverse_mappings[id_value] = name

            # Add common aliases
            if name.upper() == "TEST CASE":
                type_mappings["TEST_CASE"] = id_value
            elif name.upper() == "KEY RESULT":
                type_mappings["KEY_RESULT"] = id_value

        self._type_mappings = type_mappings
        self._reverse_mappings = reverse_mappings
        self._discovered = True

        logger.info(f"Discovered {len(work_item_types)} work item types from project {project_path}")
        logger.debug(f"Available types: {list({wit['name'] for wit in work_item_types})}")

        return type_mappings

    async def _find_accessible_project(self) -> str | None:
        """Find any accessible project for type discovery."""
        try:
            client = GitLabGraphQLClientSingleton.get_instance()

            # Try to get user's projects
            query = """
            query getCurrentUserProjects {
              currentUser {
                projectMemberships(first: 1) {
                  nodes {
                    project {
                      fullPath
                    }
                  }
                }
              }
            }
            """

            result = await client.query(query)

            if ("currentUser" in result and result["currentUser"] and
                "projectMemberships" in result["currentUser"]):
                memberships = result["currentUser"]["projectMemberships"]["nodes"]
                if memberships:
                    project_path = memberships[0]["project"]["fullPath"]
                    logger.debug(f"Found accessible project for type discovery: {project_path}")
                    return project_path

            logger.debug("No accessible projects found via user memberships")
            return None

        except Exception as e:
            logger.debug(f"Failed to find accessible project: {e}")
            return None

    def _get_fallback_types(self) -> dict[str, str]:
        """Get fallback work item type mappings."""
        fallback = {
            "EPIC": "gid://gitlab/WorkItems::Type/1",
            "ISSUE": "gid://gitlab/WorkItems::Type/2",
            "INCIDENT": "gid://gitlab/WorkItems::Type/3",
            "TASK": "gid://gitlab/WorkItems::Type/4",
            "TEST_CASE": "gid://gitlab/WorkItems::Type/5",
            "REQUIREMENT": "gid://gitlab/WorkItems::Type/6",
            "OBJECTIVE": "gid://gitlab/WorkItems::Type/7",
            "KEY_RESULT": "gid://gitlab/WorkItems::Type/8",
            "TICKET": "gid://gitlab/WorkItems::Type/9",
        }

        self._type_mappings = fallback
        self._reverse_mappings = {v: k for k, v in fallback.items()}

        logger.info("Using fallback work item type mappings")
        return fallback

    def get_type_id(self, type_name: str) -> str | None:
        """Get the global ID for a work item type name.

        Args:
            type_name: Work item type name (case-insensitive).

        Returns:
            Global ID string or None if type not found.
        """
        if not self._discovered:
            logger.warning("Work item types not discovered yet, using fallback lookup")
            return self._get_fallback_types().get(type_name.upper())

        return self._type_mappings.get(type_name.upper()) or self._type_mappings.get(type_name)

    def get_type_name(self, type_id: str) -> str | None:
        """Get the type name for a global ID.

        Args:
            type_id: Global work item type ID.

        Returns:
            Type name string or None if ID not found.
        """
        return self._reverse_mappings.get(type_id)

    def get_all_types(self) -> dict[str, str]:
        """Get all discovered work item types.

        Returns:
            Dictionary mapping type names to global IDs.
        """
        if not self._discovered:
            logger.warning("Work item types not discovered yet, returning fallback types")
            return self._get_fallback_types()

        return self._type_mappings.copy()

    def is_discovered(self) -> bool:
        """Check if work item types have been discovered from GitLab."""
        return self._discovered


class WorkItemTypeManagerSingleton:
    """Singleton for WorkItemTypeManager."""
    _instance: WorkItemTypeManager | None = None

    @classmethod
    def get_instance(cls) -> WorkItemTypeManager:
        """Get the global work item type manager instance."""
        if cls._instance is None:
            cls._instance = WorkItemTypeManager()
        return cls._instance


def get_work_item_type_manager() -> WorkItemTypeManager:
    """Get the global work item type manager instance."""
    return WorkItemTypeManagerSingleton.get_instance()


async def initialize_work_item_types(project_path: str | None = None) -> dict[str, str]:
    """Initialize work item types discovery.

    This should be called during server startup to populate type mappings.

    Args:
        project_path: Optional project path for discovery.

    Returns:
        Dictionary of discovered type mappings.
    """
    manager = get_work_item_type_manager()
    return await manager.discover_types(project_path)


def get_work_item_type_id(type_name: str) -> str | None:
    """Convenience function to get work item type ID by name."""
    manager = get_work_item_type_manager()
    return manager.get_type_id(type_name)


def get_work_item_type_name(type_id: str) -> str | None:
    """Convenience function to get work item type name by ID."""
    manager = get_work_item_type_manager()
    return manager.get_type_name(type_id)
