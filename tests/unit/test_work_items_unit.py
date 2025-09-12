"""Unit tests for Work Items service using mocks (no API calls).

These tests verify business logic, error handling, and data transformations
without making actual GitLab API requests.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.schemas.work_items import (
    CreateWorkItemInput,
    DeleteWorkItemInput,
    GetWorkItemInput,
    ListWorkItemsInput,
    UpdateWorkItemInput,
    WorkItemState,
    WorkItemType,
)
from src.services.work_items import (
    _build_create_input,
    _process_create_result,
    _resolve_work_item_type_id,
    create_work_item,
    delete_work_item,
    get_work_item,
    list_work_items,
    update_work_item,
)


class TestGetWorkItem:
    """Unit tests for get_work_item function."""

    @pytest.fixture
    def mock_graphql_client(self):
        """Mock GraphQL client."""
        with patch('src.services.work_items.get_graphql_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def sample_work_item_response(self):
        """Sample work item GraphQL response."""
        return {
            "workItem": {
                "id": "gid://gitlab/WorkItem/123",
                "iid": 42,
                "title": "Test Issue",
                "state": "OPEN",
                "confidential": False,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z",
                "closedAt": None,
                "author": {
                    "id": "gid://gitlab/User/456",
                    "name": "Test User",
                    "username": "testuser",
                    "webUrl": "https://gitlab.example.com/testuser"
                },
                "project": {
                    "id": "gid://gitlab/Project/789",
                    "name": "test-project",
                    "fullPath": "group/test-project"
                },
                "workItemType": {
                    "id": "gid://gitlab/WorkItems::Type/2",
                    "name": "Issue"
                },
                "webUrl": "https://gitlab.example.com/group/test-project/-/issues/42",
                "reference": "group/test-project#42",
                "widgets": [
                    {
                        "type": "DESCRIPTION",
                        "description": "Test description"
                    }
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_get_work_item_by_id_success(self, mock_graphql_client, sample_work_item_response):
        """Test successful retrieval by global ID."""
        mock_graphql_client.query.return_value = sample_work_item_response

        input_model = GetWorkItemInput(id="gid://gitlab/WorkItem/123")
        result = await get_work_item(input_model)

        assert result["id"] == "gid://gitlab/WorkItem/123"
        assert result["title"] == "Test Issue"
        assert result["state"] == "OPEN"

        mock_graphql_client.query.assert_called_once()
        call_args = mock_graphql_client.query.call_args
        assert "getWorkItem" in call_args[0][0]  # Query contains getWorkItem
        assert call_args[0][1]["id"] == "gid://gitlab/WorkItem/123"

    @pytest.mark.asyncio
    async def test_get_work_item_by_iid_success(self, mock_graphql_client):
        """Test successful retrieval by IID and project path."""
        project_response = {
            "project": {
                "workItems": {
                    "nodes": [{
                        "id": "gid://gitlab/WorkItem/123",
                        "iid": 42,
                        "title": "Test Issue by IID",
                        "state": "OPEN"
                    }]
                }
            }
        }
        mock_graphql_client.query.return_value = project_response

        input_model = GetWorkItemInput(iid=42, project_path="group/test-project")
        result = await get_work_item(input_model)

        assert result["iid"] == 42
        assert result["title"] == "Test Issue by IID"

        mock_graphql_client.query.assert_called_once()
        call_args = mock_graphql_client.query.call_args
        assert "getWorkItemByIid" in call_args[0][0]
        assert call_args[0][1]["projectPath"] == "group/test-project"
        assert call_args[0][1]["iid"] == "42"

    @pytest.mark.asyncio
    async def test_get_work_item_not_found_by_id(self, mock_graphql_client):
        """Test work item not found by ID."""
        mock_graphql_client.query.return_value = {"workItem": None}

        input_model = GetWorkItemInput(id="gid://gitlab/WorkItem/999")

        with pytest.raises(GitLabAPIError) as exc_info:
            await get_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.NOT_FOUND
        assert "Work item gid://gitlab/WorkItem/999 not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_work_item_not_found_by_iid(self, mock_graphql_client):
        """Test work item not found by IID."""
        mock_graphql_client.query.return_value = {
            "project": {"workItems": {"nodes": []}}
        }

        input_model = GetWorkItemInput(iid=999, project_path="group/test-project")

        with pytest.raises(GitLabAPIError) as exc_info:
            await get_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.NOT_FOUND
        assert "Work item 999 not found in project group/test-project" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_work_item_missing_parameters(self, mock_graphql_client):
        """Test missing required parameters."""
        input_model = GetWorkItemInput()

        with pytest.raises(GitLabAPIError) as exc_info:
            await get_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Either 'id' or both 'iid' and 'project_path' must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_work_item_partial_iid_parameters(self, mock_graphql_client):
        """Test partial IID parameters (missing project_path)."""
        input_model = GetWorkItemInput(iid=42)

        with pytest.raises(GitLabAPIError) as exc_info:
            await get_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED

    @pytest.mark.asyncio
    async def test_get_work_item_graphql_exception(self, mock_graphql_client):
        """Test handling of GraphQL client exceptions."""
        mock_graphql_client.query.side_effect = Exception("GraphQL connection failed")

        input_model = GetWorkItemInput(id="gid://gitlab/WorkItem/123")

        with pytest.raises(GitLabAPIError) as exc_info:
            await get_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.SERVER_ERROR
        assert "Unexpected error getting work item" in str(exc_info.value)


class TestListWorkItems:
    """Unit tests for list_work_items function."""

    @pytest.fixture
    def mock_graphql_client(self):
        """Mock GraphQL client."""
        with patch('src.services.work_items.get_graphql_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def sample_work_items_response(self):
        """Sample work items list response."""
        return {
            "project": {
                "workItems": {
                    "nodes": [
                        {
                            "id": "gid://gitlab/WorkItem/123",
                            "iid": 42,
                            "title": "First Issue",
                            "state": "OPEN",
                            "workItemType": {"id": "gid://gitlab/WorkItems::Type/2", "name": "Issue"},
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-02T00:00:00Z",
                            "author": {"id": "gid://gitlab/User/456", "name": "Test User", "username": "testuser"},
                            "webUrl": "https://gitlab.example.com/group/test-project/-/issues/42"
                        },
                        {
                            "id": "gid://gitlab/WorkItem/124",
                            "iid": 43,
                            "title": "Second Issue",
                            "state": "CLOSED",
                            "workItemType": {"id": "gid://gitlab/WorkItems::Type/2", "name": "Issue"},
                            "createdAt": "2024-01-03T00:00:00Z",
                            "updatedAt": "2024-01-04T00:00:00Z",
                            "author": {"id": "gid://gitlab/User/457", "name": "Another User", "username": "anotheruser"},
                            "webUrl": "https://gitlab.example.com/group/test-project/-/issues/43"
                        }
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }

    @pytest.mark.asyncio
    async def test_list_work_items_project_success(self, mock_graphql_client, sample_work_items_response):
        """Test successful listing of work items from project."""
        mock_graphql_client.query.return_value = sample_work_items_response

        input_model = ListWorkItemsInput(
            project_path="group/test-project",
            first=10
        )
        result = await list_work_items(input_model)

        assert len(result) == 2
        assert result[0]["id"] == "gid://gitlab/WorkItem/123"
        assert result[0]["title"] == "First Issue"
        assert result[1]["id"] == "gid://gitlab/WorkItem/124"
        assert result[1]["title"] == "Second Issue"

        mock_graphql_client.query.assert_called_once()
        call_args = mock_graphql_client.query.call_args
        assert "listProjectWorkItems" in call_args[0][0]
        assert call_args[0][1]["projectPath"] == "group/test-project"
        assert call_args[0][1]["first"] == 10

    @pytest.mark.asyncio
    async def test_list_work_items_namespace_success(self, mock_graphql_client):
        """Test successful listing of work items from namespace/group."""
        namespace_response = {
            "group": {
                "workItems": {
                    "nodes": [{
                        "id": "gid://gitlab/WorkItem/125",
                        "iid": 1,
                        "title": "Epic Item",
                        "state": "OPEN",
                        "workItemType": {"id": "gid://gitlab/WorkItems::Type/7", "name": "Epic"},
                        "createdAt": "2024-01-05T00:00:00Z",
                        "updatedAt": "2024-01-05T00:00:00Z",
                        "author": {"id": "gid://gitlab/User/458", "name": "Epic User", "username": "epicuser"},
                        "webUrl": "https://gitlab.example.com/groups/group/-/epics/1"
                    }],
                    "pageInfo": {"hasNextPage": False, "endCursor": None}
                }
            }
        }
        mock_graphql_client.query.return_value = namespace_response

        input_model = ListWorkItemsInput(
            namespace_path="group",
            first=5
        )
        result = await list_work_items(input_model)

        assert len(result) == 1
        assert result[0]["workItemType"]["name"] == "Epic"

        call_args = mock_graphql_client.query.call_args
        assert "listGroupWorkItems" in call_args[0][0]
        assert call_args[0][1]["groupPath"] == "group"

    @pytest.mark.asyncio
    async def test_list_work_items_with_filters(self, mock_graphql_client, sample_work_items_response):
        """Test listing work items with various filters."""
        mock_graphql_client.query.return_value = sample_work_items_response

        input_model = ListWorkItemsInput(
            project_path="group/test-project",
            work_item_types=[WorkItemType.ISSUE, WorkItemType.TASK],
            state=WorkItemState.OPEN,
            search="bug",
            sort="CREATED_DESC",
            first=20,
            after="cursor123"
        )
        result = await list_work_items(input_model)

        assert len(result) == 2

        call_args = mock_graphql_client.query.call_args
        variables = call_args[0][1]
        assert variables["types"] == ["ISSUE", "TASK"]
        assert variables["state"] == "opened"  # Converted from OPEN to opened
        assert variables["search"] == "bug"
        assert variables["sort"] == "CREATED_DESC"
        assert variables["first"] == 20
        assert variables["after"] == "cursor123"

    @pytest.mark.asyncio
    async def test_list_work_items_closed_state_conversion(self, mock_graphql_client, sample_work_items_response):
        """Test state conversion for CLOSED state."""
        mock_graphql_client.query.return_value = sample_work_items_response

        input_model = ListWorkItemsInput(
            project_path="group/test-project",
            state=WorkItemState.CLOSED
        )
        await list_work_items(input_model)

        call_args = mock_graphql_client.query.call_args
        assert call_args[0][1]["state"] == "closed"  # Converted from CLOSED to closed

    @pytest.mark.asyncio
    async def test_list_work_items_missing_context(self, mock_graphql_client):
        """Test missing both project_path and namespace_path."""
        input_model = ListWorkItemsInput(first=10)

        with pytest.raises(GitLabAPIError) as exc_info:
            await list_work_items(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Either project_path or namespace_path must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_work_items_project_not_found(self, mock_graphql_client):
        """Test project not found or no access."""
        mock_graphql_client.query.return_value = None

        input_model = ListWorkItemsInput(project_path="nonexistent/project")

        with pytest.raises(GitLabAPIError) as exc_info:
            await list_work_items(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "not found or has no work items access" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_work_items_empty_result(self, mock_graphql_client):
        """Test empty work items result."""
        empty_response = {"project": {"workItems": {"nodes": []}}}
        mock_graphql_client.query.return_value = empty_response

        input_model = ListWorkItemsInput(project_path="group/empty-project")
        result = await list_work_items(input_model)

        assert result == []


class TestCreateWorkItem:
    """Unit tests for create_work_item function."""

    @pytest.fixture
    def mock_graphql_client(self):
        """Mock GraphQL client."""
        with patch('src.services.work_items.get_graphql_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def mock_work_item_type_manager(self):
        """Mock work item type manager."""
        with patch('src.services.work_items.get_work_item_type_manager') as mock:
            manager = Mock()
            manager.get_type_id.return_value = "gid://gitlab/WorkItems::Type/2"
            mock.return_value = manager
            yield manager

    @pytest.fixture
    def sample_create_response(self):
        """Sample successful creation response."""
        return {
            "workItemCreate": {
                "workItem": {
                    "id": "gid://gitlab/WorkItem/123",
                    "iid": 42,
                    "title": "New Issue",
                    "state": "OPEN",
                    "workItemType": {
                        "id": "gid://gitlab/WorkItems::Type/2",
                        "name": "Issue"
                    },
                    "createdAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:00:00Z",
                    "author": {
                        "id": "gid://gitlab/User/456",
                        "name": "Creator",
                        "username": "creator",
                        "webUrl": "https://gitlab.example.com/creator"
                    },
                    "project": {
                        "id": "gid://gitlab/Project/789",
                        "name": "test-project",
                        "fullPath": "group/test-project"
                    },
                    "webUrl": "https://gitlab.example.com/group/test-project/-/issues/42",
                    "reference": "group/test-project#42",
                    "widgets": []
                },
                "errors": []
            }
        }

    @pytest.mark.asyncio
    async def test_create_work_item_success_with_project(self, mock_graphql_client, mock_work_item_type_manager, sample_create_response):
        """Test successful work item creation in project."""
        mock_graphql_client.mutation.return_value = sample_create_response

        input_model = CreateWorkItemInput(
            work_item_type_id="ISSUE",
            project_path="group/test-project",
            title="New Issue",
            description="Test description",
            confidential=False
        )
        result = await create_work_item(input_model)

        assert result["id"] == "gid://gitlab/WorkItem/123"
        assert result["title"] == "New Issue"
        assert result["state"] == "OPEN"

        # Verify type ID resolution was called
        mock_work_item_type_manager.get_type_id.assert_called_once_with("ISSUE")

        # Verify GraphQL mutation was called correctly
        mock_graphql_client.mutation.assert_called_once()
        call_args = mock_graphql_client.mutation.call_args
        assert "workItemCreate" in call_args[0][0]

        mutation_input = call_args[0][1]["input"]
        assert mutation_input["workItemTypeId"] == "gid://gitlab/WorkItems::Type/2"
        assert mutation_input["projectPath"] == "group/test-project"
        assert mutation_input["title"] == "New Issue"
        assert mutation_input["description"] == "Test description"
        assert mutation_input["confidential"] is False

    @pytest.mark.asyncio
    async def test_create_work_item_success_with_namespace(self, mock_graphql_client, mock_work_item_type_manager, sample_create_response):
        """Test successful work item creation in namespace (for epics)."""
        mock_work_item_type_manager.get_type_id.return_value = "gid://gitlab/WorkItems::Type/7"
        sample_create_response["workItemCreate"]["workItem"]["workItemType"]["name"] = "Epic"
        mock_graphql_client.mutation.return_value = sample_create_response

        input_model = CreateWorkItemInput(
            work_item_type_id="EPIC",
            namespace_path="group",
            title="New Epic"
        )
        result = await create_work_item(input_model)

        assert result["id"] == "gid://gitlab/WorkItem/123"

        call_args = mock_graphql_client.mutation.call_args
        mutation_input = call_args[0][1]["input"]
        assert mutation_input["namespacePath"] == "group"
        assert "projectPath" not in mutation_input

    @pytest.mark.asyncio
    async def test_create_work_item_with_global_id(self, mock_graphql_client, sample_create_response):
        """Test creation with already resolved global ID."""
        mock_graphql_client.mutation.return_value = sample_create_response

        input_model = CreateWorkItemInput(
            work_item_type_id="gid://gitlab/WorkItems::Type/2",
            project_path="group/test-project",
            title="New Issue"
        )
        result = await create_work_item(input_model)

        assert result["title"] == "New Issue"

        # Type manager should not be called for global IDs
        with patch('src.services.work_items.get_work_item_type_manager'):
            await create_work_item(input_model)
            # Should not be called because ID is already a global ID
            # The _resolve_work_item_type_id function should return the ID as-is

    @pytest.mark.asyncio
    async def test_create_work_item_missing_context(self, mock_graphql_client, mock_work_item_type_manager):
        """Test creation without project_path or namespace_path."""
        input_model = CreateWorkItemInput(
            work_item_type_id="ISSUE",
            title="Orphaned Issue"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await create_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Either project_path or namespace_path must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_work_item_unknown_type(self, mock_graphql_client, mock_work_item_type_manager):
        """Test creation with unknown work item type."""
        mock_work_item_type_manager.get_type_id.return_value = None

        input_model = CreateWorkItemInput(
            work_item_type_id="UNKNOWN_TYPE",
            project_path="group/test-project",
            title="Test Issue"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await create_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Unknown work item type: UNKNOWN_TYPE" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_work_item_graphql_errors(self, mock_graphql_client, mock_work_item_type_manager):
        """Test handling of GraphQL mutation errors."""
        error_response = {
            "workItemCreate": {
                "workItem": None,
                "errors": ["Title can't be blank", "Work item type is invalid"]
            }
        }
        mock_graphql_client.mutation.return_value = error_response

        input_model = CreateWorkItemInput(
            work_item_type_id="ISSUE",
            project_path="group/test-project",
            title=""
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await create_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Title can't be blank; Work item type is invalid" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_work_item_no_data_returned(self, mock_graphql_client, mock_work_item_type_manager):
        """Test handling when no work item data is returned."""
        empty_response = {
            "workItemCreate": {
                "workItem": None,
                "errors": []
            }
        }
        mock_graphql_client.mutation.return_value = empty_response

        input_model = CreateWorkItemInput(
            work_item_type_id="ISSUE",
            project_path="group/test-project",
            title="Test Issue"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await create_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Work item creation returned no data" in str(exc_info.value)


class TestUpdateWorkItem:
    """Unit tests for update_work_item function."""

    @pytest.fixture
    def mock_graphql_client(self):
        """Mock GraphQL client."""
        with patch('src.services.work_items.get_graphql_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def sample_update_response(self):
        """Sample successful update response."""
        return {
            "workItemUpdate": {
                "workItem": {
                    "id": "gid://gitlab/WorkItem/123",
                    "iid": 42,
                    "title": "Updated Issue Title",
                    "state": "CLOSED",
                    "confidential": True,
                    "createdAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-02T00:00:00Z",
                    "closedAt": "2024-01-02T00:00:00Z"
                },
                "errors": []
            }
        }

    @pytest.mark.asyncio
    async def test_update_work_item_success(self, mock_graphql_client, sample_update_response):
        """Test successful work item update."""
        mock_graphql_client.mutation.return_value = sample_update_response

        input_model = UpdateWorkItemInput(
            id="gid://gitlab/WorkItem/123",
            title="Updated Issue Title",
            state_event="close",
            confidential=True
        )
        result = await update_work_item(input_model)

        assert result["id"] == "gid://gitlab/WorkItem/123"
        assert result["title"] == "Updated Issue Title"
        assert result["state"] == "CLOSED"
        assert result["confidential"] is True

        mock_graphql_client.mutation.assert_called_once()
        call_args = mock_graphql_client.mutation.call_args
        assert "workItemUpdate" in call_args[0][0]

        mutation_input = call_args[0][1]["input"]
        assert mutation_input["id"] == "gid://gitlab/WorkItem/123"
        assert mutation_input["title"] == "Updated Issue Title"
        assert mutation_input["stateEvent"] == "CLOSE"  # Converted to uppercase
        assert mutation_input["confidential"] is True

    @pytest.mark.asyncio
    async def test_update_work_item_partial_update(self, mock_graphql_client, sample_update_response):
        """Test partial work item update (only title)."""
        sample_update_response["workItemUpdate"]["workItem"]["confidential"] = False
        mock_graphql_client.mutation.return_value = sample_update_response

        input_model = UpdateWorkItemInput(
            id="gid://gitlab/WorkItem/123",
            title="Only Title Update"
        )
        result = await update_work_item(input_model)

        assert result["title"] == "Updated Issue Title"  # From response

        call_args = mock_graphql_client.mutation.call_args
        mutation_input = call_args[0][1]["input"]
        assert mutation_input["id"] == "gid://gitlab/WorkItem/123"
        assert mutation_input["title"] == "Only Title Update"
        assert "stateEvent" not in mutation_input
        assert "confidential" not in mutation_input

    @pytest.mark.asyncio
    async def test_update_work_item_state_event_conversion(self, mock_graphql_client, sample_update_response):
        """Test state event conversion to uppercase."""
        mock_graphql_client.mutation.return_value = sample_update_response

        input_model = UpdateWorkItemInput(
            id="gid://gitlab/WorkItem/123",
            state_event="reopen"
        )
        await update_work_item(input_model)

        call_args = mock_graphql_client.mutation.call_args
        mutation_input = call_args[0][1]["input"]
        assert mutation_input["stateEvent"] == "REOPEN"  # Converted to uppercase

    @pytest.mark.asyncio
    async def test_update_work_item_confidential_false(self, mock_graphql_client, sample_update_response):
        """Test setting confidential to False explicitly."""
        sample_update_response["workItemUpdate"]["workItem"]["confidential"] = False
        mock_graphql_client.mutation.return_value = sample_update_response

        input_model = UpdateWorkItemInput(
            id="gid://gitlab/WorkItem/123",
            confidential=False
        )
        result = await update_work_item(input_model)

        assert result["confidential"] is False

        call_args = mock_graphql_client.mutation.call_args
        mutation_input = call_args[0][1]["input"]
        assert mutation_input["confidential"] is False

    @pytest.mark.asyncio
    async def test_update_work_item_graphql_errors(self, mock_graphql_client):
        """Test handling of GraphQL mutation errors."""
        error_response = {
            "workItemUpdate": {
                "workItem": None,
                "errors": ["Work item not found", "Access denied"]
            }
        }
        mock_graphql_client.mutation.return_value = error_response

        input_model = UpdateWorkItemInput(
            id="gid://gitlab/WorkItem/999",
            title="Update Non-existent"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await update_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Work item not found; Access denied" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_work_item_no_data_returned(self, mock_graphql_client):
        """Test handling when no work item data is returned."""
        empty_response = {
            "workItemUpdate": {
                "workItem": None,
                "errors": []
            }
        }
        mock_graphql_client.mutation.return_value = empty_response

        input_model = UpdateWorkItemInput(
            id="gid://gitlab/WorkItem/123",
            title="Test Update"
        )

        with pytest.raises(GitLabAPIError) as exc_info:
            await update_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Work item update returned no data" in str(exc_info.value)


class TestDeleteWorkItem:
    """Unit tests for delete_work_item function."""

    @pytest.fixture
    def mock_graphql_client(self):
        """Mock GraphQL client."""
        with patch('src.services.work_items.get_graphql_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def sample_delete_response(self):
        """Sample successful deletion response."""
        return {
            "workItemDelete": {
                "project": {
                    "id": "gid://gitlab/Project/789"
                },
                "errors": []
            }
        }

    @pytest.mark.asyncio
    async def test_delete_work_item_success(self, mock_graphql_client, sample_delete_response):
        """Test successful work item deletion."""
        mock_graphql_client.mutation.return_value = sample_delete_response

        input_model = DeleteWorkItemInput(id="gid://gitlab/WorkItem/123")
        result = await delete_work_item(input_model)

        assert result["message"] == "Work item deleted successfully"
        assert result["id"] == "gid://gitlab/WorkItem/123"

        mock_graphql_client.mutation.assert_called_once()
        call_args = mock_graphql_client.mutation.call_args
        assert "workItemDelete" in call_args[0][0]

        mutation_input = call_args[0][1]["input"]
        assert mutation_input["id"] == "gid://gitlab/WorkItem/123"

    @pytest.mark.asyncio
    async def test_delete_work_item_graphql_errors(self, mock_graphql_client):
        """Test handling of GraphQL mutation errors."""
        error_response = {
            "workItemDelete": {
                "project": None,
                "errors": ["Work item not found", "Cannot delete work item with children"]
            }
        }
        mock_graphql_client.mutation.return_value = error_response

        input_model = DeleteWorkItemInput(id="gid://gitlab/WorkItem/999")

        with pytest.raises(GitLabAPIError) as exc_info:
            await delete_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Work item not found; Cannot delete work item with children" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_work_item_mutation_exception(self, mock_graphql_client):
        """Test handling of mutation exceptions."""
        mock_graphql_client.mutation.side_effect = Exception("Connection timeout")

        input_model = DeleteWorkItemInput(id="gid://gitlab/WorkItem/123")

        with pytest.raises(GitLabAPIError) as exc_info:
            await delete_work_item(input_model)

        assert exc_info.value.error_type == GitLabErrorType.SERVER_ERROR
        assert "Unexpected error deleting work item" in str(exc_info.value)


class TestWorkItemHelperFunctions:
    """Unit tests for helper functions."""

    def test_resolve_work_item_type_id_global_id(self):
        """Test resolving already global ID."""
        global_id = "gid://gitlab/WorkItems::Type/2"
        result = _resolve_work_item_type_id(global_id)
        assert result == global_id

    @patch('src.services.work_items.get_work_item_type_manager')
    def test_resolve_work_item_type_id_name_success(self, mock_manager):
        """Test resolving type name to global ID."""
        manager = Mock()
        manager.get_type_id.return_value = "gid://gitlab/WorkItems::Type/2"
        mock_manager.return_value = manager

        result = _resolve_work_item_type_id("ISSUE")
        assert result == "gid://gitlab/WorkItems::Type/2"
        manager.get_type_id.assert_called_once_with("ISSUE")

    @patch('src.services.work_items.get_work_item_type_manager')
    def test_resolve_work_item_type_id_name_not_found(self, mock_manager):
        """Test resolving unknown type name."""
        manager = Mock()
        manager.get_type_id.return_value = None
        mock_manager.return_value = manager

        with pytest.raises(GitLabAPIError) as exc_info:
            _resolve_work_item_type_id("UNKNOWN_TYPE")

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Unknown work item type: UNKNOWN_TYPE" in str(exc_info.value)

    def test_build_create_input_project_context(self):
        """Test building create input with project context."""
        input_model = CreateWorkItemInput(
            work_item_type_id="gid://gitlab/WorkItems::Type/2",
            project_path="group/test-project",
            title="Test Issue",
            description="Test description",
            confidential=True
        )
        resolved_type_id = "gid://gitlab/WorkItems::Type/2"

        result = _build_create_input(input_model, resolved_type_id)

        expected = {
            "workItemTypeId": "gid://gitlab/WorkItems::Type/2",
            "title": "Test Issue",
            "projectPath": "group/test-project",
            "description": "Test description",
            "confidential": True
        }
        assert result == expected

    def test_build_create_input_namespace_context(self):
        """Test building create input with namespace context."""
        input_model = CreateWorkItemInput(
            work_item_type_id="gid://gitlab/WorkItems::Type/7",
            namespace_path="group",
            title="Test Epic"
        )
        resolved_type_id = "gid://gitlab/WorkItems::Type/7"

        result = _build_create_input(input_model, resolved_type_id)

        expected = {
            "workItemTypeId": "gid://gitlab/WorkItems::Type/7",
            "title": "Test Epic",
            "namespacePath": "group"
        }
        assert result == expected

    def test_build_create_input_missing_context(self):
        """Test building create input without context."""
        input_model = CreateWorkItemInput(
            work_item_type_id="gid://gitlab/WorkItems::Type/2",
            title="Orphaned Issue"
        )
        resolved_type_id = "gid://gitlab/WorkItems::Type/2"

        with pytest.raises(GitLabAPIError) as exc_info:
            _build_create_input(input_model, resolved_type_id)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Either project_path or namespace_path must be provided" in str(exc_info.value)

    def test_build_create_input_optional_fields(self):
        """Test building create input with minimal required fields."""
        input_model = CreateWorkItemInput(
            work_item_type_id="gid://gitlab/WorkItems::Type/2",
            project_path="group/test-project",
            title="Minimal Issue"
        )
        resolved_type_id = "gid://gitlab/WorkItems::Type/2"

        result = _build_create_input(input_model, resolved_type_id)

        expected = {
            "workItemTypeId": "gid://gitlab/WorkItems::Type/2",
            "title": "Minimal Issue",
            "projectPath": "group/test-project"
        }
        assert result == expected

    def test_process_create_result_success(self):
        """Test processing successful create result."""
        result = {
            "workItemCreate": {
                "workItem": {
                    "id": "gid://gitlab/WorkItem/123",
                    "title": "Test Issue"
                },
                "errors": []
            }
        }

        work_item = _process_create_result(result)
        assert work_item["id"] == "gid://gitlab/WorkItem/123"
        assert work_item["title"] == "Test Issue"

    def test_process_create_result_with_errors(self):
        """Test processing create result with errors."""
        result = {
            "workItemCreate": {
                "workItem": None,
                "errors": ["Title can't be blank", "Invalid type"]
            }
        }

        with pytest.raises(GitLabAPIError) as exc_info:
            _process_create_result(result)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Title can't be blank; Invalid type" in str(exc_info.value)

    def test_process_create_result_no_data(self):
        """Test processing create result with no work item data."""
        result = {
            "workItemCreate": {
                "workItem": None,
                "errors": []
            }
        }

        with pytest.raises(GitLabAPIError) as exc_info:
            _process_create_result(result)

        assert exc_info.value.error_type == GitLabErrorType.REQUEST_FAILED
        assert "Work item creation returned no data" in str(exc_info.value)
