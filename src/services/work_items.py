"""Work Items service for GitLab GraphQL API.

This module provides functions for managing Work Items using GitLab's
modern GraphQL API. Work Items are the unified way to handle epics,
issues, tasks, requirements, and other work tracking entities.

This replaces the deprecated REST API for epics and provides enhanced
functionality for issues through the widget-based architecture.
"""

from typing import Any

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.graphql_client import get_graphql_client
from src.schemas.work_items import (
    CreateWorkItemInput,
    DeleteWorkItemInput,
    GetWorkItemInput,
    GitLabWorkItem,
    ListWorkItemsInput,
    UpdateWorkItemInput,
)

# GraphQL Queries and Mutations

GET_WORK_ITEM_QUERY = """
query getWorkItem($id: WorkItemID!) {
  workItem(id: $id) {
    id
    iid
    title
    state
    confidential
    createdAt
    updatedAt
    closedAt
    author {
      id
      name
      username
      webUrl
    }
    project {
      id
      name
      fullPath
    }
    namespace {
      id
      name
      fullPath
    }
    workItemType {
      id
      name
    }
    webUrl
    reference
    widgets {
      type
      ... on WorkItemWidgetAssignees {
        assignees {
          nodes {
            id
            name
            username
            webUrl
          }
        }
      }
      ... on WorkItemWidgetHierarchy {
        parent {
          id
          iid
          title
          webUrl
        }
        children {
          nodes {
            id
            iid
            title
            webUrl
            workItemType {
              name
            }
          }
        }
      }
      ... on WorkItemWidgetLabels {
        labels {
          nodes {
            id
            title
            color
            description
          }
        }
      }
      ... on WorkItemWidgetMilestone {
        milestone {
          id
          title
          description
          state
        }
      }
      ... on WorkItemWidgetIteration {
        iteration {
          id
          title
          description
          state
          webUrl
        }
      }
      ... on WorkItemWidgetStartAndDueDate {
        startDate
        dueDate
      }
      ... on WorkItemWidgetDescription {
        description
        descriptionHtml
      }
      ... on WorkItemWidgetProgress {
        progress
      }
      ... on WorkItemWidgetHealthStatus {
        healthStatus
      }
      ... on WorkItemWidgetWeight {
        weight
      }
    }
  }
}
"""

GET_WORK_ITEM_BY_IID_QUERY = """
query getWorkItemByIid($projectPath: ID!, $iid: String!) {
  project(fullPath: $projectPath) {
    workItems(iid: $iid, first: 1) {
      nodes {
      id
      iid
      title
      state
      confidential
      createdAt
      updatedAt
      closedAt
      author {
        id
        name
        username
        webUrl
      }
      project {
        id
        name
        fullPath
      }
      workItemType {
        id
        name
      }
      webUrl
      reference
      widgets {
        type
        ... on WorkItemWidgetAssignees {
          assignees {
            nodes {
              id
              name
              username
              webUrl
            }
          }
        }
        ... on WorkItemWidgetHierarchy {
          parent {
            id
            iid
            title
            webUrl
          }
          children {
            nodes {
              id
              iid
              title
              webUrl
              workItemType {
                name
              }
            }
          }
        }
        ... on WorkItemWidgetLabels {
          labels {
            nodes {
              id
              title
              color
              description
            }
          }
        }
        ... on WorkItemWidgetMilestone {
          milestone {
            id
            title
            description
            state
          }
        }
        ... on WorkItemWidgetIteration {
          iteration {
            id
            title
            description
            state
            webUrl
          }
        }
        ... on WorkItemWidgetStartAndDueDate {
          startDate
          dueDate
        }
        ... on WorkItemWidgetDescription {
          description
          descriptionHtml
        }
        ... on WorkItemWidgetProgress {
          progress
        }
        ... on WorkItemWidgetHealthStatus {
          healthStatus
        }
        ... on WorkItemWidgetWeight {
          weight
        }
      }
      }
    }
  }
}
"""

