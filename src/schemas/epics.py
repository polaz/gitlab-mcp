"""Epic schemas for GitLab API.

This module defines Pydantic models for GitLab epics functionality.
Epics are available in GitLab Premium and Ultimate tiers only.
"""

from typing import Any

from pydantic import BaseModel, Field

from .base import GitLabResponseBase


class GitLabEpic(GitLabResponseBase):
    """GitLab epic model with comprehensive field support.

    Represents an epic from GitLab API responses.
    Epics are high-level containers for issues and child epics.

    Attributes:
        id: Epic ID (unique across GitLab instance).
        iid: Epic internal ID (unique within group).
        title: Epic title/name.
        description: Epic description (supports Markdown).
        state: Epic state ('opened' or 'closed').
        group_id: ID of the group that owns this epic.
        parent_id: ID of parent epic (for nested epics).
        author: User who created the epic.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        start_date: Epic start date (YYYY-MM-DD format).
        due_date: Epic due date (YYYY-MM-DD format).
        end_date: Epic end date (YYYY-MM-DD format).
        labels: List of labels applied to epic.
        upvotes: Number of upvotes.
        downvotes: Number of downvotes.
        color: Epic color code.
        text_color: Epic text color.
        web_url: Web URL to view epic in GitLab UI.
        references: Epic reference information.
        relative_position: Epic position for ordering.
        confidential: Whether epic is confidential.
        _links: Related links for the epic.
    """

    id: int
    iid: int
    title: str
    description: str | None = None
    state: str
    group_id: int
    parent_id: int | None = None
    author: dict[str, Any]
    created_at: str
    updated_at: str
    start_date: str | None = None
    due_date: str | None = None
    end_date: str | None = None
    labels: list[str] = Field(default_factory=list)
    upvotes: int = 0
    downvotes: int = 0
    color: str | None = None
    text_color: str | None = None
    web_url: str
    references: dict[str, Any] | None = None
    relative_position: int | None = None
    confidential: bool = False
    links: dict[str, Any] | None = Field(None, alias="_links")


