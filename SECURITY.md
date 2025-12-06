# Neo4j Query Plugin - Security

## Overview

This plugin implements comprehensive security measures to prevent Cypher injection attacks, unauthorized database modifications, and resource exhaustion while maintaining a simple and familiar interface.

## Security Architecture

The plugin uses a **multi-layered security approach**:

1. **Preflight Validation** - EXPLAIN-based query checks before execution
2. **Query Type Detection** - Automatic read/write classification
3. **Write Protection** - Explicit user consent required for modifications
4. **Resource Limits** - Configurable record and query size limits
5. **Parameterization** - Safe value substitution in queries

```python
# ✅ SECURE - Parameterized query with validation
{
  "query": "MATCH (n:Person {name: $name}) RETURN n",
  "parameters": {"name": "John"}
}
```

## Security Features

### 1. **Preflight EXPLAIN Checks**

Before executing any query, the plugin runs `EXPLAIN` to:
- **Validate syntax** - Catch errors before execution
- **Detect query type** - Identify read ('r'), write ('w'), read-write ('rw'), or schema ('s') queries
- **Enforce permissions** - Block write queries unless explicitly allowed

```python
# Plugin automatically runs: EXPLAIN <your_query>
# Checks summary.query_type before actual execution
```

### 2. **Write Query Protection**

**Default Behavior (Secure):**
- ❌ `CREATE` operations blocked
- ❌ `DELETE` / `DETACH DELETE` blocked
- ❌ `SET` / `REMOVE` operations blocked
- ❌ `MERGE` operations blocked
- ✅ `MATCH` and `RETURN` allowed
- ✅ Schema queries (`SHOW`, `CREATE INDEX`) allowed

**When `allow_write_queries` is enabled:**
- ⚠️ User explicitly opts in via checkbox
- ⚠️ Warning messages displayed
- ✅ All write operations permitted
- ❌ Administrative operations still blocked

**Always Blocked (Even with Write Permission):**
- `CREATE DATABASE` / `DROP DATABASE`
- `CREATE USER` / `DROP USER`
- `CREATE ROLE` / `DROP ROLE`
- `SET PASSWORD`
- `CALL dbms.*` system procedures

### 3. **Resource Limits**

**Query Length:**
- Maximum: 2000 characters
- Prevents buffer overflow attacks

**Record Limits:**
- Default: 1000 records per query
- Configurable via `max_records` parameter
- Uses efficient streaming with `fetch_size`
- Prevents memory exhaustion

**Connection Management:**
- Singleton driver pattern per tool instance
- Automatic connection pooling
- Proper cleanup on destruction

### 4. **Parameterized Queries**

Always use Neo4j's standard parameterization syntax:

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

### Write Operations (Requires Permission)

```python
{
  "query": "CREATE (p:Person {name: $name, age: $age}) RETURN p",
  "parameters": {"name": "Charlie", "age": 35},
  "allow_write_queries": true
}
```

```python
{
  "query": "MATCH (p:Person {id: $id}) SET p.status = $status RETURN p",
  "parameters": {"id": "123", "status": "active"},
  "allow_write_queries": true
}
```

## Error Messages

The plugin provides specific error messages for different security violations:

### Write Query Blocked
```
Write queries are not allowed. Query type: 'w'. 
Enable 'Allow Write Queries' to execute write operations.
```

### Syntax Error
```
Query syntax error: Neo.ClientError.Statement.SyntaxError
```

### Query Too Long
```
Query too long (max 2000 characters)
```

## Validation Flow

```
1. Basic Validation
   ├─ Check query is non-empty string
   └─ Check query length ≤ 2000 chars

2. Preflight Check
   ├─ Execute: EXPLAIN <query>
   ├─ Check for syntax errors
   ├─ Get query_type from summary
   └─ Validate: if write_disabled && type not in ['r','s'] → REJECT

3. Query Execution
   ├─ Execute query with parameters
   ├─ Stream results with fetch_size
   └─ Limit to max_records
```

## Best Practices

### 1. Always Use Parameters
```python
# ✅ GOOD
{"query": "MATCH (n:Person {name: $name}) RETURN n", "parameters": {"name": user_input}}

# ❌ BAD - Vulnerable to injection
{"query": f"MATCH (n:Person {{name: '{user_input}'}}) RETURN n"}
```

### 2. Enable Write Queries Sparingly
- Keep disabled by default
- Enable only for trusted operations
- Review queries before execution
- Use in controlled workflows

### 3. Limit Result Sets
```python
# Use max_records parameter
{
  "query": "MATCH (n:Person) RETURN n",
  "max_records": 100  # Limit to 100 records
}
```

### 4. Multi-Database Isolation
```python
# Target specific databases
{
  "query": "MATCH (n:Node) RETURN n",
  "database": "production"  # Isolate to specific database
}
```

## Credential Security

- **Storage**: Credentials encrypted in Dify platform
- **Transmission**: HTTPS/TLS for all connections
- **Validation**: Connection tested during credential setup
- **Timeout**: 10-second connection timeout prevents hanging
- **No Logging**: Credentials never logged or exposed

## Reporting Security Issues

If you discover a security vulnerability:
1. **Do NOT** open a public issue
2. Email: security@neo4j.com
3. Include detailed reproduction steps
4. Allow time for patching before disclosure

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