LIST_PROJECT_WORK_ITEMS_QUERY = """
query listProjectWorkItems(
  $projectPath: ID!
  $types: [IssueType!]
  $state: IssuableState
  $search: String
  $sort: WorkItemSort
  $first: Int
  $after: String
) {
  project(fullPath: $projectPath) {
    workItems(
      types: $types
      state: $state
      search: $search
      sort: $sort
      first: $first
      after: $after
    ) {
      nodes {
        id
        iid
        title
        state
        workItemType {
          id
          name
        }
        createdAt
        updatedAt
        author {
          name
          username
        }
        webUrl
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

LIST_GROUP_WORK_ITEMS_QUERY = """
query listGroupWorkItems(
  $groupPath: ID!
  $types: [IssueType!]
  $state: IssuableState
  $search: String
  $sort: WorkItemSort
  $first: Int
  $after: String
) {
  group(fullPath: $groupPath) {
    workItems(
      types: $types
      state: $state
      search: $search
      sort: $sort
      first: $first
      after: $after
    ) {
      nodes {
        id
        iid
        title
        state
        workItemType {
          id
          name
        }
        createdAt
        updatedAt
        author {
          name
          username
        }
        webUrl
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
}
"""

CREATE_WORK_ITEM_MUTATION = """
mutation createWorkItem(
  $input: WorkItemCreateInput!
) {
  workItemCreate(input: $input) {
    workItem {
      id
      iid
      title
      state
      workItemType {
        id
        name
      }
      createdAt
      updatedAt
      author {
        id
        name
        username
        webUrl
      }
      project {
        id
        name
        fullPath
      }
      namespace {
        id
        name
        fullPath
      }
      webUrl
      reference
      widgets {
        type
        ... on WorkItemWidgetAssignees {
          assignees {
            nodes {
              id
              name
              username
              webUrl
            }
          }
        }
        ... on WorkItemWidgetHierarchy {
          parent {
            id
            iid
            title
            webUrl
          }
        }
        ... on WorkItemWidgetLabels {
          labels {
            nodes {
              id
              title
              color
            }
          }
        }
        ... on WorkItemWidgetDescription {
          description
        }
      }
    }
    errors
  }
}
"""

UPDATE_WORK_ITEM_MUTATION = """
mutation updateWorkItem(
  $input: WorkItemUpdateInput!
) {
  workItemUpdate(input: $input) {
    workItem {
      id
      iid
      title
      state
      confidential
      createdAt
      updatedAt
      closedAt
      author {
        id
        name
        username
        webUrl
      }
      project {
        id
        name
        fullPath
      }
      namespace {
        id
        name
        fullPath
      }
      workItemType {
        id
        name
      }
      webUrl
      reference
      widgets {
        type
        ... on WorkItemWidgetAssignees {
          assignees {
            nodes {
              id
              name
              username
              webUrl
            }
          }
        }
        ... on WorkItemWidgetHierarchy {
          parent {
            id
            iid
            title
            webUrl
          }
          children {
            nodes {
              id
              iid
              title
              webUrl
            }
          }
        }
        ... on WorkItemWidgetLabels {
          labels {
            nodes {
              id
              title
              color
            }
          }
        }
        ... on WorkItemWidgetMilestone {
          milestone {
            id
            title
            description
            state
          }
        }
        ... on WorkItemWidgetIteration {
          iteration {
            id
            title
            description
            state
            webUrl
          }
        }
        ... on WorkItemWidgetStartAndDueDate {
          startDate
          dueDate
        }
        ... on WorkItemWidgetDescription {
          description
          descriptionHtml
        }
        ... on WorkItemWidgetProgress {
          progress
        }
        ... on WorkItemWidgetHealthStatus {
          healthStatus
        }
        ... on WorkItemWidgetWeight {
          weight
        }
      }
    }
    errors
  }
}
"""

DELETE_WORK_ITEM_MUTATION = """
mutation deleteWorkItem(
  $input: WorkItemDeleteInput!
) {
  workItemDelete(input: $input) {
    project {
      id
    }
    errors
  }
}
"""


# Service Functions

async def get_work_item(input_model: GetWorkItemInput) -> GitLabWorkItem:
    """Get a specific Work Item by ID or IID.

    Retrieves a work item using either its global ID or internal ID within a project.

    Args:
        input_model: Work item identification parameters

    Returns:
        GitLabWorkItem: The work item with all widgets

    Raises:
        GitLabAPIError: If work item not found or query fails
    """
    try:
        if input_model.id:
            # Get by global ID
            variables = {"id": input_model.id}
            result = await get_graphql_client().query(GET_WORK_ITEM_QUERY, variables)

            if not result.get("workItem"):
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Work item {input_model.id} not found"}
                )

            return GitLabWorkItem.model_validate(result["workItem"])

        elif input_model.iid and input_model.project_path:
            # Get by IID within project
            variables = {
                "projectPath": input_model.project_path,
                "iid": str(input_model.iid)
            }
            result = await get_graphql_client().query(GET_WORK_ITEM_BY_IID_QUERY, variables)

            work_items = result.get("project", {}).get("workItems", {}).get("nodes", [])
            if not work_items:
                raise GitLabAPIError(
                    GitLabErrorType.NOT_FOUND,
                    {"message": f"Work item {input_model.iid} not found in project {input_model.project_path}"}
                )

            return GitLabWorkItem.model_validate(work_items[0])

        else:
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": "Either 'id' or both 'iid' and 'project_path' must be provided"}
            )

    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Unexpected error getting work item: {exc!s}",
                "operation": "get_work_item",
            }
        ) from exc


async def list_work_items(input_model: ListWorkItemsInput) -> list[GitLabWorkItem]:
    """List Work Items from a project or group.

    Retrieves work items with optional filtering by type, state, and search terms.

    Args:
        input_model: Listing parameters with filters

    Returns:
        List[GitLabWorkItem]: List of work items matching criteria

    Raises:
        GitLabAPIError: If listing fails
    """
    try:
        # Convert state enum to GraphQL API format
        state_value = None
        if input_model.state:
            # API expects 'opened'/'closed' in queries but returns 'OPEN'/'CLOSED' in responses
            if input_model.state.value == "OPEN":
                state_value = "opened"
            elif input_model.state.value == "CLOSED":
                state_value = "closed"
            else:
                state_value = input_model.state.value
        
        variables = {
            "types": [wt.value for wt in input_model.work_item_types] if input_model.work_item_types else None,
            "state": state_value,
            "search": input_model.search,
            "sort": input_model.sort,
            "first": input_model.first,
            "after": input_model.after,
        }
        
        # Use the appropriate query and variables based on search context
        if input_model.project_path:
            variables["projectPath"] = input_model.project_path
            result = await get_graphql_client().query(LIST_PROJECT_WORK_ITEMS_QUERY, variables)
            if result is None:
                raise GitLabAPIError(
                    GitLabErrorType.REQUEST_FAILED,
                    {"message": f"Project '{input_model.project_path}' not found or has no work items access"}
                )
            work_items_data = result.get("project", {}).get("workItems", {}).get("nodes", [])
        elif input_model.namespace_path:
            variables["groupPath"] = input_model.namespace_path
            result = await get_graphql_client().query(LIST_GROUP_WORK_ITEMS_QUERY, variables)
            if result is None:
                raise GitLabAPIError(
                    GitLabErrorType.REQUEST_FAILED,
                    {"message": f"Group '{input_model.namespace_path}' not found or has no work items access"}
                )
            work_items_data = result.get("group", {}).get("workItems", {}).get("nodes", [])
        else:
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": "Either project_path or namespace_path must be provided"}
            )

        return [GitLabWorkItem.model_validate(item) for item in work_items_data]

    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Unexpected error listing work items: {exc!s}",
                "operation": "list_work_items",
            }
        ) from exc


async def create_work_item(input_model: CreateWorkItemInput) -> GitLabWorkItem:
    """Create a new Work Item.

    Creates a work item with the specified type and properties.

    Args:
        input_model: Work item creation parameters

    Returns:
        GitLabWorkItem: The created work item

    Raises:
        GitLabAPIError: If creation fails
    """
    try:
        # Build the GraphQL input
        create_input = {
            "workItemTypeId": input_model.work_item_type_id,
            "title": input_model.title,
        }

        # Add context path
        if input_model.project_path:
            create_input["projectPath"] = input_model.project_path
        elif input_model.namespace_path:
            create_input["namespacePath"] = input_model.namespace_path
        else:
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": "Either project_path or namespace_path must be provided"}
            )

        # Add optional basic fields
        if input_model.description:
            create_input["description"] = input_model.description
        if input_model.confidential is not None:
            create_input["confidential"] = input_model.confidential

        # Note: Widget-based operations (assignees, labels, hierarchy, etc.) 
        # are not yet implemented in this basic creation function.
        # They would require additional GraphQL mutation operations or
        # more complex input structure. Current implementation supports
        # basic work item creation with core fields only.

        variables = {"input": create_input}
        result = await get_graphql_client().mutation(CREATE_WORK_ITEM_MUTATION, variables)

        if result.get("workItemCreate", {}).get("errors"):
            errors = result["workItemCreate"]["errors"]
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": f"Work item creation failed: {'; '.join(errors)}"}
            )

        work_item_data = result.get("workItemCreate", {}).get("workItem")
        if not work_item_data:
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": "Work item creation returned no data"}
            )

        return GitLabWorkItem.model_validate(work_item_data)

    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Unexpected error creating work item: {exc!s}",
                "operation": "create_work_item",
            }
        ) from exc


async def update_work_item(input_model: UpdateWorkItemInput) -> GitLabWorkItem:
    """Update an existing Work Item.

    Updates work item properties using widget-based operations.

    Args:
        input_model: Work item update parameters

    Returns:
        GitLabWorkItem: The updated work item

    Raises:
        GitLabAPIError: If update fails
    """
    try:
        # Build the GraphQL input
        update_input = {"id": input_model.id}

        # Add basic fields
        if input_model.title:
            update_input["title"] = input_model.title
        if input_model.state_event:
            # Convert state event to GraphQL API format (uppercase)
            state_event = input_model.state_event.upper()
            update_input["stateEvent"] = state_event
        if input_model.confidential is not None:
            update_input["confidential"] = input_model.confidential

        # TODO: Add widget operations for more complex updates
        # This would include assignees, labels, hierarchy, etc.

        variables = {"input": update_input}
        result = await get_graphql_client().mutation(UPDATE_WORK_ITEM_MUTATION, variables)

        if result.get("workItemUpdate", {}).get("errors"):
            errors = result["workItemUpdate"]["errors"]
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": f"Work item update failed: {'; '.join(errors)}"}
            )

        work_item_data = result.get("workItemUpdate", {}).get("workItem")
        if not work_item_data:
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": "Work item update returned no data"}
            )

        return GitLabWorkItem.model_validate(work_item_data)

    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Unexpected error updating work item: {exc!s}",
                "operation": "update_work_item",
            }
        ) from exc


async def delete_work_item(input_model: DeleteWorkItemInput) -> dict[str, Any]:
    """Delete a Work Item.

    WARNING: This permanently deletes the work item and cannot be undone.

    Args:
        input_model: Work item deletion parameters

    Returns:
        Dict: Deletion confirmation

    Raises:
        GitLabAPIError: If deletion fails
    """
    try:
        variables = {"input": {"id": input_model.id}}
        result = await get_graphql_client().mutation(DELETE_WORK_ITEM_MUTATION, variables)

        if result.get("workItemDelete", {}).get("errors"):
            errors = result["workItemDelete"]["errors"]
            raise GitLabAPIError(
                GitLabErrorType.REQUEST_FAILED,
                {"message": f"Work item deletion failed: {'; '.join(errors)}"}
            )

        return {"message": "Work item deleted successfully", "id": input_model.id}

    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": f"Unexpected error deleting work item: {exc!s}",
                "operation": "delete_work_item",
            }
        ) from exc
