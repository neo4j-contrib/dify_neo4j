from collections.abc import Generator
from typing import Any
from neo4j import GraphDatabase, basic_auth
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Neo4jQueryTool(Tool):
    # Predefined query templates with parameter placeholders
    QUERY_TEMPLATES = {
        "find_nodes": {
            "query": "MATCH (n:$node_label) WHERE n.$property_name = $property_value RETURN n LIMIT $limit",
            "query_no_label": "MATCH (n) WHERE n.$property_name = $property_value RETURN n LIMIT $limit",
            "query_no_property": "MATCH (n:$node_label) RETURN n LIMIT $limit",
            "query_minimal": "MATCH (n) RETURN n LIMIT $limit"
        },
        "find_relationships": {
            "query": "MATCH (a)-[r:$relationship_type]->(b) WHERE a:$node_label RETURN a, r, b LIMIT $limit",
            "query_no_type": "MATCH (a:$node_label)-[r]->(b) RETURN a, r, b LIMIT $limit",
            "query_no_label": "MATCH (a)-[r:$relationship_type]->(b) RETURN a, r, b LIMIT $limit",
            "query_minimal": "MATCH (a)-[r]->(b) RETURN a, r, b LIMIT $limit"
        },
        "path_query": {
            "query": "MATCH p = (start:$node_label {$property_name: $property_value})-[*1..3]-(end) RETURN p LIMIT $limit",
            "query_no_property": "MATCH p = (start:$node_label)-[*1..3]-(end) RETURN p LIMIT $limit"
        },
        "neighbor_query": {
            "query": "MATCH (n:$node_label {$property_name: $property_value})--(neighbor) RETURN n, neighbor LIMIT $limit",
            "query_no_property": "MATCH (n:$node_label)--(neighbor) RETURN n, neighbor LIMIT $limit"
        }
    }
    
    def _validate_identifier(self, identifier: str) -> bool:
        """Validate that identifier contains only safe characters"""
        if not identifier:
            return False
        # Allow only alphanumeric characters, underscores, and limited special characters
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier) is not None
    
    def _sanitize_property_value(self, value: str) -> str:
        """Sanitize property values to prevent injection"""
        if not isinstance(value, str):
            return str(value)
        # Remove or escape potentially dangerous characters
        return value.replace("'", "\\'").replace('"', '\\"').replace('\\', '\\\\')
    
    def _build_parameterized_query(self, tool_parameters: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Build a parameterized query based on the query type and parameters"""
        query_type = tool_parameters.get("query_type")
        node_label = tool_parameters.get("node_label", "").strip()
        property_name = tool_parameters.get("property_name", "").strip()
        property_value = tool_parameters.get("property_value", "").strip()
        relationship_type = tool_parameters.get("relationship_type", "").strip()
        limit = min(int(tool_parameters.get("limit", 100)), 1000)  # Cap at 1000
        
        if query_type not in self.QUERY_TEMPLATES:
            raise ValueError(f"Invalid query type: {query_type}")
        
        templates = self.QUERY_TEMPLATES[query_type]
        params = {"limit": limit}
        
        # Validate identifiers to prevent injection
        if node_label and not self._validate_identifier(node_label):
            raise ValueError(f"Invalid node label: {node_label}")
        if property_name and not self._validate_identifier(property_name):
            raise ValueError(f"Invalid property name: {property_name}")
        if relationship_type and not self._validate_identifier(relationship_type):
            raise ValueError(f"Invalid relationship type: {relationship_type}")
        
        # Select appropriate template based on available parameters
        if query_type in ["find_nodes"]:
            if node_label and property_name and property_value:
                query_template = templates["query"]
                params.update({
                    "node_label": node_label,
                    "property_name": property_name,
                    "property_value": self._sanitize_property_value(property_value)
                })
            elif node_label and not (property_name and property_value):
                query_template = templates["query_no_property"]
                params["node_label"] = node_label
            elif property_name and property_value and not node_label:
                query_template = templates["query_no_label"]
                params.update({
                    "property_name": property_name,
                    "property_value": self._sanitize_property_value(property_value)
                })
            else:
                query_template = templates["query_minimal"]
        
        elif query_type in ["find_relationships"]:
            if node_label and relationship_type:
                query_template = templates["query"]
                params.update({
                    "node_label": node_label,
                    "relationship_type": relationship_type
                })
            elif node_label and not relationship_type:
                query_template = templates["query_no_type"]
                params["node_label"] = node_label
            elif relationship_type and not node_label:
                query_template = templates["query_no_label"]
                params["relationship_type"] = relationship_type
            else:
                query_template = templates["query_minimal"]
        
        elif query_type in ["path_query", "neighbor_query"]:
            if node_label and property_name and property_value:
                query_template = templates["query"]
                params.update({
                    "node_label": node_label,
                    "property_name": property_name,
                    "property_value": self._sanitize_property_value(property_value)
                })
            elif node_label:
                query_template = templates.get("query_no_property", templates["query"])
                params["node_label"] = node_label
            else:
                raise ValueError(f"Node label is required for {query_type}")
        
        # Replace template placeholders with actual identifiers (not parameterized for identifiers)
        if "node_label" in params and "$node_label" in query_template:
            query_template = query_template.replace("$node_label", params.pop("node_label"))
        if "property_name" in params and "$property_name" in query_template:
            query_template = query_template.replace("$property_name", params.pop("property_name"))  
        if "relationship_type" in params and "$relationship_type" in query_template:
            query_template = query_template.replace("$relationship_type", params.pop("relationship_type"))
        
        return query_template, params

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Access credentials from provider config
        url = self.runtime.credentials.get("AURA_URL")
        username = self.runtime.credentials.get("AURA_USERNAME")
        password = self.runtime.credentials.get("AURA_PASSWORD")

        if not all([url, username, password]):
            yield self.create_text_message("Missing required credentials.")
            return

        try:
            # Build parameterized query
            query, params = self._build_parameterized_query(tool_parameters)
            
            # Execute parameterized query
            driver = GraphDatabase.driver(url, auth=basic_auth(username, password))
            with driver.session() as session:
                result = session.run(query, params)
                records = [record.data() for record in result]
            driver.close()

            yield self.create_json_message({
                "results": records,
                "query_info": {
                    "query_type": tool_parameters.get("query_type"),
                    "parameters_used": {k: v for k, v in params.items() if k != "property_value"},
                    "result_count": len(records)
                }
            })
            
            if records:
                yield self.create_text_message(f"Found {len(records)} results from Neo4j query.")
            else:
                yield self.create_text_message("No results found for the specified query.")
                
        except ValueError as e:
            yield self.create_text_message(f"Invalid query parameters: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error executing Neo4j query: {str(e)}")