class CreateEpicInput(BaseModel):
    """Input model for creating a new epic in a GitLab group.

    Creates a new epic within the specified group.
    Epics are containers for organizing related issues and child epics.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        title: The title of the epic (REQUIRED).
               Should be descriptive and concise.
               Examples: 'User Authentication System', 'Q1 2024 Features'
        description: Detailed description of the epic (OPTIONAL).
                    Supports GitLab Flavored Markdown.
                    Examples: 'Implement OAuth2 authentication with SSO support'
        labels: List of label names to apply to the epic (OPTIONAL).
               Labels must exist in the group.
               Examples: ['backend', 'security'], ['Q1', 'high-priority']
        start_date: Epic start date in YYYY-MM-DD format (OPTIONAL).
                   Examples: '2024-01-01', '2024-03-15'
        due_date: Epic due date in YYYY-MM-DD format (OPTIONAL).
                 Examples: '2024-03-31', '2024-12-31'
        confidential: Whether the epic should be confidential (OPTIONAL).
                     true = only group members can see, false = respects group visibility
        parent_id: ID of parent epic for nested epics (OPTIONAL).
                  Use for creating epic hierarchies.
                  Examples: 42, 123
        color: Epic color code for visual organization (OPTIONAL).
              Examples: '#FF5733', '#33FF57'

    Example Usage:
        - Basic epic: group_id='my-team', title='Authentication Epic'
        - Detailed epic: group_id='company/backend', title='API v2.0',
          description='Complete rewrite of REST API', labels=['backend', 'api']
        - Child epic: group_id='team', title='Login Feature', parent_id=42
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    title: str = Field(
        ...,
        description="The title of the epic"
    )
    description: str | None = Field(
        None,
        description="The description of the epic (supports Markdown)"
    )
    labels: list[str] | None = Field(
        None,
        description="List of label names to apply to the epic"
    )
    start_date: str | None = Field(
        None,
        description="Epic start date (YYYY-MM-DD format)"
    )
    due_date: str | None = Field(
        None,
        description="Epic due date (YYYY-MM-DD format)"
    )
    confidential: bool | None = Field(
        None,
        description="Whether the epic is confidential"
    )
    parent_id: int | None = Field(
        None,
        description="ID of parent epic for nested epics"
    )
    color: str | None = Field(
        None,
        description="Epic color code for visual organization"
    )


class UpdateEpicInput(BaseModel):
    """Input model for updating an existing epic in a GitLab group.

    Updates properties of an existing epic. Only provided fields will be changed.
    All fields are optional except group_id and epic_iid for identification.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        epic_iid: The internal epic ID within the group (REQUIRED).
                 This is the epic number shown in GitLab UI (e.g., &123).
                 Examples: 42, 15, 7
        title: New title for the epic (OPTIONAL).
              Examples: 'Updated Authentication System', 'Q2 2024 Features'
        description: New description for the epic (OPTIONAL).
                    Supports GitLab Flavored Markdown.
                    Pass empty string to clear description.
        state_event: Epic state change action (OPTIONAL).
                    Values: 'close' to close epic, 'reopen' to reopen
        labels: List of label names to replace existing labels (OPTIONAL).
               Replaces ALL existing labels.
               Examples: ['backend', 'security'], [] (to clear all labels)
        add_labels: List of label names to add to existing labels (OPTIONAL).
                   Keeps existing labels and adds these.
                   Examples: ['reviewed', 'approved']
        remove_labels: List of label names to remove from existing labels (OPTIONAL).
                      Examples: ['wip', 'needs-review']
        start_date: New start date in YYYY-MM-DD format (OPTIONAL).
                   Examples: '2024-02-01', null (to clear)
        due_date: New due date in YYYY-MM-DD format (OPTIONAL).
                 Examples: '2024-06-30', null (to clear)
        confidential: Change confidentiality status (OPTIONAL).
        parent_id: Change parent epic for epic hierarchy (OPTIONAL).
                  Set to null to remove from parent.
        color: Change epic color code (OPTIONAL).
              Examples: '#FF5733', null (to clear)

    Example Usage:
        - Update title: group_id='team', epic_iid=15, title='New Epic Title'
        - Close epic: group_id='team', epic_iid=15, state_event='close'
        - Add labels: group_id='team', epic_iid=15, add_labels=['completed']
        - Change dates: group_id='team', epic_iid=15, start_date='2024-01-01', due_date='2024-03-31'
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    epic_iid: int = Field(
        ...,
        description="The internal epic ID within the group"
    )
    title: str | None = Field(
        None,
        description="New title for the epic"
    )
    description: str | None = Field(
        None,
        description="New description for the epic (supports Markdown)"
    )
    state_event: str | None = Field(
        None,
        description="Epic state change action ('close' or 'reopen')"
    )
    labels: list[str] | None = Field(
        None,
        description="List of label names to replace existing labels"
    )
    add_labels: list[str] | None = Field(
        None,
        description="List of label names to add to existing labels"
    )
    remove_labels: list[str] | None = Field(
        None,
        description="List of label names to remove from existing labels"
    )
    start_date: str | None = Field(
        None,
        description="New start date (YYYY-MM-DD format)"
    )
    due_date: str | None = Field(
        None,
        description="New due date (YYYY-MM-DD format)"
    )
    confidential: bool | None = Field(
        None,
        description="Change confidentiality status"
    )
    parent_id: int | None = Field(
        None,
        description="Change parent epic ID (null to remove parent)"
    )
    color: str | None = Field(
        None,
        description="Change epic color code"
    )


