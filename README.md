# Neo4j Query Plugin for Dify

**Version:** 1.0.0

**Type:** Tool

## Overview

The Neo4j Query Plugin is a secure and efficient integration tool that connects Dify.ai with Neo4j graph databases. It enables powerful graph-based data exploration, querying, and manipulation within Dify workflows and AI agents. The plugin supports both Neo4j Aura cloud instances and locally hosted Neo4j deployments.

## Key Features

### 🔒 Security
- **Parameterized queries** - Prevents Cypher injection attacks
- **Preflight validation** - EXPLAIN-based query validation before execution
- **Write query protection** - Optional write operations with explicit user consent
- **Query length limits** - Maximum 2000 characters per query
- **Resource limits** - Configurable maximum record limits (default: 1000)

### ⚡ Performance
- **Singleton driver pattern** - Efficient connection reuse
- **Streaming results** - Memory-efficient record fetching with configurable fetch_size
- **Connection pooling** - Built-in Neo4j driver connection management
- **User agent tracking** - Identifies plugin traffic in Neo4j logs

### 🎯 Flexibility
- **Multi-database support** - Query different databases within the same instance
- **Read/Write control** - Granular control over query capabilities
- **Both cloud and local** - Works with Neo4j Aura and self-hosted instances
- **Parameterized queries** - Safe value substitution in Cypher queries

## Latest Updates (v1.0.0)

- ✨ **Write query protection** with explicit checkbox and warnings
- ✨ **Preflight EXPLAIN checks** for syntax validation and query type detection
- ✨ **Database parameter** for multi-database support
- ✨ **Configurable record limits** with efficient streaming
- ✨ **User agent identification** for tracking plugin usage
- ✨ **Improved error messages** with detailed validation feedback
- ✨ **Thread-safe driver management** with proper cleanup
- ✨ **Better credential validation** with specific error messages
- 🔧 Renamed credentials from "Aura" to "Neo4j" for clarity
- 🔧 Optimized memory usage with itertools.islice
- 🔧 Enhanced parameter documentation with examples

## Installation

### Prerequisites
- Dify instance (self-hosted or cloud)
- Neo4j database (Aura or self-hosted)
- Dify Plugin Development Scaffold (CLI)

### Steps

1. **Install Dify Plugin CLI**
   ```bash
   # Follow instructions from Dify documentation
   # https://docs.dify.ai/plugin-dev-en/0211-getting-started-dify-tool
   ```

2. **Package the Plugin**
   ```bash
   # Navigate to parent folder of dify_neo4j
   ./dify plugin package dify_neo4j
   ```

3. **Upload to Dify**
   - Go to your Dify instance
   - Navigate to Plugins tab
   - Upload the packaged plugin

4. **Configure Credentials**
   - **Neo4j URL**: Your connection URL (e.g., `neo4j+s://xxxxx.databases.neo4j.io` or `bolt://localhost:7687`)
   - **Neo4j Username**: Your database username
   - **Neo4j Password**: Your database password

5. **Use in Workflows**
   - Add as a tool node in workflows
   - Configure as a tool for AI agents

## Usage

### Basic Query
```json
{
  "query": "MATCH (p:Person) RETURN p.name, p.age LIMIT 10",
  "parameters": {}
}
```

### Parameterized Query
```json
{
  "query": "MATCH (p:Person {name: $name}) RETURN p",
  "parameters": {"name": "Alice"}
}
```

### Multi-Database Query
```json
{
  "query": "MATCH (n:Node) RETURN n LIMIT 5",
  "database": "movies"
}
```

### Write Query (with permission)
```json
{
  "query": "CREATE (p:Person {name: $name, age: $age}) RETURN p",
  "parameters": {"name": "Bob", "age": 30},
  "allow_write_queries": true
}
```

### Configuration Options

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Cypher query to execute |
| parameters | object | No | {} | Query parameters (JSON object) |
| database | string | No | null | Target database name |
| max_records | number | No | 1000 | Maximum records to return |
| allow_write_queries | boolean | No | false | Enable write operations |

## Best Practices

### 1. Schema Context for LLMs
When using the plugin with AI agents, provide the graph schema as context:
```
Provide your LLM with:
- Node labels and their properties
- Relationship types
- Constraints and indexes
```

### 2. Two-Step Query Approach
For complex queries on large graphs:
1. **First query**: Extract relevant subgraph
2. **Second query**: Execute detailed analysis on the subgraph

### 3. Always Use Parameters
```cypher
# ✅ GOOD - Parameterized
MATCH (p:Person {name: $name}) RETURN p

# ❌ BAD - String concatenation
MATCH (p:Person {name: 'Alice'}) RETURN p
```

### 4. Write Protection
- Keep `allow_write_queries` disabled by default
- Only enable when necessary
- Review queries before execution
- Test on non-production databases first

## Security

See [SECURITY.md](SECURITY.md) for comprehensive security documentation including:
- Query validation mechanisms
- Write protection details
- Preflight checks
- Parameter handling
- Best practices

## Privacy

This plugin:
- ✅ Sends queries only to your specified Neo4j instance
- ✅ Does not store or transmit data to third parties
- ✅ Credentials are securely stored in Dify
- ✅ All data remains within your Neo4j infrastructure

## Contributors
* Nikola Milosevic



