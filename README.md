# neo4j_query Dify Plugin

**Version:** 0.0.1

**Type:** tool

## Description

The Dify Neo4j Plugin (dify_neo4j) is an integration tool designed to connect the Dify.ai platform with Neo4j graph databases, enabling powerful graph-based data exploration and querying within Dify workflows. This plugin provides seamless access to Neo4j's query engine by allowing Dify agents or workflows to send Cypher queries directly to a specified Neo4j Aura instance or URL-based Neo4j deployment. With the plugin, users can harness the expressive power of graph queries for knowledge graph applications, recommendations, search, and data analytics, all orchestrated via Dify's no-code or agentic workflows.

A key feature of the plugin is its support for integrating database schema context into LLM-powered flows, which is essential for generating accurate Cypher queries from natural language questions—especially on large knowledge graphs where context is critical. The recommended best practice is to provide the LLM with the schema and, for complex queries, first generate a subgraph relevant to the user's question before assembling and executing the final Cypher statement. The plugin respects data privacy by confining all transmitted information to the Neo4j instance, without sending user data to third parties except for query execution and required authentication with Neo4j services.

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



