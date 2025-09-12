# Dynamic Work Item Type Discovery

## Overview

The GitLab MCP Server now features **automatic dynamic work item type discovery**, eliminating the need for hardcoded type mappings that vary between GitLab instances.

## How It Works

### Server Startup
- On server initialization, the system automatically queries your GitLab instance to discover available work item types
- Creates a mapping between human-readable type names (e.g., "ISSUE", "TASK") and GitLab global IDs (e.g., "gid://gitlab/WorkItems::Type/2")
- Falls back to common default types if discovery fails

### Type Resolution
- **Input Flexibility**: Accept both type names and global IDs
- **Case Insensitive**: "issue", "Issue", "ISSUE" all work the same
- **Alias Support**: Handles variations like "TEST_CASE" and "TEST CASE"
- **Automatic Resolution**: Converts type names to required global IDs transparently

## Benefits

1. **Instance Agnostic**: Works across different GitLab instances without configuration
2. **User Friendly**: Use intuitive type names instead of cryptic global IDs
3. **Maintainable**: No hardcoded type mappings to update
4. **Robust**: Graceful fallback when discovery fails
5. **Performance**: Types discovered once at startup, cached for session

## Usage Examples

### Creating Work Items
```python
# Using type names (preferred)
create_work_item(work_item_type_id="ISSUE", title="Fix login bug")
create_work_item(work_item_type_id="TASK", title="Write unit tests")
create_work_item(work_item_type_id="EPIC", title="User authentication")

# Using global IDs (still supported)
create_work_item(work_item_type_id="gid://gitlab/WorkItems::Type/2", title="Fix login bug")
```

### Filtering Work Items
```python
# Using type names
list_work_items(work_item_types=["ISSUE", "TASK"])
list_work_items(work_item_types=["EPIC"])

# Mixed usage
list_work_items(work_item_types=["ISSUE", "gid://gitlab/WorkItems::Type/4"])
```

## Supported Type Names

The system automatically discovers available types but commonly supports:

- **EPIC**: Top-level planning containers
- **ISSUE**: Standard work items for features and bugs  
- **TASK**: Granular implementation items
- **INCIDENT**: Service disruption tracking
- **TEST_CASE**: Quality assurance items
- **REQUIREMENT**: Product/business requirements
- **OBJECTIVE**: High-level business goals (OKR)
- **KEY_RESULT**: Measurable outcomes for objectives
- **TICKET**: General purpose work items

## Type Aliases

The system handles common variations:
- "KEY_RESULT" and "KEY RESULT"
- "TEST_CASE" and "TEST CASE"  
- All case variations (uppercase, lowercase, mixed case)

## Error Handling

- **Unknown Types**: Clear error messages when type names don't exist
- **Discovery Failure**: Automatic fallback to common default types
- **Permissions**: Graceful handling when type discovery requires specific permissions

## Technical Details

### Discovery Process
1. Query accessible project for work item types via GraphQL
2. Build bidirectional mappings (name ↔ global ID)
3. Add common aliases and case variations
4. Cache mappings for session duration

### Fallback Types
When discovery fails, uses these defaults:
- EPIC: gid://gitlab/WorkItems::Type/1
- ISSUE: gid://gitlab/WorkItems::Type/2  
- INCIDENT: gid://gitlab/WorkItems::Type/3
- TASK: gid://gitlab/WorkItems::Type/4
- TEST_CASE: gid://gitlab/WorkItems::Type/5
- REQUIREMENT: gid://gitlab/WorkItems::Type/6
- OBJECTIVE: gid://gitlab/WorkItems::Type/7
- KEY_RESULT: gid://gitlab/WorkItems::Type/8
- TICKET: gid://gitlab/WorkItems::Type/9

## Implementation Files

- `src/services/work_item_types.py`: Core type management logic
- `server.py`: Server startup integration
- `src/services/work_items.py`: Type resolution in work item operations
- `tests/conftest.py`: Test-time type discovery

## Migration Notes

### Before Dynamic Discovery
```python
# Required hardcoded global IDs
create_work_item(work_item_type_id="gid://gitlab/WorkItems::Type/2", ...)
```

### After Dynamic Discovery  
```python
# Use intuitive type names
create_work_item(work_item_type_id="ISSUE", ...)
# Global IDs still work for backward compatibility
create_work_item(work_item_type_id="gid://gitlab/WorkItems::Type/2", ...)
```

## Performance Impact

- **Startup**: Small one-time GraphQL query during server initialization
- **Runtime**: Zero performance impact - types cached in memory
- **Network**: No additional API calls during normal operations

## Future Enhancements

- Real-time type discovery when new types are added to GitLab instance
- Enhanced alias support based on usage patterns
- Type validation and suggestions for typos
- Integration with GitLab's work item type administration APIs