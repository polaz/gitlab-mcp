"""Cleanup utilities for GitLab MCP Server tests.

This module provides utilities for tracking and cleaning up test entities
created during test runs to ensure proper test isolation.
"""

import asyncio
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any

from src.api.rest_client import GitLabRestClient


@dataclass
class TestEntity:
    """Represents a test entity that needs cleanup."""
    entity_type: str  # 'work_item', 'milestone', 'iteration', 'project', 'group'
    entity_id: str
    entity_data: dict[str, Any] = field(default_factory=dict)
    cleanup_order: int = 0  # Lower numbers cleaned up first


class TestCleanup:
    """Manages cleanup of test entities to ensure test isolation."""

    def __init__(self, rest_client: GitLabRestClient, graphql_client):
        self.rest_client = rest_client
        self.graphql_client = graphql_client
        self.entities: list[TestEntity] = []

        # Define cleanup order (dependencies first)
        self.cleanup_priorities = {
            'file': 1,
            'work_item': 2,
            'milestone': 3,
            'iteration': 4,
            'label': 5,
            'branch': 6,
            'merge_request': 7,
            'repository': 10,
            'project': 10,
            'group': 20
        }

    def track_work_item(self, work_item_id: str, work_item_data: dict[str, Any]):
        """Track a work item for cleanup."""
        entity = TestEntity(
            entity_type='work_item',
            entity_id=work_item_id,
            entity_data=work_item_data,
            cleanup_order=self.cleanup_priorities.get('work_item', 1)
        )
        self.entities.append(entity)

    def track_milestone(self, milestone_id: str, project_path: str, milestone_data: dict[str, Any]):
        """Track a milestone for cleanup."""
        entity = TestEntity(
            entity_type='milestone',
            entity_id=milestone_id,
            entity_data={'project_path': project_path, **milestone_data},
            cleanup_order=self.cleanup_priorities.get('milestone', 2)
        )
        self.entities.append(entity)

    def track_iteration(self, iteration_id: str, group_path: str, iteration_data: dict[str, Any]):
        """Track an iteration for cleanup."""
        entity = TestEntity(
            entity_type='iteration',
            entity_id=iteration_id,
            entity_data={'group_path': group_path, **iteration_data},
            cleanup_order=self.cleanup_priorities.get('iteration', 3)
        )
        self.entities.append(entity)

    def track_project(self, project_id: str, project_data: dict[str, Any]):
        """Track a project for cleanup."""
        entity = TestEntity(
            entity_type='project',
            entity_id=project_id,
            entity_data=project_data,
            cleanup_order=self.cleanup_priorities.get('project', 10)
        )
        self.entities.append(entity)

    def track_group(self, group_id: str, group_data: dict[str, Any]):
        """Track a group for cleanup."""
        entity = TestEntity(
            entity_type='group',
            entity_id=group_id,
            entity_data=group_data,
            cleanup_order=self.cleanup_priorities.get('group', 20)
        )
        self.entities.append(entity)

    # Convenience methods for backward compatibility
    def add_work_item(self, work_item_id: str, work_item_data: dict[str, Any] | None = None):
        """Add a work item for cleanup."""
        self.track_work_item(work_item_id, work_item_data or {})

    def add_milestone(self, milestone_id: str, project_path: str | None = None, milestone_data: dict[str, Any] | None = None):
        """Add a milestone for cleanup."""
        if not project_path:
            project_path = getattr(self, '_default_project_path', None)
        if not project_path:
            raise ValueError("project_path is required for milestone cleanup")
        self.track_milestone(milestone_id, project_path, milestone_data or {})

    def add_iteration(self, iteration_id: str, group_path: str | None = None, iteration_data: dict[str, Any] | None = None):
        """Add an iteration for cleanup."""
        if not group_path:
            group_path = getattr(self, '_default_group_path', None)
        if not group_path:
            raise ValueError("group_path is required for iteration cleanup")
        self.track_iteration(iteration_id, group_path, iteration_data or {})

    def add_project(self, project_id: str, project_data: dict[str, Any] | None = None):
        """Add a project for cleanup."""
        self.track_project(project_id, project_data or {})

    def add_group(self, group_id: str, group_data: dict[str, Any] | None = None):
        """Add a group for cleanup."""
        self.track_group(group_id, group_data or {})

    def add_repository(self, repository_id: str, repository_data: dict[str, Any] | None = None):
        """Add a repository for cleanup."""
        entity = TestEntity(
            entity_type='repository',
            entity_id=repository_id,
            entity_data=repository_data or {},
            cleanup_order=self.cleanup_priorities.get('project', 10)  # Same as project
        )
        self.entities.append(entity)

    def add_branch(self, project_path: str, branch_name: str, branch_data: dict[str, Any] | None = None):
        """Add a branch for cleanup."""
        entity = TestEntity(
            entity_type='branch',
            entity_id=f"{project_path}:{branch_name}",
            entity_data={'project_path': project_path, 'branch_name': branch_name, **(branch_data or {})},
            cleanup_order=self.cleanup_priorities.get('branch', 5)
        )
        self.entities.append(entity)

    def add_file(self, project_path: str, file_path: str, branch_name: str = "main", file_data: dict[str, Any] | None = None):
        """Add a file for cleanup."""
        entity = TestEntity(
            entity_type='file',
            entity_id=f"{project_path}:{branch_name}:{file_path}",
            entity_data={'project_path': project_path, 'file_path': file_path, 'branch_name': branch_name, **(file_data or {})},
            cleanup_order=self.cleanup_priorities.get('file', 1)  # Clean up files first
        )
        self.entities.append(entity)

    async def cleanup_work_item(self, entity: TestEntity) -> bool:
        """Clean up a work item."""
        try:
            # Use GraphQL to delete work item
            mutation = """
            mutation($input: WorkItemDeleteInput!) {
                workItemDelete(input: $input) {
                    errors
                }
            }
            """

            variables = {
                "input": {
                    "id": entity.entity_id
                }
            }

            result = await self.graphql_client.mutation(mutation, variables)

            if result.get('workItemDelete', {}).get('errors'):
                print(f"Warning: GraphQL errors deleting work item {entity.entity_id}: {result['workItemDelete']['errors']}")
                return False

            print(f"✓ Cleaned up work item: {entity.entity_id}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup work item {entity.entity_id}: {e}")
            return False

    async def cleanup_milestone(self, entity: TestEntity) -> bool:
        """Clean up a milestone."""
        try:
            project_path = entity.entity_data.get('project_path')
            if project_path:
                endpoint = f"/projects/{project_path.replace('/', '%2F')}/milestones/{entity.entity_id}"
            else:
                # Group milestone
                group_path = entity.entity_data.get('group_path')
                endpoint = f"/groups/{group_path}/milestones/{entity.entity_id}"

            await self.rest_client.delete_async(endpoint)
            print(f"✓ Cleaned up milestone: {entity.entity_id}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup milestone {entity.entity_id}: {e}")
            return False

    async def cleanup_iteration(self, entity: TestEntity) -> bool:
        """Clean up an iteration."""
        try:
            group_path = entity.entity_data.get('group_path')
            endpoint = f"/groups/{group_path}/iterations/{entity.entity_id}"

            await self.rest_client.delete_async(endpoint)
            print(f"✓ Cleaned up iteration: {entity.entity_id}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup iteration {entity.entity_id}: {e}")
            return False

    async def cleanup_project(self, entity: TestEntity) -> bool:
        """Clean up a project."""
        try:
            await self.rest_client.delete_async(f"/projects/{entity.entity_id}")
            print(f"✓ Cleaned up project: {entity.entity_id}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup project {entity.entity_id}: {e}")
            return False

    async def cleanup_group(self, entity: TestEntity) -> bool:
        """Clean up a group."""
        try:
            await self.rest_client.delete_async(f"/groups/{entity.entity_id}")
            print(f"✓ Cleaned up group: {entity.entity_id}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup group {entity.entity_id}: {e}")
            return False

    async def cleanup_repository(self, entity: TestEntity) -> bool:
        """Clean up a repository."""
        try:
            await self.rest_client.delete_async(f"/projects/{entity.entity_id}")
            print(f"✓ Cleaned up repository: {entity.entity_id}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup repository {entity.entity_id}: {e}")
            return False

    async def cleanup_branch(self, entity: TestEntity) -> bool:
        """Clean up a branch."""
        try:
            project_path = entity.entity_data.get('project_path')
            branch_name = entity.entity_data.get('branch_name')

            if not project_path or not branch_name:
                print(f"Warning: Missing project_path or branch_name for branch cleanup: {entity.entity_id}")
                return False

            # URL encode the project path
            encoded_path = project_path.replace('/', '%2F')
            endpoint = f"/projects/{encoded_path}/repository/branches/{branch_name}"

            await self.rest_client.delete_async(endpoint)
            print(f"✓ Cleaned up branch: {project_path}:{branch_name}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup branch {entity.entity_id}: {e}")
            return False

    async def cleanup_file(self, entity: TestEntity) -> bool:
        """Clean up a file."""
        try:
            project_path = entity.entity_data.get('project_path')
            file_path = entity.entity_data.get('file_path')
            branch_name = entity.entity_data.get('branch_name', 'main')

            if not project_path or not file_path:
                print(f"Warning: Missing project_path or file_path for file cleanup: {entity.entity_id}")
                return False

            # URL encode the project path and file path
            encoded_project_path = project_path.replace('/', '%2F')
            encoded_file_path = file_path.replace('/', '%2F')

            endpoint = f"/projects/{encoded_project_path}/repository/files/{encoded_file_path}"

            # Delete file with commit message
            delete_data = {
                "branch": branch_name,
                "commit_message": f"Test cleanup: Delete {file_path}"
            }

            await self.rest_client.delete_async(endpoint, json=delete_data)
            print(f"✓ Cleaned up file: {project_path}:{file_path}")
            return True

        except Exception as e:
            print(f"Warning: Failed to cleanup file {entity.entity_id}: {e}")
            return False

    async def cleanup_entity(self, entity: TestEntity) -> bool:
        """Clean up a single entity based on its type."""
        cleanup_methods = {
            'work_item': self.cleanup_work_item,
            'milestone': self.cleanup_milestone,
            'iteration': self.cleanup_iteration,
            'project': self.cleanup_project,
            'group': self.cleanup_group,
            'repository': self.cleanup_repository,
            'branch': self.cleanup_branch,
            'file': self.cleanup_file
        }

        cleanup_method = cleanup_methods.get(entity.entity_type)
        if cleanup_method:
            return await cleanup_method(entity)
        else:
            print(f"Warning: Unknown entity type for cleanup: {entity.entity_type}")
            return False

    async def _cleanup_parallel(self, sorted_entities: list[TestEntity]) -> tuple[int, int]:
        """Clean up entities in parallel by order groups."""
        success_count = 0
        failed_count = 0

        for order, group in groupby(sorted_entities, key=lambda e: e.cleanup_order):
            entities_in_group = list(group)
            print(f"Cleaning up {len(entities_in_group)} entities of order {order}...")

            tasks = [self.cleanup_entity(entity) for entity in entities_in_group]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    failed_count += 1
                elif result:
                    success_count += 1
                else:
                    failed_count += 1

        return success_count, failed_count

    async def _cleanup_sequential(self, sorted_entities: list[TestEntity]) -> tuple[int, int]:
        """Clean up entities sequentially in dependency order."""
        success_count = 0
        failed_count = 0

        print(f"Cleaning up {len(sorted_entities)} entities sequentially...")
        for entity in sorted_entities:
            try:
                success = await self.cleanup_entity(entity)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Exception during cleanup of {entity.entity_type} {entity.entity_id}: {e}")
                failed_count += 1

        return success_count, failed_count

    def _create_cleanup_stats(self, success_count: int, failed_count: int) -> dict[str, int]:
        """Create cleanup statistics dictionary."""
        stats = {
            'total': success_count + failed_count,
            'success': success_count,
            'failed': failed_count
        }

        if stats['total'] > 0:
            print(f"Cleanup completed: {stats['success']}/{stats['total']} entities cleaned successfully")
            if stats['failed'] > 0:
                print(f"Warning: {stats['failed']} entities failed to cleanup")

        return stats

    async def cleanup_all(self, parallel: bool = False) -> dict[str, int]:
        """Clean up all tracked entities.

        Args:
            parallel: If True, clean up entities of same type in parallel.
                     If False, clean up sequentially in dependency order.

        Returns:
            Dict with cleanup statistics
        """
        if not self.entities:
            return {'total': 0, 'success': 0, 'failed': 0}

        # Sort entities by cleanup order
        sorted_entities = sorted(self.entities, key=lambda e: e.cleanup_order)

        if parallel:
            success_count, failed_count = await self._cleanup_parallel(sorted_entities)
        else:
            success_count, failed_count = await self._cleanup_sequential(sorted_entities)

        # Clear the entities list
        self.entities.clear()

        return self._create_cleanup_stats(success_count, failed_count)

    async def cleanup_by_prefix(self, prefix: str) -> dict[str, int]:
        """Clean up entities matching a specific prefix.

        This is useful for cleaning up leftover test data from previous runs.
        """
        print(f"Searching for entities with prefix '{prefix}' to cleanup...")

        # This would require searching through various GitLab entities
        # For now, just cleanup tracked entities with matching names
        matching_entities = [
            entity for entity in self.entities
            if any(prefix in str(value) for value in entity.entity_data.values())
        ]

        if not matching_entities:
            print(f"No entities found with prefix '{prefix}'")
            return {'total': 0, 'success': 0, 'failed': 0}

        print(f"Found {len(matching_entities)} entities with prefix '{prefix}'")

        # Temporarily store all entities and only cleanup matching ones
        all_entities = self.entities.copy()
        self.entities = matching_entities

        stats = await self.cleanup_all()

        # Restore non-matching entities
        self.entities = [e for e in all_entities if e not in matching_entities]

        return stats

    def get_cleanup_summary(self) -> dict[str, list[str]]:
        """Get a summary of entities currently tracked for cleanup."""
        summary = {}
        for entity in self.entities:
            entity_type = entity.entity_type
            if entity_type not in summary:
                summary[entity_type] = []

            # Create a readable identifier
            identifier = entity.entity_id
            if 'title' in entity.entity_data:
                identifier += f" ({entity.entity_data['title']})"
            elif 'name' in entity.entity_data:
                identifier += f" ({entity.entity_data['name']})"

            summary[entity_type].append(identifier)

        return summary
