"""Pytest configuration and fixtures for GitLab MCP Server tests.

This module provides shared fixtures and configuration for testing
the GitLab MCP Server against a real GitLab instance.

Environment Configuration:
- The tests automatically load environment variables from a .env file if present
- Required environment variables:
  - GITLAB_API_URL: GitLab instance URL (e.g., https://gitlab.com or https://git.private.systems)
  - GITLAB_PERSONAL_ACCESS_TOKEN: Personal access token with appropriate permissions
- If .env file is not found or variables are missing, tests will be skipped with appropriate messages
"""

import contextlib
import os
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import pytest
import pytest_asyncio
from faker import Faker

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

from src.api.graphql_client import GitLabGraphQLClientSingleton
from src.api.rest_client import GitLabRestClient, gitlab_rest_client
from tests.utils.cleanup import TestCleanup
from tests.utils.test_data import TestDataFactory

# Configure faker for reproducible test data
fake = Faker()
Faker.seed(12345)

# Test configuration constants
TEST_GROUP_PATH = "test"
TEST_SUBGROUP_PATH = "test/test_subgroup"
TEST_PROJECT_PATH = "test/test_subgroup/test_project"
TEST_SECONDARY_PROJECT_PATH = "test/test_project_in_parent"
TEST_DATA_PREFIX = "MCP_TEST_"


@pytest_asyncio.fixture(autouse=True)
async def cleanup_singleton_client():
    """Automatically clean up singleton REST client after each test."""
    yield

    # Clean up singleton REST client after test
    try:
        if hasattr(gitlab_rest_client, '_httpx_client') and gitlab_rest_client._httpx_client:
            await gitlab_rest_client.aclose()
    except Exception:
        pass  # Ignore cleanup errors


@pytest_asyncio.fixture
async def gitlab_config() -> dict[str, str]:
    """Get GitLab configuration from environment variables."""
    config = {
        "api_url": os.getenv("GITLAB_API_URL"),
        "token": os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN"),
    }

    if not config["api_url"] or not config["token"]:
        pytest.skip("GitLab configuration not found. Set GITLAB_API_URL and GITLAB_PERSONAL_ACCESS_TOKEN")

    return config


@pytest_asyncio.fixture
async def rest_client(gitlab_config: dict[str, str]) -> AsyncGenerator[GitLabRestClient]:
    """Create a GitLab REST API client for the test session."""
    # Set environment variables for the client
    os.environ["GITLAB_API_URL"] = gitlab_config["api_url"]
    os.environ["GITLAB_PERSONAL_ACCESS_TOKEN"] = gitlab_config["token"]

    client = GitLabRestClient()

    # Verify connection
    try:
        await client.get_async("/user")
    except Exception as e:
        pytest.skip(f"Cannot connect to GitLab API: {e}")

    yield client

    # Cleanup: Close the HTTP client
    with contextlib.suppress(Exception):
        await client.aclose()


@pytest_asyncio.fixture
async def graphql_client(gitlab_config: dict[str, str]):
    """Create a GitLab GraphQL client for the test session."""
    # Set environment variables for the client
    os.environ["GITLAB_API_URL"] = gitlab_config["api_url"]
    os.environ["GITLAB_PERSONAL_ACCESS_TOKEN"] = gitlab_config["token"]

    client = GitLabGraphQLClientSingleton.initialize()

    # Verify GraphQL connection
    try:
        query = "query { currentUser { id name } }"
        await client.query(query)
    except Exception as e:
        pytest.skip(f"Cannot connect to GitLab GraphQL API: {e}")

    yield client

    # Cleanup
    try:
        await GitLabGraphQLClientSingleton.close_singleton()
    except AttributeError:
        # If close_singleton doesn't exist or has issues, cleanup manually
        if hasattr(GitLabGraphQLClientSingleton, '_instance') and GitLabGraphQLClientSingleton._instance is not None:
            with contextlib.suppress(Exception):
                await GitLabGraphQLClientSingleton._instance.close()
            GitLabGraphQLClientSingleton._instance = None