class ListEpicsInput(BaseModel):
    """Input model for listing epics in a GitLab group.

    Retrieves a paginated list of epics from a specific group with optional filtering.
    Supports various filters to narrow down results.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        state: Filter epics by state (OPTIONAL).
              Values: 'opened', 'closed', 'all'
              Default: Returns all epics regardless of state.
        labels: Comma-separated list of label names to filter by (OPTIONAL).
               Examples: 'backend', 'backend,security', 'Q1'
               Only returns epics that have ALL specified labels.
        author_id: Filter epics by author user ID (OPTIONAL).
                  Examples: 42, 123
        author_username: Filter epics by author username (OPTIONAL).
                        Examples: 'john.doe', 'team-lead'
        search: Search epics by title and description (OPTIONAL).
               Examples: 'authentication', 'API v2', 'user management'
        sort: Sort field for results (OPTIONAL).
             Values: 'created_at', 'updated_at', 'title'
             Default: 'created_at'
        order_by: Sort order direction (OPTIONAL).
                 Values: 'asc', 'desc'
                 Default: 'desc' (newest first)
        created_after: Filter epics created after date (OPTIONAL).
                      ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ'
                      Examples: '2024-01-01T00:00:00Z'
        created_before: Filter epics created before date (OPTIONAL).
                       ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ'
        updated_after: Filter epics updated after date (OPTIONAL).
                      ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ'
        updated_before: Filter epics updated before date (OPTIONAL).
                       ISO 8601 format: 'YYYY-MM-DDTHH:MM:SSZ'
        include_ancestor_groups: Include epics from ancestor groups (OPTIONAL).
                                true = search parent groups too, false = only this group
        include_descendant_groups: Include epics from descendant groups (OPTIONAL).
                                  true = search child groups too, false = only this group
        page: Page number for pagination (starts at 1).
        per_page: Number of epics per page (1-100, default 20).

    Example Usage:
        - List all group epics: group_id='my-team'
        - Filter by state: group_id='team', state='opened'
        - Search epics: group_id='team', search='authentication'
        - Filter by labels: group_id='team', labels='backend,security'
        - Date filtering: group_id='team', created_after='2024-01-01T00:00:00Z'
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    state: str | None = Field(
        None,
        description="Filter epics by state ('opened', 'closed', 'all')"
    )
    labels: str | None = Field(
        None,
        description="Comma-separated list of label names to filter by"
    )
    author_id: int | None = Field(
        None,
        description="Filter epics by author user ID"
    )
    author_username: str | None = Field(
        None,
        description="Filter epics by author username"
    )
    search: str | None = Field(
        None,
        description="Search epics by title and description"
    )
    sort: str | None = Field(
        None,
        description="Sort field ('created_at', 'updated_at', 'title')"
    )
    order_by: str | None = Field(
        None,
        description="Sort order ('asc', 'desc')"
    )
    created_after: str | None = Field(
        None,
        description="Filter epics created after date (ISO 8601)"
    )
    created_before: str | None = Field(
        None,
        description="Filter epics created before date (ISO 8601)"
    )
    updated_after: str | None = Field(
        None,
        description="Filter epics updated after date (ISO 8601)"
    )
    updated_before: str | None = Field(
        None,
        description="Filter epics updated before date (ISO 8601)"
    )
    include_ancestor_groups: bool | None = Field(
        None,
        description="Include epics from ancestor groups"
    )
    include_descendant_groups: bool | None = Field(
        None,
        description="Include epics from descendant groups"
    )
    page: int = Field(
        1,
        description="Page number for pagination (starts at 1)"
    )
    per_page: int = Field(
        20,
        description="Number of epics per page (1-100)"
    )


class GetEpicInput(BaseModel):
    """Input model for getting a specific epic from a GitLab group.

    Retrieves detailed information about a specific epic by its internal ID.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        epic_iid: The internal epic ID within the group (REQUIRED).
                 This is the epic number shown in GitLab UI (e.g., &123).
                 Examples: 42, 15, 7

    Example Usage:
        - Get epic details: group_id='my-team', epic_iid=42
        - Get from subgroup: group_id='company/backend-team', epic_iid=15
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    epic_iid: int = Field(
        ...,
        description="The internal epic ID within the group"
    )


