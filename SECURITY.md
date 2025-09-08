# Neo4j Query Security

## Overview

This plugin has been enhanced with parameterized queries to prevent prompt injection attacks. The implementation replaces direct query execution with secure, structured parameters and predefined query templates.

## Security Features

### 1. Parameterized Queries

Instead of accepting raw Cypher queries, the tool now uses predefined templates with proper Neo4j parameterization:

```python
# ❌ VULNERABLE (before)
session.run(user_query)  # Direct execution of user input

# ✅ SECURE (after)  
session.run(query_template, sanitized_params)  # Parameterized execution
```

### 2. Input Validation

All identifiers (labels, property names, relationship types) are validated:

- **Pattern**: `^[a-zA-Z_][a-zA-Z0-9_]*$`
- **Prevents**: SQL-style injections, special characters, command injection

```python
# ✅ Valid identifiers
"Person", "User123", "_internal", "valid_label"

# ❌ Invalid identifiers (rejected)
"Person'; DROP ALL;--", "User-Name", "123Invalid", "User.Property"
```

### 3. Value Sanitization

Property values are sanitized to escape dangerous characters:

```python
# Input: "John'; DELETE n;--"
# Output: "John\\'; DELETE n;--"
```

### 4. Query Type Restrictions

Only predefined query types are allowed:
- `find_nodes` - Find nodes by label and/or properties
- `find_relationships` - Find relationships between nodes
- `path_query` - Find paths between nodes
- `neighbor_query` - Find neighboring nodes

## Usage Examples

### Find Nodes

```yaml
query_type: find_nodes
node_label: Person
property_name: name
property_value: John
limit: 10
```

Generates: `MATCH (n:Person) WHERE n.name = $property_value RETURN n LIMIT $limit`

### Find Relationships

```yaml
query_type: find_relationships  
node_label: Person
relationship_type: KNOWS
limit: 20
```

Generates: `MATCH (a)-[r:KNOWS]->(b) WHERE a:Person RETURN a, r, b LIMIT $limit`

### Path Query

```yaml
query_type: path_query
node_label: Company
property_name: industry
property_value: Tech
limit: 5
```

Generates: `MATCH p = (start:Company {industry: $property_value})-[*1..3]-(end) RETURN p LIMIT $limit`

## Migration Guide

### Before (Vulnerable)

```yaml
parameters:
  - name: query
    type: string
    form: llm
```

Tool usage:
```cypher
MATCH (n:Person {name: "John"}) RETURN n
```

### After (Secure)

```yaml
parameters:
  - name: query_type
    type: select
    options: [find_nodes, find_relationships, path_query, neighbor_query]
  - name: node_label
    type: string
  - name: property_name  
    type: string
  - name: property_value
    type: string
  - name: limit
    type: number
    default: 100
```

Tool usage:
```yaml
query_type: find_nodes
node_label: Person
property_name: name
property_value: John
limit: 10
```

## Security Benefits

1. **Prevents Prompt Injection**: No direct query execution
2. **Input Validation**: All identifiers validated against safe patterns
3. **Value Sanitization**: Property values escaped for safety
4. **Query Whitelisting**: Only predefined query patterns allowed
5. **Resource Protection**: Result limits prevent resource exhaustion
6. **Parameter Separation**: Query structure separated from user data

## Testing

The implementation includes comprehensive security testing:

- ✅ Identifier validation prevents injection attempts
- ✅ Property value sanitization handles malicious input  
- ✅ Query building works for all supported patterns
- ✅ Integration testing confirms end-to-end security
- ✅ Edge case testing covers various attack scenarios

## Limitations

- Only supports predefined query patterns
- Complex custom queries not supported
- May require multiple tool calls for complex operations

For advanced use cases requiring custom queries, consider using the tool multiple times with different parameters to build up the required data.