@pytest_asyncio.fixture
async def test_group_name() -> str:
    """Generate a unique test group name."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"mcp-test-suite-{timestamp}"


@pytest_asyncio.fixture
async def test_group(
    rest_client: GitLabRestClient,
    test_group_name: str
) -> AsyncGenerator[dict[str, Any]]:
    """Create a test group for the entire test session."""
    # Check if group already exists
    try:
        existing_group = await rest_client.get_async(f"/groups/{test_group_name}")
        group = existing_group
    except Exception:
        # Create new group
        group_data = {
            "name": test_group_name,
            "path": test_group_name,
            "description": "Test group created by GitLab MCP Server test suite",
            "visibility": "private"
        }

        try:
            group = await rest_client.post_async("/groups", json_data=group_data)
        except Exception as e:
            pytest.skip(f"Cannot create test group: {e}")

    yield group

    # Cleanup: Delete the test group (this will cascade delete all projects)
    try:
        await rest_client.delete_async(f"/groups/{group['id']}")
    except Exception as e:
        print(f"Warning: Failed to cleanup test group {group['id']}: {e}")


@pytest_asyncio.fixture
async def test_project_name() -> str:
    """Generate a unique test project name for each test."""
    return f"test-project-{uuid.uuid4().hex[:8]}"


@pytest_asyncio.fixture
async def test_project(
    rest_client: GitLabRestClient,
    test_group: dict[str, Any],
    test_project_name: str
) -> AsyncGenerator[dict[str, Any]]:
    """Create a test project for each test."""
    project_data = {
        "name": test_project_name,
        "path": test_project_name,
        "namespace_id": test_group["id"],
        "description": "Test project created by GitLab MCP Server test suite",
        "visibility": "private",
        "initialize_with_readme": True
    }

    try:
        project = await rest_client.post_async("/projects", json_data=project_data)
    except Exception as e:
        pytest.skip(f"Cannot create test project: {e}")

    yield project

    # Cleanup: Delete the test project
    try:
        await rest_client.delete_async(f"/projects/{project['id']}")
    except Exception as e:
        print(f"Warning: Failed to cleanup test project {project['id']}: {e}")


@pytest.fixture
def test_project_path(test_project: dict[str, Any]) -> str:
    """Get the full path of the test project."""
    return test_project["path_with_namespace"]


@pytest.fixture
def test_group_path(test_group: dict[str, Any]) -> str:
    """Get the full path of the test group."""
    return test_group["full_path"]


@pytest.fixture
def static_test_project_path() -> str:
    """Get the path of the existing test project without creating new resources."""
    return TEST_PROJECT_PATH


@pytest.fixture
def static_test_group_path() -> str:
    """Get the path of the existing test group without creating new resources."""
    return TEST_GROUP_PATH


@pytest_asyncio.fixture
async def test_cleanup(
    rest_client: GitLabRestClient,
    graphql_client,
    test_project_path: str,
    test_group_path: str
) -> AsyncGenerator[TestCleanup]:
    """Create a test cleanup instance for each test."""
    cleanup = TestCleanup(rest_client, graphql_client)

    # Store context for cleanup methods that need it
    cleanup._default_project_path = test_project_path
    cleanup._default_group_path = test_group_path

    yield cleanup

    # Auto cleanup after each test
    try:
        await cleanup.cleanup_all()
    except Exception as e:
        print(f"Warning: Test cleanup failed: {e}")


@pytest_asyncio.fixture
async def test_data_factory(
    test_group: dict[str, Any],
    test_project: dict[str, Any]
) -> TestDataFactory:
    """Create a test data factory for generating test data."""
    return TestDataFactory(
        group_path=test_group["full_path"],
        project_path=test_project["path_with_namespace"],
        prefix=TEST_DATA_PREFIX
    )


@pytest.fixture
def static_test_data_factory() -> TestDataFactory:
    """Create a test data factory using existing test infrastructure."""
    return TestDataFactory(
        group_path=TEST_GROUP_PATH,
        project_path=TEST_PROJECT_PATH,
        prefix=TEST_DATA_PREFIX
    )


@pytest_asyncio.fixture
async def cleanup_tracker(
    rest_client: GitLabRestClient,
    graphql_client
) -> AsyncGenerator[TestCleanup]:
    """Track and cleanup test entities."""
    cleanup = TestCleanup(rest_client, graphql_client)
    yield cleanup

    # Perform cleanup after test
    await cleanup.cleanup_all()

    # Ensure REST client is closed
    with contextlib.suppress(Exception):
        await rest_client.aclose()


@pytest_asyncio.fixture
async def work_item_type_ids(graphql_client) -> dict[str, str]:
    """Dynamically discover work item type IDs for this GitLab instance."""
    try:
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

        variables = {"projectPath": TEST_PROJECT_PATH}
        result = await graphql_client.query(query, variables)

        if "project" in result and result["project"] and "workItemTypes" in result["project"]:
            work_item_types = result["project"]["workItemTypes"]["nodes"]
            type_map = {}

            for wit in work_item_types:
                # Map both exact names and common variations
                name = wit["name"].upper()
                type_map[name] = wit["id"]

                # Add common aliases
                if name == "TEST CASE":
                    type_map["TEST_CASE"] = wit["id"]
                elif name == "KEY RESULT":
                    type_map["KEY_RESULT"] = wit["id"]

            print(f"Discovered {len(type_map)} work item types: {list(type_map.keys())}")
            return type_map
        else:
            raise ValueError(f"Could not discover work item types for project {TEST_PROJECT_PATH}")

    except Exception as e:
        # Fallback to hardcoded values if discovery fails
        print(f"Warning: Work item type discovery failed ({e}), using fallback values")
        return {
            "EPIC": "gid://gitlab/WorkItems::Type/8",
            "ISSUE": "gid://gitlab/WorkItems::Type/1",
            "INCIDENT": "gid://gitlab/WorkItems::Type/2",
            "TEST_CASE": "gid://gitlab/WorkItems::Type/3",
            "REQUIREMENT": "gid://gitlab/WorkItems::Type/4",
            "TASK": "gid://gitlab/WorkItems::Type/5",
            "OBJECTIVE": "gid://gitlab/WorkItems::Type/6",
            "KEY_RESULT": "gid://gitlab/WorkItems::Type/7",
            "TICKET": "gid://gitlab/WorkItems::Type/9"
        }


# Test environment markers
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "work_items: marks tests related to Work Items API"
    )
    config.addinivalue_line(
        "markers", "milestones: marks tests related to Milestones API"
    )
    config.addinivalue_line(
        "markers", "search: marks tests related to Search API"
    )


def pytest_sessionstart(session):
    """Print information at the start of the test session."""
    gitlab_token = os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN")
    gitlab_url = os.getenv("GITLAB_API_URL")

    if not gitlab_token or not gitlab_url:
        print("\n" + "="*80)
        print("🧪 UNIT TESTS ONLY MODE")
        print("="*80)
        print("GitLab API credentials not found. Running unit tests only.")
        print("\nTo run integration tests, set BOTH environment variables:")
        print("- GITLAB_API_URL: GitLab instance URL (REQUIRED to prevent accidental testing)")
        print("- GITLAB_PERSONAL_ACCESS_TOKEN: Personal access token with API permissions")
        print("\nYou can create a .env file with these variables for convenience.")
        print("SAFETY: Tests require BOTH values to prevent accidental testing against gitlab.com")
        print("="*80)
    elif gitlab_url and (
        "gitlab.com" in gitlab_url.lower() or
        "gitlab.org" in gitlab_url.lower()
    ):
        print("\n" + "🚨"*20)
        print("🚨 SAFETY CHECK FAILED 🚨")
        print("🚨"*20)
        print("GitLab URL contains 'gitlab.com' or 'gitlab.org' - Integration tests BLOCKED!")
        print("Please use your own GitLab instance URL in GITLAB_API_URL.")
        print("Only unit tests will run for safety.")
        print("🚨"*20)


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    # All test files that make actual GitLab API calls (integration tests)
    api_test_files = [
        "test_branches.py",
        "test_files.py",
        "test_milestones.py",
        "test_repositories.py",
        "test_search.py",
        "test_work_items.py",
        "test_integration.py",
        "test_iterations.py"
    ]

    for item in items:
        # Mark ALL tests that make actual API calls as slow/integration
        if any(api_file in item.nodeid for api_file in api_test_files):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)

        # Mark tests in specific functional categories
        if "test_work_items" in item.nodeid:
            item.add_marker(pytest.mark.work_items)
        elif "test_milestones" in item.nodeid:
            item.add_marker(pytest.mark.milestones)
        elif "test_search" in item.nodeid:
            item.add_marker(pytest.mark.search)


def pytest_runtest_setup(item):
    """Setup for each test run."""
    # Check if GitLab credentials are available
    gitlab_token = os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN")
    gitlab_url = os.getenv("GITLAB_API_URL")

    # If no GitLab credentials, only run unit tests
    if (not gitlab_token or not gitlab_url) and "unit" not in item.keywords:
        pytest.skip(
            "GitLab API credentials not found. Only running unit tests.\n"
            "To run integration tests, set BOTH environment variables:\n"
            "- GITLAB_API_URL: GitLab instance URL (REQUIRED to prevent accidental testing)\n"
            "- GITLAB_PERSONAL_ACCESS_TOKEN: Personal access token with API permissions\n"
            "You can create a .env file with these variables for convenience."
        )

    # SAFETY CHECK: Prevent accidental testing against gitlab.com/gitlab.org
    if (gitlab_url and (
        "gitlab.com" in gitlab_url.lower() or
        "gitlab.org" in gitlab_url.lower()
    )) and "unit" not in item.keywords:
        pytest.skip(
            "🚨 SAFETY CHECK FAILED: GitLab URL contains 'gitlab.com' or 'gitlab.org'!\n"
            "Integration tests are BLOCKED to prevent accidental testing against public GitLab.\n"
            "Please use your own GitLab instance URL in GITLAB_API_URL.\n"
            "Only unit tests will run for safety."
            )

    # Skip slow tests if not explicitly requested
    if "slow" in item.keywords and not item.config.getoption("--runslow", default=False):
        pytest.skip("need --runslow option to run")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--cleanup-only", action="store_true", default=False,
        help="only run cleanup, don't run tests"
    )
    parser.addoption(
        "--keep-test-data", action="store_true", default=False,
        help="keep test data after tests (for debugging)"
    )
