# Neo4j Query Security

## Overview

This plugin implements security measures to prevent Cypher injection attacks while maintaining a simple, familiar interface.

## Security Approach

The implementation uses **automatic security validation** with the original query interface, providing the best of both worlds: simplicity and security.

```python
# ✅ SECURE - Simple interface with automatic protection
{
  "query": "MATCH (n:Person {name: $name}) RETURN n",
  "parameters": {"name": "John"}
}
```

## Security Features

### 1. **Dangerous Operation Blocking**

The following operations are automatically blocked:
- `DETACH DELETE` - Prevents data deletion
- `DELETE` - Prevents unauthorized deletions  
- `DROP` - Prevents schema/database deletion
- `CREATE DATABASE/USER/ROLE` - Prevents administrative operations
- `CALL db.*` / `CALL dbms.*` - Prevents system procedure calls

### 2. **Automatic LIMIT Protection**

- Automatically adds `LIMIT 1000` to queries without limits
- Caps existing limits to maximum 1000 results
- Prevents resource exhaustion attacks

### 3. **Query Length Validation**

- Maximum query length: 2000 characters
- Prevents buffer overflow attacks

### 4. **Built-in Parameterization Support**

Use Neo4j's standard parameterization syntax:

```python
# ✅ SECURE - Parameters are safely handled
{
  "query": "MATCH (n:Person {name: $name, age: $age}) RETURN n",
  "parameters": {"name": "John", "age": 30}
}
```

## Usage Examples

### Simple Node Search

```python
{
  "query": "MATCH (n:Person {name: $name}) RETURN n",
  "parameters": {"name": "Alice"}
}
```

### Relationship Queries

```python
{
  "query": "MATCH (a:Person)-[r:KNOWS]->(b:Person) WHERE a.name = $name RETURN r, b",
  "parameters": {"name": "Bob"}
}
```

### Path Queries

```python
{
  "query": "MATCH p = (start:Person {id: $startId})-[*1..3]-(end) RETURN p",
  "parameters": {"startId": "123"}
}
```

### Complex Filtering

```python
{
  "query": "MATCH (n:Person) WHERE n.age > $minAge AND n.city = $city RETURN n",
  "parameters": {"minAge": 25, "city": "New York"}
}
```

## Migration from Complex Implementation

**Before (Complex):**
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
  - name: relationship_type
    type: string
  - name: limit
    type: number
```

**After (Simplified):**
```yaml
parameters:
  - name: query
    type: string
  - name: parameters
    type: object
```

## What's Blocked vs Allowed

### ❌ Blocked (Dangerous Operations)

```python
"MATCH (n) DETACH DELETE n"           # Data deletion
"DROP DATABASE mydb"                  # Schema deletion
"CALL db.stats()"                     # System procedures
"CREATE USER admin"                   # Administrative operations
"DELETE n WHERE n.id = 1"            # Unparameterized deletion
```

### ✅ Allowed (Safe Operations)

```python
"MATCH (n:Person) RETURN n"                               # Simple queries
"MATCH (a)-[r]->(b) RETURN a, r, b"                      # Relationship queries
"MATCH (n:Person {name: $name}) RETURN n"                # Parameterized queries
"MATCH (n) WHERE n.age > $age RETURN n LIMIT 100"        # Filtered queries
```

## Security Benefits

1. **Familiar Interface**: Keep using standard Cypher syntax
2. **Automatic Protection**: Security is transparent to users
3. **Parameterization Support**: Full Neo4j parameter support
4. **Resource Protection**: Automatic LIMIT enforcement
5. **Operation Filtering**: Dangerous operations blocked
6. **Length Limits**: Prevents malformed queries

## Best Practices

1. **Always use parameters** for user values: `{name: $name}` not `{name: 'user_input'}`
2. **Keep queries focused**: Single-purpose queries are more secure
3. **Use appropriate limits**: Specify reasonable LIMIT values
4. **Test with parameters**: Verify parameterized queries work as expected

This simplified approach provides strong security while maintaining the familiar Cypher query interface that users expect.