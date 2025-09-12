"""Work Items schemas for GitLab GraphQL API.

This module defines Pydantic models for GitLab's Work Items functionality
using the modern GraphQL API. Work Items are the unified way to handle
epics, issues, tasks, requirements, and other work tracking entities.

CRITICAL: Field ordering is optimized for Claude Code UX - ID and title
fields are positioned first for optimal display in collapsed views.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .base import GitLabResponseBase


class WorkItemType(str, Enum):
    """Work Item types in GitLab.

    Different types of work items available in GitLab's unified system.
    """
    EPIC = "EPIC"
    ISSUE = "ISSUE"
    TASK = "TASK"
    OBJECTIVE = "OBJECTIVE"
    KEY_RESULT = "KEY_RESULT"
    INCIDENT = "INCIDENT"
    TEST_CASE = "TEST_CASE"
    REQUIREMENT = "REQUIREMENT"


class WorkItemState(str, Enum):
    """Work Item states.

    Note: GraphQL API inconsistency - queries expect 'opened'/'closed'
    but responses return 'OPEN'/'CLOSED'. We handle both.
    """
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class WorkItemWidget(BaseModel):
    """Base widget model for Work Items.

    Work Items use a widget-based architecture where different
    functionality is provided through widgets.
    """
    type: str


class WorkItemAssigneeWidget(WorkItemWidget):
    """Assignees widget for Work Items."""
    type: str = "ASSIGNEES"
    assignees: list[dict[str, Any]] = Field(default_factory=list)


class WorkItemHierarchyWidget(WorkItemWidget):
    """Hierarchy widget for parent/child relationships."""
    type: str = "HIERARCHY"
    parent: dict[str, Any] | None = None
    children: list[dict[str, Any]] = Field(default_factory=list)


class WorkItemLabelsWidget(WorkItemWidget):
    """Labels widget for Work Items."""
    type: str = "LABELS"
    labels: list[dict[str, Any]] = Field(default_factory=list)


class WorkItemMilestoneWidget(WorkItemWidget):
    """Milestone widget for Work Items."""
    type: str = "MILESTONE"
    milestone: dict[str, Any] | None = None


class WorkItemIterationWidget(WorkItemWidget):
    """Iteration widget for Work Items."""
    type: str = "ITERATION"
    iteration: dict[str, Any] | None = None


class WorkItemDatesWidget(WorkItemWidget):
    """Dates widget for start and due dates."""
    type: str = "START_AND_DUE_DATE"
    start_date: str | None = None
    due_date: str | None = None


class WorkItemDescriptionWidget(WorkItemWidget):
    """Description widget for Work Items."""
    type: str = "DESCRIPTION"
    description: str | None = None


class WorkItemNotesWidget(WorkItemWidget):
    """Notes/comments widget for Work Items."""
    type: str = "NOTES"
    # Notes are typically fetched separately


class WorkItemProgressWidget(WorkItemWidget):
    """Progress widget for objectives and key results."""
    type: str = "PROGRESS"
    progress: int | None = None  # Percentage 0-100


class WorkItemHealthStatusWidget(WorkItemWidget):
    """Health status widget (Ultimate tier)."""
    type: str = "HEALTH_STATUS"
    health_status: str | None = None  # ON_TRACK, NEEDS_ATTENTION, AT_RISK


class WorkItemWeightWidget(WorkItemWidget):
    """Weight widget for estimation."""
    type: str = "WEIGHT"
    weight: int | None = None


class GitLabWorkItem(GitLabResponseBase):
    """GitLab Work Item model with optimized field ordering for Claude Code UX.

    CRITICAL: iid and title are positioned as first fields for optimal
    display in Claude Code collapsed views. This ensures users see:
    ▶ WorkItem: {iid: 42, title: "Feature X", ...}

    Instead of uninformative:
    ▶ WorkItem: {id: "gid://gitlab/WorkItem/123", state: "OPEN", ...}

    Attributes:
        iid: Work Item internal ID (FIRST field for UX).
        title: Work Item title (SECOND field for UX).
        id: Global Work Item ID (GraphQL global ID format).
        state: Work Item state (OPEN/CLOSED).
        work_item_type: Type of work item (EPIC, ISSUE, TASK, etc.).
        project: Project information (for project-scoped items).
        namespace: Namespace information (for group-scoped items like epics).
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        closed_at: Closure timestamp (if applicable).
        author: User who created the work item.
        web_url: Web URL to view work item.
        widgets: List of widgets providing functionality.
        confidential: Whether the work item is confidential.
        reference: Reference formats for the work item.
    """

    # CRITICAL: These MUST be first two fields for Claude Code UX
    iid: int = Field(..., description="Work Item internal ID (shows first in Claude Code)")
    title: str = Field(..., description="Work Item title (shows second in Claude Code)")

    # Core identification fields
    id: str = Field(..., description="Global Work Item ID (GraphQL format)")
    state: WorkItemState
    work_item_type: dict[str, Any] = Field(..., alias="workItemType")

    # Context fields
    project: dict[str, Any] | None = None
    namespace: dict[str, Any] | None = None

    # Timestamps
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    closed_at: datetime | None = Field(None, alias="closedAt")

    # User relationships
    author: dict[str, Any]

    # URLs and references
    web_url: str = Field(..., alias="webUrl")
    reference: str | None = None

    # Widget-based functionality
    widgets: list[WorkItemWidget] = Field(default_factory=list)

    # Additional properties
    confidential: bool = False

    def get_widget(self, widget_type: str) -> WorkItemWidget | None:
        """Get a specific widget by type.

        Args:
            widget_type: Widget type to find (e.g., 'ASSIGNEES', 'HIERARCHY')

        Returns:
            The widget if found, None otherwise
        """
        for widget in self.widgets:
            if widget.type == widget_type:
                return widget
        return None

    def get_assignees(self) -> list[dict[str, Any]]:
        """Get assignees from the assignees widget."""
        assignee_widget = self.get_widget("ASSIGNEES")
        if isinstance(assignee_widget, WorkItemAssigneeWidget):
            return assignee_widget.assignees
        return []

    def get_labels(self) -> list[dict[str, Any]]:
        """Get labels from the labels widget."""
        labels_widget = self.get_widget("LABELS")
        if isinstance(labels_widget, WorkItemLabelsWidget):
            return labels_widget.labels
        return []

    def get_parent(self) -> dict[str, Any] | None:
        """Get parent work item from hierarchy widget."""
        hierarchy_widget = self.get_widget("HIERARCHY")
        if isinstance(hierarchy_widget, WorkItemHierarchyWidget):
            return hierarchy_widget.parent
        return None

    def get_children(self) -> list[dict[str, Any]]:
        """Get child work items from hierarchy widget."""
        hierarchy_widget = self.get_widget("HIERARCHY")
        if isinstance(hierarchy_widget, WorkItemHierarchyWidget):
            return hierarchy_widget.children
        return []


class CreateWorkItemInput(BaseModel):
    """Input model for creating Work Items via GraphQL.

    Creates new work items using GitLab's unified Work Items API.
    This replaces the old REST API endpoints for epics and issues.

    Attributes:
        project_path: Full path to project (for project-scoped items like issues).
                     Examples: 'gitlab-org/gitlab', 'my-group/my-project'
        namespace_path: Full path to group/namespace (for group-scoped items like epics).
                       Examples: 'gitlab-org', 'my-group/subgroup'
        work_item_type_id: ID of work item type (EPIC, ISSUE, TASK, etc.).
        title: Title of the work item (REQUIRED).
        description: Description of the work item (OPTIONAL).
        confidential: Whether the work item should be confidential.
        hierarchy_widget: Parent work item for hierarchy.
        assignees_widget: List of user IDs to assign.
        labels_widget: List of label IDs or names.
        milestone_widget: Milestone ID to assign.
        iteration_widget: Iteration ID to assign.
        dates_widget: Start and due dates.
    """

    # Context - either project_path OR namespace_path required
    project_path: str | None = Field(None, description="Project path for project-scoped items")
    namespace_path: str | None = Field(None, description="Namespace path for group-scoped items")

    # Core fields
    work_item_type_id: str = Field(..., description="Work item type ID")
    title: str = Field(..., description="Work item title")
    description: str | None = Field(None, description="Work item description")
    confidential: bool | None = Field(None, description="Whether work item is confidential")

    # Widget inputs (optional)
    hierarchy_widget: dict[str, Any] | None = Field(None, description="Hierarchy widget input")
    assignees_widget: list[str] | None = Field(None, description="Assignee user IDs")
    labels_widget: list[str] | None = Field(None, description="Label IDs or names")
    milestone_widget: str | None = Field(None, description="Milestone ID")
    iteration_widget: str | None = Field(None, description="Iteration ID")
    dates_widget: dict[str, str] | None = Field(None, description="Start and due dates")


class AssigneeWidgetOperation(BaseModel):
    """Assignees widget operation for work items.

    Supports adding, removing, or replacing assignees.
    """
    user_ids: list[str] = Field(..., description="List of GitLab user IDs (gid://gitlab/User/123 format)")


class LabelWidgetOperation(BaseModel):
    """Labels widget operation for work items.

    Supports adding or removing labels by ID or name.
    """
    add_label_ids: list[str] | None = Field(None, description="Label IDs to add (gid://gitlab/ProjectLabel/123 format)")
    remove_label_ids: list[str] | None = Field(None, description="Label IDs to remove")


class HierarchyWidgetOperation(BaseModel):
    """Hierarchy widget operation for work items.

    Sets or clears parent-child relationships.
    """
    parent_id: str | None = Field(None, description="Parent work item ID (gid://gitlab/WorkItem/123 format), null to clear")


class MilestoneWidgetOperation(BaseModel):
    """Milestone widget operation for work items.

    Associates or clears milestone assignment.
    """
    milestone_id: str | None = Field(None, description="Milestone ID (gid://gitlab/Milestone/123 format), null to clear")


class IterationWidgetOperation(BaseModel):
    """Iteration widget operation for work items.

    Associates or clears iteration assignment.
    """
    iteration_id: str | None = Field(None, description="Iteration ID (gid://gitlab/Iteration/123 format), null to clear")


class DatesWidgetOperation(BaseModel):
    """Dates widget operation for work items.

    Sets or clears start and due dates.
    """
    start_date: str | None = Field(None, description="Start date (YYYY-MM-DD format), null to clear")
    due_date: str | None = Field(None, description="Due date (YYYY-MM-DD format), null to clear")


class UpdateWorkItemInput(BaseModel):
    """Input model for updating Work Items via GraphQL.

    Updates existing work items using widget-based operations.

    Attributes:
        id: Global Work Item ID (GraphQL format) (REQUIRED).
        title: New title for the work item.
        state_event: State change action ('CLOSE' or 'REOPEN').
        confidential: Change confidentiality status.

        # Widget operations (structured)
        assignees_widget: Assignee operations.
        labels_widget: Label operations.
        hierarchy_widget: Hierarchy operations.
        milestone_widget: Milestone operations.
        iteration_widget: Iteration operations.
        dates_widget: Date operations.
        description_widget: Description operations.
    """

    id: str = Field(..., description="Global Work Item ID")
    title: str | None = Field(None, description="New title")
    state_event: str | None = Field(None, description="State change action")
    confidential: bool | None = Field(None, description="Change confidentiality")

    # Widget update operations (structured)
    assignees_widget: AssigneeWidgetOperation | None = Field(None, description="Assignee widget operations")
    labels_widget: LabelWidgetOperation | None = Field(None, description="Labels widget operations")
    hierarchy_widget: HierarchyWidgetOperation | None = Field(None, description="Hierarchy widget operations")
    milestone_widget: MilestoneWidgetOperation | None = Field(None, description="Milestone widget operations")
    iteration_widget: IterationWidgetOperation | None = Field(None, description="Iteration widget operations")
    dates_widget: DatesWidgetOperation | None = Field(None, description="Dates widget operations")
    description_widget: dict[str, Any] | None = Field(None, description="Description widget operations")


class DeleteWorkItemInput(BaseModel):
    """Input model for deleting Work Items.

    WARNING: This permanently deletes the work item and cannot be undone.

    Attributes:
        id: Global Work Item ID (GraphQL format) (REQUIRED).
    """

    id: str = Field(..., description="Global Work Item ID to delete")


class GetWorkItemInput(BaseModel):
    """Input model for getting a specific Work Item.

    Attributes:
        id: Global Work Item ID (GraphQL format) (REQUIRED).
        iid: Work Item internal ID (alternative to id).
        project_path: Project path (required when using iid).
        namespace_path: Namespace path (required when using iid for group items).
    """

    id: str | None = Field(None, description="Global Work Item ID")
    iid: int | None = Field(None, description="Work Item internal ID")
    project_path: str | None = Field(None, description="Project path (for iid lookup)")
    namespace_path: str | None = Field(None, description="Namespace path (for group items)")


class ListWorkItemsInput(BaseModel):
    """Input model for listing Work Items.

    Attributes:
        project_path: Project path to list items from.
        namespace_path: Namespace path to list items from.
        work_item_types: List of work item types to filter by.
        state: State filter (OPEN, CLOSED).
        search: Search term for title/description.
        sort: Sort field.
        sort_order: Sort direction (ASC, DESC).
        first: Number of items to return (pagination).
        after: Cursor for pagination.
    """

    project_path: str | None = Field(None, description="Project path")
    namespace_path: str | None = Field(None, description="Namespace path")
    work_item_types: list[WorkItemType] | None = Field(None, description="Work item types to filter")
    state: WorkItemState | None = Field(None, description="State filter")
    search: str | None = Field(None, description="Search term")
    sort: str | None = Field(None, description="Sort field")
    sort_order: str | None = Field(None, description="Sort direction")
    first: int | None = Field(20, description="Number of items to return")
    after: str | None = Field(None, description="Cursor for pagination")


# Work Item Type definitions for easy reference
WORK_ITEM_TYPES = {
    "EPIC": "gid://gitlab/WorkItems::Type/1",  # These IDs are typically instance-specific
    "ISSUE": "gid://gitlab/WorkItems::Type/2",
    "TASK": "gid://gitlab/WorkItems::Type/3",
    "INCIDENT": "gid://gitlab/WorkItems::Type/4",
    "TEST_CASE": "gid://gitlab/WorkItems::Type/5",
    "REQUIREMENT": "gid://gitlab/WorkItems::Type/6",
    "OBJECTIVE": "gid://gitlab/WorkItems::Type/7",
    "KEY_RESULT": "gid://gitlab/WorkItems::Type/8",
}