class DeleteEpicInput(BaseModel):
    """Input model for deleting an epic from a GitLab group.

    WARNING: This permanently deletes the epic and cannot be undone.
    All epic-issue associations will be removed.

    Attributes:
        group_id: The numeric ID OR path of the group (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        epic_iid: The internal epic ID within the group (REQUIRED).
                 This is the epic number shown in GitLab UI (e.g., &123).
                 Examples: 42, 15, 7

    Example Usage:
        - Delete epic: group_id='my-team', epic_iid=42
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    epic_iid: int = Field(
        ...,
        description="The internal epic ID within the group"
    )


class EpicIssueAssociation(BaseModel):
    """Epic-issue association model from GitLab API.

    Represents the relationship between an epic and an issue.
    """

    id: int
    epic: dict[str, Any]
    issue: dict[str, Any]
    relative_position: int | None = None


class AssignIssueToEpicInput(BaseModel):
    """Input model for assigning an issue to an epic.

    Creates an association between an issue and an epic.
    If the issue was previously assigned to another epic, it will be reassigned.

    Attributes:
        group_id: The numeric ID OR path of the group that owns the epic (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        epic_iid: The internal epic ID within the group (REQUIRED).
                 Examples: 42, 15, 7
        issue_id: The global issue ID (not issue_iid) (REQUIRED).
                 This is the numeric issue ID from the GitLab API.
                 Examples: 12345, 67890

    Example Usage:
        - Assign issue to epic: group_id='team', epic_iid=42, issue_id=12345
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    epic_iid: int = Field(
        ...,
        description="The internal epic ID within the group"
    )
    issue_id: int = Field(
        ...,
        description="The global issue ID to assign to the epic"
    )


class RemoveIssueFromEpicInput(BaseModel):
    """Input model for removing an issue from an epic.

    Removes the association between an issue and an epic.

    Attributes:
        group_id: The numeric ID OR path of the group that owns the epic (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        epic_iid: The internal epic ID within the group (REQUIRED).
                 Examples: 42, 15, 7
        epic_issue_id: The epic-issue association ID (REQUIRED).
                      This is the ID of the association, not the issue ID.
                      Get this from list_epic_issues response.
                      Examples: 54321, 98765

    Example Usage:
        - Remove issue from epic: group_id='team', epic_iid=42, epic_issue_id=54321
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    epic_iid: int = Field(
        ...,
        description="The internal epic ID within the group"
    )
    epic_issue_id: int = Field(
        ...,
        description="The epic-issue association ID"
    )


class ListEpicIssuesInput(BaseModel):
    """Input model for listing issues assigned to an epic.

    Retrieves all issues that are assigned to a specific epic.

    Attributes:
        group_id: The numeric ID OR path of the group that owns the epic (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        epic_iid: The internal epic ID within the group (REQUIRED).
                 Examples: 42, 15, 7

    Example Usage:
        - List epic issues: group_id='team', epic_iid=42
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    epic_iid: int = Field(
        ...,
        description="The internal epic ID within the group"
    )


class UpdateEpicIssueAssociationInput(BaseModel):
    """Input model for updating an epic-issue association.

    Updates the position/order of an issue within an epic.
    Useful for prioritizing issues within an epic.

    Attributes:
        group_id: The numeric ID OR path of the group that owns the epic (REQUIRED).
                 Examples: '42', 'my-group', 'parent-group/subgroup'
        epic_iid: The internal epic ID within the group (REQUIRED).
                 Examples: 42, 15, 7
        epic_issue_id: The epic-issue association ID (REQUIRED).
                      Get this from list_epic_issues response.
                      Examples: 54321, 98765
        move_before_id: ID of association to move this issue before (OPTIONAL).
                       Either move_before_id OR move_after_id should be specified.
        move_after_id: ID of association to move this issue after (OPTIONAL).
                      Either move_before_id OR move_after_id should be specified.

    Example Usage:
        - Move issue to top: group_id='team', epic_iid=42, epic_issue_id=54321, move_before_id=12345
        - Move issue down: group_id='team', epic_iid=42, epic_issue_id=54321, move_after_id=67890
    """

    group_id: str = Field(
        ...,
        description="The numeric ID or URL-encoded path of the group"
    )
    epic_iid: int = Field(
        ...,
        description="The internal epic ID within the group"
    )
    epic_issue_id: int = Field(
        ...,
        description="The epic-issue association ID"
    )
    move_before_id: int | None = Field(
        None,
        description="ID of association to move this issue before"
    )
    move_after_id: int | None = Field(
        None,
        description="ID of association to move this issue after"
    )
