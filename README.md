# neo4j_query Dify Plugin

**Version:** 0.0.1

**Type:** tool

## Description

A secure Neo4j plugin for Dify that uses parameterized queries to prevent prompt injection attacks. The plugin provides structured parameters for common graph database operations instead of accepting raw Cypher queries.

## Security Features

- ✅ **Parameterized queries** - No direct execution of user input
- ✅ **Input validation** - Identifiers validated against safe patterns  
- ✅ **Value sanitization** - Property values escaped for safety
- ✅ **Query whitelisting** - Only predefined query patterns allowed
- ✅ **Resource protection** - Results limited to prevent abuse

See [SECURITY.md](SECURITY.md) for detailed security documentation.

## Quick start guide

1. Install Dify Plugin Development Scaffold (CLI) by following instruction from https://docs.dify.ai/plugin-dev-en/0211-getting-started-dify-tool#1-1-installing-the-dify-plugin-development-scaffold-cli
2. Package plugin by going to the parent folder of dify_neo4j and run command:
`./dify plugin package dify_neo4j`
3. Upload plugin to your Dify instance (in plugins tab)
4. Create workflows using the plugin as a node or as a tool for agent

## Recommendation for use

If you are using plugin as a tool for agent, it is a good idea to pass to the LLM as a context the schema of your graph. With large graphs, natural language question to cypher may fail, and therefore it is also a good idea to ask LLM to first create a subgraph with just relevant nodes and edges to answer the question and than in the second step to generate Cypher and execute it on your KG. 

## Plugin Privacy Protection
This plugin sends query to the Aura instance, or URL deployment of Neo4j, and gets data from the graph in the instance. It is not sending or retaining any data about user anywhere apart from query and log-in details to the specified URL with Neo4j Aura

## Contributors
* Nikola Milosevic



