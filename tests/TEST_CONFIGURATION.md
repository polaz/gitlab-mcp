# GitLab MCP Server Test Configuration

This document describes the test configuration for the GitLab MCP Server against the GitLab instance at `https://git.private.systems`.

## Test Environment Structure

The tests use the existing "test" group hierarchy in the GitLab instance:

### Group Structure
- **Root Group**: `test`
- **Subgroup**: `test/test_subgroup`

### Available Projects
- `test/test_subgroup/test_project` - Main test project in subgroup
- `test/test_project_in_parent` - Test project directly in root group

## Work Item Type Mappings

This GitLab instance has the following work item type mappings (discovered via GraphQL query):

| Type Name    | Work Item Type ID                      | Icon Name             |
|--------------|---------------------------------------|-----------------------|
| Epic         | gid://gitlab/WorkItems::Type/8        | issue-type-epic       |
| Issue        | gid://gitlab/WorkItems::Type/1        | issue-type-issue      |
| Incident     | gid://gitlab/WorkItems::Type/2        | issue-type-incident   |
| Test Case    | gid://gitlab/WorkItems::Type/3        | issue-type-test-case  |
| Requirement  | gid://gitlab/WorkItems::Type/4        | issue-type-requirements |
| Task         | gid://gitlab/WorkItems::Type/5        | issue-type-task       |
| Objective    | gid://gitlab/WorkItems::Type/6        | issue-type-objective  |
| Key Result   | gid://gitlab/WorkItems::Type/7        | issue-type-keyresult  |
| Ticket       | gid://gitlab/WorkItems::Type/9        | issue-type-issue      |

**Important**: Work item types must be referenced by their global ID, not by name. The GraphQL API does not accept type names as input.

## Feature Flags and Limitations

- **Group-level Work Items**: The `create_group_level_work_items` feature flag is disabled
  - This flag controls creation of certain work item types at the group/namespace level via the unified Work Items API
  - **IMPORTANT**: This flag has NO relation to Epic creation - Epics are ALWAYS group-level only
  - Epics must be created with `namespace_path` (group path), never with `project_path`
  - Other work item types (Issue, Task, etc.) can be created at project level with `project_path`

## Test Configuration

### Environment Variables
```bash
GITLAB_API_URL=https://git.private.systems
GITLAB_PERSONAL_ACCESS_TOKEN=<token>
```

### Test Groups and Projects
- **Test Group**: `test`
- **Test Subgroup**: `test/test_subgroup`
- **Primary Test Project**: `test/test_subgroup/test_project`
- **Secondary Test Project**: `test/test_project_in_parent`

### Test Data Cleanup
All tests use the cleanup system to ensure:
- Created work items are deleted after tests
- No test pollution between test runs
- Proper resource management

## Running Tests

```bash
# Run single test
GITLAB_API_URL="https://git.private.systems" GITLAB_PERSONAL_ACCESS_TOKEN="<token>" uv run pytest tests/test_work_items.py::TestWorkItemsAPI::test_create_issue_work_item -v

# Run all work item tests
GITLAB_API_URL="https://git.private.systems" GITLAB_PERSONAL_ACCESS_TOKEN="<token>" uv run pytest tests/test_work_items.py::TestWorkItemsAPI -v

# Run all tests
GITLAB_API_URL="https://git.private.systems" GITLAB_PERSONAL_ACCESS_TOKEN="<token>" uv run pytest tests/ -v
```

## Notes

- Work item type assertions should be flexible to account for instance-specific mappings
- Group-level operations should be tested at project level where feature flags restrict group-level access
- The cleanup system automatically handles test isolation and resource cleanup